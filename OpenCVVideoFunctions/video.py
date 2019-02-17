import numpy as np
import cv2

capture = cv2.VideoCapture('highway.mp4')

while(capture.isOpened()):
    ret, frame = capture.read()
    
    cv2.imshow('frame',frame)
    key = cv2.waitKey(25)
    if key == 27:
        break
capture.release()
cv2.destroyAllWindows()