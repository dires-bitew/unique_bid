from decimal import Decimal, InvalidOperation
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from auctions.models import Auction
from notifications.models import Notification

from notifications.services import (
    create_notification,
)
User = get_user_model()
from wallets.models import WalletTransaction
from wallets.services import (
    InsufficientFunds,
    WalletService,
)

from .models import (
    AuctionResult,
    Bid,
)


class BidError(Exception):
    pass


class AuctionNotOpen(BidError):
    pass


class InvalidBidAmount(BidError):
    pass


class BidLimitReached(BidError):
    pass


class DuplicateBidAmount(BidError):
    pass


class AuctionNotReadyToClose(BidError):
    pass


def normalize_bid_amount(amount):

    try:
        amount = Decimal(
            str(amount)
        ).quantize(
            Decimal("0.01")
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        raise InvalidBidAmount(
            "Invalid bid amount."
        )

    if amount <= 0:
        raise InvalidBidAmount(
            "Bid amount must be greater than zero."
        )

    return amount

class BidService:

    @classmethod
    @transaction.atomic
    def submit_bid(
        cls,
        user,
        auction_id,
        amount,
        client_request_id,
    ):

        amount = normalize_bid_amount(
            amount
        )

        auction = (
            Auction.objects
            .select_for_update()
            .select_related(
                "product",
            )
            .get(pk=auction_id)
        )

        now = timezone.now()

        # Idempotency protection.
        existing_bid = (
            Bid.objects
            .filter(
                client_request_id=client_request_id,
                user=user,
            )
            .first()
        )

        if existing_bid:
            return existing_bid, False

        if auction.status in (
            Auction.Status.CLOSED,
            Auction.Status.CANCELLED,
            Auction.Status.DRAFT,
        ):
            raise AuctionNotOpen(
                "This auction is not accepting bids."
            )

        if now < auction.start_at:
            raise AuctionNotOpen(
                "This auction has not started yet."
            )

        if now >= auction.end_at:
            raise AuctionNotOpen(
                "This auction has already ended."
            )

        if (
            amount < auction.minimum_bid
            or amount > auction.maximum_bid
        ):
            raise InvalidBidAmount(
                (
                    f"Bid must be between "
                    f"{auction.minimum_bid} and "
                    f"{auction.maximum_bid} ETB."
                )
            )

        if Bid.objects.filter(
            auction=auction,
            user=user,
            amount=amount,
            status=Bid.Status.ACCEPTED,
        ).exists():
            raise DuplicateBidAmount(
                "You already submitted this bid amount."
            )

        bid_count = (
            Bid.objects.filter(
                auction=auction,
                user=user,
                status=Bid.Status.ACCEPTED,
            )
            .count()
        )

        if (
            bid_count
            >= auction.max_bids_per_user
        ):
            raise BidLimitReached(
                "You have reached the maximum number of bids allowed."
            )

        fee = auction.bid_fee

        if fee is None:
            raise BidError(
                "This auction has no bid fee configured."
            )

        wallet, ledger = (
            WalletService.debit(
                user=user,
                amount=fee,

                transaction_type=(
                    WalletTransaction
                    .TransactionType
                    .BID_FEE
                ),

                description=(
                    f"Bid fee for auction "
                    f"#{auction.pk}"
                ),

                metadata={
                    "auction_id": auction.pk,
                    "bid_amount": str(amount),
                    "client_request_id":
                        str(client_request_id),
                },

                idempotency_key=(
                    f"bid:{client_request_id}"
                ),
            )
        )

        bid = Bid.objects.create(
            auction=auction,
            user=user,
            amount=amount,
            fee_charged=fee,
            wallet_transaction=ledger,
            client_request_id=client_request_id,
        )

        return bid, True
class AuctionClosingService:

    @classmethod
    @transaction.atomic
    def close_auction(
        cls,
        auction_id,
        force=False,
    ):

        auction = (
            Auction.objects
            .select_for_update()
            .select_related("product")
            .get(pk=auction_id)
        )

        existing_result = (
            AuctionResult.objects
            .filter(auction=auction)
            .first()
        )

        if existing_result:
            return existing_result

        if (
            auction.status
            == Auction.Status.CANCELLED
        ):

            result = (
                AuctionResult.objects.create(
                    auction=auction,
                    result_status=(
                        AuctionResult
                        .ResultStatus
                        .CANCELLED
                    ),
                )
            )

            return result

        now = timezone.now()

        if (
            not force
            and now < auction.end_at
        ):
            raise AuctionNotReadyToClose(
                "Auction has not reached its closing time."
            )

        unique_amount = (
            Bid.objects
            .filter(
                auction=auction,
                status=Bid.Status.ACCEPTED,
            )
            .values("amount")
            .annotate(
                bid_count=Count("id")
            )
            .filter(
                bid_count=1
            )
            .order_by("amount")
            .first()
        )

        if unique_amount is None:

            result = (
                AuctionResult.objects.create(
                    auction=auction,
                    result_status=(
                        AuctionResult
                        .ResultStatus
                        .NO_UNIQUE_BID
                    ),
                )
            )

        else:

            winning_amount = (
                unique_amount["amount"]
            )

            winning_bid = (
                Bid.objects
                .select_related("user")
                .get(
                    auction=auction,
                    amount=winning_amount,
                    status=Bid.Status.ACCEPTED,
                )
            )

            result = (
                AuctionResult.objects.create(
                    auction=auction,
                    winning_bid=winning_bid,
                    winner=winning_bid.user,
                    winning_amount=(
                        winning_amount
                    ),
                    result_status=(
                        AuctionResult
                        .ResultStatus
                        .WINNER_SELECTED
                    ),
                )
            )

        auction.status = (
            Auction.Status.CLOSED
        )

        auction.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        notify_auction_result(
            auction,
            result,
        )

        return result

class AuctionCancellationService:

    @classmethod
    @transaction.atomic
    def cancel_auction(
        cls,
        auction_id,
        cancelled_by,
        reason="",
    ):

        auction = (
            Auction.objects
            .select_for_update()
            .get(pk=auction_id)
        )

        if (
            auction.status
            == Auction.Status.CLOSED
        ):
            raise BidError(
                "A closed auction cannot be cancelled."
            )

        if (
            auction.status
            == Auction.Status.CANCELLED
        ):

            refunded_count = (
                Bid.objects.filter(
                    auction=auction,
                    status=Bid.Status.REFUNDED,
                ).count()
            )

            return (
                auction,
                refunded_count,
                Decimal("0.00"),
            )

        bids = list(
            Bid.objects
            .select_for_update()
            .select_related("user")
            .filter(
                auction=auction,
                status=Bid.Status.ACCEPTED,
            )
        )

        total_refunded = Decimal("0.00")

        refunds_by_user = defaultdict(
            lambda: Decimal("0.00")
        )

        for bid in bids:

            refund_transaction = None

            if bid.fee_charged > 0:

                wallet, refund_transaction = (
                    WalletService.credit(
                        user=bid.user,

                        amount=bid.fee_charged,

                        transaction_type=(
                            WalletTransaction
                            .TransactionType
                            .REFUND
                        ),

                        description=(
                            f"Refund for cancelled "
                            f"auction #{auction.pk}"
                        ),

                        created_by=cancelled_by,

                        metadata={
                            "auction_id":
                                auction.pk,

                            "bid_id":
                                bid.pk,

                            "original_fee_transaction":
                                str(
                                    bid
                                    .wallet_transaction
                                    .reference
                                )
                                if bid.wallet_transaction
                                else None,
                        },

                        idempotency_key=(
                            f"refund:bid:{bid.pk}"
                        ),
                    )
                )

            bid.status = Bid.Status.REFUNDED

            bid.refund_transaction = (
                refund_transaction
            )

            bid.save(
                update_fields=[
                    "status",
                    "refund_transaction",
                ]
            )

            total_refunded += (
                bid.fee_charged
            )

            refunds_by_user[
                bid.user_id
            ] += bid.fee_charged

        auction.status = (
            Auction.Status.CANCELLED
        )

        auction.cancellation_reason = reason

        auction.cancelled_at = timezone.now()

        auction.save(
            update_fields=[
                "status",
                "cancellation_reason",
                "cancelled_at",
                "updated_at",
            ]
        )

        AuctionResult.objects.get_or_create(
            auction=auction,
            defaults={
                "result_status":
                    AuctionResult
                    .ResultStatus
                    .CANCELLED
            },
        )

        users = User.objects.filter(
            id__in=refunds_by_user.keys()
        )

        for user in users:

            refunded_amount = (
                refunds_by_user[user.id]
            )

            create_notification(
                user=user,

                notification_type=(
                    Notification
                    .Type
                    .AUCTION_CANCELLED
                ),

                title="Auction cancelled",

                message=(
                    f"{auction.product.name} "
                    f"auction was cancelled. "
                    f"{refunded_amount} ETB "
                    f"has been returned to "
                    f"your wallet."
                ),

                data={
                    "auction_id":
                        auction.pk,

                    "refund_amount":
                        str(refunded_amount),
                },
            )

        return (
            auction,
            len(bids),
            total_refunded,
        )


def notify_auction_result(
    auction,
    result,
):

    user_ids = (
        Bid.objects
        .filter(
            auction=auction,
            status=Bid.Status.ACCEPTED,
        )
        .values_list(
            "user_id",
            flat=True,
        )
        .distinct()
    )

    users = User.objects.filter(
        id__in=user_ids
    )

    for user in users:

        if (
            result.result_status
            == AuctionResult
            .ResultStatus
            .NO_UNIQUE_BID
        ):

            create_notification(
                user=user,

                notification_type=(
                    Notification
                    .Type
                    .NO_UNIQUE_BID
                ),

                title="Auction ended",

                message=(
                    f"{auction.product.name} "
                    f"ended without a unique "
                    f"winning bid."
                ),

                data={
                    "auction_id":
                        auction.pk,
                },
            )

        elif (
            result.winner_id
            == user.id
        ):

            create_notification(
                user=user,

                notification_type=(
                    Notification
                    .Type
                    .AUCTION_WON
                ),

                title="You won!",

                message=(
                    f"You won "
                    f"{auction.product.name} "
                    f"with the lowest unique "
                    f"bid of "
                    f"{result.winning_amount} ETB."
                ),

                data={
                    "auction_id":
                        auction.pk,

                    "winning_amount":
                        str(
                            result.winning_amount
                        ),
                },
            )

        else:

            create_notification(
                user=user,

                notification_type=(
                    Notification
                    .Type
                    .AUCTION_ENDED
                ),

                title="Auction ended",

                message=(
                    f"{auction.product.name} "
                    f"auction has ended."
                ),

                data={
                    "auction_id":
                        auction.pk,
                },
            )
