"""User model and authentication endpoint tests"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.user
class TestUserModel:
    """Unit tests for User model"""

    def test_user_creation(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@1234'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'

    def test_user_password_hashing(self):
        """Test that password is hashed"""
        user = User.objects.create_user(
            username='testuser',
            password='Test@1234'
        )
        assert user.password != 'Test@1234'
        assert user.check_password('Test@1234')

    def test_user_str_representation(self, test_user):
        """Test user string representation"""
        assert str(test_user) == 'testuser'


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationEndpoints:
    """Integration tests for authentication endpoints"""

    def test_register_new_user(self, api_client, valid_user_data):
        """Test user registration"""
        response = api_client.post('/api/auth/register/', valid_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == valid_user_data['username']

    def test_register_duplicate_username(self, api_client, test_user, valid_user_data):
        """Test registration fails with duplicate username"""
        valid_user_data['username'] = 'testuser'
        response = api_client.post('/api/auth/register/', valid_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_username(self, api_client):
        """Test registration fails with missing username"""
        data = {
            'email': 'test@example.com',
            'password': 'Test@1234'
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password(self, api_client):
        """Test registration fails with missing password"""
        data = {
            'username': 'newuser',
            'email': 'test@example.com'
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_valid_credentials(self, api_client, valid_login_data):
        """Test login with valid credentials"""
        response = api_client.post('/api/auth/login/', valid_login_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'testuser'

    def test_login_invalid_username(self, api_client):
        """Test login fails with invalid username"""
        data = {
            'username': 'nonexistent',
            'password': 'Test@1234'
        }
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_password(self, api_client, test_user):
        """Test login fails with invalid password"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_username(self, api_client):
        """Test login fails with missing username"""
        data = {'password': 'Test@1234'}
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_authenticated(self, api_client_with_user):
        """Test logout when authenticated"""
        response = api_client_with_user.post('/api/auth/logout/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_unauthenticated(self, api_client):
        """Test logout returns 401 when not authenticated"""
        response = api_client.post('/api/auth/logout/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_generation_on_login(self, api_client, valid_login_data):
        """Test that valid JWT token is generated on login"""
        response = api_client.post('/api/auth/login/', valid_login_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Try using the token
        token = response.data['token']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        user_response = api_client.get('/api/users/me/')
        assert user_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.user
class TestUserMeEndpoint:
    """Integration tests for /users/me/ endpoint"""

    def test_get_user_me_authenticated(self, api_client_with_user):
        """Test retrieving current user info"""
        response = api_client_with_user.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == api_client_with_user.user.username

    def test_get_user_me_unauthenticated(self, api_client):
        """Test retrieving user info returns 401 when not authenticated"""
        response = api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_me_email(self, api_client_with_user):
        """Test updating user email via /users/me/"""
        new_email = 'newemail@example.com'
        data = {'email': new_email}
        response = api_client_with_user.patch('/api/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == new_email
        
        api_client_with_user.user.refresh_from_db()
        assert api_client_with_user.user.email == new_email

    def test_update_user_me_password(self, api_client_with_user):
        """Test updating user password via /users/me/"""
        new_password = 'NewPassword@1234'
        data = {'password': new_password}
        response = api_client_with_user.patch('/api/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        
        api_client_with_user.user.refresh_from_db()
        assert api_client_with_user.user.check_password(new_password)

    def test_update_user_me_partial(self, api_client_with_user):
        """Test partial update via PATCH"""
        old_email = api_client_with_user.user.email
        data = {'password': 'NewPassword@1234'}
        response = api_client_with_user.patch('/api/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        
        # Email should remain unchanged
        api_client_with_user.user.refresh_from_db()
        assert api_client_with_user.user.email == old_email

    def test_delete_user_me(self, api_client_with_user):
        """Test deleting user account"""
        user_id = api_client_with_user.user.id
        response = api_client_with_user.delete('/api/users/me/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user_id).exists()

    def test_delete_user_me_cascades_data(self, api_client_with_user, test_plant):
        """Test that deleting user deletes their plants"""
        test_plant.owner = api_client_with_user.user
        test_plant.save()
        
        plant_id = test_plant.id
        response = api_client_with_user.delete('/api/users/me/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Plant should be deleted due to cascade
        from plants.models import Plant
        assert not Plant.objects.filter(id=plant_id).exists()
    def test_update_user_me_username(self, api_client_with_user):
        """Test updating username"""
        data = {'username': 'newusername'}
        response = api_client_with_user.patch('/api/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        api_client_with_user.user.refresh_from_db()
        assert api_client_with_user.user.username == 'newusername'

    def test_update_user_me_display_name(self, api_client_with_user):
        """Test updating display_name"""
        data = {'display_name': 'John Doe'}
        response = api_client_with_user.patch('/api/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        api_client_with_user.user.refresh_from_db()
        assert api_client_with_user.user.display_name == 'John Doe'

    def test_update_user_me_username_and_display_name(self, api_client_with_user):
        """Test updating both username and display_name together"""
        data = {
            'username': 'newusername',
            'display_name': 'Jane Smith'
        }
        response = api_client_with_user.patch('/api/users/me/', data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        api_client_with_user.user.refresh_from_db()
        assert api_client_with_user.user.username == 'newusername'
        assert api_client_with_user.user.display_name == 'Jane Smith'