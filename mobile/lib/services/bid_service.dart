import 'package:uuid/uuid.dart';

import '../models/bid.dart';
import 'api_service.dart';

class BidService {
  final ApiService _api = ApiService();

  final Uuid _uuid = const Uuid();

  Future<Map<String, dynamic>> submitBid({
    required int auctionId,
    required double amount,
  }) async {
    final requestId = _uuid.v4();

    final response = await _api.dio.post(
      '/auctions/$auctionId/bid/',
      data: {
        'amount':
            amount.toStringAsFixed(2),
        'client_request_id':
            requestId,
      },
    );

    return response.data;
  }

  Future<List<Bid>> getMyBids({
    int? auctionId,
  }) async {
    final response = await _api.dio.get(
      '/bids/my/',
      queryParameters: {
        if (auctionId != null)
          'auction': auctionId,
      },
    );

    final List<dynamic> data =
        response.data is List
            ? response.data
            : response.data['results'];

    return data
        .map(
          (json) => Bid.fromJson(json),
        )
        .toList();
  }

  Future<Map<String, dynamic>>
      getResult(int auctionId) async {
    final response = await _api.dio.get(
      '/auctions/$auctionId/result/',
    );

    return response.data;
  }
}