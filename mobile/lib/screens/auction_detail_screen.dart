import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/auction.dart';
import '../services/bid_service.dart';


class AuctionDetailScreen
    extends StatefulWidget {

  final Auction auction;

  const AuctionDetailScreen({
    super.key,
    required this.auction,
  });

  @override
  State<AuctionDetailScreen>
      createState() =>
          _AuctionDetailScreenState();
}


class _AuctionDetailScreenState
    extends State<AuctionDetailScreen> {

  final bidController =
      TextEditingController();

  bool submitting = false;

  Future<void> submitBid() async {
    final amount =
        double.tryParse(
      bidController.text.trim(),
    );

    if (amount == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Enter a valid bid.',
          ),
        ),
      );

      return;
    }

    final confirmed =
        await showDialog<bool>(
      context: context,

      builder: (_) =>
          AlertDialog(
        title:
            const Text(
          'Confirm Bid',
        ),

        content: Text(
          'Bid: ${amount.toStringAsFixed(2)} ETB\n\n'
          'Bid fee: ${widget.auction.bidFee.toStringAsFixed(2)} ETB\n\n'
          'The fee will be deducted from your wallet.',
        ),

        actions: [

          TextButton(
            onPressed: () =>
                Navigator.pop(
              context,
              false,
            ),
            child:
                const Text(
              'Cancel',
            ),
          ),

          FilledButton(
            onPressed: () =>
                Navigator.pop(
              context,
              true,
            ),
            child:
                const Text(
              'Pay & Submit',
            ),
          ),
        ],
      ),
    );

    if (confirmed != true) {
      return;
    }

    setState(() {
      submitting = true;
    });

    try {
      final response =
          await BidService()
              .submitBid(
        auctionId:
            widget.auction.id,
        amount: amount,
      );

      if (!mounted) return;

      bidController.clear();

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(
            'Bid accepted. Wallet balance: '
            '${response['wallet_balance']} ETB',
          ),
        ),
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(
            'Bid failed: $error',
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          submitting = false;
        });
      }
    }
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    final auction =
        widget.auction;

    final money =
        NumberFormat('#,##0.00');

    return Scaffold(
      appBar: AppBar(
        title: Text(
          auction.productName,
        ),
      ),

      body: ListView(
        padding:
            const EdgeInsets.all(20),

        children: [

          if (auction.imageUrl != null)
            Image.network(
              auction.imageUrl!,
              height: 250,
              fit: BoxFit.cover,
            ),

          const SizedBox(
            height: 20,
          ),

          Text(
            auction.productName,

            style:
                Theme.of(context)
                    .textTheme
                    .headlineSmall,
          ),

          const SizedBox(
            height: 10,
          ),

          Text(
            auction.productDescription,
          ),

          const Divider(
            height: 32,
          ),

          Text(
            'Reference price: '
            '${money.format(auction.referencePrice)} ETB',
          ),

          Text(
            'Fee per bid: '
            '${money.format(auction.bidFee)} ETB',
          ),

          Text(
            'Bid range: '
            '${money.format(auction.minimumBid)}'
            ' - '
            '${money.format(auction.maximumBid)} ETB',
          ),

          Text(
            'Maximum bids: '
            '${auction.maxBidsPerUser}',
          ),

          const SizedBox(
            height: 24,
          ),

          if (auction.isCurrentlyOpen) ...[

            TextField(
              controller:
                  bidController,

              keyboardType:
                  const TextInputType
                      .numberWithOptions(
                decimal: true,
              ),

              decoration:
                  const InputDecoration(
                labelText:
                    'Your sealed bid',
                suffixText: 'ETB',
                border:
                    OutlineInputBorder(),
              ),
            ),

            const SizedBox(
              height: 16,
            ),

            FilledButton.icon(
              icon: const Icon(
                Icons.gavel,
              ),

              onPressed:
                  submitting
                      ? null
                      : submitBid,

              label:
                  submitting
                      ? const Text(
                          'Submitting...'
                        )
                      : Text(
                          'Pay ${money.format(auction.bidFee)} ETB & Submit',
                        ),
            ),
          ] else
            const Text(
              'This auction is not currently accepting bids.',
            ),
        ],
      ),
    );
  }
}