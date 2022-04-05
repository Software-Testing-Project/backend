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

    def readFile(self):
        f= open("last_updated_file_counter_and_date.txt","r+")
        contents=f.read()
        x = contents.split(",")
        f.close()
        return x

    def videoStart(self,new_date,newCounter,fourcc,frame_size,size,videoLength,names,new_time):
        innerVideoCounter=1
        flag1=flag2=flag3=False
        innerFrameCounter=0
        flagcounter=0
        length=0
        new_path="videos/"+new_date+"/"+f"{str(newCounter)}.mp4"
        chunks = cv2.VideoWriter(new_path, fourcc, frame_size, size)
        outputList=[]
        innerList=[]
        while not self.stopped:
            cv2.imshow("DateTimeNameVideo", self.frame)
            #print('inner frame counter: ',innerFrameCounter)
            innerFrameCounter+=1
            innerVideoCounter+=1
            if innerFrameCounter==10 or innerFrameCounter==25 or innerFrameCounter==35:
                face_locations = face_recognition.face_locations(self.frame)
                length=len(face_locations)
                if length!=0 and innerFrameCounter==10:
                    flag1=True
                    flagcounter+=1
                if length!=0 and innerFrameCounter==25:
                    flag2=True
                    flagcounter+=1
                if length!=0 and innerFrameCounter==35:
                    flag3=True
                    flagcounter+=1    
            if length!=0 and names[0]=='null':
                print('A face is detected but not recognized yet in an empty room')
                for name in names:
                    innerList=[]
                    innerList.append(name)
                    innerList.append(new_date)
                    innerList.append(new_time)
                    innerList.append(new_path)
                    outputList.append(innerList)
                chunks.release()
                break
            if length==0 and names[0]!='null' and flagcounter>1:
                print('A face is not detected anymore, while the video started when a human got detected')
                for name in names:
                    innerList=[]
                    innerList.append(name)
                    innerList.append(new_date)
                    innerList.append(new_time)
                    innerList.append(new_path)
                    outputList.append(innerList)
                chunks.release()
                break
            if innerVideoCounter > videoLength:
                for name in names:
                    innerList=[]
                    innerList.append(name)
                    innerList.append(new_date)
                    innerList.append(new_time)
                    innerList.append(new_path)
                    outputList.append(innerList)
                chunks.release()
                break
            if innerFrameCounter==40:
                innerFrameCounter = 1
            chunks.write(self.frame)
            if cv2.waitKey(1) == ord("q"):
                chunks.release()
                self.stopped = True
                cv2.destroyAllWindows()
        return outputList

    def show(self):
        #local variables
        temp=0
        frame_size=int(40)
        videoLength=int(10)*frame_size 
        size,frame_counter=(int(1280),int(720)),1
        fourcc = cv2.VideoWriter.fourcc(*'MP4V')
        flagFaceFound=False

        #reading a file
        x=self.readFile()
        lastUpdatedCounter=int(x[0])
        lastUpdatedDate=str(x[1])


        #capturing frames until not stopped
        while not self.stopped:
            #reading images to be recognized and also the associated functionalities
            imgObj=images()
            knownFaceEncodings=imgObj.getKnownFaceEncodings()
            knownFaceNames=imgObj.getNames()
            #print('known faces: ',knownFaceNames)
            cv2.imshow("DateTimeNameVideo", self.frame)
            #print('framecounteroutside: ',frame_counter)
            frame_counter+=1
            flagFaceFound=False
            if frame_counter==3 or frame_counter==24 or frame_counter==39: 
                face_locations = face_recognition.face_locations(self.frame)
                length=len(face_locations)
                #start
                names = []
                if length!=0:
                    face_encodings = face_recognition.face_encodings(self.frame, face_locations)
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(knownFaceEncodings, face_encoding, tolerance=0.6)
                    index=0
                    for match in matches:
                      if match == True:
                          names.append(knownFaceNames[index])
                          flagFaceFound=True
                      index+=1
                    if flagFaceFound: 
                        print("Video making started when a human got recognized")
                        new_time=time.strftime('%H %M %S')
                        new_date=lastUpdatedDate
                        if lastUpdatedDate==" " or lastUpdatedDate!=time.strftime('%d %m %Y'):
                            new_date=time.strftime('%d %m %Y')
                            lastUpdatedDate=new_date
                            path = 'videos/'+new_date
                            os.makedirs(path)
                        if temp==0:
                            newCounter=int(lastUpdatedCounter)+1
                            temp=1
                        else:
                            newCounter=int(newCounter)+1
                        #write to file the updated values
                        fout= open("last_updated_file_counter_and_date.txt","w+")
                        fout.write(str(newCounter))
                        fout.write(',')
                        print(new_date)
                        fout.write(new_date)
                        fout.close()
                        #start making video
                        outputList=self.videoStart(new_date,newCounter,fourcc,frame_size,size,videoLength,names,new_time)
                        print(outputList)
                        outputList=[]
                        frame_counter = 1
                elif flagFaceFound==False and frame_counter==39:
                    print('Video making started when no face found')
                    new_time=time.strftime('%H %M %S')
                    new_date=lastUpdatedDate
                    if lastUpdatedDate==" " or lastUpdatedDate!=time.strftime('%d %m %Y'):
                        new_date=time.strftime('%d %m %Y')
                        lastUpdatedDate=new_date
                        path = 'videos/'+new_date
                        os.makedirs(path)
                    if temp==0:
                        newCounter=int(lastUpdatedCounter)+1
                        temp=1
                    else:
                        newCounter=int(newCounter)+1
                    #write to file the updated values
                    fout= open("last_updated_file_counter_and_date.txt","w+")
                    fout.write(str(newCounter))
                    fout.write(',')
                    print(new_date)
                    fout.write(new_date)
                    fout.close()
                    names=['null']
                    #start making video
                    outputList=self.videoStart(new_date,newCounter,fourcc,frame_size,size,videoLength,names,new_time)
                    print(outputList)
                    outputList=[]
                    frame_counter = 1
            if frame_counter==40:
                frame_counter = 1
            #end
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True
                cv2.destroyAllWindows()

    def stop(self):
        self.stopped = True

