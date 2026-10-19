from celery import shared_task

from django.db import transaction
from django.utils import timezone

from bids.services import (
    AuctionClosingService,
)

from .models import Auction


@shared_task(
    name="auctions.tasks.open_due_auctions"
)
def open_due_auctions():

    now = timezone.now()

    auction_ids = list(
        Auction.objects.filter(
            status=Auction.Status.SCHEDULED,
            start_at__lte=now,
            end_at__gt=now,
        ).values_list(
            "id",
            flat=True,
        )
    )

    opened = 0

    for auction_id in auction_ids:

        with transaction.atomic():

            auction = (
                Auction.objects
                .select_for_update()
                .get(pk=auction_id)
            )

            if (
                auction.status
                == Auction.Status.SCHEDULED
                and auction.start_at
                <= timezone.now()
                < auction.end_at
            ):

                auction.status = (
                    Auction.Status.OPEN
                )

                auction.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                opened += 1

    return opened


@shared_task(
    name="auctions.tasks.close_due_auctions"
)
def close_due_auctions():

    now = timezone.now()

    auction_ids = list(
        Auction.objects.filter(
            status__in=[
                Auction.Status.SCHEDULED,
                Auction.Status.OPEN,
            ],
            end_at__lte=now,
        ).values_list(
            "id",
            flat=True,
        )
    )

    closed = 0

    for auction_id in auction_ids:

        AuctionClosingService.close_auction(
            auction_id=auction_id
        )

        closed += 1

    return closed