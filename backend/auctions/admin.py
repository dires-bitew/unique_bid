from django.contrib import admin

from .models import (
    Auction,
    BidFeeRule,
)


@admin.register(BidFeeRule)
class BidFeeRuleAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "min_product_price",
        "max_product_price",
        "fixed_fee",
        "percentage_fee",
        "minimum_fee",
        "maximum_fee",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "min_product_price",
    )


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "status",
        "reference_price_snapshot",
        "bid_fee",
        "start_at",
        "end_at",
        "created_by",
    )

    list_filter = (
        "status",
        "start_at",
        "end_at",
    )

    readonly_fields = (
        "reference_price_snapshot",
        "bid_fee",
        "fee_rule",
        "created_at",
        "updated_at",
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):

        if not change:
            obj.created_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )