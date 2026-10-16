from django.contrib import admin

from .models import (
    AuctionResult,
    Bid,
)


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "auction",
        "user",
        "amount",
        "fee_charged",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "auction",
        "created_at",
    )

    search_fields = (
        "user__email",
        "auction__product__name",
    )

    readonly_fields = (
        "auction",
        "user",
        "amount",
        "fee_charged",
        "wallet_transaction",
        "client_request_id",
        "status",
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


@admin.register(AuctionResult)
class AuctionResultAdmin(
    admin.ModelAdmin
):

    list_display = (
        "auction",
        "result_status",
        "winner",
        "winning_amount",
        "finalized_at",
    )

    readonly_fields = (
        "auction",
        "winning_bid",
        "winner",
        "winning_amount",
        "result_status",
        "finalized_at",
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