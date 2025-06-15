"""
FILENAME: test_api_campaigns.py
DESCRIPTION/PURPOSE: API tests for campaign endpoints
Author: JP + 2025-06-15

This module tests the campaign management API endpoints for regression testing.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestCampaignsAPI:
    """Test suite for campaigns API endpoints."""

    def test_create_campaign_success(self, client: TestClient, sample_campaign_request):
        """Test successful campaign creation."""
        response = client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "campaign_id" in data
        assert "summary" in data
        assert "business_analysis" in data
        assert "social_posts" in data
        assert "created_at" in data
        assert "status" in data
        
        # Verify business analysis structure
        business_analysis = data["business_analysis"]
        assert "company_name" in business_analysis
        assert "industry" in business_analysis
        assert "target_audience" in business_analysis
        assert "value_propositions" in business_analysis
        assert isinstance(business_analysis["value_propositions"], list)
        
        # Verify social posts structure
        social_posts = data["social_posts"]
        assert isinstance(social_posts, list)
        assert len(social_posts) == 9  # 3 of each type
        
        for post in social_posts:
            assert "id" in post
            assert "type" in post
            assert "content" in post
            assert "hashtags" in post
            assert "platform_optimized" in post
            assert "engagement_score" in post
            assert "selected" in post
            assert post["type"] in ["text_url", "text_image", "text_video"]

    def test_create_campaign_validation_error(self, client: TestClient):
        """Test campaign creation with invalid data."""
        invalid_request = {
            "business_description": "",  # Too short
            "objective": "Test",
            "target_audience": "Test audience",
            "campaign_type": "invalid_type",  # Invalid enum
            "creativity_level": 15  # Out of range
        }
        
        response = client.post("/api/v1/campaigns/create", json=invalid_request)
        assert response.status_code == 422  # Validation error

    def test_create_campaign_missing_fields(self, client: TestClient):
        """Test campaign creation with missing required fields."""
        incomplete_request = {
            "business_description": "Test description"
            # Missing required fields
        }
        
        response = client.post("/api/v1/campaigns/create", json=incomplete_request)
        assert response.status_code == 422

    def test_get_campaign_success(self, client: TestClient, sample_campaign_request):
        """Test retrieving a campaign by ID."""
        # First create a campaign
        create_response = client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Then retrieve it
        get_response = client.get(f"/api/v1/campaigns/{campaign_id}")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["campaign_id"] == campaign_id
        assert "summary" in data
        assert "business_analysis" in data
        assert "social_posts" in data

    def test_get_campaign_not_found(self, client: TestClient):
        """Test retrieving a non-existent campaign."""
        response = client.get("/api/v1/campaigns/nonexistent_id")
        assert response.status_code == 404

    def test_list_campaigns_empty(self, client: TestClient):
        """Test listing campaigns when none exist."""
        response = client.get("/api/v1/campaigns/")
        assert response.status_code == 200
        
        data = response.json()
        assert "campaigns" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        assert isinstance(data["campaigns"], list)

    def test_list_campaigns_with_data(self, client: TestClient, sample_campaign_request):
        """Test listing campaigns with existing data."""
        # Create a few campaigns
        for i in range(3):
            request_data = sample_campaign_request.copy()
            request_data["objective"] = f"Test objective {i}"
            response = client.post("/api/v1/campaigns/create", json=request_data)
            assert response.status_code == 200
        
        # List campaigns
        response = client.get("/api/v1/campaigns/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["campaigns"]) >= 3
        assert data["total"] >= 3

    def test_list_campaigns_pagination(self, client: TestClient, sample_campaign_request):
        """Test campaign listing with pagination."""
        # Create multiple campaigns
        for i in range(5):
            request_data = sample_campaign_request.copy()
            request_data["objective"] = f"Test objective {i}"
            response = client.post("/api/v1/campaigns/create", json=request_data)
            assert response.status_code == 200
        
        # Test pagination
        response = client.get("/api/v1/campaigns/?limit=2&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["campaigns"]) <= 2
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_delete_campaign_success(self, client: TestClient, sample_campaign_request):
        """Test successful campaign deletion."""
        # Create a campaign
        create_response = client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Delete it
        delete_response = client.delete(f"/api/v1/campaigns/{campaign_id}")
        assert delete_response.status_code == 200
        
        data = delete_response.json()
        assert "message" in data
        assert campaign_id in data["message"]
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/campaigns/{campaign_id}")
        assert get_response.status_code == 404

    def test_delete_campaign_not_found(self, client: TestClient):
        """Test deleting a non-existent campaign."""
        response = client.delete("/api/v1/campaigns/nonexistent_id")
        assert response.status_code == 404

    def test_duplicate_campaign_success(self, client: TestClient, sample_campaign_request):
        """Test successful campaign duplication."""
        # Create original campaign
        create_response = client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        assert create_response.status_code == 200
        original_id = create_response.json()["campaign_id"]
        
        # Duplicate it
        duplicate_response = client.post(f"/api/v1/campaigns/{original_id}/duplicate")
        assert duplicate_response.status_code == 200
        
        data = duplicate_response.json()
        assert data["campaign_id"] != original_id
        assert "summary" in data
        assert "business_analysis" in data
        assert "social_posts" in data

    def test_duplicate_campaign_not_found(self, client: TestClient):
        """Test duplicating a non-existent campaign."""
        response = client.post("/api/v1/campaigns/nonexistent_id/duplicate")
        assert response.status_code == 404

    def test_export_campaign_json(self, client: TestClient, sample_campaign_request):
        """Test campaign export in JSON format."""
        # Create a campaign
        create_response = client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Export it
        export_response = client.get(f"/api/v1/campaigns/{campaign_id}/export?format=json")
        assert export_response.status_code == 200
        assert export_response.headers["content-type"] == "application/json"

    def test_export_campaign_invalid_format(self, client: TestClient, sample_campaign_request):
        """Test campaign export with invalid format."""
        # Create a campaign
        create_response = client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Try to export with invalid format
        export_response = client.get(f"/api/v1/campaigns/{campaign_id}/export?format=invalid")
        assert export_response.status_code == 400

    def test_export_campaign_not_found(self, client: TestClient):
        """Test exporting a non-existent campaign."""
        response = client.get("/api/v1/campaigns/nonexistent_id/export")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestCampaignsAPIAsync:
    """Async test suite for campaigns API endpoints."""

    async def test_create_campaign_async(self, async_client: AsyncClient, sample_campaign_request):
        """Test async campaign creation."""
        response = await async_client.post("/api/v1/campaigns/create", json=sample_campaign_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "campaign_id" in data
        assert "social_posts" in data
        assert len(data["social_posts"]) == 9

    async def test_concurrent_campaign_creation(self, async_client: AsyncClient, sample_campaign_request):
        """Test concurrent campaign creation."""
        import asyncio
        
        # Create multiple campaigns concurrently
        tasks = []
        for i in range(3):
            request_data = sample_campaign_request.copy()
            request_data["objective"] = f"Concurrent test {i}"
            task = async_client.post("/api/v1/campaigns/create", json=request_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "campaign_id" in data
        
        # Verify unique campaign IDs
        campaign_ids = [response.json()["campaign_id"] for response in responses]
        assert len(set(campaign_ids)) == len(campaign_ids)  # All unique 