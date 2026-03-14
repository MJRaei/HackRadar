"""Basic API tests for the projects endpoints."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_projects_empty(client):
    response = await client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_project_invalid_url(client):
    response = await client.post(
        "/api/v1/projects",
        json={"name": "Test", "github_url": "https://notgithub.com/user/repo"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_triggers_background_task(client):
    with patch(
        "hackradar.services.project_service.ProjectService.clone_and_index",
        new_callable=AsyncMock,
    ):
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "github_url": "https://github.com/test/repo",
                "summary": "A test project",
            },
        )
    assert response.status_code == 202
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "pending"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    response = await client.get("/api/v1/projects/nonexistent-id")
    assert response.status_code == 404
