import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from models.user import User, UserStatus
from services.user import UserService

# Create test client
client = TestClient(app)

# Mock data
mock_user = User(
    id="123e4567-e89b-12d3-a456-426614174000",
    email="test@example.com",
    username="testuser",
    full_name="Test User",
    status=UserStatus.ACTIVE,
    is_active=True,
    is_superuser=False,
    notification_enabled=True,
    webpush_enabled=True,
    email_notification_enabled=True
)

# Mock UserService for testing
@pytest.fixture
def mock_user_service():
    with patch.object(UserService, "__init__", return_value=None):
        user_service = UserService()
        
        # Mock methods
        user_service.create_user = MagicMock(return_value=mock_user)
        user_service.get_user = MagicMock(return_value=mock_user)
        user_service.update_user = MagicMock(return_value=mock_user)
        user_service.delete_user = MagicMock(return_value=True)
        user_service.authenticate_user = MagicMock(return_value=mock_user)
        user_service.get_all_users = MagicMock(return_value=([mock_user], 1))
        user_service.create_access_token = MagicMock(return_value="mock_token")
        user_service.activate_user = MagicMock(return_value=mock_user)
        user_service.deactivate_user = MagicMock(return_value=mock_user)
        user_service.add_user_device = MagicMock(return_value=True)
        user_service.update_notification_settings = MagicMock(return_value=mock_user)
        user_service.get_user_stats = MagicMock(return_value={
            "total_notifications": 5,
            "open_rate": 0.8,
            "click_rate": 0.4,
            "last_interaction": "2023-06-15T10:00:00"
        })
        
        yield user_service

# Mock authentication for tests
@pytest.fixture
def mock_authentication():
    with patch("api.deps.get_current_active_user", return_value=mock_user):
        yield

# Mock permissions for tests
@pytest.fixture
def mock_permissions():
    with patch("core.permissions.dependencies.has_permission", return_value=lambda: None):
        yield

class TestUserEndpoints:
    """Tests for user API endpoints"""
    
    def test_create_user(self, mock_user_service, mock_permissions):
        """Test creating a user"""
        # Replace app's UserService with our mock
        app.dependency_overrides[UserService] = lambda: mock_user_service
        
        # Test data
        user_data = {
            "email": "new@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "password123",
            "notification_enabled": True,
            "webpush_enabled": True,
            "email_notification_enabled": True,
            "timezone": "UTC",
            "language": "en"
        }
        
        # Make request
        response = client.post("/api/v1/users/", json=user_data)
        
        # Assertions
        assert response.status_code == 201
        assert response.json()["email"] == mock_user.email
        assert "password" not in response.json()
        
        # Verify service was called
        mock_user_service.create_user.assert_called_once()
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_get_user(self, mock_user_service, mock_permissions):
        """Test getting a user by ID"""
        # Replace app's UserService with our mock
        app.dependency_overrides[UserService] = lambda: mock_user_service
        
        # Make request
        response = client.get(f"/api/v1/users/{mock_user.id}")
        
        # Assertions
        assert response.status_code == 200
        assert response.json()["id"] == mock_user.id
        assert response.json()["email"] == mock_user.email
        
        # Verify service was called
        mock_user_service.get_user.assert_called_once_with(mock_user.id)
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_user(self, mock_user_service, mock_permissions):
        """Test updating a user"""
        # Replace app's UserService with our mock
        app.dependency_overrides[UserService] = lambda: mock_user_service
        
        # Test data
        update_data = {
            "full_name": "Updated Name",
            "notification_enabled": False
        }
        
        # Make request
        response = client.put(f"/api/v1/users/{mock_user.id}", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        assert response.json()["email"] == mock_user.email
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_login(self, mock_user_service):
        """Test user login"""
        # Replace app's UserService with our mock
        app.dependency_overrides[UserService] = lambda: mock_user_service
        
        # Test data
        form_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        
        # Make request
        response = client.post("/api/v1/users/token", data=form_data)
        
        # Assertions
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        
        # Verify service was called
        mock_user_service.authenticate_user.assert_called_once_with(
            form_data["username"], form_data["password"]
        )
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_current_user(self, mock_user_service, mock_authentication):
        """Test getting current user"""
        # Replace app's UserService with our mock
        app.dependency_overrides[UserService] = lambda: mock_user_service
        
        # Make request with authentication mock
        response = client.get("/api/v1/users/me")
        
        # Assertions
        assert response.status_code == 200
        assert response.json()["id"] == mock_user.id
        assert response.json()["email"] == mock_user.email
        
        # Clean up
        app.dependency_overrides.clear()

class TestUserService:
    """Tests for UserService"""
    
    @pytest.mark.asyncio
    async def test_create_user(self):
        """Test creating a user"""
        # Mock repository
        with patch("repositories.user.UserRepository") as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_by_email.return_value = None
            mock_repo.get_by_username.return_value = None
            mock_repo.create_with_password.return_value = mock_user
            
            # Create service with mocked repo
            service = UserService()
            service.user_repo = mock_repo
            
            # Test data
            user_data = MagicMock()
            user_data.email = "test@example.com"
            user_data.username = "testuser"
            user_data.password = "password123"
            
            # Mock password hashing
            with patch.object(service, "_hash_password", return_value="hashed_password"):
                # Call method
                result = await service.create_user(user_data)
                
                # Assertions
                assert result == mock_user
                mock_repo.create_with_password.assert_called_once()
                mock_repo.get_by_email.assert_called_once_with(user_data.email)
                mock_repo.get_by_username.assert_called_once_with(user_data.username)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful authentication"""
        # Mock repository
        with patch("repositories.user.UserRepository") as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_by_email.return_value = mock_user
            mock_repo.get_password_hash.return_value = "hashed_password"
            mock_repo.update_last_login.return_value = True
            
            # Create service with mocked repo
            service = UserService()
            service.user_repo = mock_repo
            
            # Mock password verification
            with patch.object(service, "_verify_password", return_value=True):
                # Call method
                result = await service.authenticate_user("test@example.com", "password123")
                
                # Assertions
                assert result == mock_user
                mock_repo.get_by_email.assert_called_once_with("test@example.com")
                mock_repo.get_password_hash.assert_called_once_with(mock_user.id)
                mock_repo.update_last_login.assert_called_once_with(mock_user.id)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self):
        """Test failed authentication"""
        # Mock repository
        with patch("repositories.user.UserRepository") as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_by_email.return_value = mock_user
            mock_repo.get_password_hash.return_value = "hashed_password"
            
            # Create service with mocked repo
            service = UserService()
            service.user_repo = mock_repo
            
            # Mock password verification to fail
            with patch.object(service, "_verify_password", return_value=False):
                # Call method
                result = await service.authenticate_user("test@example.com", "wrong_password")
                
                # Assertions
                assert result is None
                mock_repo.update_last_login.assert_not_called()
