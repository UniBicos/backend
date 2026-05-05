from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from unibicos.models import Usuario
from unibicos.serializers import UsuarioSerializer, UserRegistrationSerializer


class UsuariosViewSet(viewsets.ViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def list(self, request):
        queryset = Usuario.objects.all()
        return Response(UsuarioSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(id_usuario=pk)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=404)

        return Response(UsuarioSerializer(usuario).data)

    def create(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Usuário cadastrado com sucesso",
                    "data": UsuarioSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=201,
            )
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(id_usuario=pk)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=404)

        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Usuário alterado com sucesso",
                    "data": UsuarioSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(id_usuario=pk)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=404)

        usuario.delete()
        return Response({"message": "Usuário deletado com sucesso"}, status=204)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="register",
    )
    def register(self, request):
        print(request.data)
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Usuário cadastrado com sucesso",
                "data": UsuarioSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=201,
        )
