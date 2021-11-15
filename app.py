from flask import Flask, render_template, Response,request
import cv2
import base64
import numpy as np
app=Flask(__name__)
camera=cv2.VideoCapture(0)



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
    return render_template("index.html")


@app.route("/video")
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame' )

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
    print(type(obj))
    #print(len(obj))
    #print(obj)
    with open("imageToSave.jpg", "wb") as fh:
        fh.write(base64.decodebytes(obj))
    
    return (Response(),200)
       
if __name__ == "__main__":
   app.run(host="0.0.0.0")