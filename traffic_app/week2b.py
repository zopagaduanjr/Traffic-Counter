from flask import Flask, render_template, Response
import requests
import numpy as np
import cv2
import time
import argparse
from centroidtracker import CentroidTracker

app = Flask(__name__)


 
# creates a pandas data frame with the number of rows the same length as frame count
#df = pd.DataFrame(index=range(int(frames_count)))
#df.index.name = "Frames"


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

cap = cv2.VideoCapture("highway.mp4")
@app.route('/')
def hello():
    """Video streaming home page."""
    return render_template('hello.html')

@app.route('/sabta')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    ct = CentroidTracker()
    framenumber = 0  # keeps track of current frame
    carscrossedup = 0  # keeps track of cars that crossed up
    carscrosseddown = 0  # keeps track of cars that crossed down
    carids = []  # blank list to add car ids
    caridscrossed = []  # blank list to add car ids that have crossed
    totalcars = 0  # keeps track of total cars
     
    fgbg = cv2.createBackgroundSubtractorMOG2()  # create background subtractor
     

    #main Method
    make_360p() #makes dimension 360p


    width, height = cap.get( cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = int(width)
    height = int(height)

    while True:
        
        #img_resp = requests.get()
        #img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        #img = cv2.imdecode(img_arr, -1)
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
            
        objects = ct.update(rects)
        
        for (objectID, centroid) in objects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(objectID)
            cv2.putText(frame, text, (centroid[0] + 50, centroid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
        #cv2.imshow("Contours", frame)
        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
