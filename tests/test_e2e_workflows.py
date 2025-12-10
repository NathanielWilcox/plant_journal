"""End-to-end comprehensive test scenarios"""
import pytest
from rest_framework import status
from plants.models import Plant, Log
from users.models import User


@pytest.mark.django_db
@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteApplicationWorkflow:
    """End-to-end tests for complete application workflows"""

    def test_new_user_full_journey(self, api_client):
        """Test complete journey of a new user from signup to managing plants and logs"""
        
        # 1. REGISTER NEW USER
        register_data = {
            'username': 'e2e_user',
            'email': 'e2e@example.com',
            'password': 'E2E@Password123'
        }
        register_resp = api_client.post('/api/auth/register/', register_data)
        assert register_resp.status_code == status.HTTP_201_CREATED
        token = register_resp.data['token']
        user_id = register_resp.data['user']['id']
        
        # Authenticate
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 2. VERIFY ACCOUNT CREATED
        user_resp = api_client.get('/api/users/me/')
        assert user_resp.status_code == status.HTTP_200_OK
        assert user_resp.data['username'] == 'e2e_user'
        
        # 3. UPDATE ACCOUNT INFO
        update_resp = api_client.patch(
            '/api/users/me/',
            {'email': 'newemail@example.com'}
        )
        assert update_resp.status_code == status.HTTP_200_OK
        
        # 4. CREATE FIRST PLANT
        plant1_data = {
            'name': 'Monstera',
            'category': 'foliage_plant',
            'care_level': 'moderate',
            'watering_schedule': 'biweekly',
            'sunlight_preference': 'bright_indirect_light',
            'location': 'Living Room',
            'pot_size': 'large'
        }
        plant1_resp = api_client.post('/api/plants/', plant1_data)
        assert plant1_resp.status_code == status.HTTP_201_CREATED
        plant1_id = plant1_resp.data['id']
        
        # 5. CREATE SECOND PLANT
        plant2_data = {
            'name': 'Succulent',
            'category': 'succulent',
            'care_level': 'easy',
            'watering_schedule': 'monthly',
            'sunlight_preference': 'full_sun',
            'location': 'Desk',
            'pot_size': 'small'
        }
        plant2_resp = api_client.post('/api/plants/', plant2_data)
        assert plant2_resp.status_code == status.HTTP_201_CREATED
        plant2_id = plant2_resp.data['id']
        
        # 6. VERIFY PLANTS APPEAR IN LIST
        plants_resp = api_client.get('/api/plants/')
        assert plants_resp.status_code == status.HTTP_200_OK
        assert len(plants_resp.data) == 2
        
        # 7. CREATE LOGS FOR PLANT 1
        log_types = ['water', 'fertilize', 'prune']
        for log_type in log_types:
            log_data = {
                'plant': plant1_id,
                'log_type': log_type,
                'sunlight_hours': 6
            }
            log_resp = api_client.post('/api/logs/', log_data)
            assert log_resp.status_code == status.HTTP_201_CREATED
        
        # 8. CREATE LOGS FOR PLANT 2
        for i, log_type in enumerate(['water', 'fertilize']):
            log_data = {
                'plant': plant2_id,
                'log_type': log_type,
                'sunlight_hours': 10 + i
            }
            log_resp = api_client.post('/api/logs/', log_data)
            assert log_resp.status_code == status.HTTP_201_CREATED
        
        # 9. VIEW LOGS FOR SPECIFIC PLANT
        plant1_logs = api_client.get(f'/api/plants/{plant1_id}/logs/')
        assert plant1_logs.status_code == status.HTTP_200_OK
        assert len(plant1_logs.data) == 3
        
        plant2_logs = api_client.get(f'/api/plants/{plant2_id}/logs/')
        assert plant2_logs.status_code == status.HTTP_200_OK
        assert len(plant2_logs.data) == 2
        
        # 10. UPDATE PLANT DETAILS
        update_plant = api_client.patch(
            f'/api/plants/{plant1_id}/',
            {'care_level': 'difficult', 'location': 'Bedroom'}
        )
        assert update_plant.status_code == status.HTTP_200_OK
        
        # 11. UPDATE LOG DETAILS
        logs_resp = api_client.get('/api/logs/')
        first_log_id = logs_resp.data[0]['id']
        update_log = api_client.patch(
            f'/api/logs/{first_log_id}/',
            {'log_type': 'prune', 'sunlight_hours': 8}
        )
        assert update_log.status_code == status.HTTP_200_OK
        
        # 12. VERIFY TOTAL LOG COUNT
        all_logs = api_client.get('/api/logs/')
        assert len(all_logs.data) == 5
        
        # 13. DELETE ONE PLANT (cascades logs)
        delete_plant = api_client.delete(f'/api/plants/{plant2_id}/')
        assert delete_plant.status_code == status.HTTP_204_NO_CONTENT
        
        # 14. VERIFY PLANT IS DELETED
        verify_delete = api_client.get(f'/api/plants/{plant2_id}/')
        assert verify_delete.status_code == status.HTTP_404_NOT_FOUND
        
        # 15. VERIFY PLANT LOGS ARE DELETED
        remaining_logs = api_client.get('/api/logs/')
        assert len(remaining_logs.data) == 3
        
        # 16. VERIFY ONLY ONE PLANT REMAINS
        plants_final = api_client.get('/api/plants/')
        assert len(plants_final.data) == 1
        
        # 17. LOGOUT
        logout_resp = api_client.post('/api/auth/logout/')
        assert logout_resp.status_code == status.HTTP_204_NO_CONTENT

    def test_multiple_users_independent_workflows(self, api_client):
        """Test that multiple users can work independently without interference"""
        
        # USER 1: Register and create plants
        user1_data = {
            'username': 'user_one',
            'email': 'user1@example.com',
            'password': 'Pass@1234'
        }
        user1_reg = api_client.post('/api/auth/register/', user1_data)
        assert user1_reg.status_code == status.HTTP_201_CREATED
        user1_token = user1_reg.data['token']
        
        # USER 1: Create plant
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user1_token}')
        user1_plant = api_client.post(
            '/api/plants/',
            {'name': 'User1Plant', 'category': 'succulent', 'care_level': 'easy'}
        )
        assert user1_plant.status_code == status.HTTP_201_CREATED
        user1_plant_id = user1_plant.data['id']
        
        # USER 1: Create log
        user1_log = api_client.post(
            '/api/logs/',
            {'plant': user1_plant_id, 'log_type': 'water'}
        )
        assert user1_log.status_code == status.HTTP_201_CREATED
        
        # Unauthenticate
        api_client.credentials()
        
        # USER 2: Register and create plants
        user2_data = {
            'username': 'user_two',
            'email': 'user2@example.com',
            'password': 'Pass@1234'
        }
        user2_reg = api_client.post('/api/auth/register/', user2_data)
        assert user2_reg.status_code == status.HTTP_201_CREATED
        user2_token = user2_reg.data['token']
        
        # USER 2: Create plant
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user2_token}')
        user2_plant = api_client.post(
            '/api/plants/',
            {'name': 'User2Plant', 'category': 'foliage_plant', 'care_level': 'moderate', 'watering_schedule': 'weekly', 'sunlight_preference': 'partial_shade'}
        )
        assert user2_plant.status_code == status.HTTP_201_CREATED
        user2_plant_id = user2_plant.data['id']
        
        # USER 2: Verify they only see their plant
        user2_plants = api_client.get('/api/plants/')
        assert len(user2_plants.data) == 1
        assert user2_plants.data[0]['name'] == 'User2Plant'
        
        # USER 2: Attempt to access User 1's plant (should fail)
        user2_access_u1 = api_client.get(f'/api/plants/{user1_plant_id}/')
        assert user2_access_u1.status_code == status.HTTP_404_NOT_FOUND
        
        # USER 2: Attempt to create log for User 1's plant (should fail)
        user2_log_attempt = api_client.post(
            '/api/logs/',
            {'plant': user1_plant_id, 'log_type': 'water'}
        )
        assert user2_log_attempt.status_code == status.HTTP_403_FORBIDDEN
        
        # USER 1: Switch back and verify data integrity
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user1_token}')
        user1_plants = api_client.get('/api/plants/')
        assert len(user1_plants.data) == 1
        assert user1_plants.data[0]['name'] == 'User1Plant'
        
        # USER 1: Verify their logs
        user1_logs = api_client.get('/api/logs/')
        assert len(user1_logs.data) == 1


@pytest.mark.django_db
@pytest.mark.django_db
@pytest.mark.e2e
@pytest.mark.slow
class TestErrorRecoveryScenarios:
    """Test application behavior during error scenarios"""

    def test_handle_malformed_requests(self, api_client_with_user):
        """Test handling of malformed requests"""
        
        # Missing required field
        response = api_client_with_user.post(
            '/api/plants/',
            {'category': 'succulent'}  # Missing 'name'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify plants list still works after error
        plants = api_client_with_user.get('/api/plants/')
        assert plants.status_code == status.HTTP_200_OK

    def test_handle_unauthorized_access(self, api_client_with_user, test_plant_2):
        """Test handling of unauthorized access attempts"""
        
        # Try to access another user's plant
        response = api_client_with_user.get(f'/api/plants/{test_plant_2.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify authenticated user's own data still accessible
        response = api_client_with_user.get('/api/plants/')
        assert response.status_code == status.HTTP_200_OK

    def test_handle_nonexistent_resources(self, api_client_with_user):
        """Test handling of requests for non-existent resources"""
        
        # Get non-existent plant
        response = api_client_with_user.get('/api/plants/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Get non-existent log
        response = api_client_with_user.get('/api/logs/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify app is still responsive
        response = api_client_with_user.get('/api/plants/')
        assert response.status_code == status.HTTP_200_OK

    def test_cascade_delete_integrity(self, api_client_with_user, test_plant):
        """Test data integrity when cascading deletes occur"""
        
        # Create multiple logs
        for i in range(3):
            api_client_with_user.post(
                '/api/logs/',
                {'plant': test_plant.id, 'log_type': 'water'}
            )
        
        # Verify logs exist
        logs_before = api_client_with_user.get('/api/logs/')
        assert len(logs_before.data) == 3
        
        # Delete plant
        response = api_client_with_user.delete(f'/api/plants/{test_plant.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all logs are deleted
        logs_after = api_client_with_user.get('/api/logs/')
        assert len(logs_after.data) == 0
        
        # Verify user can still create new plants/logs
        new_plant = api_client_with_user.post(
            '/api/plants/',
            {'name': 'New Plant', 'category': 'succulent', 'care_level': 'easy'}
        )
        assert new_plant.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.django_db
@pytest.mark.e2e
class TestDataValidationIntegration:
    """Test data validation across API and models"""

    def test_sunlight_hours_validation_e2e(self, api_client_with_user, test_plant):
        """Test sunlight hours validation through API"""
        
        # Valid sunlight hours
        valid_log = api_client_with_user.post(
            '/api/logs/',
            {'plant': test_plant.id, 'log_type': 'water', 'sunlight_hours': 12}
        )
        assert valid_log.status_code == status.HTTP_201_CREATED
        
        # Invalid sunlight hours (too high)
        invalid_log = api_client_with_user.post(
            '/api/logs/',
            {'plant': test_plant.id, 'log_type': 'water', 'sunlight_hours': 25}
        )
        assert invalid_log.status_code == status.HTTP_400_BAD_REQUEST

    def test_log_type_validation_e2e(self, api_client_with_user, test_plant):
        """Test log type validation through API"""
        
        valid_types = ['water', 'fertilize', 'prune']
        for log_type in valid_types:
            response = api_client_with_user.post(
                '/api/logs/',
                {'plant': test_plant.id, 'log_type': log_type}
            )
            assert response.status_code == status.HTTP_201_CREATED
        
        # Invalid type
        response = api_client_with_user.post(
            '/api/logs/',
            {'plant': test_plant.id, 'log_type': 'invalid_type'}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
