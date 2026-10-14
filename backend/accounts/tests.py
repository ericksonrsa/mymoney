from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="erickson",
            email="erickson@example.com",
            password="StrongPass123!",
            first_name="Erickson",
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            reverse("auth-login"),
            {"username": "erickson", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        login = self.client.post(
            reverse("auth-login"),
            {"username": "erickson", "password": "StrongPass123!"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "erickson")

    def test_register_creates_hashed_password(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "AnotherStrong123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(username="newuser")
        self.assertTrue(user.check_password("AnotherStrong123!"))
        self.assertNotEqual(user.password, "AnotherStrong123!")
