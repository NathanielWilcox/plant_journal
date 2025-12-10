from rest_framework import serializers
from .models import Plant, Log

class LogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating logs - allows writing plant and log_type"""
    class Meta:
        model = Log
        fields = ['id', 'plant', 'log_type', 'sunlight_hours']
        read_only_fields = ['id']
    
    def validate_sunlight_hours(self, value):
        """Validate sunlight hours is between 0 and 24"""
        if value is not None and (value < 0 or value > 24):
            raise serializers.ValidationError("Sunlight hours must be between 0 and 24")
        return value

class LogSerializer(serializers.ModelSerializer):
    """Serializer for retrieving logs - includes timestamp and owner"""
    class Meta:
        model = Log
        fields = '__all__'
        read_only_fields = ['plant', 'timestamp', 'owner']

class PlantSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True, read_only=True)
    class Meta:
        model = Plant
        fields = '__all__'
        read_only_fields = ['logs', 'owner', 'added_at']

class PlantCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'category',
            'care_level',
            'watering_schedule',
            'sunlight_preference',
            'location',
            'pot_size',
            'owner',
            'added_at'
        ]
        read_only_fields = ['id', 'owner', 'added_at']