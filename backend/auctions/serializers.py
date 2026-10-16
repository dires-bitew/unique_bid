from rest_framework import serializers

from products.serializers import (
    ProductSerializer,
)

from .models import (
    Auction,
    BidFeeRule,
)


class BidFeeRuleSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = BidFeeRule

        fields = "__all__"

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AuctionSerializer(
    serializers.ModelSerializer
):

    product_details = ProductSerializer(
        source="product",
        read_only=True,
    )

    is_currently_open = serializers.BooleanField(
        read_only=True,
    )

    created_by_email = serializers.EmailField(
        source="created_by.email",
        read_only=True,
    )

    class Meta:

        model = Auction

        fields = (
            "id",
            "product",
            "product_details",
            "status",
            "start_at",
            "end_at",
            "minimum_bid",
            "maximum_bid",
            "max_bids_per_user",
            "reference_price_snapshot",
            "bid_fee",
            "is_currently_open",
            "created_by_email",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "reference_price_snapshot",
            "bid_fee",
            "created_by_email",
            "created_at",
            "updated_at",
        )