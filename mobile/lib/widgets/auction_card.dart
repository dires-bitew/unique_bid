import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/auction.dart';


class AuctionCard extends StatelessWidget {
  final Auction auction;
  final VoidCallback onTap;

  const AuctionCard({
    super.key,
    required this.auction,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final money =
        NumberFormat('#,##0.00');

    return Card(
      margin:
          const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),

      child: InkWell(
        onTap: onTap,

        child: Padding(
          padding:
              const EdgeInsets.all(16),

          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,

            children: [

              if (auction.imageUrl != null)
                ClipRRect(
                  borderRadius:
                      BorderRadius.circular(
                    8,
                  ),

                  child: Image.network(
                    auction.imageUrl!,
                    height: 180,
                    width:
                        double.infinity,
                    fit: BoxFit.cover,

                    errorBuilder:
                        (_, __, ___) =>
                            const SizedBox(),
                  ),
                ),

              const SizedBox(
                height: 12,
              ),

              Text(
                auction.productName,

                style: Theme.of(context)
                    .textTheme
                    .titleLarge,
              ),

              const SizedBox(
                height: 8,
              ),

              Text(
                'Value: ${money.format(auction.referencePrice)} ETB',
              ),

              Text(
                'Bid fee: ${money.format(auction.bidFee)} ETB',
              ),

              Text(
                'Status: ${auction.status.toUpperCase()}',
              ),
            ],
          ),
        ),
      ),
    );
  }
}