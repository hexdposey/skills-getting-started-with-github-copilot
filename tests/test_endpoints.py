"""
Tests for the Mergington High School Management System API using AAA pattern.

Tests cover:
- GET / (redirect to static index.html)
- GET /activities (list all activities)
- POST /activities/{activity_name}/signup (sign up for an activity)
- POST /activities/{activity_name}/unregister (unregister from an activity)

AAA Pattern (Arrange-Act-Assert):
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestRootRedirect:
    """Tests for the root endpoint redirect."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Arrange
        # No setup needed - just testing the route behavior
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [307, 308]
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 OK"""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all 9 activities"""
        # Arrange
        expected_count = 9
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data) == expected_count
    
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            assert isinstance(activity_name, str)
            assert set(activity.keys()) == required_fields
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)
    
    def test_get_activities_contains_specific_activities(self, client):
        """Test that response contains expected activity names"""
        # Arrange
        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Class",
            "Drama Club",
            "Debate Club",
            "Science Club",
        }
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert set(data.keys()) == expected_activities
    
    def test_get_activities_participants_is_list_of_strings(self, client):
        """Test that participants field is a list of strings"""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            assert isinstance(activity["participants"], list)
            for participant in activity["participants"]:
                assert isinstance(participant, str)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds the student to participants"""
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity]["participants"])
        participants_list = response_after.json()[activity]["participants"]
        
        # Assert
        assert final_count == initial_count + 1
        assert email in participants_list
    
    def test_signup_invalid_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404"""
        # Arrange
        invalid_activity = "Non Existent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up with an already-registered email returns 400"""
        # Arrange
        activity = "Chess Club"
        # michael@mergington.edu is already in Chess Club (from fixtures)
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert data["detail"] == "Student already signed up"
    
    def test_signup_missing_email_param_returns_422(self, client):
        """Test that signup without email parameter returns 422"""
        # Arrange
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup")
        
        # Assert
        # FastAPI returns 422 for missing required parameters
        assert response.status_code == 422
    
    def test_signup_multiple_different_emails(self, client):
        """Test that multiple different emails can sign up for same activity"""
        # Arrange
        activity = "Art Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email2}
        )
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in participants
        assert email2 in participants
    
    def test_signup_to_different_activities(self, client):
        """Test that same email can sign up for multiple different activities"""
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Drama Club"
        email = "versatile@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        participants1 = activities_response.json()[activity1]["participants"]
        participants2 = activities_response.json()[activity2]["participants"]
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in participants1
        assert email in participants2


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered from fixtures
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the student from participants"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity]["participants"])
        initial_has_email = email in response_before.json()[activity]["participants"]
        
        # Act
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity]["participants"])
        participants_list = response_after.json()[activity]["participants"]
        
        # Assert
        assert initial_has_email is True
        assert final_count == initial_count - 1
        assert email not in participants_list
    
    def test_unregister_invalid_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        # Arrange
        invalid_activity = "Non Existent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered_returns_400(self, client):
        """Test that unregistering a non-registered student returns 400"""
        # Arrange
        activity = "Chess Club"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": unregistered_email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert data["detail"] == "Student not registered for this activity"
    
    def test_unregister_missing_email_param_returns_422(self, client):
        """Test that unregister without email parameter returns 422"""
        # Arrange
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister")
        
        # Assert
        # FastAPI returns 422 for missing required parameters
        assert response.status_code == 422
    
    def test_signup_then_unregister_flow(self, client):
        """Test the full signup-then-unregister flow"""
        # Arrange
        activity = "Science Club"
        email = "transitional@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        check_after_signup = client.get("/activities")
        participants_after_signup = check_after_signup.json()[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        check_after_unregister = client.get("/activities")
        participants_after_unregister = check_after_unregister.json()[activity]["participants"]
        
        # Assert
        assert signup_response.status_code == 200
        assert email in participants_after_signup
        assert unregister_response.status_code == 200
        assert email not in participants_after_unregister
    
    def test_unregister_then_signup_again(self, client):
        """Test that unregistering allows re-signup"""
        # Arrange
        activity = "Debate Club"
        email = "fickle@mergington.edu"
        
        # Act - Initial signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})
        
        # Act - Sign up again
        second_signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        check = client.get("/activities")
        final_participants = check.json()[activity]["participants"]
        
        # Assert
        assert second_signup_response.status_code == 200
        assert email in final_participants


class TestIntegration:
    """Integration tests covering multiple endpoints and workflows."""
    
    def test_full_workflow_signup_and_unregister(self, client):
        """Test complete workflow: list -> signup -> list -> unregister -> list"""
        # Arrange
        activity = "Tennis Club"
        email = "integrated@mergington.edu"
        
        # Act - Get initial activities
        response_1_get = client.get("/activities")
        initial_participants = response_1_get.json()[activity]["participants"].copy()
        
        # Act - Sign up
        response_2_signup = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        response_3_get = client.get("/activities")
        participants_after_signup = response_3_get.json()[activity]["participants"]
        
        # Act - Unregister
        response_4_unregister = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        response_5_get = client.get("/activities")
        participants_after_unregister = response_5_get.json()[activity]["participants"]
        
        # Assert
        assert response_1_get.status_code == 200
        assert email not in initial_participants
        assert response_2_signup.status_code == 200
        assert email in participants_after_signup
        assert response_4_unregister.status_code == 200
        assert email not in participants_after_unregister
    
    def test_multiple_concurrent_signups(self, client):
        """Test multiple students signing up for the same activity"""
        # Arrange
        activity = "Programming Class"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act - Sign up all students
        signup_responses = []
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            signup_responses.append(response)
        
        # Get final state
        final_response = client.get("/activities")
        participants = final_response.json()[activity]["participants"]
        
        # Assert
        for response in signup_responses:
            assert response.status_code == 200
        for email in emails:
            assert email in participants
    
    def test_isolation_between_activities(self, client):
        """Test that signup to one activity doesn't affect others"""
        # Arrange
        activity1 = "Art Class"
        activity2 = "Gym Class"
        email = "isolated@mergington.edu"
        
        # Act
        signup_response = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        final_response = client.get("/activities")
        participants_activity1 = final_response.json()[activity1]["participants"]
        participants_activity2 = final_response.json()[activity2]["participants"]
        
        # Assert
        assert signup_response.status_code == 200
        assert email in participants_activity1
        assert email not in participants_activity2
    
    def test_signup_unregister_signup_cycle(self, client):
        """Test repeated signup-unregister-signup cycles"""
        # Arrange
        activity = "Basketball Team"
        email = "cyclist@mergington.edu"
        cycles = 2
        
        # Act & Assert for each cycle
        for cycle in range(cycles):
            # Sign up
            signup_response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            check_after_signup = client.get("/activities")
            assert signup_response.status_code == 200
            assert email in check_after_signup.json()[activity]["participants"]
            
            # Unregister
            unregister_response = client.post(
                f"/activities/{activity}/unregister",
                params={"email": email}
            )
            check_after_unregister = client.get("/activities")
            assert unregister_response.status_code == 200
            assert email not in check_after_unregister.json()[activity]["participants"]
