#   cd /home/pi/Downloads/pi-face-recognition/Lib

import lib
import time 
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24
led  =  25

GPIO.setwarnings(False) 

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(led,GPIO.OUT)

lib.ex('Hello')

while True:
    c = lib.ultra(TRIG,ECHO)
    if c < 5:
        print ("error")
        GPIO.output(led,False)
    else:
        print (c)
        GPIO.output(led,True)