"""
Authentication views for login and registration endpoints.
These handle token generation and user creation.
"""
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from users.serializers import UserSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint - accepts username/password, returns access token.
    
    Request body:
        {
            "username": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "id": 1,
                "username": "user@example.com",
                "email": "user@example.com"
            }
        }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=400
        )
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=401)
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Registration endpoint - creates new user and returns token.
    NO authentication required.
    
    Request body:
        {
            "username": "newuser",
            "email": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "id": 1,
                "username": "newuser",
                "email": "user@example.com"
            }
        }
    """
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=201)
    
    # Extract first error message for cleaner display
    error_dict = serializer.errors
    first_error = None
    for field, errors in error_dict.items():
        if isinstance(errors, list) and errors:
            first_error = errors[0]
            break
    
    return Response({"error": first_error or "Registration failed"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint (client-side token discard). Returns 204 No Content.

    Note: JWT tokens are stateless. To fully revoke tokens implement
    token blacklisting. This endpoint exists so the frontend has a
    server-side route to call during logout; it simply returns 204.
    """
    return Response(status=204)
