from django.core.management.base import (
    BaseCommand,
)

from django.utils import timezone

from auctions.models import Auction

from bids.services import (
    AuctionClosingService,
)


class Command(BaseCommand):

    help = (
        "Close auctions whose end time "
        "has passed."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        now = timezone.now()

        auction_ids = list(
            Auction.objects.filter(
                status__in=[
                    Auction.Status.OPEN,
                    Auction.Status.SCHEDULED,
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Closed {closed} auction(s)."
            )
        )