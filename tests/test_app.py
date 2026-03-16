import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, dict)
    assert set(data.keys()) == set(activities.keys())
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Check participant was added
    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    first = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert first.status_code == 400
    assert first.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404():
    email = "anyone@mergington.edu"
    response = client.post(f"/activities/Nonexistent%20Club/signup?email={email}")
    assert response.status_code == 404


def test_remove_participant_succeeds():
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    activities_response = client.get("/activities").json()
    assert email not in activities_response["Chess Club"]["participants"]


def test_remove_nonexisting_participant_404():
    email = "nonexistent@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_unknown_activity_404():
    email = "anyone@mergington.edu"
    response = client.delete(f"/activities/NoSuchClub/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
