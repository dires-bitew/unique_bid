from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):

    def setUp(self):

        self.registration_data = {
            "email": "customer@example.com",
            "first_name": "Customer",
            "last_name": "One",
            "phone_number": "+251911222333",
            "password": "StrongPass2026!",
            "password_confirm": "StrongPass2026!",
        }

    def test_user_registration(self):

        response = self.client.post(
            reverse("register"),
            self.registration_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email="customer@example.com"
            ).exists()
        )

        user = User.objects.get(
            email="customer@example.com"
        )

        self.assertEqual(
            user.role,
            User.Role.CUSTOMER,
        )

    def test_user_login(self):

        User.objects.create_user(
            email="customer@example.com",
            password="StrongPass2026!",
        )

        response = self.client.post(
            reverse("login"),
            {
                "email": "customer@example.com",
                "password": "StrongPass2026!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_protected_profile(self):

        user = User.objects.create_user(
            email="customer@example.com",
            password="StrongPass2026!",
        )

        self.client.force_authenticate(
            user=user
        )

        response = self.client.get(
            reverse("me")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            "customer@example.com",
        )