import cv2
import face_recognition
import os
import pickle

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print("ImageList: ",pathList)   #image names 
imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
    print("StudentIds: ",studentIds)   #student ID

def image():
    imgPath  = pathList
    imgList.append(cv2.imread(os.path.join(folderPath,imgPath)))
    print(imgPath)

    return imgPath

def findEncodings(imagesList):    
    encodeList = []
    for img in imagesList:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #OpenCV uses BGR so to encode we have to convert it to RGB  as FaceRecognition Lib uses it.  
        try:
            encode = face_recognition.face_encodings(imgRGB)[0]
            encodeList.append(encode)
        except IndexError:
            print(f"Skipping {img} - No face found")

    return encodeList

# print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("Encoded File Saved")
