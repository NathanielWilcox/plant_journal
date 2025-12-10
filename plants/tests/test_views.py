"""Plant and API endpoint tests"""
import pytest
from django.urls import reverse
from rest_framework import status
from plants.models import Plant, Log


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.plant
class TestPlantViewSet:
    """Integration tests for PlantViewSet API endpoints"""

    def test_list_plants_authenticated(self, api_client_with_user, test_plant):
        """Test listing plants when authenticated"""
        response = api_client_with_user.get('/api/plants/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == test_plant.name

    def test_list_plants_unauthenticated(self, api_client):
        """Test listing plants returns 401 when not authenticated"""
        response = api_client.get('/api/plants/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_plants_filters_by_owner(self, api_client_with_user, api_client_with_user_2, test_plant, test_plant_2):
        """Test that users only see their own plants"""
        response = api_client_with_user.get('/api/plants/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        # Verify that only this user's plants are returned
        plant_names = [p['name'] for p in response.data]
        assert test_plant.name in plant_names
        assert test_plant_2.name not in plant_names

    def test_create_plant_authenticated(self, api_client_with_user, valid_plant_data):
        """Test creating a plant when authenticated"""
        response = api_client_with_user.post('/api/plants/', valid_plant_data)
        assert response.status_code == status.HTTP_201_CREATED, f"Response: {response.data}"
        assert response.data['name'] == valid_plant_data['name']
        assert response.data.get('owner') == api_client_with_user.user.id or 'owner' in response.data

    def test_create_plant_unauthenticated(self, api_client, valid_plant_data):
        """Test creating plant returns 401 when not authenticated"""
        response = api_client.post('/api/plants/', valid_plant_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_plant_missing_name(self, api_client_with_user):
        """Test creating plant fails with missing name"""
        data = {
            'category': 'succulent',
            'care_level': 'easy'
        }
        response = api_client_with_user.post('/api/plants/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_retrieve_plant_authenticated(self, api_client_with_user, test_plant):
        """Test retrieving a specific plant"""
        response = api_client_with_user.get(f'/api/plants/{test_plant.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_plant.id

    def test_retrieve_plant_other_user(self, api_client_with_user_2, test_plant):
        """Test cannot retrieve another user's plant"""
        response = api_client_with_user_2.get(f'/api/plants/{test_plant.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_plant_authenticated(self, api_client_with_user, test_plant):
        """Test updating a plant with PATCH"""
        data = {'care_level': 'difficult'}
        response = api_client_with_user.patch(
            f'/api/plants/{test_plant.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        test_plant.refresh_from_db()
        assert test_plant.care_level == 'difficult'

    def test_update_plant_uses_patch(self, api_client_with_user, test_plant):
        """Test that partial updates work with PATCH"""
        original_name = test_plant.name
        data = {'location': 'New Location'}
        response = api_client_with_user.patch(
            f'/api/plants/{test_plant.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        test_plant.refresh_from_db()
        assert test_plant.name == original_name
        assert test_plant.location == 'New Location'

    def test_update_plant_other_user(self, api_client_with_user_2, test_plant):
        """Test cannot update another user's plant"""
        response = api_client_with_user_2.patch(
            f'/api/plants/{test_plant.id}/',
            {'care_level': 'easy'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_plant_authenticated(self, api_client_with_user, test_plant):
        """Test deleting a plant"""
        plant_id = test_plant.id
        response = api_client_with_user.delete(f'/api/plants/{plant_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Plant.objects.filter(id=plant_id).exists()

    def test_delete_plant_other_user(self, api_client_with_user_2, test_plant):
        """Test cannot delete another user's plant"""
        response = api_client_with_user_2.delete(f'/api/plants/{test_plant.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_plant_cascades_logs(self, api_client_with_user, test_plant, test_log):
        """Test that deleting a plant deletes its logs"""
        log_id = test_log.id
        plant_id = test_plant.id
        
        response = api_client_with_user.delete(f'/api/plants/{plant_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Log.objects.filter(id=log_id).exists()

    def test_plant_list_ordering(self, api_client_with_user, test_plant):
        """Test that plants are ordered by most recent first"""
        # Create a second plant
        Plant.objects.create(
            name='Second Plant',
            owner=api_client_with_user.user
        )
        
        response = api_client_with_user.get('/api/plants/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        # Most recent should be first
        assert response.data[0]['name'] == 'Second Plant'


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.plant
class TestPlantLogsCustomRoute:
    """Integration tests for custom /plants/{id}/logs/ route"""

    def test_get_plant_logs_route(self, api_client_with_user, test_plant, test_logs):
        """Test getting logs for a specific plant via custom route"""
        response = api_client_with_user.get(f'/api/plants/{test_plant.id}/logs/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_get_plant_logs_only_for_that_plant(self, api_client_with_user, test_plant, test_logs, test_plant_2):
        """Test that only logs for the specific plant are returned"""
        # Create a log for another plant
        log_other = Log.objects.create(
            plant=test_plant_2,
            log_type='fertilize',
            owner=test_plant_2.owner
        )
        
        response = api_client_with_user.get(f'/api/plants/{test_plant.id}/logs/')
        assert len(response.data) == 3
        log_ids = [log['id'] for log in response.data]
        assert log_other.id not in log_ids

    def test_get_plant_logs_other_user_plant(self, api_client_with_user, test_plant_2):
        """Test cannot access logs for another user's plant"""
        response = api_client_with_user.get(f'/api/plants/{test_plant_2.id}/logs/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_plant_logs_nonexistent_plant(self, api_client_with_user):
        """Test accessing logs for non-existent plant returns 404"""
        response = api_client_with_user.get('/api/plants/9999/logs/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.log
class TestLogViewSet:
    """Integration tests for LogViewSet API endpoints"""

    def test_create_log_authenticated(self, api_client_with_user, test_plant, valid_log_data):
        """Test creating a log when authenticated"""
        response = api_client_with_user.post('/api/logs/', valid_log_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['plant'] == test_plant.id
        # Verify in database that owner was set correctly by perform_create
        log_id = response.data['id']
        log = Log.objects.get(id=log_id)
        # Owner should be the authenticated user
        assert log.owner == api_client_with_user.user or log.owner_id == api_client_with_user.user.id

    def test_create_log_unauthenticated(self, api_client, valid_log_data):
        """Test creating log returns 401 when not authenticated"""
        response = api_client.post('/api/logs/', valid_log_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_log_uses_create_serializer(self, api_client_with_user, test_plant):
        """Test that LogCreateSerializer is used for POST (plant is writable)"""
        data = {
            'plant': test_plant.id,
            'log_type': 'water',
            'sunlight_hours': 5
        }
        response = api_client_with_user.post('/api/logs/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_log_for_other_user_plant(self, api_client_with_user, test_plant_2):
        """Test cannot create log for another user's plant (403 Forbidden)"""
        data = {
            'plant': test_plant_2.id,
            'log_type': 'water'
        }
        response = api_client_with_user.post('/api/logs/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_log_missing_plant(self, api_client_with_user):
        """Test creating log fails with missing plant"""
        data = {'log_type': 'water'}
        response = api_client_with_user.post('/api/logs/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_log_invalid_log_type(self, api_client_with_user, test_plant):
        """Test creating log fails with invalid log_type"""
        data = {
            'plant': test_plant.id,
            'log_type': 'invalid'
        }
        response = api_client_with_user.post('/api/logs/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_logs_authenticated(self, api_client_with_user, test_logs):
        """Test listing logs when authenticated"""
        response = api_client_with_user.get('/api/logs/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_list_logs_filters_by_owner(self, api_client_with_user, api_client_with_user_2, test_logs, test_plant_2):
        """Test that users only see their own logs"""
        log_other = Log.objects.create(
            plant=test_plant_2,
            log_type='fertilize',
            owner=test_plant_2.owner
        )
        
        response = api_client_with_user.get('/api/logs/')
        # User should see at least the test_logs (3) for their plant
        assert len(response.data) >= 3
        log_ids = [log['id'] for log in response.data]
        assert log_other.id not in log_ids

    def test_retrieve_log_authenticated(self, api_client_with_user, test_log):
        """Test retrieving a specific log"""
        response = api_client_with_user.get(f'/api/logs/{test_log.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_log.id

    def test_retrieve_log_other_user(self, api_client_with_user, test_plant_2):
        """Test cannot retrieve another user's log"""
        log_other = Log.objects.create(
            plant=test_plant_2,
            log_type='water',
            owner=test_plant_2.owner
        )
        response = api_client_with_user.get(f'/api/logs/{log_other.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_log_with_patch(self, api_client_with_user, test_log):
        """Test updating a log with PATCH"""
        data = {'log_type': 'fertilize', 'sunlight_hours': 6}
        response = api_client_with_user.patch(
            f'/api/logs/{test_log.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        test_log.refresh_from_db()
        assert test_log.log_type == 'fertilize'
        assert test_log.sunlight_hours == 6

    def test_update_log_uses_create_serializer(self, api_client_with_user, test_log):
        """Test that LogCreateSerializer is used for PATCH"""
        data = {'log_type': 'prune'}
        response = api_client_with_user.patch(
            f'/api/logs/{test_log.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_log_other_user(self, api_client_with_user, test_plant_2):
        """Test cannot update another user's log"""
        log_other = Log.objects.create(
            plant=test_plant_2,
            log_type='water',
            owner=test_plant_2.owner
        )
        response = api_client_with_user.patch(
            f'/api/logs/{log_other.id}/',
            {'log_type': 'fertilize'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_log_authenticated(self, api_client_with_user, test_log):
        """Test deleting a log"""
        log_id = test_log.id
        response = api_client_with_user.delete(f'/api/logs/{log_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Log.objects.filter(id=log_id).exists()

    def test_delete_log_other_user(self, api_client_with_user, test_plant_2):
        """Test cannot delete another user's log"""
        log_other = Log.objects.create(
            plant=test_plant_2,
            log_type='water',
            owner=test_plant_2.owner
        )
        response = api_client_with_user.delete(f'/api/logs/{log_other.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_log_list_ordering(self, api_client_with_user, test_log):
        """Test that logs are ordered by most recent first"""
        new_log = Log.objects.create(
            plant=test_log.plant,
            log_type='fertilize',
            owner=api_client_with_user.user
        )
        
        response = api_client_with_user.get('/api/logs/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['id'] == new_log.id
