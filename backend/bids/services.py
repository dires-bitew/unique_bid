from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from auctions.models import Auction

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

        return result