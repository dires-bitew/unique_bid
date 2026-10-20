import '../models/notification_model.dart';
import 'api_service.dart';

class NotificationService {
  final ApiService _api = ApiService();

  Future<List<AppNotification>>
      getNotifications() async {
    final response =
        await _api.dio.get(
      '/notifications/',
    );

    final List<dynamic> data =
        response.data is List
            ? response.data
            : response.data['results'];

    return data
        .map(
          (json) =>
              AppNotification.fromJson(json),
        )
        .toList();
  }

  Future<int> getUnreadCount() async {
    final response =
        await _api.dio.get(
      '/notifications/unread-count/',
    );

    return response.data[
            'unread_count'] ??
        0;
  }

  Future<void> markRead(
    int id,
  ) async {
    await _api.dio.post(
      '/notifications/$id/read/',
    );
  }
}