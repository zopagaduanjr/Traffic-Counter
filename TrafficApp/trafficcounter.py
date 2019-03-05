import numpy as np
import cv2
import time
import sqlite3
import sys
import argparse
from centroidtracker import CentroidTracker
from trackableobject import TrackableObject

totalFrames = 0
totalDown = 0
totalUp = 0

ct = CentroidTracker()
trackableObjects = {}
cap = cv2.VideoCapture('highway.mp4')
 
# creates a pandas data frame with the number of rows the same length as frame count
#df = pd.DataFrame(index=range(int(frames_count)))
#df.index.name = "Frames"


 
fgbg = cv2.createBackgroundSubtractorMOG2()  # create background subtractor
 
#make 360p
def make_360p():
    cap.set(3, 480)
    cap.set(4, 360)
    
#rescale frame
def rescale_frame(frame):
    percent = 50;
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)


def log_values(carsup, carsdown):
    conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/project/traffic_app.db')  #It is important to provide an
                                 #absolute path to the database
                                 #file, otherwise Cron won't be
                                 #able to find it!
    curs=conn.cursor()
    curs.execute("""INSERT INTO carsup values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?))""", (carsup,))
    curs.execute("""INSERT INTO carsdown values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?))""", (carsdown,))
    conn.commit()
    conn.close()

#main Method
make_360p() #makes dimension 360p

#make_360p()
width, height = cap.get( cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = int(width)
height = int(height)

while True:
    
    _, frame = cap.read()    
    frame = rescale_frame(frame)  #rescales frame by 25%
    #frame = cv2.transpose(frame,frame)
    #frame = cv2.flip(frame, 1)
    #if W is None or H is None:
        #(H, W) = frame.shape[:2]
    rects = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #converts frame to gray
    fgmask = fgbg.apply(gray) #uses the background subtraction
    
    #4 filters to improve opencv background subtraction
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # kernel to apply to the morphology
    closing = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    dilation = cv2.dilate(opening, kernel)
    retvalbin, bins = cv2.threshold(dilation, 220, 255, cv2.THRESH_BINARY)  # removes the shadows
    
    
    # creates contours
    (contours, hierarchy) = cv2.findContours(bins, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #box them contours
    for contour in contours:
        if cv2.contourArea(contour) < 700:
            continue
        (x,y,w,h) = cv2.boundingRect(contour)
        box = (x,y,x+w,y+h)
        rects.append(box)
        cv2.rectangle(frame, (x,y),(x+w,y+h),(240,32,160),3)
        
    lineypos = 200
    cv2.line(frame, (0, lineypos), (width, lineypos), (255, 0, 0), 5)
    objects = ct.update(rects)
    
    for (objectID, centroid) in objects.items():
        # check to see if a trackable object exists for the current
        # object ID
        to = trackableObjects.get(objectID, None)

        # if there is no existing trackable object, create one
        if to is None:
            to = TrackableObject(objectID, centroid)

        # otherwise, there is a trackable object so we can utilize it
        # to determine direction
        else:
            # the difference between the y-coordinate of the *current*
            # centroid and the mean of *previous* centroids will tell
            # us in which direction the object is moving (negative for
            # 'up' and positive for 'down')
            y = [c[1] for c in to.centroids]
            direction = centroid[1] - np.mean(y)
            to.centroids.append(centroid)

            # check to see if the object has been counted or not
            if not to.counted:
                # if the direction is negative (indicating the object
                # is moving up) AND the centroid is above the center
                # line, count the object
                if direction < 0 and centroid[1] < lineypos:
                    totalUp += 1
                    to.counted = True
                    log_values(1,0)

                # if the direction is positive (indicating the object
                # is moving down) AND the centroid is below the
                # center line, count the object
                elif direction > 0 and centroid[1] > lineypos:
                    totalDown += 1
                    to.counted = True
                    log_values(0,1)

        # store the trackable object in our dictionary
        trackableObjects[objectID] = to

        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    # construct a tuple of information we will be displaying on the
    # frame
    info = [
        ("Up", totalUp),
        ("Down", totalDown),
    ]

    # loop over the info tuples and draw them on our frame
    text2 = "Up {}".format(totalUp)
    text3 = "Down {}".format(totalDown)
    cv2.putText(frame, text2, (10,50),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(frame, text3, (10,70),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Contours", frame)
    #cv2.imshow("binary", bins)
    key = cv2.waitKey(1)
    if key == 27:
        break
    
cap.release()
cv2.destroyAllWindows()