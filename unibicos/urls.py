from rest_framework import routers
from django.urls import path

from unibicos.views import (
    AuthViewSet,
    CategoriasViewSet,
    CompradoresViewSet,
    EntregadoresViewSet,
    InstituicoesEnsinoViewSet,
    LojasViewSet,
    MovimentacoesViewSet,
    PagamentoViewSet,
    PedidosViewSet,
    ProdutosViewSet,
    UsuariosViewSet,
)

router = routers.DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"categorias", CategoriasViewSet, basename="categorias")
router.register(r"produtos", ProdutosViewSet, basename="produtos")
router.register(r"pedidos", PedidosViewSet, basename="pedidos")
router.register(r"entregadores", EntregadoresViewSet, basename="entregadores")
router.register(r"lojas", LojasViewSet, basename="lojas")
router.register(r"compradores", CompradoresViewSet, basename="compradores")
router.register(r"pagamentos", PagamentoViewSet, basename="pagamentos")
router.register(r"movimentacoes", MovimentacoesViewSet, basename="movimentacoes")
router.register(
    r"instituicoes_ensino", InstituicoesEnsinoViewSet, basename="instituicoes_ensino"
)
router.register(r"usuarios", UsuariosViewSet)

urlpatterns = router.urls
