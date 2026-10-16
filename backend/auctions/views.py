from rest_framework.permissions import (
    IsAdminUser,
)

from rest_framework.viewsets import (
    ModelViewSet,
)

from core.permissions import (
    IsAdminOrReadOnly,
)

from .models import (
    Auction,
    BidFeeRule,
)

from .serializers import (
    AuctionSerializer,
    BidFeeRuleSerializer,
)


class AuctionViewSet(ModelViewSet):

    queryset = (
        Auction.objects
        .select_related(
            "product",
            "created_by",
            "fee_rule",
        )
        .all()
    )

    serializer_class = AuctionSerializer

    permission_classes = [
        IsAdminOrReadOnly
    ]

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            created_by=self.request.user
        )

    def get_queryset(self):

        queryset = super().get_queryset()

        status_value = (
            self.request.query_params
            .get("status")
        )

        if status_value:
            queryset = queryset.filter(
                status=status_value
            )

        return queryset


class BidFeeRuleViewSet(
    ModelViewSet
):

    queryset = (
        BidFeeRule.objects.all()
    )

    serializer_class = (
        BidFeeRuleSerializer
    )

    permission_classes = [
        IsAdminUser
    ]