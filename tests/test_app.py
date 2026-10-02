import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def test_api(monkeypatch):
    activities = {
        "Test Activity": {
            "description": "A test activity",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as client:
        yield client, activities


def test_get_activities_returns_activity_data(test_api):
    # Arrange
    client, activities = test_api

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(test_api):
    # Arrange
    client, activities = test_api
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Test Activity"
    }
    assert email in activities["Test Activity"]["participants"]


def test_duplicate_signup_returns_400_without_adding_participant(test_api):
    # Arrange
    client, activities = test_api
    email = "existing@example.com"

    # Act
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities["Test Activity"]["participants"].count(email) == 1


def test_signup_for_unknown_activity_returns_404(test_api):
    # Arrange
    client, _ = test_api

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "new@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(test_api):
    # Arrange
    client, activities = test_api
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Test Activity"
    }
    assert email not in activities["Test Activity"]["participants"]


def test_unregister_of_unregistered_participant_returns_404(test_api):
    # Arrange
    client, activities = test_api
    email = "absent@example.com"

    # Act
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities["Test Activity"]["participants"] == ["existing@example.com"]


def test_unregister_from_unknown_activity_returns_404(test_api):
    # Arrange
    client, _ = test_api

    # Act
    response = client.delete(
        "/activities/Unknown Activity/signup",
        params={"email": "existing@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}