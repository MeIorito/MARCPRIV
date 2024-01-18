from abc import ABC, abstractmethod
import RPi.GPIO as GPIO
from time import sleep
import threading
import math

# Pin declaration
EMERGENCY = 32 # Emergency Pin

TILTZERO = 22 # Tilt Zero Pin water leveled

DIRTABLE  = 36 # Turntable Pins
STEPTABLE = 33 

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

# Abstract class for the motors to inherit from.
class Motor(ABC):

    def calculateEase(self, step, range):
        sleepTime = (math.cos(math.pi*step/(range/2))+1.1)/40000
        return sleepTime

    def moveMotorUp(self):
        pass

    def moveMotorDown(self):
        pass

# Class for the controlling of tilt motor, inherits from Motor.
class tiltMotor(Motor):

    # Move the Tilthead <distance> steps clockwise; 88 steps/degree.
    def moveMotorUp(self, distance):
        GPIO.output(DIRTILT,CW)
        for _ in range(distance):
            print("In loop")
            if GPIO.input(EMERGENCY) != False:
                break
            GPIO.output(STEPTILT,GPIO.HIGH)
            sleep(TILTSPEEDFAST)
            GPIO.output(STEPTILT,GPIO.LOW)
            sleep(TILTSPEEDFAST)

    # Move the Tilthead <distance> steps counter clockwise; 88 steps/degree.
    def moveMotorDown(self, distance):
        GPIO.output(DIRTILT,CCW)
        for _ in range(distance):
            if GPIO.input(EMERGENCY) != False:
                break
            GPIO.output(STEPTILT,GPIO.HIGH)
            sleep(TILTSPEEDFAST)
            GPIO.output(STEPTILT,GPIO.LOW)
            sleep(TILTSPEEDFAST)

    # Calibrate the Tilthead to the zero position (straight up).
    def calibrateTilthead(self):
        if GPIO.input(TILTZERO) != False:
            while GPIO.input(TILTZERO) != False:
                self.moveMotorUp(1)
                sleep(TILTSPEEDSLOW)
        else:
            while GPIO.input(TILTZERO) == False:
                self.moveMotorDown(1)
                sleep(TILTSPEEDSLOW)
            for _ in range(800):
                self.moveMotorDown(1)
                sleep(TILTSPEEDSLOW)
            while GPIO.input(TILTZERO) != False:
                self.moveMotorUp(1)

# Class for the controlling of lift motor, inherits from Motor.
class heightMotor(Motor):

    # Move the Lift <distance> steps up; 400 steps/cm.
    def moveMotorUp(self, distance):
        GPIO.output(DIRLIFT,CW)
        for x in range(distance):
            if GPIO.input(TOPSWITCH) == False:
                break
            if GPIO.input(EMERGENCY) != False:
                break
            GPIO.output(STEPLIFT,GPIO.HIGH)
            sleep(self.calculateEase(x, distance))
            GPIO.output(STEPLIFT,GPIO.LOW)
            sleep(self.calculateEase(x, distance))

    # Move the Lift <distance> steps down; 400 steps/cm.
    def moveMotorDown(self, distance):
        GPIO.output(DIRLIFT,CCW)
        for x in range(distance):
            if GPIO.input(TOPSWITCH) == False:
                break
            if GPIO.input(EMERGENCY) != False:
                break
            GPIO.output(STEPLIFT,GPIO.HIGH)
            sleep(self.calculateEase(x, distance))
            GPIO.output(STEPLIFT,GPIO.LOW)
            sleep(self.calculateEase(x, distance))

    # Calibrate the Lift to the zero position (bottom).
    def calibrateCameraLift(self):
        print(GPIO.input(BOTSWITCH))
        if GPIO.input(BOTSWITCH) != False:
            while GPIO.input(BOTSWITCH) != False:
                if GPIO.input(EMERGENCY) != False:
                    break
                self.moveMotorDown(1)

# Class for the controlling of turntable motor, inherits from Motor.
class tableMotor(Motor):

    def __init__(self, menuController):
        super().__init__()
        self.mc = menuController

    # Move the Turntable <distance> steps clockwise; 88.888- steps/degree.
    def moveMotorUp(self, distance, waitTime):
        GPIO.output(DIRTABLE,CW)
        for _ in range(distance):
            if GPIO.input(EMERGENCY) != False:
                break
            GPIO.output(STEPTABLE,GPIO.HIGH)
            sleep(waitTime)
            GPIO.output(STEPTABLE,GPIO.LOW)
            sleep(waitTime)

    # Move the Turntable <distance> steps counter clockwise; 88.888- steps/degree.
    def moveMotorDown(self, distance, waitTime):
        GPIO.output(DIRTABLE,CCW)
        for _ in range(distance):
            if GPIO.input(EMERGENCY) != False:
                break
            GPIO.output(STEPTABLE,GPIO.HIGH)
            sleep(waitTime)
            GPIO.output(STEPTABLE,GPIO.LOW)
            sleep(waitTime)

    # Starts scan without stopping for pictures, still takes pictures.
    def fullTurnCycle(self, picsPerKeyframe, speed):
        GPIO.output(FOCUS,  1)
        sleep(1)
        stepsPerKeyframe = int(64000 / picsPerKeyframe)

        for _ in range(picsPerKeyframe):
            if self.mc.firstScreen._MainWindow__emergencyFlag != True:
                for _ in range(stepsPerKeyframe):
                    if GPIO.input(EMERGENCY) != False:
                        print("Emergency triggered")
                        break
                    GPIO.output(STEPTABLE,GPIO.HIGH)
                    sleep(speed)
                    GPIO.output(STEPTABLE,GPIO.LOW)
                    sleep(speed)
                camThread = camera()
                camThread.start()
            else:
                GPIO.output(FOCUS,  0)
                break
        GPIO.output(FOCUS,  0)

# Class for the controlling of camera, inherits from Thread.
class camera(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.captureImage()

    # Capture an image using the 3.5mm jack.
    def captureImage(self):
        GPIO.output(SHUTTER,1)
        sleep(0.2)
        GPIO.output(SHUTTER,0)