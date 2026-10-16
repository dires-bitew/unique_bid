from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import (
    Wallet,
    WalletTransaction,
)


class WalletError(Exception):
    pass


class InvalidWalletAmount(WalletError):
    pass


class InsufficientFunds(WalletError):
    pass


def normalize_amount(amount):

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
        raise InvalidWalletAmount(
            "Invalid amount."
        )

    if amount <= 0:
        raise InvalidWalletAmount(
            "Amount must be greater than zero."
        )

    return amount


class WalletService:

    @staticmethod
    def _get_locked_wallet(user):

        wallet, _ = (
            Wallet.objects.get_or_create(
                user=user
            )
        )

        return (
            Wallet.objects
            .select_for_update()
            .get(pk=wallet.pk)
        )

    @classmethod
    @transaction.atomic
    def credit(
        cls,
        user,
        amount,
        transaction_type,
        description="",
        created_by=None,
        metadata=None,
        idempotency_key=None,
    ):

        amount = normalize_amount(
            amount
        )

        wallet = cls._get_locked_wallet(
            user
        )

        balance_before = wallet.balance

        balance_after = (
            balance_before + amount
        )

        wallet.balance = balance_after

        wallet.save(
            update_fields=[
                "balance",
                "updated_at",
            ]
        )

        ledger_entry = (
            WalletTransaction.objects.create(
                wallet=wallet,

                transaction_type=(
                    transaction_type
                ),

                direction=(
                    WalletTransaction
                    .Direction
                    .CREDIT
                ),

                amount=amount,

                balance_before=(
                    balance_before
                ),

                balance_after=(
                    balance_after
                ),

                description=description,

                created_by=created_by,

                metadata=metadata or {},

                idempotency_key=(
                    idempotency_key
                ),
            )
        )

        return wallet, ledger_entry

    @classmethod
    @transaction.atomic
    def debit(
        cls,
        user,
        amount,
        transaction_type,
        description="",
        created_by=None,
        metadata=None,
        idempotency_key=None,
    ):

        amount = normalize_amount(
            amount
        )

        wallet = cls._get_locked_wallet(
            user
        )

        balance_before = wallet.balance

        if balance_before < amount:
            raise InsufficientFunds(
                "Insufficient wallet balance."
            )

        balance_after = (
            balance_before - amount
        )

        wallet.balance = balance_after

        wallet.save(
            update_fields=[
                "balance",
                "updated_at",
            ]
        )

        ledger_entry = (
            WalletTransaction.objects.create(
                wallet=wallet,

                transaction_type=(
                    transaction_type
                ),

                direction=(
                    WalletTransaction
                    .Direction
                    .DEBIT
                ),

                amount=amount,

                balance_before=(
                    balance_before
                ),

                balance_after=(
                    balance_after
                ),

                description=description,

                created_by=created_by,

                metadata=metadata or {},

                idempotency_key=(
                    idempotency_key
                ),
            )
        )

        return wallet, ledger_entry