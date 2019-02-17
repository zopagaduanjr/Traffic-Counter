import cv2
import numpy as np

cap = cv2.VideoCapture('grace4.mp4')

def make_360p():
    cap.set(3, 480)
    cap.set(4, 360)

def rescale_frame(frame):
    percent = 25;
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

subtractor = cv2.createBackgroundSubtractorMOG2()
fps = cap.get(cv2.CAP_PROP_FPS)


make_360p()
while True:
    _, frame = cap.read()    
    frame38 = rescale_frame(frame)
    frame38 = cv2.transpose(frame38,frame38)
    frame38 = cv2.flip(frame38, 1)
    
    mask = subtractor.apply(frame38)
    (contours,_) = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < 190:
            continue
        (x,y,w,h) = cv2.boundingRect(contour)
        cv2.rectangle(frame38, (x,y),(x+w,y+h),(240,32,160),3)
        
        
    
    cv2.imshow("Zal", frame38)
    key = cv2.waitKey(30)
    if key == 27:
        break
    
cap.release()
cv2.destroyAllWindows()