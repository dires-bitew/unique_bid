import '../models/auction.dart';
import 'api_service.dart';

class AuctionService {
  final ApiService _api = ApiService();

  Future<List<Auction>> getAuctions({
    String? status,
  }) async {
    final response = await _api.dio.get(
      '/auctions/',
      queryParameters: {
        if (status != null)
          'status': status,
      },
    );

    final List<dynamic> data =
        response.data is List
            ? response.data
            : response.data['results'];

    return data
        .map(
          (json) => Auction.fromJson(json),
        )
        .toList();
  }

  Future<Auction> getAuction(
    int id,
  ) async {
    final response =
        await _api.dio.get(
      '/auctions/$id/',
    );

    return Auction.fromJson(
      response.data,
    );
  }
}