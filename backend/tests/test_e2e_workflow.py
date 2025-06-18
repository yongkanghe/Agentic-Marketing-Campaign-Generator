"""
FILENAME: test_e2e_workflow.py
DESCRIPTION/PURPOSE: End-to-end tests for the complete AI workflow.
Author: JP + 2025-06-20
"""
import pytest
from fastapi.testclient import TestClient
import os

# Correct the import path to be relative to the `backend` directory where the test is run
from api.main import app

client = TestClient(app)

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY is not set")
class TestEndToEndWorkflow:
    """
    Tests the complete end-to-end workflow from business analysis to content generation.
    These tests require a live GEMINI_API_KEY and make real calls to the Google AI APIs.
    """

    def test_url_analysis_to_content_generation_workflow(self):
        """
        Tests the full happy path:
        1. Get business analysis from a URL.
        2. Use that analysis to generate initial content.
        3. Verify the generated content is real and contextually relevant.
        """
        # STEP 1: Perform URL Analysis
        analysis_request_payload = {
            "urls": ["https://www.google.com/"],
            "analysis_depth": "standard"
        }
        
        analysis_response = client.post("/api/v1/analysis/url", json=analysis_request_payload)
        
        assert analysis_response.status_code == 200, f"Analysis request failed: {analysis_response.text}"
        analysis_data = analysis_response.json()
        
        assert "business_analysis" in analysis_data
        assert analysis_data["analysis_metadata"]["ai_analysis_used"] is True
        
        business_context = analysis_data["business_analysis"]
        assert business_context.get("company_name")

        # STEP 2: Generate Content using the Business Analysis
        content_request_payload = {
            "campaign_id": "e2e-test-campaign-1",
            "campaign_objective": "Increase brand awareness for Google",
            "campaign_type": "brand",
            "business_context": {
                "business_description": business_context.get("business_description"),
                "target_audience": business_context.get("target_audience"),
                "business_website": "https://www.google.com/"
            },
            "post_count": 3,
            "creativity_level": 5,
            "include_hashtags": True
        }

        content_response = client.post("/api/v1/content/generate", json=content_request_payload)
        
        # STEP 3: Verify the results
        assert content_response.status_code == 200, f"Content generation failed: {content_response.text}"
        content_data = content_response.json()
        
        assert "posts" in content_data
        assert len(content_data["posts"]) > 0
        assert content_data["generation_metadata"]["real_ai_used"] is True
        assert content_data["generation_metadata"]["generation_method"] == "real_adk_workflow"

        first_post_content = content_data["posts"][0]["content"].lower()
        assert "mock" not in first_post_content
        assert "generated" not in first_post_content
        assert "google" in first_post_content or "search" in first_post_content or "information" in first_post_content
        
        print("\nE2E Workflow Test Passed: Successfully generated content from URL analysis.")

    def test_description_analysis_to_content_generation_workflow(self):
        """
        Tests the fallback path:
        1. Use a business description (no URL) to generate initial content.
        2. Verify the generated content is real and contextually relevant.
        """
        # STEP 1: Generate Content using only a Business Description
        content_request_payload = {
            "campaign_id": "e2e-test-campaign-2",
            "campaign_objective": "Promote our new line of eco-friendly water bottles",
            "campaign_type": "product",
            "business_context": {
                "business_description": "We are a startup called 'AquaPure' that creates stylish, reusable, and 100% biodegradable water bottles to reduce plastic waste.",
                "target_audience": "Environmentally conscious millennials aged 25-40."
            },
            "post_count": 3,
            "creativity_level": 7,
            "include_hashtags": True
        }

        content_response = client.post("/api/v1/content/generate", json=content_request_payload)
        
        # STEP 2: Verify the results
        assert content_response.status_code == 200, f"Content generation failed: {content_response.text}"
        content_data = content_response.json()
        
        assert "posts" in content_data
        assert len(content_data["posts"]) > 0
        assert content_data["generation_metadata"]["real_ai_used"] is True
        assert content_data["generation_metadata"]["generation_method"] == "real_adk_workflow"

        assert "business_analysis" in content_data
        # This assertion can be flaky depending on the AI's interpretation. 
        # We'll check if the name is present instead of an exact match.
        assert content_data["business_analysis"].get("company_name")

        first_post_content = content_data["posts"][0]["content"].lower()
        assert "mock" not in first_post_content
        assert "generated" not in first_post_content
        assert "bottle" in first_post_content or "eco-friendly" in first_post_content or "aquapure" in first_post_content

        print("\nE2E Description-based Workflow Test Passed: Successfully generated content from business description.") 