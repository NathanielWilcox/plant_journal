import os
import django
from django.conf import settings
from pathlib import Path

# Ensure Django is set up before running tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import pytest
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from plants.models import Plant, Log
import factory
from faker import Faker

fake = Faker()


# ============================================================================
# FACTORIES - Test Data Generators
# ============================================================================

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser_{n}')
    email = factory.Sequence(lambda n: f'testuser_{n}@example.com')
    password = 'Test@1234'

    @classmethod
    def create(cls, **kwargs):
        """Override create to hash password"""
        user = cls.build(**kwargs)
        user.set_password(kwargs.get('password', 'Test@1234'))
        user.save()
        return user


class PlantFactory(factory.django.DjangoModelFactory):
    """Factory for creating test plants"""
    class Meta:
        model = Plant

    name = factory.Faker('word')
    category = 'succulent'
    care_level = 'easy'
    watering_schedule = 'weekly'
    sunlight_preference = 'bright_indirect_light'
    location = factory.Faker('city')
    pot_size = 'medium'
    owner = factory.SubFactory(UserFactory)


class LogFactory(factory.django.DjangoModelFactory):
    """Factory for creating test logs"""
    class Meta:
        model = Log

    plant = factory.SubFactory(PlantFactory)
    log_type = 'water'
    sunlight_hours = 4.5
    owner = factory.LazyAttribute(lambda o: o.plant.owner)


# ============================================================================
# FIXTURES - Test Setup & Teardown
# ============================================================================

@pytest.fixture
def api_client():
    """Fixture providing an unauthenticated API client"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """Fixture providing an authenticated API client"""
    user = UserFactory.create(username='authuser', password='Test@1234')
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    api_client.user = user
    return api_client


@pytest.fixture
def test_user(db):
    """Fixture providing a test user"""
    return UserFactory.create(username='testuser', password='Test@1234')


@pytest.fixture
def test_user_2(db):
    """Fixture providing a second test user"""
    return UserFactory.create(username='testuser2', password='Test@1234')


@pytest.fixture
def test_plant(db, test_user):
    """Fixture providing a test plant owned by test_user"""
    return PlantFactory.create(owner=test_user, name='Test Plant')


@pytest.fixture
def test_plant_2(db, test_user_2):
    """Fixture providing a test plant owned by test_user_2"""
    return PlantFactory.create(owner=test_user_2, name='Other User Plant')


@pytest.fixture
def test_log(db, test_plant, test_user):
    """Fixture providing a test log for test_plant"""
    return LogFactory.create(plant=test_plant, owner=test_user, log_type='water')


@pytest.fixture
def test_logs(db, test_plant, test_user):
    """Fixture providing multiple test logs"""
    logs = []
    log_types = ['water', 'fertilize', 'prune']
    for i, log_type in enumerate(log_types):
        log = LogFactory.create(
            plant=test_plant,
            owner=test_user,
            log_type=log_type,
            sunlight_hours=3 + i
        )
        logs.append(log)
    return logs




@pytest.fixture
def api_client_with_user(db, test_user):
    """Fixture providing API client authenticated as test_user"""
    client = APIClient()
    refresh = RefreshToken.for_user(test_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.user = test_user
    return client


@pytest.fixture
def api_client_with_user_2(db, test_user_2):
    """Fixture providing API client authenticated as test_user_2"""
    client = APIClient()
    refresh = RefreshToken.for_user(test_user_2)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    client.user = test_user_2
    return client


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def valid_plant_data():
    """Fixture providing valid plant creation data"""
    return {
        'name': 'Monstera Deliciosa',
        'category': 'foliage_plant',
        'care_level': 'moderate',
        'watering_schedule': 'biweekly',
        'sunlight_preference': 'bright_indirect_light',
        'location': 'Living Room',
        'pot_size': 'large'
    }


@pytest.fixture
def valid_log_data(test_plant):
    """Fixture providing valid log creation data"""
    return {
        'plant': test_plant.id,
        'log_type': 'water',
        'sunlight_hours': 5.5
    }


@pytest.fixture
def valid_user_data():
    """Fixture providing valid user creation data"""
    return {
        'username': fake.user_name(),
        'email': fake.email(),
        'password': 'Test@1234'
    }


@pytest.fixture
def valid_login_data(test_user):
    """Fixture providing valid login credentials"""
    return {
        'username': 'testuser',
        'password': 'Test@1234'
    }
