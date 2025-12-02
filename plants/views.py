from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from huggingface_hub import User
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from .models import Plant, Log
from .serializers import PlantCreateUpdateSerializer, PlantSerializer, LogSerializer

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


class LogViewSet(viewsets.ModelViewSet): # ViewSet for Log model
    queryset = Log.objects.all()

    serializer_class = LogSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): # get_queryset to filter logs by plants owned by user
        return Log.objects.filter(plant__owner=self.request.user).order_by('-timestamp')
    def perform_create(self, serializer): # perform_create to set owner of plant when creating log
        plant = serializer.validated_data['plant']
        if plant.owner != self.request.user:
            raise PermissionError("You do not have permission to add logs to this plant.")
        serializer.save()

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
