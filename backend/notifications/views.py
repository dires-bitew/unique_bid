from django.utils import timezone

from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response

from rest_framework.views import APIView

from .models import Notification

from .serializers import (
    NotificationSerializer,
)


class MyNotificationListView(
    generics.ListAPIView
):

    serializer_class = (
        NotificationSerializer
    )

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            Notification.objects
            .filter(
                user=self.request.user
            )
        )


class MarkNotificationReadView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
        notification_id,
    ):

        notification = (
            Notification.objects
            .filter(
                id=notification_id,
                user=request.user,
            )
            .first()
        )

        if notification is None:

            return Response(
                {
                    "detail":
                    "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if notification.read_at is None:

            notification.read_at = (
                timezone.now()
            )

            notification.save(
                update_fields=[
                    "read_at"
                ]
            )

        return Response(
            NotificationSerializer(
                notification
            ).data
        )


class NotificationUnreadCountView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
    ):

        count = (
            Notification.objects
            .filter(
                user=request.user,
                read_at__isnull=True,
            )
            .count()
        )

        return Response(
            {
                "unread_count":
                    count
            }
        )