import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class Wallet(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    currency = models.CharField(
        max_length=3,
        default="ETB",
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="wallet_balance_must_not_be_negative",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.balance} {self.currency}"
        )


class WalletTransaction(models.Model):

    class TransactionType(models.TextChoices):
        TOP_UP = "top_up", "Top Up"
        BID_FEE = "bid_fee", "Bid Fee"
        REFUND = "refund", "Refund"
        ADMIN_CREDIT = "admin_credit", "Admin Credit"
        ADMIN_DEBIT = "admin_debit", "Admin Debit"

    class Direction(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TransactionType.choices,
    )

    direction = models.CharField(
        max_length=10,
        choices=Direction.choices,
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    balance_before = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    balance_after = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_wallet_transactions",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "wallet",
                    "created_at",
                ]
            ),
            models.Index(
                fields=[
                    "transaction_type",
                ]
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="wallet_transaction_amount_positive",
            ),
        ]

    def __str__(self):
        return (
            f"{self.wallet.user.email} - "
            f"{self.transaction_type} - "
            f"{self.amount} ETB"
        )