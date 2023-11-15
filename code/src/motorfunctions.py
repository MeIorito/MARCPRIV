import RPi.GPIO as GPIO
import math
from time import sleep

# Pin declaration
EMERGENCY = 32 # Emergency Pin

TILTZERO = 25

DIRTABLE  = 36 # Turntable Pins
STEPTABLE = 33 #

DIRLIFT   = 38 # Lift Pins
STEPLIFT  = 40 #

DIRTILT   = 35 # Tilthead Pins
STEPTILT  = 37 #

TOPSWITCH = 11 # Top limit switch for Lift
BOTSWITCH = 12 # Bottom limit switch for Lift

FOCUS     = 15 # Shutter And Focus for 3.5mm Jack
SHUTTER   = 13 #

# 0/1 used to signify clockwise or counterclockwise.
CW = 1
CCW = 0

# Speed between HIGH and LOW within a step
LIFTSPEED  = 0.00005
TABLESPEED = 0.0005
TILTSPEEDSLOW  = 0.002
TILTSPEEDFAST = 0.001

# Setup pin layout on PI
GPIO.setmode(GPIO.BOARD)

# Establish Pins in software
GPIO.setup(DIRTABLE,  GPIO.OUT)
GPIO.setup(STEPTABLE, GPIO.OUT)
GPIO.setup(DIRLIFT,   GPIO.OUT)
GPIO.setup(STEPLIFT,  GPIO.OUT)
GPIO.setup(DIRTILT,   GPIO.OUT)
GPIO.setup(STEPTILT,  GPIO.OUT)
GPIO.setup(FOCUS,     GPIO.OUT)
GPIO.setup(SHUTTER,   GPIO.OUT)
GPIO.setup(TILTZERO,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TOPSWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BOTSWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(EMERGENCY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set the first direction you want it to spin
GPIO.output(DIRTABLE, CW)
GPIO.output(DIRLIFT,  CW)
GPIO.output(DIRTILT,  CW)


def calibrateTilthead():
    if GPIO.input(TILTZERO) != False:
        while GPIO.input(TILTZERO) != False:
            if GPIO.input(EMERGENCY) != False:
                break
            motorTiltCCW(1)
            sleep(TILTSPEEDSLOW)
    else:
        while GPIO.input(TILTZERO) == False:
            if GPIO.input(EMERGENCY) != False:
                break
            motorTiltCW(20)
            sleep(TILTSPEEDSLOW)
        while GPIO.input(TILTZERO) != False:
            if GPIO.input(EMERGENCY) != False:
                break
            motorTiltCCW(1)
            sleep(TILTSPEEDSLOW)

def calibrateCameraLift():
    if GPIO.input(BOTSWITCH) != False:
        while GPIO.input(BOTSWITCH) != False:
            if GPIO.input(EMERGENCY) != False:
                break
            motorLiftDown(1)
    

def calculateEase(step, range):
    sleepTime = (math.cos(math.pi*step/(range/2))+1.1)/40000
    return sleepTime

# Motor Functions
def motorLiftUp(distance):  # Move the Lift <distance> steps up; 400 steps/cm
    GPIO.output(DIRLIFT,CW)
    for x in range(distance):
        if GPIO.input(TOPSWITCH) == False:
            print("Top switch triggered")
            break
        if GPIO.input(EMERGENCY) != False:
            print("Emergency triggered")
            break
        GPIO.output(STEPLIFT,GPIO.HIGH)
        sleep(calculateEase(x, distance))
        GPIO.output(STEPLIFT,GPIO.LOW)
        sleep(calculateEase(x, distance))

def motorLiftDown(distance): # Move the Lift <distance> steps down; 400 steps/cm
    GPIO.output(DIRLIFT,CCW)
    for x in range(distance):
        if GPIO.input(TOPSWITCH) == False:
            print("Bottom switch triggered")
            break
        if GPIO.input(EMERGENCY) != False:
            print("Emergency triggered")
            break
        GPIO.output(STEPLIFT,GPIO.HIGH)
        sleep(calculateEase(x, distance))
        GPIO.output(STEPLIFT,GPIO.LOW)
        sleep(calculateEase(x, distance))

def motorTableCW(distance, waitTime): # Move the Turntable <distance> steps clockwise; 88.888- steps/degree
    GPIO.output(DIRTABLE,CW)
    for x in range(distance):
        if GPIO.input(EMERGENCY) != False:
            print("Emergency triggered")
            break
        GPIO.output(STEPTABLE,GPIO.HIGH)
        sleep(waitTime)
        GPIO.output(STEPTABLE,GPIO.LOW)
        sleep(waitTime)

def motorTableCCW(distance): # Move the Turntable <distance> steps counter clockwise; 88.888- steps/degree
    GPIO.output(DIRTABLE,CCW)
    for x in range(distance):
        if GPIO.input(EMERGENCY) != False:
            print("Emergency triggered")
            break
        GPIO.output(STEPTABLE,GPIO.HIGH)
        sleep(TABLESPEED)
        GPIO.output(STEPTABLE,GPIO.LOW)
        sleep(TABLESPEED)

def motorTiltCW(distance): # Move the Tilthead <distance> steps clockwise; 88 steps/degree
    GPIO.output(DIRTILT,CW)
    for x in range(distance):
        if GPIO.input(EMERGENCY) != False:
            print("Emergency triggered")
            break
        GPIO.output(STEPTILT,GPIO.HIGH)
        sleep(TILTSPEEDFAST)
        GPIO.output(STEPTILT,GPIO.LOW)
        sleep(TILTSPEEDFAST)

def motorTiltCCW(distance): # Move the Tilthead <distance> steps counter clockwise; 88 steps/degree
    GPIO.output(DIRTILT,CCW)
    for x in range(distance):
        if GPIO.input(EMERGENCY) != False:
            print("Emergency triggered")
            break
        GPIO.output(STEPTILT,GPIO.HIGH)
        sleep(TILTSPEEDFAST)
        GPIO.output(STEPTILT,GPIO.LOW)
        sleep(TILTSPEEDFAST)

def captureImage():
    GPIO.output(FOCUS,  1)
    sleep(1)
    GPIO.output(SHUTTER,1)
    sleep(2)
    GPIO.output(FOCUS,  0)
    GPIO.output(SHUTTER,0)
