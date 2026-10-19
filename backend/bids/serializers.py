from rest_framework import serializers

from .models import (
    AuctionResult,
    Bid,
)


class BidCreateSerializer(
    serializers.Serializer
):

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    client_request_id = (
        serializers.UUIDField()
    )


class MyBidSerializer(
    serializers.ModelSerializer
):

    auction_name = serializers.CharField(
        source="auction.product.name",
        read_only=True,
    )

    class Meta:

        model = Bid

        fields = (
            "id",
            "auction",
            "auction_name",
            "amount",
            "fee_charged",
            "status",
            "client_request_id",
            "created_at",
        )

        read_only_fields = fields


class AuctionResultSerializer(
    serializers.ModelSerializer
):

    winner = serializers.SerializerMethodField()

    product_name = serializers.CharField(
        source="auction.product.name",
        read_only=True,
    )

    class Meta:

        model = AuctionResult

        fields = (
            "auction",
            "product_name",
            "result_status",
            "winner",
            "winning_amount",
            "finalized_at",
        )

        read_only_fields = fields

    def get_winner(
        self,
        obj,
    ):

        if not obj.winner:
            return None

        email = obj.winner.email

        try:
            local, domain = email.split(
                "@",
                1,
            )

        except ValueError:
            return "Winner"

        visible = local[:2]

        return (
            f"{visible}***@{domain}"
        )