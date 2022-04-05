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
from readVideo import readVideo
from writeThreadDateTimeName import writeThreadDateTimeName
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
NAME = ['ahmed', 'hassan']
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
        #audio_text = r.record(source, duration=20)
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
    for word in processed_text:
        if word in NAME:
            names.append(word)
    return names


def is_date_feasible(day, month, year):
    isValidDate = True
    try:
        date = datetime.date(year, month, day)
    except ValueError:
        isValidDate = False
    if isValidDate:
        if date >= START_DATE and date <= datetime.date.today():
            return True
    return False


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


def is_time_feasible(hours, minutes):
    isValidTime = True
    try:
        time = datetime.time(hours, minutes, 0)
    except ValueError:
        isValidTime = False
    return isValidTime


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

config_firebase = {
    "apiKey": "AIzaSyDatGf-08IgqLhQX7fliKu4Mjyh5VPuHjc",
    "authDomain": "trie-994c1.firebaseapp.com",
    "projectId": "trie-994c1",
    "storageBucket": "trie-994c1.appspot.com",
    "messagingSenderId": "815090125887",
    "appId": "1:815090125887:web:acd4a2a3346b7ace447c8a",
    "serviceAccount": "serciveaccountkey.json"
}


cur_path = os.path.dirname(__file__)
app = Flask(__name__)


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


def multiThreads(source=0):
    counter = 0
    readVideoObj = readVideo(source).start()
    writeThreadDateTimeNameObj = writeThreadDateTimeName(
        readVideoObj.frame).start()  # thread for Video Chunking via Name Date Time
    while True:
        if readVideoObj.stopped or writeThreadDateTimeNameObj.stopped:
            readVideoObj.stop()
            writeThreadDateTimeNameObj.stop()
            break
        frame = readVideoObj.frame
        writeThreadDateTimeNameObj.frame = frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/video")
def video():
    return Response(multiThreads(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/")
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
    f = request.files['file']
    f.save(secure_filename(f.filename))
    x = {"message": "Yes"}
    return jsonify(x)


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
    time = search_time(processed_text)
    x = {"message": audio_text}
    return jsonify(x)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
