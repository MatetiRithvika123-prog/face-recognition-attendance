import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Ensure the directory exists
path = 'Images_Attendance'
if not os.path.exists(path):
    print(f"Error: The folder '{path}' does not exist. Please create it and add images.")
    exit()

images = []
classNames = []
myList = os.listdir(path)
print("Images found:", myList)

for cl in myList:
    curImg = cv2.imread(os.path.join(path, cl))
    if curImg is not None:
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    else:
        print(f"Warning: Could not read image {cl}")

print("Class Names:", classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("Warning: No face detected in one of the images.")
    return encodeList

def markAttendance(name):
    file_name = 'Attendance.csv'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write("Name,Time,Date\n")
    
    with open(file_name, 'r+') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0] for line in myDataList]
        
        if name not in nameList:
            time_now = datetime.now()
            tString = time_now.strftime('%H:%M:%S')
            dString = time_now.strftime('%d/%m/%Y')
            f.write(f'{name},{tString},{dString}\n')

encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Error:Could not access the webcam.")
else:
    while True:
        success, img = cap.read()
        if not success:
            print("Error: Failed to capture image from webcam.")
            break
        cv2.imshow("Webcam Test",img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame) if facesCurFrame else []

    if encodesCurFrame:  # Only proceed if there are detected faces
       for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if len(faceDis) > 0:  # Ensure faceDis is not empty
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex] and faceDis[matchIndex] < 0.5:  # Confidence threshold
                name = classNames[matchIndex].upper()
                print("Recognized:", name)

                # Draw rectangle around the face
                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                markAttendance(name)
            else:
                print("Unrecognized person")


 
def show_image(img):
    """ Alternative display function using Matplotlib """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

cap.release()
cv2.destroyAllWindows()