from django.urls import path
from .views import (
    RegisterView,
    UserDetailView,
    MeView,
    ValidateTokenView,
    LogoutView,
)

urlpatterns = [
    # Registration
    path("", RegisterView.as_view(), name="user-register"),          # POST /api/users/

    # Current user convenience endpoints
    path("me/", MeView.as_view(), name="user-me"),                   # GET/PUT /api/users/me/

    # Per-user endpoints (admin or self)
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"), # GET/PUT/DELETE /api/users/<user_id>/
]