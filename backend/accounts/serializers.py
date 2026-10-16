from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "email_verified",
            "date_joined",
        )

        read_only_fields = (
            "id",
            "email",
            "role",
            "email_verified",
            "date_joined",
        )


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User

        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password_confirm",
        )

        read_only_fields = (
            "id",
        )

    def validate_phone_number(self, value):
        if value == "":
            return None

        return value

    def validate(self, attrs):

        password = attrs.get("password")
        password_confirm = attrs.pop(
            "password_confirm",
            None,
        )

        if password != password_confirm:
            raise serializers.ValidationError(
                {
                    "password_confirm":
                    "Passwords do not match."
                }
            )

        validate_password(password)

        return attrs

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            role=User.Role.CUSTOMER,
            **validated_data,
        )

        return user


class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token["email"] = user.email
        token["role"] = user.role

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        data["user"] = UserSerializer(
            self.user
        ).data

        return data