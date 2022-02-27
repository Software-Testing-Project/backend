import re
from flask import Flask, render_template, Response, request
import cv2
import base64
import time
import os
import sys
from twilio.rest import Client
import requests as req
from flask import jsonify
import face_recognition
import numpy as np
import time
import base64
from multiprocessing import Value


counter = Value('i', 0)

config_firebase = {
    "apiKey": "AIzaSyDatGf-08IgqLhQX7fliKu4Mjyh5VPuHjc",
    "authDomain": "trie-994c1.firebaseapp.com",
    "projectId": "trie-994c1",
    "storageBucket": "trie-994c1.appspot.com",
    "messagingSenderId": "815090125887",
    "appId": "1:815090125887:web:acd4a2a3346b7ace447c8a",
    "serviceAccount": "serciveaccountkey.json"
}

obama_image = face_recognition.load_image_file("ehsan1.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

reem_image = face_recognition.load_image_file("ehsan1.jpg")
reem_face_encoding = face_recognition.face_encodings(reem_image)[0]


cur_path = os.path.dirname(__file__)
app = Flask(__name__)
camera = cv2.VideoCapture(0)
known_face_encodings = [
    obama_face_encoding,
    reem_face_encoding

]
known_face_names = [
    "Ehsan",
    "Reem"
]


def checkpath(name):

    isExist = os.path.exists(name)
    if not isExist:
      # Create a new directory because it does not exist
        os.makedirs(name)
        print("The new directory is created!")

# seprate /people should be called to display the names of people in video


@app.route("/people")
def people():
    f = open("test.txt", 'r')
    x = f.read()
    f.close()
    return x


def generate_frames():
    while True:

        success, frame = camera.read()
        half = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        if not success:
            with counter.get_lock():
                counter.value = 0
            break
        else:
            if counter.value == 0:
                face_locations = face_recognition.face_locations(half)
                face_encodings = face_recognition.face_encodings(
                    half, face_locations)
                face_names = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding, tolerance=0.52)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                    face_names.append(name)
                f = open("test.txt", 'w')
                for name in zip(face_names):
                    # print(name)
                    f.write(str(name))
                    # people(name)
                f.close()
                with counter.get_lock():
                    counter.value += 1

        with counter.get_lock():
            counter.value += 1
            if counter.value >= 20:
                counter.value = 0
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/video")
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/a")
def index():
    send_notifications_wrapper()

    return render_template("index.html")


@app.route("/call_sim", methods=['POST'])
def call_sim():
    account_sid = 'ACa70d045e9ea85caa79c86ebfb3e5300a'
    auth_token = 'c37a229fba02be84ce3d96292e14a309'
    request_data = request.get_json()
    number = request_data["PhoneNumber"]
    print(number)
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        twiml='<Resposne><Say>hello success learner</Say></Response>', to=number, from_='+16205778296')
    print(call.sid)
    if call.sid:
        return (Response("Done", 200))
    else:
        return (Response("No", 404))


def check_subscribers(token):
    try:
        file = open("Subscribers.txt", "r")

        readfile = file.read()
        if token in readfile:
            return True
        else:
            return False
    except:
        return False


@app.route("/subscribe", methods=['POST'])
def subscribe():
    token = request.get_json()
    print(token)
    token = token["to"]
    print(type(token))
    flag = check_subscribers(token)
    if flag != True:
        f = open("Subscribers.txt", "a")
        f.write(token)
        f.write("\n")
        f.close()
        x = {"result": "OK"}
        return jsonify(x)
    else:
        x = {"result": "Already Subscribed"}
        return jsonify(x)


@app.route("/ehsan")
def ehsan():
    return "ehsan"


@app.route("/Postimages",  methods=['POST'])
def post_images():
    r = request
    obj = r.get_json()
    obj = obj["img"]
    obj = base64.b64decode(obj)
    print(type(obj))

    # convert string of image data to uint8
    # decode image
   # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    name = "Ahamd"
    t = time.localtime()

    img_name = name+"_" + str(t.tm_mday)+"_"+str(t.tm_mon)+"_"+str(
        t.tm_year)+"_"+str(t.tm_hour)+"_"+str(t.tm_min)+"_"+str(t.tm_sec)
    img_name += ".jpg"

    save_path = "./"+name
    completeName = os.path.join(save_path, img_name)
    checkpath(save_path)

    with open(completeName, "wb") as fh:
        fh.write(obj)

    return (Response(), 200)


def send_notifications_wrapper():
    try:
        file = open("Subscribers.txt", "r")

        readfile = file.read().splitlines()
        count = 0
        for line in readfile:

            send_notifications(line, "Video Made", "Press to view")
    except:
        return False


def send_notifications(expo_token, title, body):
    print("Inside")
    message = {
        'to': expo_token,
        'title': title,
        'body': body
    }
    return req.post('https://exp.host/--/api/v2/push/send', json=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
