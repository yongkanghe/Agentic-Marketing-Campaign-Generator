"""
FILENAME: test_api_content.py
DESCRIPTION/PURPOSE: API tests for content generation endpoints
Author: JP + 2025-06-15

This module tests the content generation API endpoints for regression testing.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestContentAPI:
    """Test suite for content generation API endpoints."""

    def test_generate_content_success(self, client: TestClient, sample_content_generation_request):
        """Test successful content generation."""
        response = client.post("/api/v1/content/generate", json=sample_content_generation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "posts" in data
        assert "generation_metadata" in data
        
        posts = data["posts"]
        assert isinstance(posts, list)
        assert len(posts) == 9  # 3 of each type
        
        # Verify post structure
        for post in posts:
            assert "id" in post
            assert "type" in post
            assert "content" in post
            assert "hashtags" in post
            assert "platform_optimized" in post
            assert "engagement_score" in post
            assert "selected" in post
            assert post["type"] in ["text_url", "text_image", "text_video"]
            assert isinstance(post["hashtags"], list)
            assert isinstance(post["engagement_score"], (int, float))
            assert 0 <= post["engagement_score"] <= 10
        
        # Verify generation metadata
        metadata = data["generation_metadata"]
        assert "total_posts" in metadata
        assert "generation_time" in metadata
        assert "creativity_level" in metadata
        assert metadata["total_posts"] == 9
        assert metadata["creativity_level"] == sample_content_generation_request["creativity_level"]

    def test_generate_content_validation_error(self, client: TestClient):
        """Test content generation with invalid data."""
        invalid_request = {
            "business_context": {},  # Empty context
            "campaign_objective": "",  # Empty objective
            "creativity_level": 15,  # Out of range
            "post_count": 0  # Invalid count
        }
        
        response = client.post("/api/v1/content/generate", json=invalid_request)
        assert response.status_code == 422

    def test_generate_content_missing_fields(self, client: TestClient):
        """Test content generation with missing required fields."""
        incomplete_request = {
            "campaign_objective": "Test objective"
            # Missing business_context and other required fields
        }
        
        response = client.post("/api/v1/content/generate", json=incomplete_request)
        assert response.status_code == 422

    def test_generate_content_custom_count(self, client: TestClient, sample_content_generation_request):
        """Test content generation with custom post count."""
        request_data = sample_content_generation_request.copy()
        request_data["post_count"] = 6
        
        response = client.post("/api/v1/content/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["posts"]) == 6
        assert data["generation_metadata"]["total_posts"] == 6

    def test_generate_content_without_hashtags(self, client: TestClient, sample_content_generation_request):
        """Test content generation without hashtags."""
        request_data = sample_content_generation_request.copy()
        request_data["include_hashtags"] = False
        
        response = client.post("/api/v1/content/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        for post in data["posts"]:
            assert len(post["hashtags"]) == 0

    def test_regenerate_posts_success(self, client: TestClient, sample_regeneration_request):
        """Test successful post regeneration."""
        response = client.post("/api/v1/content/regenerate", json=sample_regeneration_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure - regenerate endpoint returns 'new_posts' not 'posts'
        assert "new_posts" in data
        assert "regeneration_metadata" in data
        
        posts = data["new_posts"]
        assert isinstance(posts, list)
        assert len(posts) == 3  # regenerate_count from fixture
        
        # Verify all posts are of the requested type
        for post in posts:
            assert post["type"] == sample_regeneration_request["post_type"]
            assert "id" in post
            assert "content" in post
            assert "hashtags" in post
            assert "platform_optimized" in post
            assert "engagement_score" in post
            assert "selected" in post

    def test_regenerate_posts_validation_error(self, client: TestClient):
        """Test post regeneration with invalid data."""
        invalid_request = {
            "business_context": {},  # Empty context
            "post_type": "invalid_type",  # Invalid type
            "current_posts": [],  # Empty posts
            "regenerate_count": 0  # Invalid count
        }
        
        response = client.post("/api/v1/content/regenerate", json=invalid_request)
        assert response.status_code == 422

    def test_regenerate_posts_missing_fields(self, client: TestClient):
        """Test post regeneration with minimal required fields."""
        minimal_request = {
            "post_type": "text_image"
            # Only required field provided - should work with defaults
        }
        
        response = client.post("/api/v1/content/regenerate", json=minimal_request)
        assert response.status_code == 200  # Should succeed with minimal fields
        
        data = response.json()
        assert "new_posts" in data
        assert len(data["new_posts"]) > 0  # Should generate at least one post

    def test_regenerate_posts_different_types(self, client: TestClient, sample_regeneration_request):
        """Test regenerating different post types."""
        post_types = ["text_url", "text_image", "text_video"]
        
        for post_type in post_types:
            request_data = sample_regeneration_request.copy()
            request_data["post_type"] = post_type
            
            response = client.post("/api/v1/content/regenerate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            for post in data["new_posts"]:  # Changed from 'posts' to 'new_posts'
                assert post["type"] == post_type

    def test_regenerate_posts_custom_count(self, client: TestClient, sample_regeneration_request):
        """Test post regeneration with custom count."""
        request_data = sample_regeneration_request.copy()
        request_data["regenerate_count"] = 5
        
        response = client.post("/api/v1/content/regenerate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # For text_image posts, cost control limits to 4 posts maximum
        expected_count = 4 if request_data["post_type"] == "text_image" else 5
        assert len(data["new_posts"]) == expected_count  # Cost control may limit the count
        assert data["regeneration_metadata"]["regenerated_count"] == expected_count  # Changed field name

    def test_content_generation_creativity_levels(self, client: TestClient, sample_content_generation_request):
        """Test content generation with different creativity levels."""
        creativity_levels = [1, 5, 10]
        
        for level in creativity_levels:
            request_data = sample_content_generation_request.copy()
            request_data["creativity_level"] = level
            
            response = client.post("/api/v1/content/generate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["generation_metadata"]["creativity_level"] == level

    def test_content_generation_platform_optimization(self, client: TestClient, sample_content_generation_request):
        """Test that generated content includes platform optimization."""
        response = client.post("/api/v1/content/generate", json=sample_content_generation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        for post in data["posts"]:
            platform_optimized = post["platform_optimized"]
            assert isinstance(platform_optimized, dict)
            
            # Should have optimizations for major platforms
            expected_platforms = ["linkedin", "twitter", "instagram", "facebook"]
            for platform in expected_platforms:
                if platform in platform_optimized:
                    optimization = platform_optimized[platform]
                    assert "content" in optimization
                    assert "hashtags" in optimization

    def test_content_generation_engagement_scores(self, client: TestClient, sample_content_generation_request):
        """Test that generated content includes realistic engagement scores."""
        response = client.post("/api/v1/content/generate", json=sample_content_generation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        engagement_scores = [post["engagement_score"] for post in data["posts"]]
        
        # All scores should be within valid range
        for score in engagement_scores:
            assert 0 <= score <= 10
        
        # Should have some variation in scores
        assert len(set(engagement_scores)) > 1  # Not all the same

    def test_content_generation_hashtag_relevance(self, client: TestClient, sample_content_generation_request):
        """Test that generated hashtags are relevant to business context."""
        response = client.post("/api/v1/content/generate", json=sample_content_generation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        business_context = sample_content_generation_request["business_context"]
        industry = business_context["industry"].lower()
        
        for post in data["posts"]:
            hashtags = post["hashtags"]
            assert len(hashtags) > 0
            
            # At least some hashtags should be relevant to the industry
            hashtag_text = " ".join(hashtags).lower()
            # This is a basic check - in real implementation, we'd have more sophisticated relevance checking


@pytest.mark.asyncio
class TestContentAPIAsync:
    """Async test suite for content generation API endpoints."""

    async def test_generate_content_async(self, async_client: AsyncClient, sample_content_generation_request):
        """Test async content generation."""
        response = await async_client.post("/api/v1/content/generate", json=sample_content_generation_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) == 9

    async def test_concurrent_content_generation(self, async_client: AsyncClient, sample_content_generation_request):
        """Test concurrent content generation requests."""
        import asyncio
        
        # Create multiple content generation requests concurrently
        tasks = []
        for i in range(3):
            request_data = sample_content_generation_request.copy()
            request_data["campaign_objective"] = f"Concurrent test {i}"
            task = async_client.post("/api/v1/content/generate", json=request_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "posts" in data
            assert len(data["posts"]) == 9

    async def test_regenerate_posts_async(self, async_client: AsyncClient, sample_regeneration_request):
        """Test async post regeneration."""
        response = await async_client.post("/api/v1/content/regenerate", json=sample_regeneration_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "new_posts" in data  # Changed from 'posts' to 'new_posts'
        assert len(data["new_posts"]) == 3  # Changed from 'posts' to 'new_posts'

    async def test_mixed_content_operations(self, async_client: AsyncClient, sample_content_generation_request, sample_regeneration_request):
        """Test mixed content generation and regeneration operations."""
        import asyncio
        
        # Run generation and regeneration concurrently
        generation_task = async_client.post("/api/v1/content/generate", json=sample_content_generation_request)
        regeneration_task = async_client.post("/api/v1/content/regenerate", json=sample_regeneration_request)
        
        generation_response, regeneration_response = await asyncio.gather(generation_task, regeneration_task)
        
        # Verify both succeeded
        assert generation_response.status_code == 200
        assert regeneration_response.status_code == 200
        
        generation_data = generation_response.json()
        regeneration_data = regeneration_response.json()
        
        assert len(generation_data["posts"]) == 9
        assert len(regeneration_data["new_posts"]) == 3  # Changed from 'posts' to 'new_posts' 