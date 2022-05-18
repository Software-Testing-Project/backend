from crypt import methods
from sqlalchemy import true
import db as database
import re
from flask import Flask, render_template, Response, request, send_file, stream_with_context
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
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import speech_recognition as sr
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
import datetime
from pydub import AudioSegment
from os import path
import glob
from pathlib import Path
import threading
dir_path = os.path.dirname(os.path.realpath(__file__))
cur_path = os.path.dirname(__file__)
app = Flask(__name__)

known_face_encodings = []
known_face_names = []


def encode_faces():
    path = "/home/ehsan/Desktop/FYP/fyp_server/fyp_server/faceImages"
    print("Training faces for recognition")
    for filePath in glob.iglob(path + '**/*.jpg', recursive=True):
        known_face_encodings.append(face_recognition.face_encodings(
            face_recognition.load_image_file(filePath))[0])
        known_face_names.append(Path(filePath).stem)
    print("Training Completed")

################Database#############

#####################################


################## NLP###########################


def convert_file():
    m4a_file = 'test.m4a'
    wav_filename = r"abc.wav"
    track = AudioSegment.from_file(m4a_file,  format='m4a')
    file_handle = track.export(wav_filename, format='wav')


# nltk.download('wordnet')
MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]
NAME = ['ahmed', 'hassan', 'ayesha', 'ehsan']
START_DATE = datetime.date(2021, 2, 1)


def fetch_audio_text():
    text = None
    r = sr.Recognizer()
    # with sr.Microphone() as source:
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "abc.wav")
    with sr.AudioFile(AUDIO_FILE) as source:
        r.adjust_for_ambient_noise(source)
        print("Talk")
        # <class 'speech_recognition.AudioData'>
        # audio_text = r.record(source, duration=20)
        audio_text = r.record(source)  # read the entire audio file
        print("Time over, thanks")
        try:
            text = r.recognize_google(audio_text)
            print("you said: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(e))
    return text


def fetch_synonyms(words):
    synonyms = []
    for word in words:
        for syn in wn.synsets(word):
            for l in syn.lemmas():
                synonyms.append(l.name())
    synonym_verbs = []
    lemmatizer = WordNetLemmatizer()
    for word in synonyms:
        synonym_verbs.append(lemmatizer.lemmatize(word, pos='v'))
    synonym_verbs = list(set(synonym_verbs))
    return synonym_verbs


def process_text(audio_text):
    word_list = nltk.word_tokenize(audio_text)
    lemmatizer = WordNetLemmatizer()
    lemmatized_list = []
    for word in word_list:
        lemmatized_list.append(lemmatizer.lemmatize(word, pos='v'))
    return lemmatized_list


def search_action(processed_text, synonyms):
    for word in processed_text:
        for key_action in synonyms:
            if word in synonyms[key_action]:
                return key_action


def search_name(processed_text):
    names = []
    s = ""
    print("known faces are", known_face_names)
    for word in processed_text:

        list_to_str = "".join(map(str, word))
        list_to_str = list_to_str.title()
        print("Title is ", list_to_str)
        if list_to_str.title() in known_face_names:
            print("Yes")
            names.append(list_to_str)
            s = ""
    print(names)
    return names


@app.route("/date_feasible", methods=["POST"])
def is_date_feasible():
    isValidDate = True
    data = request.form
    try:
        date = datetime.date(int(data['year']), int(
            data['month']), int(data['day']))
    except ValueError:
        isValidDate = False
    if isValidDate:
        if date >= START_DATE and date <= datetime.date.today():
            return "True"
    return "False"


def search_date(processed_text):
    day = month = year = None
    for i in range(len(processed_text)):
        processed_text[i] = processed_text[i]. lower()
        if processed_text[i] in MONTHS:
            month = MONTHS.index(processed_text[i])+1
        if processed_text[i][-2:] in DAY_EXTENTIONS and processed_text[i][:-2].isdigit():
            day = int(processed_text[i][:-2])
        if processed_text[i][:4].isdigit():
            year = int(processed_text[i][:4])
            break
    if day != None and month != None and year != None:
        if is_date_feasible(day, month, year):
            return datetime.date(year, month, day)
    else:
        return None


def search_time(processed_text):
    hour = minutes = None
    if 'p.m' or 'a.m' in processed_text:
        for item in processed_text:
            if ':' in item:
                if item[:2].isdigit() and item[3:].isdigit():
                    if 'a.m' in processed_text:
                        hour = int(item[:2])
                        minutes = int(item[3:])
                        break
                    elif 'p.m' in processed_text:
                        hour = int(item[:2])+12
                        minutes = int(item[3:])
                        break
    if hour != None and minutes != None:
        if is_time_feasible(hour, minutes):
            return datetime.time(hour, minutes, 0)
    else:
        return None

#####################################


counter = Value('i', 0)


def checkpath(name):

    isExist = os.path.exists(name)
    if not isExist:
      # Create a new directory because it does not exist
        os.makedirs(name)
        print("The new directory is created!")

# seprate /people should be called to display the names of people in video


@app.route("/people", methods=['GET'])
def people():
    f = open("test.txt", 'r')
    x = f.read()
    f.close()
    return x

# it doesnot return the boolean values


@app.route("/feasible_time", methods=['POST'])
def is_time_feasibles():
    isValidTime = "Yes"
    data = request.form

    try:
        time = datetime.time(data['hours'], data['minutes'], 0)
        if time:
            return "Yes"
        else:
            return "No"
    except ValueError:
        isValidTime = "No"
    finally:
        return isValidTime


def send_live_stream():
    while true:
        success, frame = camera.read()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def multiThreads():
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    counter = 0
    videoLength = 1500  # 15 seconds long video
    # set your screen size here
    frame_width = int(camera.get(3))
    frame_height = int(camera.get(4))
    size = (frame_width, frame_height)
    location = time.strftime('%d%m%Y-%H%M%S')
    result = cv2.VideoWriter(f"videos/{location}.mp4",
                             cv2.VideoWriter_fourcc(*'mp4v'),
                             20, size)
    i = 0
    all_faces = set()
    while True:
        i += 1  # For chucnking
        counter += 1
        if(counter > 10):  # For detecting face
            counter = 0
        if i > videoLength:
            for i in all_faces:
                print(i)
                database.insert_query(i, location)
            all_faces = set()
            result.release()
            i = 0
            location = time.strftime('%d%m%Y-%H%M%S')
            result = cv2.VideoWriter(f"videos/{location}.mp4",
                                     cv2.VideoWriter_fourcc(*'mp4v'),
                                     20, size)
        success, frame = camera.read()
        half = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = half[:, :, ::-1]

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            result.write(frame)
            ########################
            if(counter == 1 or counter == 5 or counter == 10):
                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(
                        rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(
                        rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(
                            known_face_encodings, face_encoding)
                        name = "Unknown"

                        # # If a match was found in known_face_encodings, just use the first one.
                        # if True in matches:
                        #     first_match_index = matches.index(True)
                        #     name = known_face_names[first_match_index]

                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(
                            known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                process_this_frame = not process_this_frame

            # Display the results
            for name in face_names:

                all_faces.add(name)

            ##########################


@app.route("/video")
def video():

    return Response(send_live_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


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


@app.route("/Postimages",  methods=['POST'])
def post_images():

    f = request.files['file']
    #f.save(os.path.join("faceImages", secure_filename(f.filename)))
    x = {"message": "Yes"}
    return jsonify(x)


@app.route("/send_notificaton", methods={"GET"})
def send_notifications_wrapper():
    try:
        file = open("Subscribers.txt", "r")

        readfile = file.read().splitlines()
        count = 0
        for line in readfile:

            send_notifications(line, "Video Made", "Press to view")
        return "Send"
    except:
        return "Not Send"


def send_notifications(expo_token, title, body):
    print("Inside")
    message = {
        'to': expo_token,
        'title': title,
        'body': body
    }
    return req.post('https://exp.host/--/api/v2/push/send', json=message)


@app.route("/voice", methods=['POST'])
def voice():
    f = request.files['file']
    f.save(secure_filename(f.filename))
    convert_file()
    synonyms = {}
    synonyms['search'] = fetch_synonyms(['search', 'find'])
    synonyms['set'] = fetch_synonyms(['set'])
    audio_text = fetch_audio_text()
    processed_text = process_text(audio_text)

    action_verb = search_action(processed_text, synonyms)
    date = search_date(processed_text)

    names = search_name(processed_text)
    print(audio_text)
    time = search_time(processed_text)
    if len(names) != 0:
        print("Size not 0")
        l1 = database.make_list(database.get_by_name(names[0].title()))
        x = {"message": audio_text, "data": l1}
    else:
        x = {"message": "No result found", "data": "err"}
    return jsonify(x)


@app.route("/video_stored/<video_id>")
def video_stored(video_id):

    return send_file(
        "videos/{}".format(video_id+".mp4"))


if __name__ == "__main__":
    encode_faces()

    global camera
    global success
    global frame
    camera = cv2.VideoCapture(0)
    th = threading.Thread(target=multiThreads)
    th.start()
    print(known_face_names)
    app.run(host="0.0.0.0")
