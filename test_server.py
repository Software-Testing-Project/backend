from io import StringIO
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


def test_feasible_date():
    response = app.test_client().post(
        "/date_feasible", data={"year": 2000, "month": 11, "day": 16})  # As the start date is starting from 2021
    response2 = app.test_client().post(
        "/date_feasible", data={"year": 2022, "month": 3, "day": 16})
    print(response)
    assert response.data == b'False'
    assert response2.data == b'True'


def test_PostImages():
    image = open("umar.jpeg", "rb").read()
    headers = {'content_type': 'multipart/form-data'}

    response = app.test_client().post(
        "/Postimages", data=dict({'media': (image, "umar.jpeg")}), headers=headers)
    assert response.json == b'{"message": "Yes"}'


def test_send_notification():
    response = app.test_client().get("/send_notificaton")
    assert response.data == b"Send"
