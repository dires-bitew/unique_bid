class Wallet {
  final int id;
  final String userEmail;
  final double balance;
  final String currency;

  Wallet({
    required this.id,
    required this.userEmail,
    required this.balance,
    required this.currency,
  });

  factory Wallet.fromJson(Map<String, dynamic> json) {
    return Wallet(
      id: json['id'],
      userEmail: json['user_email'] ?? '',
      balance:
          double.tryParse(json['balance'].toString()) ?? 0,
      currency: json['currency'] ?? 'ETB',
    );
  }
}