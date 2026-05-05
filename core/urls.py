"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

# 🔥 IMPORTE AS VIEWS DO CARRINHO
from unibicos.views import (
    get_carrinho,
    adicionar_ao_carrinho,
    remover_do_carrinho,
    finalizar_carrinho
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # ========================
    # AUTH (JWT)
    # ========================
    path("api/token/", TokenObtainPairView.as_view(), name="token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),

    # ========================
    # DOCUMENTAÇÃO
    # ========================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    
    # ========================
    # CARRINHO (SACOLA)
    # ========================
    path('api/carrinho/', get_carrinho, name='get_carrinho'),
    path('api/carrinho/adicionar/', adicionar_ao_carrinho, name='adicionar_carrinho'),
    path('api/carrinho/remover/<int:produto_id>/', remover_do_carrinho, name='remover_carrinho'),
    path('api/carrinho/finalizar/', finalizar_carrinho, name='finalizar_carrinho'),
    
    # ========================
    # APP
    # ========================
    path("api/", include("unibicos.urls")),
]

# ========================
# MEDIA (UPLOAD DE IMAGEM)
# ========================
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)