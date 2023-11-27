import json
import time
import slack
import random
import threading
from constants import constants
from controllers import motorfunctions
from time import sleep


class cycleThread(threading.Thread):
    # Messages for the slack bot to send (Can delete and customize) chatGPT generated.
    __marcMessages = [
        "Scan completed! Time for the big reveal.",
        "Ta-da! The 3D scan is ready for inspection.",
        "Mission accomplished! What do you think of the result?",
        "Good news! The scan is ready to view.",
        "Bing! The scan is complete. Let's see what I've captured.",
        "Scanning is finished. Curious about the final result?",
        "Ready to see what I've created? The scan is complete!",
        "The wait is over! Quickly view the 3D images.",
        "MARC has worked its magic again. The result is here!",
        "The 3D scan is ready. What do you think of it?",
    ]

    # Constructor, needs the wait times, pictures per keyframe and rotations for the cycle.
    def __init__(self, menuController, waitBeforeTime, waitAfterTime, picsPerKeyframe):
        threading.Thread.__init__(self)
        self.mc = menuController
        self.__beforeWaitTime = waitBeforeTime
        self.__afterWaitTime = waitAfterTime
        self.__picsPerKeyframe = picsPerKeyframe
        self.__turntableSpeed = self.mc.fifthScreen.turntableSpeed
        self.__degreesPerRotation = int(64000 / self.__picsPerKeyframe)

    def sendSlackMessage(self, text):
        try:
            client = slack.WebClient(token=constants.slackToken)
            client.chat_postMessage(channel=constants.slackChannel, text=text)
        except:
            print("Oops! Something went wrong with the connection to Slack!")

    # Capture cycle. Takes a picture, rotates the table and repeats.
    def run(self):
        with open(constants.cycleCounterFile, "r") as jsonFile:
            cycleCounter = json.load(jsonFile)

        # Checks if the cycle limit has been reached, after 200 cycles the motors need to be readjusted
        if cycleCounter["CycleCounter"] <= 200:
            self.mc.firstScreen.setCycleState(True)
            startTime = time.time()

            # Total amount of keyframes
            totKeyframes = self.mc.secondScreen.keyframeTable.rowCount()
           
            with open(constants.settingsFile, "r") as jsonFile:
                keyframesData = json.load(jsonFile)

            # Loops through all keyframes and moves the height and tilt accordingly. Also checks regurelally for emergency stop
            for i in range(1, totKeyframes + 1):
                if self.mc.firstScreen.getEmercenyFlag() != True:
                    if keyframesData is not None:
                        if self.mc.firstScreen.getEmercenyFlag() != True:

                            self.mc.firstScreen.moveToPosition(
                                keyframesData[f"Keyframe {i}"]["liftHeight"]
                            )
                            self.mc.firstScreen.angleToPosition(
                                keyframesData[f"Keyframe {i}"]["tiltDegree"]
                            )
                           
                            # Set slider and variables to height of current keyframe
                            self.mc.firstScreen.setSliderVal(keyframesData[f"Keyframe {i}"]["liftHeight"])
                            self.mc.firstScreen.setTiltLabelVal(keyframesData[f"Keyframe {i}"]["tiltDegree"])

                            for _ in range(self.__picsPerKeyframe):
                                if not self.mc.firstScreen.getEmercenyFlag():
                                    sleep(self.__beforeWaitTime)
                                    motorfunctions.captureImage()
                                    sleep(self.__afterWaitTime)
                                    motorfunctions.motorTableCW(self.__degreesPerRotation, self.__turntableSpeed)
                                else:
                                    text = "The emergency button has been pressed!"
                                    break
                        else:
                            break
               
                        text = (
                            str(random.choice(self.__marcMessages))
                            + " It took: "
                            + str(round(time.time() - startTime, 2))
                            + " seconds"
                        )
                else:
                    text = "The emergency button has been pressed!"
                    break
                self.sendSlackMessage(f'Keyframe {i} is done! Keyframes to go: {totKeyframes - i}')

            # Sends message to Slack workspace
            self.sendSlackMessage(text)

            # Updates busy flag
            self.mc.firstScreen.setCycleState(False)
            cycleCounter["CycleCounter"] += 1
           
            # Resets the motors and the counter
            self.mc.firstScreen.reset()
           
            # Write the updated dictionary to the JSON file
            with open(constants.cycleCounterFile, "w") as jsonFile:
                json.dump(cycleCounter, jsonFile)
           
        else:
            text = "The cycle limit has been reached! Readjust the motors and reset the counter!"

            # Sends message to Slack workspace
            self.sendSlackMessage(text)
