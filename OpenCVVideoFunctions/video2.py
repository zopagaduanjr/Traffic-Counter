import numpy as np
import cv2

cap = cv2.VideoCapture('grace.mp4')

def make_480p():
    cap.set(3, 640)
    cap.set(4, 480)

def rescale_frame(frame):
    percent = 25;
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

make_480p()
while (cap.isOpened()):
    ret, frame = cap.read()
    
    frame25 = rescale_frame(frame)
    
    cv2.imshow('frame25', frame25)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()