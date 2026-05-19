from rest_framework import serializers
from django.db import transaction

from unibicos.models import Usuario
from unibicos.models import Compradores
from unibicos.models import Lojas
from unibicos.models import Entregadores


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user

    def get_user_roles(self, obj):
        roles = []
        if hasattr(obj, "comprador"):
            roles.append("comprador")
        if obj.lojas.exists():
            roles.append("vendedor")
        if obj.entregadores.exists():
            roles.append("entregador")
        return roles

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.id_instituicao:
            data["id_instituicao"] = obj.id_instituicao.id_instituicao

        data["roles"] = self.get_user_roles(obj)
        if hasattr(obj, "lojas") and obj.lojas.exists():
            loja = obj.lojas.first()
            data["loja"] = {
                "id_loja": loja.id_loja,
                "nome_fantasia": loja.nome_fantasia,
                "localizacao": loja.localizacao,
                "departamento": loja.departamento,
            }
        if hasattr(obj, "entregadores") and obj.entregadores.exists():
            entregador = obj.entregadores.first()
            data["entregador"] = {
                "id_entregador": entregador.id_entregador,
            }
        return data


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "nome",
            "email",
            "telefone",
            "cpf",
            "cnpj",
            "matricula",
            "id_instituicao",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "nome": {"required": False},
            "telefone": {"required": False},
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=["comprador", "vendedor", "entregador"], write_only=True
    )
    # Vendedor fields
    nome_fantasia = serializers.CharField(
        max_length=120, required=False, allow_blank=True, allow_null=True
    )
    localizacao = serializers.CharField(
        max_length=300, required=False, allow_blank=True, allow_null=True
    )
    departamento = serializers.CharField(
        max_length=120, required=False, allow_blank=True, allow_null=True
    )
    # Entregador fields
    agencia = serializers.CharField(
        max_length=10, required=False, allow_blank=True, allow_null=True
    )
    conta = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    codigo_banco = serializers.CharField(
        max_length=10, required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Usuario
        fields = [
            "email",
            "password",
            "nome",
            "cpf",
            "cnpj",
            "telefone",
            "matricula",
            "id_instituicao",
            "role",
            "nome_fantasia",
            "localizacao",
            "departamento",
            "agencia",
            "conta",
            "codigo_banco",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        with transaction.atomic():
            role = validated_data.pop("role")

            cnpj = validated_data.get("cnpj", None)
            nome_fantasia = validated_data.pop("nome_fantasia", None)
            localizacao = validated_data.pop("localizacao", None)
            departamento = validated_data.pop("departamento", None)

            _ = validated_data.pop("agencia", None)
            _ = validated_data.pop("conta", None)
            _ = validated_data.pop("codigo_banco", None)

            user = Usuario.objects.create_user(**validated_data)

            if cnpj is None:
                Compradores.objects.create(
                    id_usuario=user, id_user_cad=user
                )  # Todo usuário que não seja PJ é um comprador potencial.

            elif role == "entregador":
                Entregadores.objects.create(
                    id_usuario=user,
                    id_user_cad=user,
                )

            elif role == "vendedor":
                if not nome_fantasia or not localizacao:
                    raise serializers.ValidationError(
                        "nome_fantasia and localizacao are required for vendedores."
                    )
                Lojas.objects.create(
                    id_usuario=user,
                    id_user_cad=user,
                    nome_fantasia=nome_fantasia,
                    localizacao=localizacao,
                    departamento=departamento,
                )

        return user
