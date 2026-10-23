
from flask import Flask, request, redirect, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "events.json"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Calendar App - v1</title>
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
        }
        h1 { color: #1d4ed8; }
        input, textarea, button {
            display: block;
            width: 100%;
            box-sizing: border-box;
            padding: 11px;
            margin: 10px 0;
        }
        button {
            background: #2563eb;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        .event {
            background: #eff6ff;
            padding: 15px;
            margin-top: 12px;
            border-left: 4px solid #2563eb;
        }
        .message { color: #15803d; }
    </style>
</head>
<body>
<div class="container">
    <h1>Calendar Management - v1</h1>
    <p>Create and view your calendar events.</p>

    {% if message %}
        <p class="message">{{ message }}</p>
    {% endif %}

    <h2>Add New Event</h2>
    <form action="/add" method="POST">
        <input name="title" placeholder="Event title" required>
        <input name="date" type="date" required>
        <input name="time" type="time" required>
        <textarea name="description"
                  placeholder="Event description"></textarea>
        <button type="submit">Add Event</button>
    </form>

    <h2>Your Events ({{ events|length }})</h2>
    {% for event in events %}
        <div class="event">
            <h3>{{ event.title }}</h3>
            <p>Date: {{ event.date }} | Time: {{ event.time }}</p>
            <p>{{ event.description }}</p>
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
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4)

@app.route("/")
def home():
    return render_template_string(
        HTML, events=load_events(), message=request.args.get("message", "")
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
    events.append({
        "title": title,
        "date": date,
        "time": time,
        "description": description
    })
    save_events(events)

    return redirect("/?message=Event+added+successfully")

@app.route("/health")
def health():
    return {"status": "healthy", "version": "v1"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
