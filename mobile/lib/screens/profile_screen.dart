import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import 'login_screen.dart';


class ProfileScreen
    extends StatelessWidget {

  const ProfileScreen({
    super.key,
  });

  @override
  Widget build(
    BuildContext context,
  ) {
    final auth =
        context.watch<AuthProvider>();

    final user =
        auth.user;

    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Profile'),
      ),

      body:
          user == null
              ? const Center(
                  child:
                      Text('Not logged in'),
                )
              : Padding(
                  padding:
                      const EdgeInsets.all(
                    24,
                  ),

                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment
                            .start,

                    children: [

                      Text(
                        user.fullName,

                        style:
                            Theme.of(context)
                                .textTheme
                                .headlineSmall,
                      ),

                      const SizedBox(
                        height: 8,
                      ),

                      Text(
                        user.email,
                      ),

                      Text(
                        'Role: ${user.role}',
                      ),

                      const SizedBox(
                        height: 32,
                      ),

                      FilledButton.icon(
                        icon:
                            const Icon(
                          Icons.logout,
                        ),

                        label:
                            const Text(
                          'Logout',
                        ),

                        onPressed:
                            () async {

                          await auth.logout();

                          if (!context
                              .mounted) {
                            return;
                          }

                          Navigator
                              .pushAndRemoveUntil(
                            context,

                            MaterialPageRoute(
                              builder:
                                  (_) =>
                                      const LoginScreen(),
                            ),

                            (_) => false,
                          );
                        },
                      ),
                    ],
                  ),
                ),
    );
  }
}