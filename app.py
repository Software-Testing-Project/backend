import re
from flask import Flask, render_template, Response,request
import cv2
import base64
import time
import os
from twilio.rest import Client
import requests as req
from flask import jsonify

config_firebase ={
    "apiKey": "AIzaSyDatGf-08IgqLhQX7fliKu4Mjyh5VPuHjc",
  "authDomain": "trie-994c1.firebaseapp.com",
  "projectId": "trie-994c1",
  "storageBucket": "trie-994c1.appspot.com",
  "messagingSenderId": "815090125887",
  "appId": "1:815090125887:web:acd4a2a3346b7ace447c8a",
  "serviceAccount":"serciveaccountkey.json"
}


cur_path = os.path.dirname(__file__)
app=Flask(__name__)
camera=cv2.VideoCapture(0)

def checkpath(name):
    path ="./"+ name
    isExist = os.path.exists(path)
    if not isExist:
  # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")

def generate_frames():
    while True:
        success, frame =camera.read()
        half = cv2.resize(frame, (0, 0), fx = 0.3, fy = 0.3)
        
        if not success:
            break
        else:
            ret, buffer =cv2.imencode('.jpg',half)

            frame=buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route("/")
def index():
    send_notifications_wrapper()
    return render_template("index.html")


@app.route("/call_sim", methods=['POST'])
def call_sim():
    account_sid='ACa70d045e9ea85caa79c86ebfb3e5300a'
    auth_token='c37a229fba02be84ce3d96292e14a309'
    request_data = request.get_json()
    number= request_data["PhoneNumber"]
    print(number)
    client=Client(account_sid,auth_token)
    call=client.calls.create(twiml='<Resposne><Say>hello success learner</Say></Response>',to=number,from_='+16205778296')
    print(call.sid)
    if call.sid:
        return (Response("Done",200))
    else:
        return (Response("No",404))


@app.route("/video")
def video():
    
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame' )


def check_subscribers(token):
    try:
        file= open("Subscribers.txt","r")
    
        readfile = file.read()
        if token in readfile: 
            return True
        else:
            return False
    except:
        return False
    

@app.route("/subscribe", methods=['POST'])
def subscribe():
    token= request.get_json()
    print(token)
    token=token["to"]
    print(type(token))
    flag=check_subscribers(token)
    if flag != True:
        f = open("Subscribers.txt", "a")
        f.write(token)
        f.write("\n")
        f.close()
        x={"result":"OK"}
        return jsonify(x)
    else:
        x={"result":"Already Subscribed"}
        return jsonify(x)
    

    

@app.route("/ehsan")
def ehsan():
    return  "ehsan"

@app.route("/Postimages",  methods=['POST'])
def post_images():
    r = request
    # convert string of image data to uint8
    #nparr = np.fromstring(r.data, np.uint8)
    # decode image
   # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    obj= r.data.decode("utf-8")  
    obj=obj.strip(""" {"img":"  """)
    obj=obj.strip(""" "}  """)
    obj  = bytes(obj, 'ascii')
    name="Ehsan"
    t = time.localtime()
    
    img_name =name+"_"+ str(t.tm_mday)+"_"+str(t.tm_mon)+"_"+str(t.tm_year)+"_"+str(t.tm_hour)+"_"+str(t.tm_min)+"_"+str(t.tm_sec)
    img_name +=".jpg"
    
    checkpath(name)
    new_path = os.path.relpath('.\\{}\\{}'.format(name,img_name), cur_path)

    with open(new_path, "wb") as fh:
        fh.write(base64.decodebytes(obj))
    
    return (Response(),200)

def send_notifications_wrapper():
    try:
        file= open("Subscribers.txt","r")
    
        readfile = file.read().splitlines()
        count=0
        for line in readfile:
           
            send_notifications(line,"Video Made","Press to view")
    except:
        return False

def send_notifications(expo_token, title, body):
  print("Inside")  
  message = {
    'to' : expo_token,
    'title' : title,
    'body' : body
  }
  return req.post('https://exp.host/--/api/v2/push/send', json = message)

       
if __name__ == "__main__":
   app.run(host="0.0.0.0")