from flask import Flask, render_template, Response, request
import numpy as np
import cv2
import datetime
import time
import sqlite3
import sys
import argparse
from centroidtracker import CentroidTracker
from trackableobject import TrackableObject

 
app = Flask(__name__)

#opencvdefines
def make_360p():
    cap.set(3, 480)
    cap.set(4, 360)
    
#rescale frame
def rescale_frame(frame):
    percent = 15;
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

#sqlite3defines
def getLastData():
    conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/traffic_app/claveria_count.db')
    curs=conn.cursor()
    for row in curs.execute("SELECT * FROM carsdown ORDER BY rDatetime DESC LIMIT 1"):
        time = str(row[0])
        cars = row[1]
    conn.close()
    return time, cars



def GetHistData(path, tablename):
    conn=sqlite3.connect(path)
    curs = conn.cursor()
    curs.execute("SELECT strftime('%d-%H-%M', rDatetime) AS minutes, sum(vehicles) AS totalcars FROM "+str(tablename)+" GROUP BY minutes ORDER BY minutes")
    result = curs.fetchall()
    dates = []
    vehicles = []
    for row in result:
        dates.append(row[0])
        vehicles.append(row[1])
    conn.close()
    return dates, vehicles


def log_values(carsup, carsdown):
    conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/traffic_app/abreeza_count.db')  #It is important to provide an
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


def TableChecker(table):
    conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/traffic_app/carlog.db')
    res = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    result_items = []
    for name in res:
        result_items.append(name[0])
        #print (name[0])
    if table in result_items:
        conn.close()
        return True
    else:
        query = "CREATE TABLE %s(%s datetime, %s numeric)"
        conn.execute(query % (table,'time',table))
        conn.commit()
        conn.close()

cap = cv2.VideoCapture('highway.mp4')
 
@app.route("/")
def chart():
    bankerohanpath = '/home/pi/Documents/MicroLab/Project/traffic_app/banke_count.db'
    claveriapath = '/home/pi/Documents/MicroLab/Project/traffic_app/claveria_count.db'
    abreezapath = '/home/pi/Documents/MicroLab/Project/traffic_app/abreeza_count.db'
    bankedates1,bankevehicles1 = GetHistData(bankerohanpath, 'carsup')
    bankedates2,bankevehicles2 = GetHistData(bankerohanpath, 'carsdown')
    
    
    legend1 = 'Cars Going Up'
    legend2 = 'Cars Going Down'
    bankelabels1 = bankedates1
    bankevalues1 = bankevehicles1
    bankevalues2 = bankevehicles2
    claveriadates1,claveriavehicles1 = GetHistData(claveriapath,'carsup')
    claveriadates1,claveriavehicles2 = GetHistData(claveriapath,'carsdown')
    claverialabels1 = claveriadates1
    claveriavalues1 = claveriavehicles1
    claveriavalues2 = claveriavehicles2
    abreezadates1, abreezavehicles1 = GetHistData(abreezapath,'carsup')
    abreezadates2, abreezavehicles2 = GetHistData(abreezapath,'carsdown')
    abreezalabels1 = abreezadates1
    abreezavalues1 = abreezavehicles1
    abreezavalues2 = abreezavehicles2
    return render_template('index.html',
                           claveriavalues1=claveriavalues1, claverialabels1=claverialabels1, claveriavalues2=claveriavalues2,
                           abreezavalues1 = abreezavalues1, abreezalabels1 = abreezalabels1, abreezavalues2 = abreezavalues2,
                           
                           bankevalues1=bankevalues1, bankelabels1=bankelabels1, bankevalues2=bankevalues2,
                           
                           legend1=legend1, legend2=legend2)


@app.route('/videofeed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



    
def gen():
    totalFrames = 0
    totalDown = 0
    totalUp = 0   
    ct = CentroidTracker()
    trackableObjects = {}
    fgbg = cv2.createBackgroundSubtractorMOG2()  # create background subtractor
     

    #main Method
    make_360p() #makes dimension 360p


    width, height = cap.get( cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = int(width)
    height = int(height)

    while True:
        
        _, frame = cap.read()
        #frame = cv2.transpose(frame,frame)
        #frame = cv2.flip(frame, 1)
        if(_):
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
                if cv2.contourArea(contour) < 2000:
                    continue
                (x,y,w,h) = cv2.boundingRect(contour)
                box = (x,y,x+w,y+h)
                rects.append(box)
                cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,255),3)
                
            lineypos = 150
            cv2.line(frame, (0, lineypos), (width, lineypos), (255, 0, 0), 5)
            #cv2.line(frame, (0, 0), (255, 255), (255, 0, 0), 5)
            #cv2.line(frame, (lineypos, 0), (lineypos, width), (255, 0, 0), 1)
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
            text2 = "Left {}".format(totalUp)
            text3 = "Right {}".format(totalDown)
            cv2.putText(frame, text2, (10,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, text3, (10,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                
                
                
                
            #cv2.imshow("Contours", frame      
            cv2.imwrite('t.jpg', frame)
            yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

        else:
            cap.release()
            cv2.destroyAllWindows()



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)