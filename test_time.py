from flask_app import app
from flask import json


def test_people_file():

    response = app.test_client().get("/people")

    # Check that there was one redirect response.
    assert response.data == b"abc"
    assert response.status_code == 200


def test_feasible_time():
    response = app.test_client().post(
        "/feasible_time", data={"hours": "10", "minutes": "20"})
    response2 = app.test_client().post(
        "/feasible_time", data={"hours": "25220", "minutes": "20"})
    assert response.data == b"Yes"
    assert response2.data == b"Yes"
