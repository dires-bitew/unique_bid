import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _api = ApiService();

  Future<User> login({
    required String email,
    required String password,
  }) async {
    final response = await _api.dio.post(
      '/auth/login/',
      data: {
        'email': email,
        'password': password,
      },
    );

    await _api.saveTokens(
      access: response.data['access'],
      refresh: response.data['refresh'],
    );

    return User.fromJson(
      response.data['user'],
    );
  }

  Future<User> register({
    required String email,
    required String firstName,
    required String lastName,
    required String? phone,
    required String password,
  }) async {
    final response = await _api.dio.post(
      '/auth/register/',
      data: {
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'phone':
            phone?.trim().isEmpty == true
                ? null
                : phone,
        'password': password,
        'password_confirm': password,
      },
    );

    return User.fromJson(
      response.data,
    );
  }

  Future<User> me() async {
    final response =
        await _api.dio.get('/auth/me/');

    return User.fromJson(
      response.data,
    );
  }

  Future<void> logout() async {
    final refresh =
        await _api.getRefreshToken();

    if (refresh != null) {
      try {
        await _api.dio.post(
          '/auth/logout/',
          data: {
            'refresh': refresh,
          },
        );
      } catch (_) {
        // Token may already be expired/blacklisted.
      }
    }

    await _api.clearTokens();
  }
}