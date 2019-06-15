import RPi.GPIO as GPIO
import time 

GPIO.setmode(GPIO.BCM)

def ex(data):
	print(data)
def plus(a,b):
	return a+b
def ultra(TRIG,ECHO):
	GPIO.output(TRIG, False)
	time.sleep(2)
	
	GPIO.output(TRIG,True)
	time.sleep(0.00001)
	GPIO.output(TRIG,False)
    pulse_start = 0
    pulse_end = 0
	while GPIO.input(ECHO) == 0:
		pulse_start = time.time()
		
	while GPIO.input(ECHO) == 1:
		pulse_end = time.time()
	
	pulse_duration = pulse_end - pulse_start
	
	distance = pulse_duration * 17150
	distance = round(distance,2)
	
	return distance
	
def lamp(hour,load):
	if hour > 18 or hour < 6:
		GPIO.output(load,True)
	else:
		GPIO.output(load,False)

def move(path):
	shutil.rmtree(path)

def keyinit():
	KEYPAD = [
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]
	]
	ROW_PINS = [4, 14, 15, 17] # BCM numbering
	COL_PINS = [18, 27, 22, 23] # BCM numbering
	factory = rpi_gpio.KeypadFactory()
	keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
	