from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from products.models import Product

def get_bid_fee_rule(product_price):
        rules = BidFeeRule.objects.filter(
            is_active=True,
            min_product_price__lte=product_price,
        ).order_by(
            "-min_product_price"
        )

        for rule in rules:
            if rule.matches_price(product_price):
                return rule

        return None
class BidFeeRule(models.Model):
    
    name = models.CharField(
        max_length=150,
    )

    min_product_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    max_product_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave empty for no upper limit.",
    )

    fixed_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    percentage_fee = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=Decimal("0.000"),
        help_text="Percentage of product reference price.",
    )

    minimum_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    maximum_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["min_product_price"]

    

    def __str__(self):
        if self.max_product_price:
            return (
                f"{self.name}: "
                f"{self.min_product_price} - "
                f"{self.max_product_price}"
            )

        return f"{self.name}: {self.min_product_price}+"

    def clean(self):
        if (
            self.max_product_price is not None
            and self.max_product_price < self.min_product_price
        ):
            raise ValidationError({
                "max_product_price":
                "Maximum price cannot be lower than minimum price."
            })

        if self.fixed_fee < 0:
            raise ValidationError({
                "fixed_fee":
                "Fixed fee cannot be negative."
            })

        if self.percentage_fee < 0:
            raise ValidationError({
                "percentage_fee":
                "Percentage fee cannot be negative."
            })

        if (
            self.minimum_fee is not None
            and self.maximum_fee is not None
            and self.minimum_fee > self.maximum_fee
        ):
            raise ValidationError({
                "maximum_fee":
                "Maximum fee cannot be lower than minimum fee."
            })

    def matches_price(self, price):
        if price < self.min_product_price:
            return False

        if (
            self.max_product_price is not None
            and price > self.max_product_price
        ):
            return False

        return True

    def calculate_fee(self, product_price):
        fee = self.fixed_fee

        percentage_amount = (
            product_price
            * self.percentage_fee
            / Decimal("100")
        )

        fee += percentage_amount

        if (
            self.minimum_fee is not None
            and fee < self.minimum_fee
        ):
            fee = self.minimum_fee

        if (
            self.maximum_fee is not None
            and fee > self.maximum_fee
        ):
            fee = self.maximum_fee

        return fee.quantize(
            Decimal("0.01")
        )



class Auction(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="auctions",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_auctions",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    start_at = models.DateTimeField()

    end_at = models.DateTimeField()

    minimum_bid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
    )

    maximum_bid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    max_bids_per_user = models.PositiveIntegerField(
        default=10,
    )

    reference_price_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        null=True,
    )

    bid_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        null=True,
    )

    fee_rule = models.ForeignKey(
        BidFeeRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="auctions",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.product.name} "
            f"({self.get_status_display()})"
        )
    def clean(self):

        if self.end_at <= self.start_at:
            raise ValidationError(
                {
                    "end_at":
                    "Auction end time must be after start time."
                }
            )

        if self.minimum_bid <= 0:
            raise ValidationError(
                {
                    "minimum_bid":
                    "Minimum bid must be greater than zero."
                }
            )

        if self.maximum_bid <= self.minimum_bid:
            raise ValidationError(
                {
                    "maximum_bid":
                    "Maximum bid must be greater than minimum bid."
                }
            )

        if self.max_bids_per_user < 1:
            raise ValidationError(
                {
                    "max_bids_per_user":
                    "At least one bid per user must be allowed."
                }
            )
    def prepare_fee_snapshot(self):

        if self.reference_price_snapshot is not None:
            return

        product_price = self.product.reference_price

        rule = get_bid_fee_rule(
            product_price
        )

        if rule is None:
            raise ValidationError(
                "No active bid fee rule matches this product price."
            )

        self.reference_price_snapshot = (
            product_price
        )

        self.bid_fee = rule.calculate_fee(
            product_price
        )

        self.fee_rule = rule

    def save(self, *args, **kwargs):

        if self._state.adding:
            self.prepare_fee_snapshot()

        self.full_clean()

        return super().save(
            *args,
            **kwargs
        )
    @property
    def is_currently_open(self):

        now = timezone.now()

        return (
            self.status
            in [
                self.Status.SCHEDULED,
                self.Status.OPEN,
            ]
            and self.start_at <= now < self.end_at
        )
    