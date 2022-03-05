
import face_recognition
import glob
from pathlib import Path

class images:
    __namesList = []
    __addedImages= []
    __knownFaceEncodings = []
    def __init__(self,addedImages=None,namesList=None,knownfaceEncondings=None):
        self.addedImages=addedImages
        self.namesList=namesList
        self.knownFaceEncodings=knownfaceEncondings
        self.setImagesData()
    def checkImagesLength(self):
        return len(self.namesList)

    def setImagesData(self):
        listImages=[]
        names=[]
        knownEncodings=[]
        
        rootpath = "/home/ria/Desktop/fyp_server/faceImages" #define your root path here
        for filePath in glob.iglob(rootpath + '**/*.JPG', recursive=True): #It will dynamically read all the files            
            listImages.append(face_recognition.load_image_file(filePath))
            names.append(Path(filePath).stem)
        self.addedImages=listImages

        self.namesList=names

        for image in self.addedImages:
            knownEncodings.append(face_recognition.face_encodings(image)[0])
        self.knownFaceEncodings=knownEncodings

    def getNames(self):
        return self.namesList

    def getKnownFaceEncodings(self):
        return self.knownFaceEncodings

    def getAddedFaces(self):
        return self.addedImages
