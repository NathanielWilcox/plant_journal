from rest_framework import serializers
from .models import Plant, Log

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
        read_only_fields = ['plant', 'timestamp']

class PlantSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True, read_only=True)
    class Meta:
        model = Plant
        fields = '__all__'
        read_only_fields = ['logs', 'owner', 'added_at']

class PlantCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['name', 'species', 'location']
        read_only_fields = ['owner', 'added_at']