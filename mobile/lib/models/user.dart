class User {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String? phoneNumber;
  final String role;
  final bool emailVerified;

  User({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.phoneNumber,
    required this.role,
    required this.emailVerified,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      phoneNumber: json['phone'],
      role: json['role'] ?? 'customer',
      emailVerified: json['email_verified'] ?? false,
    );
  }

  String get fullName {
    final value = '$firstName $lastName'.trim();

    if (value.isEmpty) {
      return email;
    }

    return value;
  }
}