"""Tests for criteria set CRUD endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_criteria_set(client):
    response = await client.post(
        "/api/v1/criteria",
        json={
            "name": "General Hackathon",
            "description": "Standard judging criteria",
            "criteria": [
                {"name": "Innovation", "description": "How novel is the idea?", "weight": 0.3},
                {"name": "Technical", "description": "Code quality", "weight": 0.4},
                {"name": "Impact", "description": "Real-world impact", "weight": 0.3},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "General Hackathon"
    assert len(data["criteria"]) == 3
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_criteria_empty_list(client):
    response = await client.post(
        "/api/v1/criteria",
        json={"name": "Empty", "criteria": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_criteria_sets(client):
    # Create one first
    await client.post(
        "/api/v1/criteria",
        json={
            "name": "Test Set",
            "criteria": [{"name": "Quality", "description": "Code quality", "weight": 1.0}],
        },
    )
    response = await client.get("/api/v1/criteria")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_criteria_set_not_found(client):
    response = await client.get("/api/v1/criteria/does-not-exist")
    assert response.status_code == 404
