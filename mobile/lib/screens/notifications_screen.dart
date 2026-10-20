import 'package:flutter/material.dart';

import '../models/notification_model.dart';
import '../services/notification_service.dart';


class NotificationsScreen
    extends StatefulWidget {

  const NotificationsScreen({
    super.key,
  });

  @override
  State<NotificationsScreen>
      createState() =>
          _NotificationsScreenState();
}


class _NotificationsScreenState
    extends State<NotificationsScreen> {

  final service =
      NotificationService();

  late Future<
      List<AppNotification>>
      notifications;

  @override
  void initState() {
    super.initState();

    notifications =
        service.getNotifications();
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text(
          'Notifications',
        ),
      ),

      body:
          FutureBuilder<
              List<AppNotification>>(
        future: notifications,

        builder:
            (context, snapshot) {

          if (!snapshot.hasData) {
            return const Center(
              child:
                  CircularProgressIndicator(),
            );
          }

          final items =
              snapshot.data!;

          if (items.isEmpty) {
            return const Center(
              child: Text(
                'No notifications.',
              ),
            );
          }

          return ListView.builder(
            itemCount:
                items.length,

            itemBuilder:
                (context, index) {

              final item =
                  items[index];

              return ListTile(
                leading:
                    Icon(
                  item.isRead
                      ? Icons
                          .notifications_none
                      : Icons
                          .notifications_active,
                ),

                title:
                    Text(item.title),

                subtitle:
                    Text(
                  item.message,
                ),

                onTap: () async {
                  await service.markRead(
                    item.id,
                  );

                  setState(() {
                    notifications =
                        service
                            .getNotifications();
                  });
                },
              );
            },
          );
        },
      ),
    );
  }
}