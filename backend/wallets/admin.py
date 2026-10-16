from django.contrib import admin

from .models import (
    Wallet,
    WalletTransaction,
)


@admin.register(Wallet)
class WalletAdmin(
    admin.ModelAdmin
):

    list_display = (
        "user",
        "balance",
        "currency",
        "updated_at",
    )

    search_fields = (
        "user__email",
    )

    readonly_fields = (
        "user",
        "balance",
        "currency",
        "created_at",
        "updated_at",
    )

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


@admin.register(WalletTransaction)
class WalletTransactionAdmin(
    admin.ModelAdmin
):

    list_display = (
        "reference",
        "wallet",
        "transaction_type",
        "direction",
        "amount",
        "balance_before",
        "balance_after",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "direction",
        "created_at",
    )

    search_fields = (
        "wallet__user__email",
        "reference",
        "description",
    )

    readonly_fields = (
        "reference",
        "wallet",
        "transaction_type",
        "direction",
        "amount",
        "balance_before",
        "balance_after",
        "description",
        "idempotency_key",
        "metadata",
        "created_by",
        "created_at",
    )

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False