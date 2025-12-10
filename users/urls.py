from django.urls import path
from .views import (
    RegisterView,
    UserUpdateView,
)

urlpatterns = [
    # Registration
    path("", RegisterView.as_view(), name="user-register"),          # POST /api/users/

    # Current user convenience endpoints
    path("me/", UserUpdateView.as_view(), name="user-me"),           # GET/PUT /api/users/me/
]