from rest_framework import routers
from unibicos.views import ProdutosViewSet

router = routers.DefaultRouter()
router.register(r'produtos', ProdutosViewSet, basename='produtos')

urlpatterns = router.urls