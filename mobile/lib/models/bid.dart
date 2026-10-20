class Bid {
  final int id;
  final int auctionId;
  final String auctionName;
  final double amount;
  final double feeCharged;
  final String status;
  final DateTime createdAt;

  Bid({
    required this.id,
    required this.auctionId,
    required this.auctionName,
    required this.amount,
    required this.feeCharged,
    required this.status,
    required this.createdAt,
  });

  factory Bid.fromJson(Map<String, dynamic> json) {
    return Bid(
      id: json['id'],
      auctionId: json['auction'],
      auctionName: json['auction_name'] ?? '',
      amount:
          double.tryParse(json['amount'].toString()) ?? 0,
      feeCharged:
          double.tryParse(json['fee_charged'].toString()) ?? 0,
      status: json['status'] ?? '',
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}