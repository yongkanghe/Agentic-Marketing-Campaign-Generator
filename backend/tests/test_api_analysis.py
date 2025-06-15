"""
FILENAME: test_api_analysis.py
DESCRIPTION/PURPOSE: API tests for analysis endpoints
Author: JP + 2025-06-15

This module tests the URL and file analysis API endpoints for regression testing.
"""

import pytest
import io
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestAnalysisAPI:
    """Test suite for analysis API endpoints."""

    def test_analyze_url_success(self, client: TestClient, sample_url_analysis_request):
        """Test successful URL analysis."""
        response = client.post("/api/v1/analysis/url", json=sample_url_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "analysis_results" in data
        assert "business_context" in data
        assert "analysis_metadata" in data
        
        # Verify analysis results structure
        analysis_results = data["analysis_results"]
        assert isinstance(analysis_results, list)
        assert len(analysis_results) == len(sample_url_analysis_request["urls"])
        
        for result in analysis_results:
            assert "url" in result
            assert "content_summary" in result
            assert "key_insights" in result
            assert "business_relevance" in result
            assert "analysis_status" in result
            assert result["analysis_status"] in ["success", "failed", "partial"]
        
        # Verify business context structure
        business_context = data["business_context"]
        assert "company_name" in business_context
        assert "industry" in business_context
        assert "target_audience" in business_context
        assert "value_propositions" in business_context
        assert isinstance(business_context["value_propositions"], list)

    def test_analyze_url_validation_error(self, client: TestClient):
        """Test URL analysis with invalid data."""
        invalid_request = {
            "urls": [],  # Empty URLs
            "analysis_depth": "invalid_depth"  # Invalid depth
        }
        
        response = client.post("/api/v1/analysis/url", json=invalid_request)
        assert response.status_code == 422

    def test_analyze_url_missing_fields(self, client: TestClient):
        """Test URL analysis with missing required fields."""
        incomplete_request = {
            "analysis_depth": "standard"
            # Missing urls field
        }
        
        response = client.post("/api/v1/analysis/url", json=incomplete_request)
        assert response.status_code == 422

    def test_analyze_url_invalid_urls(self, client: TestClient):
        """Test URL analysis with invalid URLs."""
        invalid_request = {
            "urls": ["not-a-url", "http://", "ftp://invalid"],
            "analysis_depth": "standard"
        }
        
        response = client.post("/api/v1/analysis/url", json=invalid_request)
        assert response.status_code == 200  # Should handle gracefully
        
        data = response.json()
        analysis_results = data["analysis_results"]
        
        # Should have results for each URL, even if failed
        assert len(analysis_results) == 3
        for result in analysis_results:
            # Invalid URLs should have failed status
            assert result["analysis_status"] in ["failed", "partial"]

    def test_analyze_url_different_depths(self, client: TestClient):
        """Test URL analysis with different analysis depths."""
        depths = ["basic", "standard", "comprehensive"]
        
        for depth in depths:
            request_data = {
                "urls": ["https://example.com"],
                "analysis_depth": depth
            }
            
            response = client.post("/api/v1/analysis/url", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["analysis_metadata"]["analysis_depth"] == depth

    def test_analyze_url_multiple_urls(self, client: TestClient):
        """Test URL analysis with multiple URLs."""
        request_data = {
            "urls": [
                "https://example.com",
                "https://example.com/about",
                "https://example.com/products",
                "https://example.com/contact"
            ],
            "analysis_depth": "standard"
        }
        
        response = client.post("/api/v1/analysis/url", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        analysis_results = data["analysis_results"]
        assert len(analysis_results) == 4
        
        # Each URL should have its own analysis
        analyzed_urls = [result["url"] for result in analysis_results]
        assert set(analyzed_urls) == set(request_data["urls"])

    def test_analyze_files_success(self, client: TestClient):
        """Test successful file analysis."""
        # Create mock file data
        test_files = [
            ("files", ("test.txt", io.BytesIO(b"Test document content"), "text/plain")),
            ("files", ("test.pdf", io.BytesIO(b"Mock PDF content"), "application/pdf")),
        ]
        
        form_data = {
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/api/v1/analysis/files", files=test_files, data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "analysis_results" in data
        assert "extracted_insights" in data
        assert "analysis_metadata" in data
        
        # Verify analysis results
        analysis_results = data["analysis_results"]
        assert isinstance(analysis_results, list)
        assert len(analysis_results) == 2  # Two files uploaded
        
        for result in analysis_results:
            assert "filename" in result
            assert "file_type" in result
            assert "content_summary" in result
            assert "key_insights" in result
            assert "analysis_status" in result
            assert result["analysis_status"] in ["success", "failed", "partial"]

    def test_analyze_files_no_files(self, client: TestClient):
        """Test file analysis with no files uploaded."""
        form_data = {
            "analysis_type": "standard"
        }
        
        response = client.post("/api/v1/analysis/files", data=form_data)
        assert response.status_code == 422  # Should require files

    def test_analyze_files_invalid_type(self, client: TestClient):
        """Test file analysis with invalid analysis type."""
        test_files = [
            ("files", ("test.txt", io.BytesIO(b"Test content"), "text/plain")),
        ]
        
        form_data = {
            "analysis_type": "invalid_type"
        }
        
        response = client.post("/api/v1/analysis/files", files=test_files, data=form_data)
        assert response.status_code == 422

    def test_analyze_files_different_types(self, client: TestClient):
        """Test file analysis with different file types."""
        file_types = [
            ("test.txt", b"Text content", "text/plain"),
            ("test.pdf", b"PDF content", "application/pdf"),
            ("test.jpg", b"Image content", "image/jpeg"),
            ("test.docx", b"Word content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ]
        
        for filename, content, mime_type in file_types:
            test_files = [
                ("files", (filename, io.BytesIO(content), mime_type)),
            ]
            
            form_data = {
                "analysis_type": "standard"
            }
            
            response = client.post("/api/v1/analysis/files", files=test_files, data=form_data)
            assert response.status_code == 200
            
            data = response.json()
            analysis_results = data["analysis_results"]
            assert len(analysis_results) == 1
            assert analysis_results[0]["filename"] == filename
            assert analysis_results[0]["file_type"] == mime_type

    def test_analyze_files_large_batch(self, client: TestClient):
        """Test file analysis with multiple files."""
        # Create multiple test files
        test_files = []
        for i in range(5):
            filename = f"test_{i}.txt"
            content = f"Test document content {i}".encode()
            test_files.append(("files", (filename, io.BytesIO(content), "text/plain")))
        
        form_data = {
            "analysis_type": "standard"
        }
        
        response = client.post("/api/v1/analysis/files", files=test_files, data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        analysis_results = data["analysis_results"]
        assert len(analysis_results) == 5
        
        # Verify each file was processed
        filenames = [result["filename"] for result in analysis_results]
        expected_filenames = [f"test_{i}.txt" for i in range(5)]
        assert set(filenames) == set(expected_filenames)

    def test_analyze_files_analysis_types(self, client: TestClient):
        """Test file analysis with different analysis types."""
        analysis_types = ["basic", "standard", "comprehensive"]
        
        for analysis_type in analysis_types:
            test_files = [
                ("files", ("test.txt", io.BytesIO(b"Test content"), "text/plain")),
            ]
            
            form_data = {
                "analysis_type": analysis_type
            }
            
            response = client.post("/api/v1/analysis/files", files=test_files, data=form_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["analysis_metadata"]["analysis_type"] == analysis_type

    def test_analyze_files_extracted_insights(self, client: TestClient):
        """Test that file analysis extracts meaningful insights."""
        test_files = [
            ("files", ("business_plan.txt", io.BytesIO(b"Our company focuses on AI solutions for small businesses"), "text/plain")),
        ]
        
        form_data = {
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/api/v1/analysis/files", files=test_files, data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        extracted_insights = data["extracted_insights"]
        
        # Should extract business-relevant insights
        assert "business_focus" in extracted_insights
        assert "target_market" in extracted_insights
        assert "key_themes" in extracted_insights
        assert isinstance(extracted_insights["key_themes"], list)


@pytest.mark.asyncio
class TestAnalysisAPIAsync:
    """Async test suite for analysis API endpoints."""

    async def test_analyze_url_async(self, async_client: AsyncClient, sample_url_analysis_request):
        """Test async URL analysis."""
        response = await async_client.post("/api/v1/analysis/url", json=sample_url_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_results" in data
        assert "business_context" in data

    async def test_concurrent_url_analysis(self, async_client: AsyncClient):
        """Test concurrent URL analysis requests."""
        import asyncio
        
        # Create multiple URL analysis requests concurrently
        tasks = []
        for i in range(3):
            request_data = {
                "urls": [f"https://example{i}.com"],
                "analysis_depth": "standard"
            }
            task = async_client.post("/api/v1/analysis/url", json=request_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "analysis_results" in data

    async def test_analyze_files_async(self, async_client: AsyncClient):
        """Test async file analysis."""
        test_files = [
            ("files", ("test.txt", io.BytesIO(b"Test content"), "text/plain")),
        ]
        
        form_data = {
            "analysis_type": "standard"
        }
        
        response = await async_client.post("/api/v1/analysis/files", files=test_files, data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_results" in data

    async def test_mixed_analysis_operations(self, async_client: AsyncClient, sample_url_analysis_request):
        """Test mixed URL and file analysis operations."""
        import asyncio
        
        # Prepare file analysis
        test_files = [
            ("files", ("test.txt", io.BytesIO(b"Test content"), "text/plain")),
        ]
        form_data = {
            "analysis_type": "standard"
        }
        
        # Run URL and file analysis concurrently
        url_task = async_client.post("/api/v1/analysis/url", json=sample_url_analysis_request)
        file_task = async_client.post("/api/v1/analysis/files", files=test_files, data=form_data)
        
        url_response, file_response = await asyncio.gather(url_task, file_task)
        
        # Verify both succeeded
        assert url_response.status_code == 200
        assert file_response.status_code == 200
        
        url_data = url_response.json()
        file_data = file_response.json()
        
        assert "analysis_results" in url_data
        assert "analysis_results" in file_data 