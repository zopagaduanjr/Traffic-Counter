import sqlite3
import sys

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

# If you don't have a sensor but still wish to run this program, comment out all the 
# sensor related lines, and uncomment the following lines (these will produce random
# numbers for the temperature and humidity variables):
#import random
#humidity = random.randint(1,100)
#temperature = random.randint(10,30)
count = 1
if count is not None:
    log_values(0,1)
