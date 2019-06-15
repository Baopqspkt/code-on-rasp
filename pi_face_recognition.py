# USAGE
# python3 pi_face_recognition.py 

# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import imutils
import pickle
import os
import time
import cv2
from datetime import datetime
import shutil
import RPi.GPIO as GPIO
import socket 
import smtplib
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('google.com',0))
ipAdress = s.getsockname()[0]
s.close()

content = ipAdress
mail = smtplib.SMTP('smtp.gmail.com',587)
mail.ehlo()
mail.starttls()
mail.login('baopq.spkt@gmail.com','bao0985265185')
mail.sendmail('baopq.spkt@gmail.com','baopq.spkt@gmail.com',content)
mail.close()

now = datetime.now()
formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

TRIG = 23
ECHO = 24
led  =  25

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(led,GPIO.OUT)

continu = 1
SampleNum=0
writer = None
pulse_start = 0
pulse_end = 0;

# Decleare information about ultra 
def ultra(TRIG,ECHO):
    global pulse_start
    global pulse_end
    GPIO.output(TRIG, False)
    time.sleep(2)
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance,2)
    return distance

# Decleare information about mysql and python 
def commitdata(name):
    try:
        connection = mysql.connector.connect(host = "103.95.197.126",
        user = "baopqspkt",
        passwd = "bao0985265185",
        database = "baopqspk_control")
        sql_insert_query = """ INSERT INTO `Door`
                          (`Day`,`Name`) VALUES (%s,%s)"""
        cursor = connection.cursor()
        result  = cursor.execute(sql_insert_query,(formatted_date,name))
        connection.commit()
    except mysql.connector.Error as error :
        connection.rollback() #rollback if any exception occured
    finally:
        #closing database connection.
        if(connection.is_connected()):
            cursor.close()
            connection.close()



data = pickle.loads(open("/home/pi/Downloads/pi-face-recognition/encodings.pickle", "rb").read())
detector = cv2.CascadeClassifier("/home/pi/Downloads/pi-face-recognition/haarcascade_frontalface_default.xml")

vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=True).start()


time.sleep(2.0)
now = datetime.now()
minute = now.minute
minuteold = now.minute+10
# loop over frames from the video file stream
while minute != minuteold:
    GPIO.output(TRIG,False)
    distance =  ultra(TRIG,ECHO)
    print(distance)
    now = datetime.now()
    minute = now.minute
    hour = now.hour
    day = now.day
    month = now.month
    year = now.year
    frame = vs.read()
    frame = imutils.resize(frame, width = 600)
    if (distance > 50) and (distance < 100):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=2, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"],
                encoding)
            name = "Unknown"
            # check to see if we have found a match
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
            names.append(name)
            print(name)
            if (name == "Unknown"):
                print("Unknown")
                mypath='/home/pi/Downloads/pi-face-recognition/Nguoila/' + str(year) + '-' + str(month) + '-' + str(day) + '/'
                if not os.path.isdir(mypath):
                    os.makedirs(mypath)
                frame = vs.read()
                cv2.imwrite(mypath + str(hour) + '-' + str(minute) + '-' + '.jpg',frame)
                break
            else:
                commitdata(name)
                GPIO.output(TRIG,True)
                time.sleep(5)
                GPIO.output(TRIG,False)
                break
    pathvideo = "/home/pi/Downloads/pi-face-recognition/output/" 
    pathvideo = pathvideo + str(day) + '-' + str(month) + '-' + str(year) 
    if not os.path.isdir(pathvideo):
        os.makedirs(pathvideo)
    pathvideo = pathvideo + "/home.avi"
    if writer is None and pathvideo is not None:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(pathvideo, fourcc, 5.0 ,
            (frame.shape[1],frame.shape[0]), True)
    if writer is not None:
        writer.write(frame)
    cv2.imshow("Frame", frame)
cv2.destroyAllWindows()
vs.stop()   
#Move file Video to USB
pathvideousb = "/media/pi/KINGSTON/Video/output"
#Delete file before copy to usb
shutil.rmtree(pathvideousb) 
shutil.move("/home/pi/Downloads/pi-face-recognition/output","/media/pi/KINGSTON/Video")
shutil.move("/home/pi/Downloads/pi-face-recognition/Nguoila","/media/pi/KINGSTON/Nguoila")
#check to see if the video writer point needs to be release
if writer is not None:
    writer.release() 