from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from huggingface_hub import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .models import Plant, Log
from .serializers import PlantCreateUpdateSerializer, PlantSerializer, LogSerializer, LogCreateSerializer

# Create your views here.    
class PlantViewSet(viewsets.ModelViewSet): # ViewSet for Plant model
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): # get_queryset to filter plants by owner
        return Plant.objects.filter(owner=self.request.user).order_by('-added_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PlantCreateUpdateSerializer
        return PlantSerializer

    def perform_create(self, serializer): # perform_create to set owner of plant when creating plant
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Custom route: GET /plants/{plant_id}/logs/ - returns logs for a specific plant"""
        plant = self.get_object()
        logs = plant.logs.all().order_by('-timestamp')
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)


class LogViewSet(viewsets.ModelViewSet): # ViewSet for Log model
    queryset = Log.objects.all()

    serializer_class = LogSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LogCreateSerializer
        return LogSerializer

    def get_queryset(self): # get_queryset to filter logs by plants owned by user
        return Log.objects.filter(plant__owner=self.request.user).order_by('-timestamp')
    def perform_create(self, serializer): # perform_create to set owner of plant when creating log
        plant = serializer.validated_data['plant']
        if plant.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(detail="You do not have permission to add logs to this plant.")
        serializer.save(owner=self.request.user)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
