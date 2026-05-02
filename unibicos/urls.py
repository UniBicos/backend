from rest_framework import routers
from django.urls import path

from unibicos.views import (
    CompradoresViewSet,
    EntregadoresViewSet,
    InstituicoesEnsinoViewSet,
    LojasViewSet,
    MovimentacoesViewSet,
    PagamentoViewSet,
    PedidosViewSet,
    ProdutosViewSet,
    UsuariosViewSet,
    stripe_webhook,
)

router = routers.DefaultRouter()
router.register(r"produtos", ProdutosViewSet)
router.register(r"pedidos", PedidosViewSet)
router.register(r"entregadores", EntregadoresViewSet)
router.register(r"lojas", LojasViewSet)
router.register(r"compradores", CompradoresViewSet)
router.register(r"pagamentos", PagamentoViewSet)
router.register(r"movimentacoes", MovimentacoesViewSet)
router.register(r"instituicoes_ensino", InstituicoesEnsinoViewSet)
router.register(r"usuarios", UsuariosViewSet)

urlpatterns = [
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),
] + router.urls
