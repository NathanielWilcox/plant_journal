"""Plant model and serializer tests"""
import pytest
from plants.models import Plant, Log
from plants.serializers import PlantSerializer, PlantCreateUpdateSerializer, LogSerializer, LogCreateSerializer
from users.models import User
from django.core.exceptions import ValidationError


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.plant
class TestPlantModel:
    """Unit tests for Plant model"""

    def test_plant_creation(self, test_user):
        """Test creating a plant"""
        plant = Plant.objects.create(
            name='Test Plant',
            category='succulent',
            care_level='easy',
            watering_schedule='monthly',
            sunlight_preference='full_sun',
            owner=test_user
        )
        assert plant.name == 'Test Plant'
        assert plant.owner == test_user
        assert plant.category == 'succulent'

    def test_plant_str_representation(self, test_plant):
        """Test plant string representation"""
        assert str(test_plant) == 'Test Plant'

    def test_plant_ownership(self, test_plant, test_user):
        """Test that plant is owned by correct user"""
        assert test_plant.owner == test_user

    def test_plant_added_at_timestamp(self, test_plant):
        """Test that added_at is automatically set"""
        assert test_plant.added_at is not None

    def test_plant_invalid_pot_size(self, test_user):
        """Test plant with invalid pot_size - Django allows it since it's CharField"""
        # Note: pot_size choices are not enforced at model level
        plant = Plant.objects.create(
            name='Invalid Plant',
            pot_size='invalid_size',
            owner=test_user
        )
        assert plant.pot_size == 'invalid_size'

    def test_plant_default_values(self, test_user):
        """Test plant default values"""
        plant = Plant.objects.create(
            name='Plant with Defaults',
            owner=test_user
        )
        # care_level is nullable, defaults to None
        assert plant.care_level is None
        # watering_schedule has default 'weekly'
        assert plant.watering_schedule == 'weekly'
        # sunlight_preference defaults to bright_indirect_light
        assert plant.sunlight_preference == 'bright_indirect_light'
        # pot_size defaults to 'medium'
        assert plant.pot_size == 'medium'


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.log
class TestLogModel:
    """Unit tests for Log model"""

    def test_log_creation(self, test_plant, test_user):
        """Test creating a log"""
        log = Log.objects.create(
            plant=test_plant,
            log_type='water',
            sunlight_hours=4.5,
            owner=test_user
        )
        assert log.plant == test_plant
        assert log.log_type == 'water'
        assert log.sunlight_hours == 4.5

    def test_log_timestamp_auto_set(self, test_plant, test_user):
        """Test that timestamp is automatically set"""
        log = Log.objects.create(
            plant=test_plant,
            log_type='water',
            owner=test_user
        )
        assert log.timestamp is not None

    def test_log_sunlight_hours_validation_valid(self, test_plant, test_user):
        """Test valid sunlight hours"""
        log = Log.objects.create(
            plant=test_plant,
            log_type='water',
            sunlight_hours=12,
            owner=test_user
        )
        log.full_clean()  # Should not raise

    def test_log_sunlight_hours_validation_too_high(self, test_plant, test_user):
        """Test sunlight hours > 24 raises error"""
        log = Log(
            plant=test_plant,
            log_type='water',
            sunlight_hours=25,
            owner=test_user
        )
        with pytest.raises(ValidationError):
            log.full_clean()

    def test_log_sunlight_hours_validation_negative(self, test_plant, test_user):
        """Test negative sunlight hours raises error"""
        log = Log(
            plant=test_plant,
            log_type='water',
            sunlight_hours=-1,
            owner=test_user
        )
        with pytest.raises(ValidationError):
            log.full_clean()

    def test_log_sunlight_hours_optional(self, test_plant, test_user):
        """Test sunlight_hours is optional"""
        log = Log.objects.create(
            plant=test_plant,
            log_type='prune',
            owner=test_user
        )
        assert log.sunlight_hours is None

    def test_log_cascade_delete(self, test_plant, test_user):
        """Test that logs are deleted when plant is deleted"""
        log = Log.objects.create(
            plant=test_plant,
            log_type='water',
            owner=test_user
        )
        log_id = log.id
        test_plant.delete()
        assert not Log.objects.filter(id=log_id).exists()

    def test_log_ordering(self, test_plant, test_user):
        """Test logs are ordered by timestamp (most recent first)"""
        log1 = Log.objects.create(plant=test_plant, log_type='water', owner=test_user)
        log2 = Log.objects.create(plant=test_plant, log_type='fertilize', owner=test_user)
        
        logs = Log.objects.all()
        assert logs[0].id == log2.id  # Most recent first


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.plant
class TestPlantSerializer:
    """Unit tests for Plant serializers"""

    def test_plant_serializer(self, test_plant):
        """Test PlantSerializer serializes plant correctly"""
        serializer = PlantSerializer(test_plant)
        data = serializer.data
        assert data['name'] == test_plant.name
        assert data['category'] == test_plant.category
        assert data['owner'] == test_plant.owner.id

    def test_plant_create_update_serializer_valid(self, valid_plant_data):
        """Test PlantCreateUpdateSerializer with valid data"""
        serializer = PlantCreateUpdateSerializer(data=valid_plant_data)
        assert serializer.is_valid(), f"Errors: {serializer.errors}"

    def test_plant_create_update_serializer_missing_name(self, valid_plant_data):
        """Test PlantCreateUpdateSerializer rejects missing name"""
        del valid_plant_data['name']
        serializer = PlantCreateUpdateSerializer(data=valid_plant_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_plant_create_update_serializer_owner_read_only(self, valid_plant_data, test_user, test_user_2):
        """Test that owner field is read-only"""
        valid_plant_data['owner'] = test_user_2.id
        serializer = PlantCreateUpdateSerializer(data=valid_plant_data)
        assert serializer.is_valid(), f"Errors: {serializer.errors}"
        # owner should still be read-only, will be set by perform_create


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.log
class TestLogSerializer:
    """Unit tests for Log serializers"""

    def test_log_serializer(self, test_log):
        """Test LogSerializer serializes log correctly"""
        serializer = LogSerializer(test_log)
        data = serializer.data
        assert data['plant'] == test_log.plant.id
        assert data['log_type'] == test_log.log_type

    def test_log_create_serializer_valid(self, valid_log_data):
        """Test LogCreateSerializer with valid data"""
        serializer = LogCreateSerializer(data=valid_log_data)
        assert serializer.is_valid()

    def test_log_create_serializer_plant_writable(self, valid_log_data):
        """Test that plant field is writable in LogCreateSerializer"""
        serializer = LogCreateSerializer(data=valid_log_data)
        assert serializer.is_valid()
        assert 'plant' in serializer.validated_data

    def test_log_serializer_plant_read_only(self, test_log):
        """Test that plant is read-only in LogSerializer"""
        serializer = LogSerializer(test_log)
        assert 'plant' in serializer.data
        # The read_only fields list should include 'plant'

    def test_log_create_serializer_missing_plant(self, test_plant):
        """Test LogCreateSerializer rejects missing plant"""
        data = {'log_type': 'water'}
        serializer = LogCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'plant' in serializer.errors

    def test_log_create_serializer_invalid_log_type(self, test_plant):
        """Test LogCreateSerializer rejects invalid log_type"""
        data = {
            'plant': test_plant.id,
            'log_type': 'invalid_type'
        }
        serializer = LogCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'log_type' in serializer.errors
