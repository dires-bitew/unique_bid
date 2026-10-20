import 'package:flutter/material.dart';

import '../models/auction.dart';
import '../services/auction_service.dart';
import '../widgets/auction_card.dart';

import 'auction_detail_screen.dart';
import 'my_bids_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';
import 'wallet_screen.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
  });

  @override
  State<HomeScreen>
      createState() =>
          _HomeScreenState();
}


class _HomeScreenState
    extends State<HomeScreen> {

  final AuctionService service =
      AuctionService();

  late Future<List<Auction>>
      auctions;

  @override
  void initState() {
    super.initState();

    refresh();
  }

  void refresh() {
    auctions =
        service.getAuctions();
  }

  Future<void> reload() async {
    setState(refresh);

    await auctions;
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Unique Bid'),

        actions: [

          IconButton(
            icon: const Icon(
              Icons.account_balance_wallet,
            ),

            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) =>
                      const WalletScreen(),
                ),
              );
            },
          ),

          IconButton(
            icon: const Icon(
              Icons.notifications,
            ),

            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) =>
                      const NotificationsScreen(),
                ),
              );
            },
          ),
        ],
      ),

      drawer: Drawer(
        child: ListView(
          children: [

            const DrawerHeader(
              child: Text(
                'Unique Bid',
                style:
                    TextStyle(
                  fontSize: 28,
                ),
              ),
            ),

            ListTile(
              leading:
                  const Icon(
                Icons.gavel,
              ),

              title:
                  const Text(
                'My Bids',
              ),

              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        const MyBidsScreen(),
                  ),
                );
              },
            ),

            ListTile(
              leading:
                  const Icon(
                Icons.account_balance_wallet,
              ),

              title:
                  const Text(
                'Wallet',
              ),

              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        const WalletScreen(),
                  ),
                );
              },
            ),

            ListTile(
              leading:
                  const Icon(
                Icons.person,
              ),

              title:
                  const Text(
                'Profile',
              ),

              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        const ProfileScreen(),
                  ),
                );
              },
            ),
          ],
        ),
      ),

      body:
          FutureBuilder<List<Auction>>(
        future: auctions,

        builder:
            (context, snapshot) {

          if (snapshot.connectionState
              ==
              ConnectionState
                  .waiting) {
            return const Center(
              child:
                  CircularProgressIndicator(),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Text(
                'Unable to load auctions.\n${snapshot.error}',
                textAlign:
                    TextAlign.center,
              ),
            );
          }

          final items =
              snapshot.data ?? [];

          if (items.isEmpty) {
            return const Center(
              child: Text(
                'No auctions available.',
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: reload,

            child:
                ListView.builder(
              itemCount:
                  items.length,

              itemBuilder:
                  (context, index) {

                final auction =
                    items[index];

                return AuctionCard(
                  auction: auction,

                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) =>
                            AuctionDetailScreen(
                          auction:
                              auction,
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          );
        },
      ),
    );
  }
}