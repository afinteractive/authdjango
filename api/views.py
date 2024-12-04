from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ArticleSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from .perimission import IsAdminOrMaster, IsAdminRole, IsMasterOrUserRole, IsUserRole
from .models import Article
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrMaster]

    def get_serializer_context(self):
        return {"request": self.request}


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            response = Response(
                {
                    "user": user_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
            access_token_lifetime = refresh.access_token.lifetime
            refresh_token_lifetime = refresh.lifetime

            response.set_cookie(
                key="access_token",
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=access_token_lifetime.total_seconds(),
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=refresh_token_lifetime.total_seconds(),
            )
            return response
        else:
            return Response({"error": "Invalid Credentials"}, status=401)


class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        respone = Response(
            {"message": "Logged out successfuly"}, status=status.HTTP_200_OK
        )
        respone.delete_cookie("access_token")
        respone.delete_cookie("refresh_token")
        return respone


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        users = User.objects.all()
        print(users)
        user_serializer = UserSerializer(users, many=True)
        return Response(
            {
                "message": "Welcome to dashboard",
                "user": user_serializer.data,
            },
            200,
        )


class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsMasterOrUserRole]

    def perform_create(self, request, serializer):
        print("Authorization Header:", request.META.get("HTTP_AUTHORIZATION"))
        serializer.save(author=self.request.user)


class ArticleDeatilView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsUserRole]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # Override the retrieve method to customize the response
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "code": 200,
            }
        )


class TokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token missing."}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            # Set the new access token in cookies
            response = Response(
                {"message": "Access token refreshed."}, status=status.HTTP_200_OK
            )
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=refresh.access_token.lifetime.total_seconds(),
            )
            return response
        except InvalidToken:
            return Response({"error": "Invalid or expired refresh token."}, status=401)