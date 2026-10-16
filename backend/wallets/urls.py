from django.urls import path

from .views import (
    AdminWalletAdjustmentView,
    MyWalletTransactionListView,
    MyWalletView,
)


urlpatterns = [

    path(
        "",
        MyWalletView.as_view(),
        name="my-wallet",
    ),

    path(
        "transactions/",
        MyWalletTransactionListView.as_view(),
        name="wallet-transactions",
    ),

    path(
        "admin/adjust/",
        AdminWalletAdjustmentView.as_view(),
        name="admin-wallet-adjustment",
    ),
]