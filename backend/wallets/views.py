from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)

from rest_framework.response import (
    Response,
)

from rest_framework.views import APIView

from .models import (
    Wallet,
    WalletTransaction,
)

from .serializers import (
    AdminWalletAdjustmentSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
)

from .services import (
    InsufficientFunds,
    WalletService,
)


class MyWalletView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        wallet, _ = (
            Wallet.objects.get_or_create(
                user=request.user
            )
        )

        serializer = WalletSerializer(
            wallet
        )

        return Response(
            serializer.data
        )


class MyWalletTransactionListView(
    generics.ListAPIView
):

    serializer_class = (
        WalletTransactionSerializer
    )

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            WalletTransaction.objects
            .filter(
                wallet__user=self.request.user
            )
            .order_by("-created_at")
        )


class AdminWalletAdjustmentView(
    APIView
):

    permission_classes = [
        IsAdminUser
    ]

    def post(self, request):

        serializer = (
            AdminWalletAdjustmentSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        amount = serializer.validated_data[
            "amount"
        ]

        operation = (
            serializer.validated_data[
                "operation"
            ]
        )

        description = (
            serializer.validated_data.get(
                "description",
                "",
            )
        )

        try:

            if operation == "credit":

                wallet, ledger = (
                    WalletService.credit(
                        user=user,

                        amount=amount,

                        transaction_type=(
                            WalletTransaction
                            .TransactionType
                            .ADMIN_CREDIT
                        ),

                        description=(
                            description
                            or "Administrative wallet credit."
                        ),

                        created_by=request.user,
                    )
                )

            else:

                wallet, ledger = (
                    WalletService.debit(
                        user=user,

                        amount=amount,

                        transaction_type=(
                            WalletTransaction
                            .TransactionType
                            .ADMIN_DEBIT
                        ),

                        description=(
                            description
                            or "Administrative wallet debit."
                        ),

                        created_by=request.user,
                    )
                )

        except InsufficientFunds as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=(
                    status
                    .HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "wallet":
                    WalletSerializer(
                        wallet
                    ).data,

                "transaction":
                    WalletTransactionSerializer(
                        ledger
                    ).data,
            },
            status=status.HTTP_200_OK,
        )