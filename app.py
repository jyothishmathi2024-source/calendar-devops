from flask import Flask, request, redirect, render_template_string, abort
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "events.json"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Calendar App - v2</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 35px;
        }
        .container {
            max-width: 750px;
            margin: auto;
            background: white;
            padding: 28px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        h1 { color: #1d4ed8; }
        h2 { color: #334155; margin-top: 24px; }
        input, textarea, button {
            display: block;
            width: 100%;
            box-sizing: border-box;
            padding: 11px;
            margin: 10px 0;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 14px;
        }
        button {
            background: #2563eb;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 6px;
            font-weight: 600;
        }
        button:hover {
            background: #1d4ed8;
        }
        .btn-cancel {
            display: inline-block;
            text-align: center;
            background: #94a3b8;
            color: white;
            text-decoration: none;
            padding: 10px;
            border-radius: 6px;
            box-sizing: border-box;
            font-weight: 600;
            width: 100%;
        }
        .btn-cancel:hover {
            background: #64748b;
        }
        .btn-edit {
            display: inline-block;
            background: #0284c7;
            color: white;
            padding: 6px 14px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            margin-top: 8px;
        }
        .btn-edit:hover {
            background: #0369a1;
        }
        .event {
            background: #eff6ff;
            padding: 16px;
            margin-top: 14px;
            border-left: 4px solid #2563eb;
            border-radius: 0 6px 6px 0;
        }
        .event h3 { margin: 0 0 6px 0; color: #1e293b; }
        .event p { margin: 4px 0; color: #475569; }
        .message {
            background: #dcfce7;
            color: #15803d;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #bbf7d0;
            font-weight: 500;
        }
        .badge-v2 {
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            font-size: 12px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 12px;
            vertical-align: middle;
            margin-left: 8px;
        }
        .edit-box {
            background: #f8fafc;
            border: 2px dashed #0284c7;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Calendar Management <span class="badge-v2">v2: Modify Enabled</span></h1>
    <p>Create, view, and modify your calendar events.</p>

    {% if message %}
        <p class="message">{{ message }}</p>
    {% endif %}

    {% if edit_event %}
        <div class="edit-box">
            <h2>Edit / Modify Event</h2>
            <form action="/edit/{{ edit_event.id }}" method="POST">
                <label><strong>Title:</strong></label>
                <input name="title" value="{{ edit_event.title }}" required>
                <label><strong>Date:</strong></label>
                <input name="date" type="date" value="{{ edit_event.date }}" required>
                <label><strong>Time:</strong></label>
                <input name="time" type="time" value="{{ edit_event.time }}" required>
                <label><strong>Description:</strong></label>
                <textarea name="description" rows="3">{{ edit_event.description }}</textarea>
                <button type="submit">Update Event</button>
                <a href="/" class="btn-cancel">Cancel</a>
            </form>
        </div>
    {% else %}
        <h2>Add New Event</h2>
        <form action="/add" method="POST">
            <input name="title" placeholder="Event title" required>
            <input name="date" type="date" required>
            <input name="time" type="time" required>
            <textarea name="description" placeholder="Event description" rows="3"></textarea>
            <button type="submit">Add Event</button>
        </form>
    {% endif %}

    <h2>Your Events ({{ events|length }})</h2>
    {% for event in events %}
        <div class="event">
            <h3>{{ event.title }}</h3>
            <p><strong>Date:</strong> {{ event.date }} | <strong>Time:</strong> {{ event.time }}</p>
            <p>{{ event.description }}</p>
            <a href="/edit/{{ event.id }}" class="btn-edit">Edit Event</a>
        </div>
    {% else %}
        <p>No events yet. Add your first event above!</p>
    {% endfor %}
</div>
</body>
</html>
"""

def load_events():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    # Ensure every event has an id
    modified = False
    for idx, event in enumerate(events, start=1):
        if "id" not in event:
            event["id"] = idx
            modified = True
    if modified:
        save_events(events)

    return events

def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4)

def get_next_id(events):
    if not events:
        return 1
    return max(int(e.get("id", 0)) for e in events) + 1

@app.route("/")
def home():
    return render_template_string(
        HTML, events=load_events(), message=request.args.get("message", ""), edit_event=None
    )

@app.route("/add", methods=["POST"])
def add_event():
    title = request.form.get("title", "").strip()
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    description = request.form.get("description", "").strip()

    if not title or not date or not time:
        return "Title, date and time are required.", 400

    try:
        datetime.strptime(date, "%Y-%m-%d")
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return "Invalid date or time.", 400

    events = load_events()
    new_event = {
        "id": get_next_id(events),
        "title": title,
        "date": date,
        "time": time,
        "description": description
    }
    events.append(new_event)
    save_events(events)

    return redirect("/?message=Event+added+successfully")

@app.route("/edit/<int:event_id>", methods=["GET"])
def edit_event_form(event_id):
    events = load_events()
    event = next((e for e in events if int(e.get("id")) == event_id), None)
    if not event:
        return "Event not found", 404
    return render_template_string(
        HTML, events=events, message="", edit_event=event
    )

@app.route("/edit/<int:event_id>", methods=["POST"])
def update_event(event_id):
    title = request.form.get("title", "").strip()
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    description = request.form.get("description", "").strip()

    if not title or not date or not time:
        return "Title, date and time are required.", 400

    try:
        datetime.strptime(date, "%Y-%m-%d")
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return "Invalid date or time.", 400

    events = load_events()
    event = next((e for e in events if int(e.get("id")) == event_id), None)
    if not event:
        return "Event not found", 404

    event["title"] = title
    event["date"] = date
    event["time"] = time
    event["description"] = description
    save_events(events)

    return redirect("/?message=Event+updated+successfully")

@app.route("/health")
def health():
    return {"status": "healthy", "version": "v2"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
