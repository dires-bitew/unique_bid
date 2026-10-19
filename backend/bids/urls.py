from django.urls import path

from .views import (
    AuctionResultView,
    CloseAuctionView,
    MyBidListView,
    SubmitBidView,
    CancelAuctionView,
)


urlpatterns = [

    path(
        "auctions/<int:auction_id>/bid/",
        SubmitBidView.as_view(),
        name="submit-bid",
    ),

    path(
        "bids/my/",
        MyBidListView.as_view(),
        name="my-bids",
    ),

    path(
        "auctions/<int:auction_id>/result/",
        AuctionResultView.as_view(),
        name="auction-result",
    ),

    path(
        "auctions/<int:auction_id>/close/",
        CloseAuctionView.as_view(),
        name="close-auction",
    ),

    path(
        "auctions/<int:auction_id>/cancel/",
        CancelAuctionView.as_view(),
        name="cancel-auction",
    ),
]