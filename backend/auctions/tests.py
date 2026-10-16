from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from products.models import Product

from .models import (
    Auction,
    BidFeeRule,
)


class BidFeeTests(TestCase):

    def setUp(self):

        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass2026!",
        )

    def test_fixed_fee_rule(self):

        rule = BidFeeRule.objects.create(
            name="Medium",
            min_product_price=Decimal(
                "5000"
            ),
            max_product_price=Decimal(
                "15000"
            ),
            fixed_fee=Decimal(
                "20"
            ),
        )

        fee = rule.calculate_fee(
            Decimal("8000")
        )

        self.assertEqual(
            fee,
            Decimal("20.00"),
        )

    def test_percentage_fee_rule(self):

        rule = BidFeeRule.objects.create(
            name="Premium",
            min_product_price=Decimal(
                "100000"
            ),
            percentage_fee=Decimal(
                "0.10"
            ),
            minimum_fee=Decimal(
                "100"
            ),
            maximum_fee=Decimal(
                "300"
            ),
        )

        fee = rule.calculate_fee(
            Decimal("200000")
        )

        self.assertEqual(
            fee,
            Decimal("200.00"),
        )

    def test_auction_fee_snapshot(self):

        BidFeeRule.objects.create(
            name="High",
            min_product_price=Decimal(
                "50000"
            ),
            max_product_price=Decimal(
                "100000"
            ),
            fixed_fee=Decimal(
                "75"
            ),
        )

        product = Product.objects.create(
            name="Phone",
            description="Test phone",
            reference_price=Decimal(
                "80000"
            ),
        )

        now = timezone.now()

        auction = Auction.objects.create(
            product=product,
            created_by=self.admin,
            status=Auction.Status.SCHEDULED,
            start_at=now,
            end_at=now + timedelta(days=1),
            minimum_bid=Decimal(
                "1"
            ),
            maximum_bid=Decimal(
                "1000"
            ),
        )

        self.assertEqual(
            auction.bid_fee,
            Decimal("75.00"),
        )

        self.assertEqual(
            auction.reference_price_snapshot,
            Decimal("80000.00"),
        )