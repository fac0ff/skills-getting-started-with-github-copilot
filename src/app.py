"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import csv

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": []
    }
}

# Folder for CSV files
var_dir = os.path.join(current_dir, "var")

# Ensure the "var" directory exists
os.makedirs(var_dir, exist_ok=True)

def get_csv_path(activity_name: str) -> str:
    """Generate the CSV file path for a given activity name."""
    csv_file = f"{activity_name.replace(' ', '_').lower()}_participants.csv"
    return os.path.join(var_dir, csv_file)

# Load participants from CSV files
for activity_name, activity in activities.items():
    csv_path = get_csv_path(activity_name)
    if os.path.exists(csv_path):
        with open(csv_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            participants = [row[0] for row in reader if row]  # Load participants
            activity["participants"].extend(participants)
            # Decrease max_participants by the number of already enrolled participants
            activity["max_participants"] -= len(participants)

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
def get_activities():
    return activities

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if the participant is already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Participant already signed up")

    # Add student
    activity["participants"].append(email)

    # Append the new participant to a CSV file in the "var" directory
    csv_path = get_csv_path(activity_name)
    with open(csv_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([email])  # Append only the new participant

    return {"message": f"Signed up {email} for {activity_name}"}
