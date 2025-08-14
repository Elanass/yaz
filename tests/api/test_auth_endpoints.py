from fastapi.testclient import TestClient

from apps.surge.main import app


client = TestClient(app)


class TestAuthEndpoints:
    def test_user_registration(self):
        """Test user registration endpoint."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    def test_user_login(self):
        """Test user login endpoint."""
        # First register a user
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "logintest",
                "email": "login@example.com",
                "password": "testpassword123",
            },
        )

        # Then login
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "testpassword123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_token_refresh(self):
        """Test token refresh endpoint."""
        # Register and get tokens
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "refreshtest",
                "email": "refresh@example.com",
                "password": "testpassword123",
            },
        )
        refresh_token = register_response.json()["refresh_token"]

        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
