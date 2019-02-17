import cv2
import numpy as np

cap = cv2.VideoCapture('highway.mp4')

def make_480p():
    cap.set(3, 640)
    cap.set(4, 480)

def rescale_frame(frame):
    percent = 38;
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

make_480p()
_, first_frame = cap.read()
firstframe38 = rescale_frame(first_frame)
while True:
    _, frame = cap.read()    
    frame38 = rescale_frame(frame)
    
    difference = cv2.absdiff(firstframe38, frame38)
    
    cv2.imshow("first frame", firstframe38)
    cv2.imshow('frame38', frame38)
    cv2.imshow("difference", difference)
    key = cv2.waitKey(30)
    if key == 27:
        break
    
cap.release()
cv2.destroyAllWindows()