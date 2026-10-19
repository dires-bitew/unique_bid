from django.shortcuts import get_object_or_404

from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)

from rest_framework.response import Response
from rest_framework.views import APIView

from auctions.models import Auction
from wallets.services import InsufficientFunds

from .models import (
    AuctionResult,
    Bid,
)

from .serializers import (
    AuctionResultSerializer,
    BidCreateSerializer,
    MyBidSerializer,
)

from .services import (
    AuctionClosingService,
    AuctionNotOpen,
    AuctionNotReadyToClose,
    BidError,
    BidLimitReached,
    BidService,
    DuplicateBidAmount,
    InvalidBidAmount,
)

from .services import (
    AuctionCancellationService,
)


class SubmitBidView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
        auction_id,
    ):

        serializer = BidCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            bid, created = (
                BidService.submit_bid(
                    user=request.user,
                    auction_id=auction_id,
                    amount=(
                        serializer
                        .validated_data[
                            "amount"
                        ]
                    ),
                    client_request_id=(
                        serializer
                        .validated_data[
                            "client_request_id"
                        ]
                    ),
                )
            )

        except Auction.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Auction not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except (
            AuctionNotOpen,
            InvalidBidAmount,
            BidLimitReached,
            DuplicateBidAmount,
            InsufficientFunds,
            BidError,
        ) as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        bid.refresh_from_db()

        request.user.wallet.refresh_from_db()

        return Response(
            {
                "created": created,

                "bid": MyBidSerializer(
                    bid
                ).data,

                "wallet_balance":
                    str(
                        request.user
                        .wallet
                        .balance
                    ),
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )

class MyBidListView(
    generics.ListAPIView
):

    serializer_class = (
        MyBidSerializer
    )

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        queryset = (
            Bid.objects
            .filter(
                user=self.request.user
            )
            .select_related(
                "auction",
                "auction__product",
            )
        )

        auction_id = (
            self.request.query_params
            .get("auction")
        )

        if auction_id:
            queryset = queryset.filter(
                auction_id=auction_id
            )

        return queryset

class AuctionResultView(APIView):

    permission_classes = [
        AllowAny
    ]

    def get(
        self,
        request,
        auction_id,
    ):

        auction = get_object_or_404(
            Auction,
            pk=auction_id,
        )

        if (
            auction.status
            != Auction.Status.CLOSED
            and auction.status
            != Auction.Status.CANCELLED
        ):

            return Response(
                {
                    "detail":
                    "Auction result is not available yet."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        result = get_object_or_404(
            AuctionResult,
            auction=auction,
        )

        serializer = (
            AuctionResultSerializer(
                result
            )
        )

        return Response(
            serializer.data
        )

class CloseAuctionView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def post(
        self,
        request,
        auction_id,
    ):

        force = (
            str(
                request.data.get(
                    "force",
                    "false",
                )
            ).lower()
            == "true"
        )

        try:

            result = (
                AuctionClosingService
                .close_auction(
                    auction_id=auction_id,
                    force=force,
                )
            )

        except Auction.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Auction not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except AuctionNotReadyToClose as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            AuctionResultSerializer(
                result
            ).data
        )


class CancelAuctionView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def post(
        self,
        request,
        auction_id,
    ):

        reason = request.data.get(
            "reason",
            "",
        )

        try:

            (
                auction,
                refunded_count,
                total_refunded,
            ) = (
                AuctionCancellationService
                .cancel_auction(
                    auction_id=auction_id,
                    cancelled_by=request.user,
                    reason=reason,
                )
            )

        except Auction.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Auction not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except BidError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "auction_id":
                    auction.pk,

                "status":
                    auction.status,

                "refunded_bids":
                    refunded_count,

                "total_refunded":
                    str(total_refunded),
            }
        )