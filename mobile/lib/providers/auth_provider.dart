import 'package:flutter/foundation.dart';

import '../models/user.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  User? user;

  bool loading = false;

  bool get loggedIn => user != null;

  Future<bool> restoreSession() async {
    loading = true;
    notifyListeners();

    try {
      user = await _authService.me();
      return true;
    } catch (_) {
      user = null;
      return false;
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> login(
    String email,
    String password,
  ) async {
    loading = true;
    notifyListeners();

    try {
      user = await _authService.login(
        email: email,
        password: password,
      );
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    try {
      await _authService.logout();
    } finally {
      user = null;
      notifyListeners();
    }
  }
}