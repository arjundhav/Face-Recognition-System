import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
from decouple import config  # Importing the function from decouple.py
from sqlDB import insert_record # Importing the function from sqlDbCon.py
import pyodbc
from datetime import datetime

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)   # Listing all the files in that folder
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load encoding file
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds

# Connect to MS SQL Server database
connection_string = (
        'DRIVER=' + config('driver') + ';'
        'SERVER=' + config('server') + ';'
        'DATABASE=' + config('database') + ';'
        'UID=' + config('username') + ';'
        'PWD=' + config('password')
)

connection = pyodbc.connect(connection_string) # Creating a connection
cursor = connection.cursor()    # Creating a cursor

# Initialize modeType and counter
modeType = 0
counter  = 0

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img    #startheight:endheight(start+overallheight)
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[0]
    
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)    #distance
            print(f'Matches {matches} faceDis {faceDis}')

            matchIndex = np.argmin(faceDis)
        #   print("Match Index", matchIndex)
            
            if matches[matchIndex]:
                print(".............. Known Face Detected ...........")
                print("Student ID:",studentIds[matchIndex])
                # Bounding Box Value
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    modeType = 1
                    counter = 1
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
               
        if counter != 0:
            if counter == 1:
                # image_path = f'Images/{id}.png'
                # array = np.frombuffer(image_path, np.uint8)
                # imgBg = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            
                current_time = datetime.now()
                # Check if there is a previous record for the same ID
                cursor.execute("SELECT MAX(time) FROM punchs WHERE id = ?", (id,))
                last_insert_time = cursor.fetchone()[0]

                if last_insert_time:
                    time_difference = current_time - last_insert_time
                    
                    # Check if the time difference is greater than 5 minutes
                    if time_difference.total_seconds() >= 300:
                        insert_record(id)
                        print("Record updated after 5min successfully.")
                        counter = 2
                        modeType = 2
                    else:
                        print("Record not inserted. Time difference is less than 5 minutes.")
                        modeType = 3
                        counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                else:
                    # If there is no previous record, insert the current record
                    insert_record(id)
                    print("Record inserted successfully.")
                    counter = 2
                    modeType = 2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(id), (1006, 493),cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    #imgBackground[175:175 + 216, 909:909 + 216] = imgBg
                counter += 1

                if counter > 20:
                    counter = 0
                    modeType = 0
                    #imgBg = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0
        
     
    cv2.imshow("Face Attendance", imgBackground)   #For viewing Webcam 
    cv2.waitKey(1)    #Waits for 1ms before capturing next frame
