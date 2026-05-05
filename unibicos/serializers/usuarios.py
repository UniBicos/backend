import stripe

from rest_framework import serializers

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

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.id_instituicao:
            data["id_instituicao"] = obj.id_instituicao.id_instituicao
        return data


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
    conta = serializers.CharField(
        max_length=20, required=False, allow_blank=True, allow_null=True
    )
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
        role = validated_data.pop("role")

        # Vendedor/Loja fields
        nome_fantasia = validated_data.pop("nome_fantasia", None)
        localizacao = validated_data.pop("localizacao", None)
        departamento = validated_data.pop("departamento", None)

        # Entregador fields
        agencia = validated_data.pop("agencia", None)
        conta = validated_data.pop("conta", None)
        codigo_banco = validated_data.pop("codigo_banco", None)

        user = Usuario.objects.create_user(**validated_data)

        if role == "comprador":
            Compradores.objects.create(id_usuario=user, id_user_cad=user)
        elif role == "vendedor":
            if not nome_fantasia or not localizacao:
                raise serializers.ValidationError(
                    "nome_fantasia and localizacao are required for vendedores."
                )

            # Stripe account creation for Loja
            try:
                account = stripe.Account.create(
                    type="express",
                    country="BR",
                    email=user.email,
                    business_type="individual",  # Assuming individual for now
                    business_profile={"name": nome_fantasia},
                    metadata={"merchant_name": user.nome},
                )
                Lojas.objects.create(
                    id_usuario=user,
                    id_user_cad=user,
                    nome_fantasia=nome_fantasia,
                    localizacao=localizacao,
                    departamento=departamento,
                    id_stripe=account.id,
                )
            except Exception as e:
                user.delete()
                raise serializers.ValidationError({"stripe_error": str(e)})

        elif role == "entregador":
            if not agencia or not conta or not codigo_banco:
                raise serializers.ValidationError(
                    "agencia, conta, and codigo_banco are required for entregadores."
                )

            # Stripe account creation for Entregador
            try:
                account = stripe.Account.create(
                    type="express",
                    country="BR",
                    email=user.email,
                    business_type="individual",
                    business_profile={"name": user.nome},
                    metadata={"merchant_name": user.nome},
                )
                bank_account = stripe.Account.create_external_account(
                    account.id,
                    external_account={
                        "object": "bank_account",
                        "country": "BR",
                        "currency": "brl",
                        "routing_number": f"{codigo_banco}-{agencia}",
                        "account_number": conta,
                    },
                )
                Entregadores.objects.create(
                    id_usuario=user,
                    id_user_cad=user,
                    id_stripe=account.id,
                    id_bancaria_stripe=bank_account.id,
                )
            except Exception as e:
                user.delete()
                raise serializers.ValidationError({"stripe_error": str(e)})

        return user
