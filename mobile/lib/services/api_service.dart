import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../config/app_config.dart';

class ApiService {
  static final ApiService _instance =
      ApiService._internal();

  factory ApiService() {
    return _instance;
  }

  late final Dio dio;

  final FlutterSecureStorage storage =
      const FlutterSecureStorage();

  bool _refreshing = false;

  ApiService._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Content-Type': 'application/json',
        },
      ),
    );

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (
          options,
          handler,
        ) async {
          final accessToken =
              await storage.read(key: 'access_token');

          if (accessToken != null) {
            options.headers['Authorization'] =
                'Bearer $accessToken';
          }

          handler.next(options);
        },

        onError: (
          error,
          handler,
        ) async {
          if (error.response?.statusCode != 401) {
            handler.next(error);
            return;
          }

          if (_refreshing) {
            handler.next(error);
            return;
          }

          final refreshToken =
              await storage.read(key: 'refresh_token');

          if (refreshToken == null) {
            handler.next(error);
            return;
          }

          try {
            _refreshing = true;

            final response = await Dio().post(
              '${AppConfig.baseUrl}/auth/token/refresh/',
              data: {
                'refresh': refreshToken,
              },
            );

            final newAccess =
                response.data['access'] as String?;

            final newRefresh =
                response.data['refresh'] as String?;

            if (newAccess == null) {
              throw Exception(
                'Unable to refresh authentication.',
              );
            }

            await storage.write(
              key: 'access_token',
              value: newAccess,
            );

            if (newRefresh != null) {
              await storage.write(
                key: 'refresh_token',
                value: newRefresh,
              );
            }

            final requestOptions =
                error.requestOptions;

            requestOptions.headers['Authorization'] =
                'Bearer $newAccess';

            final retryResponse =
                await dio.fetch(requestOptions);

            handler.resolve(retryResponse);
          } catch (_) {
            await clearTokens();

            handler.next(error);
          } finally {
            _refreshing = false;
          }
        },
      ),
    );
  }

  Future<void> saveTokens({
    required String access,
    required String refresh,
  }) async {
    await storage.write(
      key: 'access_token',
      value: access,
    );

    await storage.write(
      key: 'refresh_token',
      value: refresh,
    );
  }

  Future<void> clearTokens() async {
    await storage.delete(
      key: 'access_token',
    );

    await storage.delete(
      key: 'refresh_token',
    );
  }

  Future<String?> getRefreshToken() {
    return storage.read(
      key: 'refresh_token',
    );
  }
}