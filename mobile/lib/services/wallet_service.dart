import '../models/wallet.dart';
import 'api_service.dart';

class WalletService {
  final ApiService _api = ApiService();

  Future<Wallet> getWallet() async {
    final response =
        await _api.dio.get('/wallet/');

    return Wallet.fromJson(
      response.data,
    );
  }

  Future<List<dynamic>> getTransactions() async {
    final response =
        await _api.dio.get(
      '/wallet/transactions/',
    );

    if (response.data is List) {
      return response.data;
    }

    return response.data['results'] ?? [];
  }
}