import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "db" in data

    @pytest.mark.asyncio
    async def test_health_returns_request_id(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert "x-request-id" in response.headers

    @pytest.mark.asyncio
    async def test_health_check_cache_unavailable(self, client: AsyncClient):
        """Cache is None in tests — health check should report cache unavailable."""
        response = await client.get("/api/v1/health")
        data = response.json()
        assert data["cache"] == "unavailable"

    @pytest.mark.asyncio
    async def test_health_custom_request_id(self, client: AsyncClient):
        """Should echo back the provided request ID."""
        response = await client.get(
            "/api/v1/health",
            headers={"X-Request-ID": "custom-123"},
        )
        assert response.headers["x-request-id"] == "custom-123"


class TestStudiesAPI:
    @pytest.mark.asyncio
    async def test_create_study(self, client: AsyncClient):
        payload = {
            "patient_id": "PAT-001",
            "modality": "CT",
            "description": "Chest CT scan",
        }
        response = await client.post("/api/v1/studies", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == "PAT-001"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_studies(self, client: AsyncClient):
        response = await client.get("/api/v1/studies")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_study_not_found(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/studies/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_and_get_study(self, client: AsyncClient):
        payload = {
            "patient_id": "PAT-002",
            "modality": "MRI",
            "description": "Brain MRI scan",
        }
        create_resp = await client.post("/api/v1/studies", json=payload)
        study_id = create_resp.json()["id"]

        get_resp = await client.get(f"/api/v1/studies/{study_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["patient_id"] == "PAT-002"

    @pytest.mark.asyncio
    async def test_create_and_delete_study(self, client: AsyncClient):
        payload = {
            "patient_id": "PAT-003",
            "modality": "X-RAY",
            "description": "Chest X-Ray",
        }
        create_resp = await client.post("/api/v1/studies", json=payload)
        study_id = create_resp.json()["id"]

        del_resp = await client.delete(f"/api/v1/studies/{study_id}")
        assert del_resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient):
        response = await client.delete(
            "/api/v1/studies/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_study_validation_error(self, client: AsyncClient):
        payload = {"patient_id": "", "modality": "CT", "description": ""}
        response = await client.post("/api/v1/studies", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_patch_study(self, client: AsyncClient):
        payload = {
            "patient_id": "PAT-004",
            "modality": "CT",
            "description": "Original description",
        }
        create_resp = await client.post("/api/v1/studies", json=payload)
        study_id = create_resp.json()["id"]

        patch_resp = await client.patch(
            f"/api/v1/studies/{study_id}",
            json={"description": "Updated description"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["description"] == "Updated description"
        assert patch_resp.json()["patient_id"] == "PAT-004"

    @pytest.mark.asyncio
    async def test_patch_not_found(self, client: AsyncClient):
        response = await client.patch(
            "/api/v1/studies/00000000-0000-0000-0000-000000000000",
            json={"description": "New"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_studies_with_filter(self, client: AsyncClient):
        await client.post(
            "/api/v1/studies",
            json={"patient_id": "FILTER-001", "modality": "CT", "description": "CT scan"},
        )
        await client.post(
            "/api/v1/studies",
            json={"patient_id": "FILTER-002", "modality": "MRI", "description": "MRI scan"},
        )

        response = await client.get("/api/v1/studies?modality=CT")
        data = response.json()
        assert response.status_code == 200
        for item in data["items"]:
            assert item["modality"] == "CT"

    @pytest.mark.asyncio
    async def test_patch_study_status_and_image_count(self, client: AsyncClient):
        payload = {
            "patient_id": "PAT-010",
            "modality": "MRI",
            "description": "Brain scan",
        }
        create_resp = await client.post("/api/v1/studies", json=payload)
        study_id = create_resp.json()["id"]

        patch_resp = await client.patch(
            f"/api/v1/studies/{study_id}",
            json={"status": "in_progress", "image_count": 15},
        )
        assert patch_resp.status_code == 200
        data = patch_resp.json()
        assert data["status"] == "in_progress"
        assert data["image_count"] == 15

    @pytest.mark.asyncio
    async def test_full_crud_lifecycle(self, client: AsyncClient):
        """Create -> Read -> Update -> Delete lifecycle."""
        # Create
        resp = await client.post(
            "/api/v1/studies",
            json={"patient_id": "LIFECYCLE-001", "modality": "PET", "description": "PET scan"},
        )
        assert resp.status_code == 201
        study_id = resp.json()["id"]

        # Read
        resp = await client.get(f"/api/v1/studies/{study_id}")
        assert resp.status_code == 200
        assert resp.json()["patient_id"] == "LIFECYCLE-001"

        # Update
        resp = await client.patch(
            f"/api/v1/studies/{study_id}",
            json={"description": "Updated PET scan", "status": "completed", "image_count": 100},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "Updated PET scan"
        assert resp.json()["status"] == "completed"

        # Delete
        resp = await client.delete(f"/api/v1/studies/{study_id}")
        assert resp.status_code == 204

        # Verify deleted
        resp = await client.get(f"/api/v1/studies/{study_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_studies_pagination(self, client: AsyncClient):
        for i in range(3):
            await client.post(
                "/api/v1/studies",
                json={
                    "patient_id": f"PAGE-{i}",
                    "modality": "PET",
                    "description": f"Study {i}",
                },
            )

        response = await client.get("/api/v1/studies?limit=2&status=pending")
        data = response.json()
        assert response.status_code == 200
        assert len(data["items"]) <= 2
