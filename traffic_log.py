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
def TablePrinter():
    conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/traffic_app/carlog.db')
    res = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    result_items = []
    for name in res:
        result_items.append(name[0])
        print (name[0])
    conn.close()

def GetHistData():
    conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/project/traffic_app.db')
    curs = conn.cursor()
    curs.execute("SELECT strftime('%d-%H-%M', rDatetime) AS minutes, sum(vehicles) AS totalcars FROM carsup GROUP BY minutes ORDER BY minutes")
    result = curs.fetchall()
    dates = []
    vehicles = []
    for row in reversed(result):
        dates.append(row[0])
        vehicles.append(row[1])
    conn.close()
    return dates, vehicles
    
# If you don't have a sensor but still wish to run this program, comment out all the 
# sensor related lines, and uncomment the following lines (these will produce random
# numbers for the temperature and humidity variables):
#import random
#humidity = random.randint(1,100)
#temperature = random.randint(10,30)
count = 1
if count is not None:
    #conn=sqlite3.connect('/home/pi/Documents/MicroLab/Project/project/traffic_app.db')
    #curs = conn.cursor()
    #curs.execute("SELECT strftime('%d-%H-%M', rDatetime) AS minutes, sum(vehicles) AS totalcars FROM carsup GROUP BY minutes ORDER BY minutes")
    #result = curs.fetchall()
    date, car = GetHistData()
    print(car[1])
    #curs.execute("select sum(vehicles) from carsup;")
    #result = curs.fetchall()
    #print(result)
    #conn.close()

    #return render_template("lab_env_db.html",temp=temperatures,hum=humidities)
    #return render_template("index.html")
