import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from auctions.models import Auction
from wallets.models import WalletTransaction


class Bid(models.Model):

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        REFUNDED = "refunded", "Refunded"

    auction = models.ForeignKey(
        Auction,
        on_delete=models.PROTECT,
        related_name="bids",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bids",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    fee_charged = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    wallet_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.PROTECT,
        related_name="bid",
        null=True,
        blank=True,
    )

    client_request_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACCEPTED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "auction",
                    "user",
                    "amount",
                ],
                name="unique_user_bid_amount_per_auction",
            ),

            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="bid_amount_must_be_positive",
            ),

            models.CheckConstraint(
                condition=models.Q(fee_charged__gte=0),
                name="bid_fee_must_not_be_negative",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "auction",
                    "amount",
                ],
            ),

            models.Index(
                fields=[
                    "user",
                    "created_at",
                ],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.auction.product.name} - "
            f"{self.amount}"
        )


class AuctionResult(models.Model):

    class ResultStatus(models.TextChoices):
        WINNER_SELECTED = (
            "winner_selected",
            "Winner Selected",
        )

        NO_UNIQUE_BID = (
            "no_unique_bid",
            "No Unique Bid",
        )

        CANCELLED = (
            "cancelled",
            "Cancelled",
        )

    auction = models.OneToOneField(
        Auction,
        on_delete=models.PROTECT,
        related_name="result",
    )

    winning_bid = models.OneToOneField(
        Bid,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="winning_result",
    )

    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="auction_wins",
    )

    winning_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    result_status = models.CharField(
        max_length=30,
        choices=ResultStatus.choices,
    )

    finalized_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"Result - {self.auction.product.name}"
        )