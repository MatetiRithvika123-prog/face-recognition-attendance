import cv2

cap = cv2.VideoCapture(0)  # Try changing 0 to 1 or 2 if you have multiple cameras

if not cap.isOpened():
    print("Error: Couldn't access the webcam!")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Webcam", frame)
        cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()
