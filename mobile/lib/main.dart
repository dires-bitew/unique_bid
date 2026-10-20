import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';


void main() {
  WidgetsFlutterBinding
      .ensureInitialized();

  runApp(
    ChangeNotifierProvider(
      create: (_) =>
          AuthProvider(),

      child:
          const UniqueBidApp(),
    ),
  );
}


class UniqueBidApp
    extends StatelessWidget {

  const UniqueBidApp({
    super.key,
  });

  @override
  Widget build(
    BuildContext context,
  ) {
    return MaterialApp(
      debugShowCheckedModeBanner:
          false,

      title: 'Unique Bid',

      theme: ThemeData(
        useMaterial3: true,

        colorScheme:
            ColorScheme.fromSeed(
          seedColor:
              Colors.indigo,
        ),
      ),

      home:
          const StartupScreen(),
    );
  }
}


class StartupScreen
    extends StatefulWidget {

  const StartupScreen({
    super.key,
  });

  @override
  State<StartupScreen>
      createState() =>
          _StartupScreenState();
}


class _StartupScreenState
    extends State<StartupScreen> {

  bool checking = true;
  bool authenticated = false;

  @override
  void initState() {
    super.initState();

    restore();
  }

  Future<void> restore() async {
    final auth =
        context.read<AuthProvider>();

    authenticated =
        await auth.restoreSession();

    if (mounted) {
      setState(() {
        checking = false;
      });
    }
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    if (checking) {
      return const Scaffold(
        body: Center(
          child:
              CircularProgressIndicator(),
        ),
      );
    }

    if (authenticated) {
      return const HomeScreen();
    }

    return const LoginScreen();
  }
}