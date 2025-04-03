import pytest
from httpx import AsyncClient
from uuid import UUID

from tests.utils.utils import create_test_user, get_auth_headers

@pytest.mark.asyncio
async def test_create_campaign_template(client: AsyncClient):
    """Test creating a campaign template"""
    # Create a test user and get auth headers
    user = await create_test_user()
    headers = await get_auth_headers(client, user.email)
    
    # Test data
    template_data = {
        "name": "Test Campaign Template",
        "description": "A test template",
        "category": "informational",
        "content": {
            "title": "Test notification",
            "body": "This is a test notification",
            "variables": ["user_name", "product_name"]
        }
    }
    
    # Make the request
    response = await client.post(
        "/api/v1/campaign-templates/", 
        json=template_data,
        headers=headers
    )
    
    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["description"] == template_data["description"]
    assert data["category"] == template_data["category"]
    assert "id" in data
    
    # Use the created template ID for further tests
    template_id = data["id"]
    
    # Test retrieving the template
    response = await client.get(
        f"/api/v1/campaign-templates/{template_id}",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == template_id
