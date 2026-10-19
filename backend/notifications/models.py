from django.conf import settings
from django.db import models


class Notification(models.Model):

    class Type(models.TextChoices):

        AUCTION_CANCELLED = (
            "auction_cancelled",
            "Auction Cancelled",
        )

        BID_REFUNDED = (
            "bid_refunded",
            "Bid Refunded",
        )

        AUCTION_WON = (
            "auction_won",
            "Auction Won",
        )

        AUCTION_ENDED = (
            "auction_ended",
            "Auction Ended",
        )

        NO_UNIQUE_BID = (
            "no_unique_bid",
            "No Unique Bid",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices,
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    data = models.JSONField(
        default=dict,
        blank=True,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "user",
                    "read_at",
                ]
            ),
        ]

    @property
    def is_read(self):
        return self.read_at is not None

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.title}"
        )