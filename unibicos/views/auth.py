from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import action


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )
        return Response({"error": "Credenciais inválidas"}, status=400)

    @action(detail=False, methods=["post"])
    def signup(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name")
        phone = request.data.get("phone")
        if User.objects.filter(username=email).exists():
            return Response({"error": "Usuário já existe"}, status=400)
        user = User.objects.create_user(
            username=email, email=email, password=password, first_name=name
        )
        # Criar Usuario, etc. - ajustar conforme necessário
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
