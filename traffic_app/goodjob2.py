from flask import Flask, render_template, Response, request
import numpy as np
import cv2
import datetime
import time
import sqlite3
import sys
from centroidtracker import CentroidTracker
from trackableobject import TrackableObject
import argparse
from imutils.video import VideoStream
import imutils
 
app = Flask(__name__)

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
    help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

#opencvdefines
def make_360p():
    cap.set(3, 480)
    cap.set(4, 360)
    
#rescale frame
def rescale_frame(frame):
    percent = 100;
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

#cap = cv2.VideoCapture(0)
 
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
    abreezalabels1 = abreezadates1
    abreezavalues1 = abreezavehicles1
    return render_template('index.html',
                           claveriavalues1=claveriavalues1, claverialabels1=claverialabels1, claveriavalues2=claveriavalues2,
                           abreezavalues1 = abreezavalues1, abreezalabels1 = abreezalabels1,
                           
                           bankevalues1=bankevalues1, bankelabels1=bankelabels1, bankevalues2=bankevalues2,
                           
                           legend1=legend1, legend2=legend2)


@app.route('/videofeed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



 
# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
 
# initialize the video stream and allow the camera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
# loop over the frames from the video stream

    
def gen():
    ct = CentroidTracker()
    (H, W) = (None, None)
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
 
    # if the frame dimensions are None, grab them
    if W is None or H is None:
        (H, W) = frame.shape[:2]
 
    # construct a blob from the frame, pass it through the network,
    # obtain our output predictions, and initialize the list of
    # bounding box rectangles
    blob = cv2.dnn.blobFromImage(frame, 1.0, (W, H),
        (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    rects = []
        # loop over the detections
    for i in range(0, detections.shape[2]):
        # filter out weak detections by ensuring the predicted
        # probability is greater than a minimum threshold
        if detections[0, 0, i, 2] > args["confidence"]:
            # compute the (x, y)-coordinates of the bounding box for
            # the object, then update the bounding box rectangles list
            box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
            rects.append(box.astype("int"))
 
            # draw a bounding box surrounding the object so we can
            # visualize it
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                (0, 255, 0), 2)
                # update our centroid tracker using the computed set of bounding
    # box rectangles
    objects = ct.update(rects)
 
    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
 
    # show the output frame
                
                
                
                
            #cv2.imshow("Contours", frame      
    cv2.imwrite('t.jpg', frame)
    yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)