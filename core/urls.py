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
from unibicos.services.webhook import stripe_webhook

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),
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
    # APP
    # ========================
    path("api/", include("unibicos.urls")),
]

# ========================
# MEDIA (UPLOAD DE IMAGEM)
# ========================
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
