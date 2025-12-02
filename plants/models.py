from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from core.auth.decorators import with_db_retry


class Plant(models.Model):
    POT_SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('x-large', 'X-Large')
    ]
    
    CATEGORY_CHOICES = [
        ('succulent', 'Succulent'),
        ('herb', 'Herb'),
        ('fern', 'Fern'),
        ('flowering_plant', 'Flowering Plant'),
        ('vegetable', 'Vegetable'),
        ('foliage_plant', 'Foliage Plant')
    ]
    
    WATERING_SCHEDULE_CHOICES = [
        ('daily', 'Daily'),
        ('twice_weekly', 'Twice Weekly'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
        ('infrequent', 'Infrequent'),
        ('moderate', 'Moderate'),
        ('consistent', 'Consistent'),
        ('when_soil_is_dry', 'When Soil is Dry'),
        ('frequent', 'Frequent'),
        ('occasionally', 'Occasionally'),
        ('none', 'None')
    ]
    
    SUNLIGHT_PREFERENCE_CHOICES = [
        ('full_sun', 'Full Sun'),
        ('partial_sun', 'Partial Sun'),
        ('partial_shade', 'Partial Shade'),
        ('full_shade', 'Full Shade'),
        ('bright_indirect_light', 'Bright Indirect Light'),
        ('indirect_light', 'Indirect Light'),
        ('low_light', 'Low Light'),
        ('medium_light', 'Medium Light')
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='foliage_plant')
    care_level = models.CharField(max_length=50, blank=True, null=True, help_text="Overall care difficulty (e.g., Easy, Moderate)")
    watering_schedule = models.CharField(
        max_length=50, 
        choices=WATERING_SCHEDULE_CHOICES,
        default='weekly',
        help_text="How often to water the plant"
    )
    sunlight_preference = models.CharField(
        max_length=50, 
        choices=SUNLIGHT_PREFERENCE_CHOICES,
        default='bright_indirect_light',
        help_text="Amount of sunlight needed"
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    pot_size = models.CharField(max_length=10, choices=POT_SIZE_CHOICES, default='medium')
    added_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="plants",
        null=True,
        blank=True
    )

    def suggest_care_settings(self):
        """Suggest care settings based on plant name and category"""
        from .utils import suggest_plant_care
        suggestions = suggest_plant_care(self.name, self.category)
        if suggestions:
            self.watering_schedule = suggestions['watering_schedule']
            self.sunlight_preference = suggestions['sunlight_preference']
            return True
        return False

    def save(self, *args, **kwargs):
        """Override save to auto-suggest care settings if not provided"""
        if not self.watering_schedule or not self.sunlight_preference:
            self.suggest_care_settings()
        super().save(*args, **kwargs)

    @with_db_retry(max_retries=3)
    def get_last_watering(self):
        """Get the most recent watering log."""
        return self.logs.filter(log_type='water').order_by('-timestamp').first()

    @with_db_retry(max_retries=3)
    def get_watering_schedule(self, days=30):
        """Analyze watering pattern over the last specified days."""
        recent_waterings = self.logs.filter(
            log_type='water',
            timestamp__gte=timezone.now() - timedelta(days=days)
        ).order_by('timestamp')
        return recent_waterings

    @with_db_retry(max_retries=3)
    def needs_water(self, days_threshold=7):
        """Check if plant needs water based on last watering."""
        last_watering = self.get_last_watering()
        if not last_watering:
            return True
        days_since_watering = (timezone.now() - last_watering.timestamp).days
        return days_since_watering >= days_threshold

    @with_db_retry(max_retries=3)
    def get_maintenance_summary(self, days=30):
        """Get summary of all maintenance activities."""
        recent_logs = self.logs.filter(
            timestamp__gte=timezone.now() - timedelta(days=days)
        ).order_by('-timestamp')
        return {
            'water_count': recent_logs.filter(log_type='water').count(),
            'fertilize_count': recent_logs.filter(log_type='fertilize').count(),
            'prune_count': recent_logs.filter(log_type='prune').count(),
            'total_water_amount': sum(log.water_amount or 0 for log in recent_logs.filter(log_type='water')),
            'avg_sunlight_hours': recent_logs.filter(sunlight_hours__isnull=False).aggregate(
                models.Avg('sunlight_hours')
            )['sunlight_hours__avg']
        }

class Log(models.Model):
    PLANT_LOG_CHOICES = [
        ('water','water'),
        ('fertilize','fertilize'),
        ('prune','prune')
    ]
    
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=20, choices=PLANT_LOG_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    sunlight_hours = models.FloatField(null=True, blank=True, help_text="Number of hours of sunlight received (0-24)")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="logs",
        null=True,
        blank=True
    )

    def clean(self):
        """Validate log data."""
        # Sunlight hours validation only if provided
        if self.sunlight_hours is not None and (self.sunlight_hours < 0 or self.sunlight_hours > 24):
            raise ValidationError({'sunlight_hours': 'Sunlight hours must be between 0 and 24'})

    def save(self, *args, **kwargs):
        """Override save to handle special cases."""
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to ensure photo cleanup."""
        self.delete
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-timestamp']  # Most recent logs first


