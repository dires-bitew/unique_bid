class Auction {
  final int id;
  final String status;
  final DateTime startAt;
  final DateTime endAt;

  final double minimumBid;
  final double maximumBid;
  final int maxBidsPerUser;

  final double referencePrice;
  final double bidFee;

  final bool isCurrentlyOpen;

  final int productId;
  final String productName;
  final String productDescription;
  final String? imageUrl;

  Auction({
    required this.id,
    required this.status,
    required this.startAt,
    required this.endAt,
    required this.minimumBid,
    required this.maximumBid,
    required this.maxBidsPerUser,
    required this.referencePrice,
    required this.bidFee,
    required this.isCurrentlyOpen,
    required this.productId,
    required this.productName,
    required this.productDescription,
    this.imageUrl,
  });

  factory Auction.fromJson(Map<String, dynamic> json) {
    final product =
        json['product_details'] as Map<String, dynamic>? ?? {};

    return Auction(
      id: json['id'],
      status: json['status'] ?? '',
      startAt: DateTime.parse(json['start_at']),
      endAt: DateTime.parse(json['end_at']),
      minimumBid:
          double.tryParse(json['minimum_bid'].toString()) ?? 0,
      maximumBid:
          double.tryParse(json['maximum_bid'].toString()) ?? 0,
      maxBidsPerUser: json['max_bids_per_user'] ?? 0,
      referencePrice: double.tryParse(
            json['reference_price_snapshot'].toString(),
          ) ??
          0,
      bidFee:
          double.tryParse(json['bid_fee'].toString()) ?? 0,
      isCurrentlyOpen: json['is_currently_open'] ?? false,
      productId: product['id'] ?? json['product'] ?? 0,
      productName: product['name'] ?? '',
      productDescription: product['description'] ?? '',
      imageUrl: product['image_url'],
    );
  }
}