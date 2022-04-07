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
        #local variables
        frame_size=int(40)
        videoLength=int(10)*frame_size #10 seconds long video
        size,frame_counter=(int(1280),int(720)),1 #set your screen size here
        fourcc = cv2.VideoWriter.fourcc(*'MP4V')
        chunks = cv2.VideoWriter(f"videos/{time.strftime('%d %m %Y - %H %M %S')}.mp4", fourcc, frame_size,size)
        i = 0
        while not self.stopped:
            cv2.imshow("DateTimeNameVideo", self.frame)
            i += 1
            if i > videoLength:
                chunks.release()
                chunks = cv2.VideoWriter(f"videos/{time.strftime('%d %m %Y - %H %M %S')}.mp4", fourcc,frame_size, size)
                i = 0
            chunks.write(self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True
                cv2.destroyAllWindows()

    def stop(self):
        self.stopped = True
