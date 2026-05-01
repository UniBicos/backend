from rest_framework import serializers

from unibicos.models import Pagamento


class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id_pagamento': obj.id_pagamento,
            'id_pedido': obj.id_pedido.id_pedido,
            'status_pagamento': obj.status_pagamento,
        }
