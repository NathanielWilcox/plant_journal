"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core.auth.views import login_view, register_view
from core.auth.views import logout_view


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Auth endpoints (login/register)
    path('api/auth/login/', login_view, name='auth_login'),
    path('api/auth/register/', register_view, name='auth_register'),
    path('api/auth/logout/', logout_view, name='auth_logout'),

    # API endpoints
    path('api/', include('plants.urls')),
    path('api/users/', include('users.urls')),

    # Browsable API login
    path('api-auth/', include('rest_framework.urls')),
    
    # Swagger/OpenAPI documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('', RedirectView.as_view(url='http://127.0.0.1:7860/', permanent=False)),  # 👈 root goes to Gradio

    # JWT auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
