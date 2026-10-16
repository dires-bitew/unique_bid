from decimal import Decimal

from django.urls import reverse

from rest_framework import status
from rest_framework.test import (
    APITestCase,
)

from accounts.models import User

from .models import (
    Wallet,
    WalletTransaction,
)

from .services import (
    InsufficientFunds,
    WalletService,
)


class WalletTests(APITestCase):

    def setUp(self):

        self.user = (
            User.objects.create_user(
                email="wallet@example.com",
                password="StrongPass2026!",
            )
        )

    def test_wallet_created_automatically(
        self
    ):

        self.assertTrue(
            Wallet.objects.filter(
                user=self.user
            ).exists()
        )

        self.assertEqual(
            self.user.wallet.balance,
            Decimal("0.00"),
        )

    def test_wallet_credit(self):

        wallet, transaction = (
            WalletService.credit(
                user=self.user,
                amount=Decimal("500.00"),

                transaction_type=(
                    WalletTransaction
                    .TransactionType
                    .TOP_UP
                ),

                description="Test top up",
            )
        )

        self.assertEqual(
            wallet.balance,
            Decimal("500.00"),
        )

        self.assertEqual(
            transaction.balance_before,
            Decimal("0.00"),
        )

        self.assertEqual(
            transaction.balance_after,
            Decimal("500.00"),
        )

    def test_wallet_debit(self):

        WalletService.credit(
            user=self.user,
            amount=Decimal("500.00"),

            transaction_type=(
                WalletTransaction
                .TransactionType
                .TOP_UP
            ),
        )

        wallet, transaction = (
            WalletService.debit(
                user=self.user,
                amount=Decimal("40.00"),

                transaction_type=(
                    WalletTransaction
                    .TransactionType
                    .BID_FEE
                ),
            )
        )

        self.assertEqual(
            wallet.balance,
            Decimal("460.00"),
        )

        self.assertEqual(
            transaction.balance_after,
            Decimal("460.00"),
        )

    def test_insufficient_balance(
        self
    ):

        with self.assertRaises(
            InsufficientFunds
        ):

            WalletService.debit(
                user=self.user,
                amount=Decimal("100.00"),

                transaction_type=(
                    WalletTransaction
                    .TransactionType
                    .BID_FEE
                ),
            )

        self.user.wallet.refresh_from_db()

        self.assertEqual(
            self.user.wallet.balance,
            Decimal("0.00"),
        )

    def test_authenticated_user_can_view_wallet(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            reverse("my-wallet")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Decimal(
                response.data["balance"]
            ),
            Decimal("0.00"),
        )