from rest_framework import generics, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import (
    RefreshToken,
    TokenError,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get(
            "refresh"
        )

        if not refresh_token:
            return Response(
                {
                    "detail":
                    "Refresh token is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                {
                    "detail":
                    "Successfully logged out."
                },
                status=status.HTTP_205_RESET_CONTENT,
            )

        except TokenError:

            return Response(
                {
                    "detail":
                    "Invalid or expired refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )