import os
import sys
from urllib.parse import quote

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect some known activities exist
    assert "Chess Club" in data


def test_signup_success_and_cleanup():
    activity = "Chess Club"
    email = "tester+pytest@mergington.edu"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Perform signup
    path = f"/activities/{quote(activity)}/signup"
    resp = client.post(path, params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Cleanup
    activities[activity]["participants"].remove(email)


def test_signup_already_exists_returns_400():
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]
    path = f"/activities/{quote(activity)}/signup"
    resp = client.post(path, params={"email": existing})
    assert resp.status_code == 400
    assert resp.json().get("detail") == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    activity = "Nonexistent Activity"
    email = "someone@mergington.edu"
    path = f"/activities/{quote(activity)}/signup"
    resp = client.post(path, params={"email": email})
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Activity not found"
