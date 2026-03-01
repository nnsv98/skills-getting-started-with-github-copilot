"""
FastAPI tests for the Mergington High School Activities API.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity.
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client: TestClient):
        """
        Test: Get all activities returns 200 status code
        Arrange: No setup required (using test fixtures)
        Act: Make GET request to /activities
        Assert: Status code should be 200
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """
        Test: Get all activities returns correct activity data
        Arrange: Test activities are set up in fixtures
        Act: Make GET request to /activities
        Assert: Response should contain expected activities
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_participants(self, client: TestClient):
        """
        Test: Activities include participants list
        Arrange: Test activities with participants are set up
        Act: Make GET request to /activities
        Assert: Participants should be correctly listed
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "john@mergington.edu" in data["Gym Class"]["participants"]
        assert len(data["Programming Class"]["participants"]) == 0

    def test_get_activities_returns_activity_details(self, client: TestClient):
        """
        Test: Activities contain all required fields
        Arrange: Test activities are set up in fixtures
        Act: Make GET request to /activities
        Assert: Each activity should have required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]

        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_index(self, client: TestClient):
        """
        Test: Root endpoint redirects to index.html
        Arrange: No setup required
        Act: Make GET request to root without following redirects
        Assert: Should return 307 redirect status
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, client: TestClient):
        """
        Test: Successfully sign up a new participant
        Arrange: Programming Class has no participants
        Act: Sign up alice@mergington.edu for Programming Class
        Assert: Should return 200 and confirm signup
        """
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_participant_added_to_activity(self, client: TestClient):
        """
        Test: New participant appears in activity's participant list
        Arrange: Programming Class with no participants
        Act: Sign up a participant, then fetch activities
        Assert: Participant should appear in participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "bob@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_participant_fails(self, client: TestClient):
        """
        Test: Cannot sign up same participant twice
        Arrange: michael@mergington.edu is already signed up for Chess Club
        Act: Try to sign up michael@mergington.edu again
        Assert: Should return 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client: TestClient):
        """
        Test: Cannot sign up for non-existent activity
        Arrange: Non-existent activity name
        Act: Try to sign up for Fake Activity
        Assert: Should return 404 error
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_participants(self, client: TestClient):
        """
        Test: Multiple different participants can sign up for same activity
        Arrange: Programming Class with no participants
        Act: Sign up two different participants
        Assert: Both should be in the participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "alice@mergington.edu"
        email2 = "charlie@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email1}")
        client.post(f"/activities/{activity_name}/signup?email={email2}")
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 2


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_existing_participant_success(self, client: TestClient):
        """
        Test: Successfully unregister an existing participant
        Arrange: michael@mergington.edu is signed up for Chess Club
        Act: Delete michael@mergington.edu from Chess Club
        Assert: Should return 200 and confirm removal
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_unregister_participant_removed_from_list(self, client: TestClient):
        """
        Test: Unregistered participant is removed from participants list
        Arrange: michael@mergington.edu is in Chess Club
        Act: Delete michael@mergington.edu, then fetch activities
        Assert: Participant should not appear in list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity_name]["participants"]
        assert email not in participants
        assert len(participants) == 0

    def test_unregister_nonregistered_participant_fails(self, client: TestClient):
        """
        Test: Cannot unregister participant who is not signed up
        Arrange: notregistered@mergington.edu is not in Chess Club
        Act: Try to delete notregistered@mergington.edu from Chess Club
        Assert: Should return 404 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client: TestClient):
        """
        Test: Cannot unregister from non-existent activity
        Arrange: Non-existent activity name
        Act: Try to delete from Fake Activity
        Assert: Should return 404 error
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_multiple_participants_independently(
        self, client: TestClient
    ):
        """
        Test: Can selectively unregister participants
        Arrange: Chess Club has michael@mergington.edu; we add another
        Act: Add a second participant, then remove only the first
        Assert: Only the removed participant should be gone
        """
        # Arrange
        activity_name = "Chess Club"
        email1 = "michael@mergington.edu"
        email2 = "david@mergington.edu"

        # Act - add second participant
        client.post(f"/activities/{activity_name}/signup?email={email2}")

        # Act - remove first participant
        client.delete(f"/activities/{activity_name}/signup?email={email1}")

        # Act - fetch updated list
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity_name]["participants"]
        assert email1 not in participants
        assert email2 in participants
