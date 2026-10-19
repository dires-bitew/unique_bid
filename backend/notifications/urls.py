from django.urls import path

from .views import (
    MarkNotificationReadView,
    MyNotificationListView,
    NotificationUnreadCountView,
)


urlpatterns = [

    path(
        "",
        MyNotificationListView.as_view(),
        name="my-notifications",
    ),

    path(
        "unread-count/",
        NotificationUnreadCountView.as_view(),
        name="notification-unread-count",
    ),

    path(
        "<int:notification_id>/read/",
        MarkNotificationReadView.as_view(),
        name="notification-read",
    ),
]