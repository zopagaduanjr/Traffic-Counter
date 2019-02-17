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


firstgray38 = cv2.cvtColor(firstframe38, cv2.COLOR_BGR2GRAY)
firstgray38 = cv2.GaussianBlur(firstgray38,(5,5),0)

while True:
    _, frame = cap.read()    
    frame38 = rescale_frame(frame)
    gray38 = cv2.cvtColor(frame38, cv2.COLOR_BGR2GRAY)
    gray38 = cv2.GaussianBlur(gray38,(5,5),0)
    
    
    difference = cv2.absdiff(firstgray38, gray38)
    _, difference = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)

    cv2.imshow("difference", difference)
    key = cv2.waitKey(30)
    if key == 27:
        break
    
cap.release()
cv2.destroyAllWindows()