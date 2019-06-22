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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

## Get Ip and send to email
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('google.com',0))
ipAdress = s.getsockname()[0]
s.close()
to = 'baopq.spkt@gmail.com'
fromemail = 'baopq.spkt@gmail.com'
your_pass = "bao0985265185"
body = "User: pi\n" + "Password: raspberry\n" + "Your Ip connect to network: " + str(ipAdress)
subject = "Information Camera System"
message = MIMEMultipart()
message['From'] = fromemail
message['To'] = to
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))
text = message.as_string()
mail = smtplib.SMTP('smtp.gmail.com', 587)
mail.ehlo()
mail.starttls()
mail.login(fromemail,your_pass)
mail.sendmail(fromemail,to,text)
mail.close()

now = datetime.now()
formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

TRIG = 23
ECHO = 24
led  =  25
space = 22

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(led,GPIO.OUT)
GPIO.setup(space,GPIO.OUT)

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
def commitdata(name,formatted_date):
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
        #print ("Commit Done")
    except mysql.connector.Error as error :
        connection.rollback() #rollback if any exception occured
        #print ("Commit Error {}".format(error))
    finally:
        #closing database connection.
        if(connection.is_connected()):
            cursor.close()
            connection.close()

# Declare Path
def pathinfor(dev):
    fulldir = "/media/pi/"+dev
    return fulldir

def deletefolder(fulldir,folder1,folder2):
    disk = os.statvfs(fulldir)
    totalAvailSpace = float(disk.f_bsize*disk.f_bfree)
    if (totalAvailSpace < 500):
        GPIO.output(space,True)
    else : 
        GPIO.output(space,False)
    if (totalAvailSpace < 100):
        shutil.rmtree(folder1)
        shutil.rmtree(folder2)
        # re-make folder after delete
        if not os.path.isdir(folder1):
                        os.makedirs(folder1)
        if not os.path.isdir(folder2):
                        os.makedirs(folder2)
        print("Delete Done")
    else:
        print ("Not Delete Because Have More Space")
    
def movefile(pathimagelocal,pathimageusb,pathvideolocal,pathvideousb):
    shutil.move(pathimagelocal,pathimageusb)
    shutil.move(pathvideolocal,pathvideousb)
    
def checkusb(pathimagelocal,pathvideolocal):
    Name = os.listdir("/media/pi/")
    if (len(Name) > 0):
        pathimageusb = pathinfor(str(Name[0])) + "/Image"
        if not os.path.isdir(pathimageusb):
                        os.makedirs(pathimageusb)
        pathvideousb = pathinfor(str(Name[0])) + "/Video"
        if not os.path.isdir(pathvideousb):
                        os.makedirs(pathvideousb)
        deletefolder(pathinfor(str(Name[0])),pathimageusb,pathvideousb)
        movefile(pathimagelocal,pathimageusb,pathvideolocal,pathvideousb)
    else :
        print("Don't Have USB")

data = pickle.loads(open("/home/pi/Desktop/code-on-rasp/encoding.pickle", "rb").read())
detector = cv2.CascadeClassifier("/home/pi/Desktop/code-on-rasp/haarcascade_frontalface_default.xml")

vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=True).start()


time.sleep(2.0)
now = datetime.now()
date = now.day
dateold = date+1

Name = os.listdir("/media/pi/")
mypath = pathinfor(str(Name[0]))

# loop over frames from the video file stream
while True:
    while date != dateold:
        GPIO.output(TRIG,False)
        distance =  ultra(TRIG,ECHO)
        print(distance)
        now = datetime.now()
        minute = now.minute
        hour = now.hour
        date = now.day
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
                    pathimagelocal = "/home/pi/Desktop/code-on-rasp/Nguoila"
                    pathimagelocalarg = pathimagelocal
                    pathimagelocal= pathimagelocal + '/' + str(year) + '-' + str(month) + '-' + str(date) + '/'
                    if not os.path.isdir(pathimagelocal):
                        os.makedirs(pathimagelocal)
                    frame = vs.read()
                    cv2.imwrite(pathimagelocal + str(hour) + '-' + str(minute) + '-' + '.jpg',frame)
                    break
                else:
                    commitdata(name,formatted_date)
                    GPIO.output(TRIG,True)
                    time.sleep(5)
                    GPIO.output(TRIG,False)
                    break
        pathvideolocal = "/home/pi/Desktop/code-on-rasp/output" 
        pathvideolocalarg = pathvideolocal
        pathvideolocal = pathvideolocal + '/' + str(date) + '-' + str(month) + '-' + str(year) 
        if not os.path.isdir(pathvideolocal):
            os.makedirs(pathvideolocal)
        pathvideolocal = pathvideolocal + "/home.avi"
        if writer is None and pathvideolocal is not None:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writer = cv2.VideoWriter(pathvideolocal, fourcc, 5.0 ,
                (frame.shape[1],frame.shape[0]), True)
        if writer is not None:
            writer.write(frame)
        cv2.imshow("Frame", frame)
        
    checkusb(pathimagelocalarg,pathvideolocalarg)
    dateold = date + 1
cv2.destroyAllWindows()
vs.stop()   
#Move file Video to USB
#pathvideousb = "/media/pi/KINGSTON/Video/output"
#Delete file before copy to usb
#shutil.rmtree(pathvideousb) 
#shutil.move("/home/pi/Downloads/pi-face-recognition/output","/media/pi/KINGSTON/Video")
#shutil.move("/home/pi/Downloads/pi-face-recognition/Nguoila","/media/pi/KINGSTON/Nguoila")
#check to see if the video writer point needs to be release
if writer is not None:
    writer.release() 