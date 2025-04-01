import pytest
from httpx import AsyncClient
from fastapi import status
from tests.utils.users import create_test_user, create_random_user
from tests.utils.utils import random_email, random_lower_string

async def test_create_user(
    client: AsyncClient,
    admin_token_headers: dict
) -> None:
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "name": random_lower_string(),
    }
    response = await client.post(
        "/api/v1/users/",
        headers=admin_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["email"] == data["email"]
    assert "password" not in content

# ...additional test cases...
