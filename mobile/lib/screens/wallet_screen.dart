import 'package:flutter/material.dart';

import '../models/wallet.dart';
import '../services/wallet_service.dart';


class WalletScreen
    extends StatefulWidget {

  const WalletScreen({
    super.key,
  });

  @override
  State<WalletScreen>
      createState() =>
          _WalletScreenState();
}


class _WalletScreenState
    extends State<WalletScreen> {

  final service =
      WalletService();

  late Future<Wallet> wallet;

  @override
  void initState() {
    super.initState();

    wallet =
        service.getWallet();
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Wallet'),
      ),

      body:
          FutureBuilder<Wallet>(
        future: wallet,

        builder:
            (context, snapshot) {

          if (!snapshot.hasData) {
            return const Center(
              child:
                  CircularProgressIndicator(),
            );
          }

          final wallet =
              snapshot.data!;

          return Center(
            child: Card(
              margin:
                  const EdgeInsets.all(
                24,
              ),

              child: Padding(
                padding:
                    const EdgeInsets.all(
                  32,
                ),

                child: Column(
                  mainAxisSize:
                      MainAxisSize.min,

                  children: [

                    const Text(
                      'Available Balance',
                    ),

                    const SizedBox(
                      height: 12,
                    ),

                    Text(
                      '${wallet.balance.toStringAsFixed(2)} ${wallet.currency}',

                      style:
                          Theme.of(context)
                              .textTheme
                              .headlineMedium,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}