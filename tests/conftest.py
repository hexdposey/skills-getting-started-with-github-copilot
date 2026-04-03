"""
Pytest configuration and fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities state before each test to ensure test isolation."""
    # Store original state
    original_activities = {
        activity_name: {
            "description": activity.get("description", ""),
            "schedule": activity.get("schedule", ""),
            "max_participants": activity.get("max_participants", 0),
            "participants": activity.get("participants", []).copy()
        }
        for activity_name, activity in activities.items()
    }
    
    yield  # Run the test
    
    # Restore original state after test
    for activity_name in list(activities.keys()):
        if activity_name in original_activities:
            activities[activity_name]["participants"] = original_activities[activity_name]["participants"].copy()
