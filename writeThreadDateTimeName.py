#thread for Date Time Name Video Chunking
from threading import Thread
import cv2
import time
import face_recognition
from images import images
import numpy as np
import os

class writeThreadDateTimeName:

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        #At the end of this function it would print the list with a list[name, date, time]
        #read a last updated file counter and date from a file
        #run for the first time
        temp=0
        f= open("last_updated_file_counter_and_date.txt","r+")
        contents=f.read()
        x = contents.split(",")
        lastUpdatedCounter=int(x[0])#when no file created, the value will be zero
        lastUpdatedDate=str(x[1])#when no date created, the value will be empty space in the file 
        f.close()

        imgObj=images()
        if imgObj.checkImagesLength()!=0:
            #There lies one to one correspondence between the known face encodings and the knownFaceNames
            #For example, the first entry of the known face encoding would be the encoding for the name in the known face names
            #This function gets the encodings of the saved images 
            knownFaceEncodings=imgObj.getKnownFaceEncodings()
            #This function gets the names of the saved names in the database
            knownFaceNames=imgObj.getNames()
            print('known faces: ',knownFaceNames)
            #Configurations foe setting the duration of a video
            frame_size=int(40)
            videoLength=int(10)*frame_size #set videoLength to any number of seconds, here it is 10 seconds
            #Setting the size( or resolution) of video's frame
            size,frame_counter=(int(1280),int(720)),1
            #Setting the format of the video
            fourcc = cv2.VideoWriter.fourcc(*'MP4V')
            #flag for detecting the presence of the recognized face in the video
            flagFaceFound=False
            #Keep taking frames until a key 'q' is not pressed
            while not self.stopped:
                cv2.imshow("DateTimeNameVideo", self.frame)
                frame_counter+=1
                innerVideoCounter=1
                #In order to reduce the processing speed of the model, only model is used over fixed frame number
                if frame_counter==3 or frame_counter==24 or frame_counter==39: 
                    #This function detects the multiple faces's face locations
                    face_locations = face_recognition.face_locations(self.frame)
                    #If there is no person in the video then this face recognition would not work
                    length=len(face_locations)
                    #print(length)
                    if length!=0:
                        #Stores the recognized names
                        names = []
                        #This function helps in getting the encodingd for the face locations
                        face_encodings = face_recognition.face_encodings(self.frame, face_locations)
                        #We would match the encodings of the recognized faces in the video with the known encodings
                        for face_encoding in face_encodings:
                            matches = face_recognition.compare_faces(knownFaceEncodings, face_encoding, tolerance=0.6)
                        #print(matches)
                        index=0
                        flagFaceFound=False
                        # check to see if we have found a match
                        for match in matches:
                            if match == True:
                                names.append(knownFaceNames[index])
                                flagFaceFound=True
                        index+=1
                        #print(names)
                        if flagFaceFound: #start making video of 1 minute long duration as set above
                            print("Video making started")
                            # chunks = cv2.VideoWriter(f"videoClipsDateName/{name+' - '+time.strftime('%d %m %Y - %H %M %S')}.mp4", fourcc, frame_size, size)
                            #we need to make a path for storing the video using datefolder in videos folder
                            #Check the updateddatefolder has a space or not
                            new_time=time.strftime('%H %M %S')
                            #print(new_time)
                            if lastUpdatedDate==" " or lastUpdatedDate!=time.strftime('%d %m %Y'):
                                new_date=time.strftime('%d %m %Y')
                                lastUpdatedDate=new_date
                                path = 'videos/'+new_date
                                #make a directory folder with new date
                                os.makedirs(path)
                            if temp==0:
                                newCounter=int(lastUpdatedCounter)+1
                                temp=1
                            else:
                                newCounter=int(newCounter)+1
                            f= open("last_updated_file_counter_and_date.txt","w+")
                            f.write(str(newCounter))
                            f.write(',')
                            f.write(new_date)
                            f.close()
                            #check the date folder exist in the videos folder or not
                            new_path="videos/"+new_date+"/"+f"{str(newCounter)}.mp4"
                            chunks = cv2.VideoWriter(new_path, fourcc, frame_size, size)
                            outputList=[]
                            innerList=[]
                            while not self.stopped:
                                cv2.imshow("DateTimeNameVideo", self.frame)
                                innerVideoCounter+=1
                                if innerVideoCounter > videoLength:
                                    #Now we want to make a output List
                                    for name in names:
                                        innerList=[]
                                        innerList.append(name)
                                        innerList.append(new_date)
                                        innerList.append(new_time)
                                        innerList.append(new_path)
                                        outputList.append(innerList)
                                    chunks.release()
                                    frame_counter = 1
                                    break
                                chunks.write(self.frame)
                                if cv2.waitKey(1) == ord("q"):
                                    chunks.release()
                                    self.stopped = True
                                    cv2.destroyAllWindows()
                            print(outputList)
                            outputList=[]
                if frame_counter==40:
                    frame_counter = 1
                if cv2.waitKey(1) == ord("q"):
                    self.stopped = True
                    cv2.destroyAllWindows()
        else:
            print("Please add images in the faceImages Folder and also give right path of the face images folder in the images.py file")
    def stop(self):
        self.stopped = True
