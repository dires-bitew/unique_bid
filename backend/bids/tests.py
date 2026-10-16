from datetime import timedelta
from decimal import Decimal
import uuid

from django.test import TestCase
from django.utils import timezone

from accounts.models import User

from auctions.models import (
    Auction,
    BidFeeRule,
)

from products.models import Product

from wallets.models import (
    WalletTransaction,
)

from wallets.services import (
    WalletService,
)

from .models import (
    AuctionResult,
    Bid,
)

from .services import (
    AuctionClosingService,
    BidService,
    DuplicateBidAmount,
)

class BidEngineTests(TestCase):

    def setUp(self):

        self.admin = (
            User.objects.create_superuser(
                email="admin@example.com",
                password="StrongPass2026!",
            )
        )

        self.users = []

        for number in range(1, 7):

            user = User.objects.create_user(
                email=(
                    f"user{number}@example.com"
                ),
                password="StrongPass2026!",
            )

            WalletService.credit(
                user=user,
                amount=Decimal("1000.00"),
                transaction_type=(
                    WalletTransaction
                    .TransactionType
                    .TOP_UP
                ),
            )

            self.users.append(user)

        BidFeeRule.objects.create(
            name="Test Fee",
            min_product_price=Decimal(
                "0.00"
            ),
            max_product_price=Decimal(
                "100000.00"
            ),
            fixed_fee=Decimal(
                "10.00"
            ),
        )

        self.product = Product.objects.create(
            name="Test Phone",
            description="Testing",
            reference_price=Decimal(
                "50000.00"
            ),
        )

        now = timezone.now()

        self.auction = Auction.objects.create(
            product=self.product,
            created_by=self.admin,
            status=Auction.Status.OPEN,
            start_at=(
                now - timedelta(hours=1)
            ),
            end_at=(
                now + timedelta(hours=1)
            ),
            minimum_bid=Decimal(
                "1.00"
            ),
            maximum_bid=Decimal(
                "1000.00"
            ),
            max_bids_per_user=10,
        )

    def submit(
        self,
        user,
        amount,
    ):

        return BidService.submit_bid(
            user=user,
            auction_id=self.auction.pk,
            amount=Decimal(str(amount)),
            client_request_id=uuid.uuid4(),
        )[0]

    def test_bid_fee_is_deducted(self):

        user = self.users[0]

        self.submit(
            user,
            "25.00",
        )

        user.wallet.refresh_from_db()

        self.assertEqual(
            user.wallet.balance,
            Decimal("990.00"),
        )

    def test_duplicate_user_amount_rejected(
        self
    ):

        user = self.users[0]

        self.submit(
            user,
            "25.00",
        )

        with self.assertRaises(
            DuplicateBidAmount
        ):

            self.submit(
                user,
                "25.00",
            )


    def test_lowest_unique_bid_wins(
        self
    ):

        bids = [
            (
                self.users[0],
                "20.00",
            ),
            (
                self.users[1],
                "20.00",
            ),
            (
                self.users[2],
                "25.00",
            ),
            (
                self.users[3],
                "30.00",
            ),
            (
                self.users[4],
                "30.00",
            ),
            (
                self.users[5],
                "40.00",
            ),
        ]

        for user, amount in bids:
            self.submit(
                user,
                amount,
            )

        result = (
            AuctionClosingService
            .close_auction(
                auction_id=(
                    self.auction.pk
                ),
                force=True,
            )
        )

        self.assertEqual(
            result.result_status,
            (
                AuctionResult
                .ResultStatus
                .WINNER_SELECTED
            ),
        )

        self.assertEqual(
            result.winning_amount,
            Decimal("25.00"),
        )

        self.assertEqual(
            result.winner,
            self.users[2],
        )

    def test_close_is_idempotent(self):

        self.submit(
            self.users[0],
            "25.00",
        )

        first = (
            AuctionClosingService
            .close_auction(
                self.auction.pk,
                force=True,
            )
        )

        second = (
            AuctionClosingService
            .close_auction(
                self.auction.pk,
                force=True,
            )
        )

        self.assertEqual(
            first.pk,
            second.pk,
        )

        self.assertEqual(
            AuctionResult.objects.filter(
                auction=self.auction
            ).count(),
            1,
        )