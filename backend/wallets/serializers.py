from decimal import Decimal

from django.contrib.auth import (
    get_user_model,
)

from rest_framework import serializers

from .models import (
    Wallet,
    WalletTransaction,
)


User = get_user_model()


class WalletSerializer(
    serializers.ModelSerializer
):

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:

        model = Wallet

        fields = (
            "id",
            "user_email",
            "balance",
            "currency",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class WalletTransactionSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WalletTransaction

        fields = (
            "id",
            "reference",
            "transaction_type",
            "direction",
            "amount",
            "balance_before",
            "balance_after",
            "description",
            "metadata",
            "created_at",
        )

        read_only_fields = fields


class AdminWalletAdjustmentSerializer(
    serializers.Serializer
):

    class Operation:
        CREDIT = "credit"
        DEBIT = "debit"

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
    )

    operation = serializers.ChoiceField(
        choices=(
            ("credit", "Credit"),
            ("debit", "Debit"),
        )
    )

    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )