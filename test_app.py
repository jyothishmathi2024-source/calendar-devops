
import json
import pytest
import app as calendar_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        calendar_app, "DATA_FILE", str(tmp_path / "events.json")
    )
    calendar_app.app.config["TESTING"] = True

    with calendar_app.app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Calendar Management - v1" in response.data
    assert b"Add New Event" in response.data


def test_add_event(client):
    response = client.post("/add", data={
        "title": "Project Review",
        "date": "2026-10-27",
        "time": "10:00",
        "description": "Calendar application v1 testing"
    })

    assert response.status_code == 302

    response = client.get("/")
    assert b"Project Review" in response.data
    assert b"Calendar application v1 testing" in response.data


def test_missing_title(client):
    response = client.post("/add", data={
        "title": "",
        "date": "2026-10-27",
        "time": "10:00",
        "description": "Test event"
    })

    assert response.status_code == 400


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["version"] == "v1"


def test_event_is_saved_as_json(client):
    client.post("/add", data={
        "title": "Lab Test",
        "date": "2026-10-28",
        "time": "14:00",
        "description": "Testing JSON storage"
    })

    with open(calendar_app.DATA_FILE, encoding="utf-8") as file:
        events = json.load(file)

    assert len(events) == 1
    assert events[0]["title"] == "Lab Test"
