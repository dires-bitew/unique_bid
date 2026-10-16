from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    AuctionViewSet,
    BidFeeRuleViewSet,
)


router = DefaultRouter()

router.register(
    "auctions",
    AuctionViewSet,
    basename="auction",
)

router.register(
    "fee-rules",
    BidFeeRuleViewSet,
    basename="fee-rule",
)


urlpatterns = router.urls