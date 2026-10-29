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
    assert b"Calendar Management" in response.data
    assert b"v2: Modify Enabled" in response.data
    assert b"Add New Event" in response.data


def test_add_event(client):
    response = client.post("/add", data={
        "title": "Project Review",
        "date": "2026-10-27",
        "time": "10:00",
        "description": "Calendar application v2 testing"
    })

    assert response.status_code == 302

    response = client.get("/")
    assert b"Project Review" in response.data
    assert b"Calendar application v2 testing" in response.data
    assert b"Edit Event" in response.data


def test_missing_title(client):
    response = client.post("/add", data={
        "title": "",
        "date": "2026-10-27",
        "time": "10:00",
        "description": "Test event"
    })

    assert response.status_code == 400


def test_edit_event_page(client):
    client.post("/add", data={
        "title": "Initial Meeting",
        "date": "2026-10-30",
        "time": "09:00",
        "description": "Initial description"
    })

    response = client.get("/edit/1")
    assert response.status_code == 200
    assert b"Edit / Modify Event" in response.data
    assert b"Initial Meeting" in response.data
    assert b"Update Event" in response.data


def test_edit_event_page_404(client):
    response = client.get("/edit/999")
    assert response.status_code == 404


def test_update_event_success(client):
    client.post("/add", data={
        "title": "Draft Presentation",
        "date": "2026-11-01",
        "time": "11:00",
        "description": "First draft"
    })

    response = client.post("/edit/1", data={
        "title": "Final Presentation",
        "date": "2026-11-02",
        "time": "14:00",
        "description": "Revised final draft"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Event updated successfully" in response.data
    assert b"Final Presentation" in response.data
    assert b"Revised final draft" in response.data

    with open(calendar_app.DATA_FILE, encoding="utf-8") as file:
        events = json.load(file)
    assert len(events) == 1
    assert events[0]["title"] == "Final Presentation"
    assert events[0]["date"] == "2026-11-02"
    assert events[0]["time"] == "14:00"


def test_update_event_validation(client):
    client.post("/add", data={
        "title": "Workshop",
        "date": "2026-11-05",
        "time": "10:00",
        "description": "Workshop"
    })

    # Missing title
    response = client.post("/edit/1", data={
        "title": "",
        "date": "2026-11-05",
        "time": "10:00",
        "description": "Workshop"
    })
    assert response.status_code == 400

    # Invalid date
    response = client.post("/edit/1", data={
        "title": "Workshop",
        "date": "invalid-date",
        "time": "10:00",
        "description": "Workshop"
    })
    assert response.status_code == 400

    # Non-existent event
    response = client.post("/edit/999", data={
        "title": "Workshop",
        "date": "2026-11-05",
        "time": "10:00",
        "description": "Workshop"
    })
    assert response.status_code == 404


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["version"] == "v2"


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
    assert "id" in events[0]
