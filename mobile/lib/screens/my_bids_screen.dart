import 'package:flutter/material.dart';

import '../models/bid.dart';
import '../services/bid_service.dart';


class MyBidsScreen
    extends StatelessWidget {

  const MyBidsScreen({
    super.key,
  });

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('My Bids'),
      ),

      body:
          FutureBuilder<List<Bid>>(
        future:
            BidService().getMyBids(),

        builder:
            (context, snapshot) {

          if (!snapshot.hasData) {
            return const Center(
              child:
                  CircularProgressIndicator(),
            );
          }

          final bids =
              snapshot.data!;

          if (bids.isEmpty) {
            return const Center(
              child:
                  Text('No bids yet.'),
            );
          }

          return ListView.builder(
            itemCount:
                bids.length,

            itemBuilder:
                (context, index) {

              final bid =
                  bids[index];

              return ListTile(
                leading:
                    const Icon(
                  Icons.gavel,
                ),

                title:
                    Text(
                  bid.auctionName,
                ),

                subtitle:
                    Text(
                  'Fee: ${bid.feeCharged.toStringAsFixed(2)} ETB',
                ),

                trailing:
                    Text(
                  '${bid.amount.toStringAsFixed(2)} ETB',
                ),
              );
            },
          );
        },
      ),
    );
  }
}