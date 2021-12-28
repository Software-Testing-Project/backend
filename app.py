from flask import Flask, render_template, Response,request
import cv2
import base64
import time
import os
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
    name="Ehsan"
    t = time.localtime()
    
    img_name =name+"_"+ str(t.tm_mday)+"_"+str(t.tm_mon)+"_"+str(t.tm_year)+"_"+str(t.tm_hour)+"_"+str(t.tm_min)+"_"+str(t.tm_sec)
    img_name +=".jpg"
    
    checkpath(name)
    new_path = os.path.relpath('.\\{}\\{}'.format(name,img_name), cur_path)

    with open(new_path, "wb") as fh:
        fh.write(base64.decodebytes(obj))
    
    return (Response(),200)
       
if __name__ == "__main__":
   app.run(host="0.0.0.0")