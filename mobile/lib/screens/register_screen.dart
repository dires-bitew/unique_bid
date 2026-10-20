import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import 'package:dio/dio.dart';

class RegisterScreen
    extends StatefulWidget {

  const RegisterScreen({
    super.key,
  });

  @override
  State<RegisterScreen>
      createState() =>
          _RegisterScreenState();
}


class _RegisterScreenState
    extends State<RegisterScreen> {

  final firstName =
      TextEditingController();

  final lastName =
      TextEditingController();

  final email =
      TextEditingController();

  final phone =
      TextEditingController();

  final password =
      TextEditingController();

  bool loading = false;

  Future<void> register() async {
    setState(() {
      loading = true;
    });

    try {
      await AuthService().register(
        email: email.text.trim(),
        firstName:
            firstName.text.trim(),
        lastName:
            lastName.text.trim(),
        phone:
            phone.text.trim(),
        password:
            password.text,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Registration successful. Please login.',
          ),
        ),
      );

      Navigator.pop(context);
    }on DioException catch (error) {
    if (!mounted) return;

    final data = error.response?.data;

    ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text(
                data != null
                    ? 'Registration failed: $data'
                    : 'Registration failed. Please check your connection.',
      ),
    ),
  );
} catch (error) {
  if (!mounted) return;

  ScaffoldMessenger.of(context).showSnackBar(
    Text(
      'Registration failed: $error',
    ) as SnackBar,
  );

    } finally {
      if (mounted) {
        setState(() {
          loading = false;
        });
      }
    }
  }

  Widget input(
    TextEditingController controller,
    String label, {
    bool passwordField = false,
  }) {
    return Padding(
      padding:
          const EdgeInsets.only(
        bottom: 16,
      ),
      child: TextField(
        controller: controller,
        obscureText: passwordField,
        decoration:
            InputDecoration(
          labelText: label,
          border:
              const OutlineInputBorder(),
        ),
      ),
    );
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Register'),
      ),

      body: ListView(
        padding:
            const EdgeInsets.all(24),
        children: [

          input(
            firstName,
            'First name',
          ),

          input(
            lastName,
            'Last name',
          ),

          input(
            email,
            'Email',
          ),

          input(
            phone,
            'Phone number',
          ),

          input(
            password,
            'Password',
            passwordField: true,
          ),

          FilledButton(
            onPressed:
                loading
                    ? null
                    : register,

            child:
                loading
                    ? const CircularProgressIndicator()
                    : const Text(
                        'Register',
                      ),
          ),
        ],
      ),
    );
  }
}