import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data():
    return {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 4,
            "participants": ["existing@school.edu"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Mondays",
            "max_participants": 3,
            "participants": [],
        },
    }


@pytest.fixture
def client(monkeypatch, activity_data):
    monkeypatch.setattr(app_module, "activities", activity_data)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_current_activities(client, activity_data):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activity_data


def test_signup_adds_participant(client, activity_data):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new@school.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@school.edu for Chess Club"}
    assert "new@school.edu" in activity_data["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activity_data):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 400
    assert activity_data["Chess Club"]["participants"] == ["existing@school.edu"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@school.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client, activity_data):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@school.edu from Chess Club"
    }
    assert activity_data["Chess Club"]["participants"] == []


def test_unregister_rejects_student_not_signed_up(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing@school.edu"},
    )

    assert response.status_code == 404


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@school.edu"},
    )

    assert response.status_code == 404
