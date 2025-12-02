from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlantViewSet, LogViewSet

router = DefaultRouter()
router.register(r'plants', PlantViewSet, basename='plants')
router.register(r'logs', LogViewSet, basename='logs')

urlpatterns = [
    path('', include(router.urls)),
]