import sys
import json
import time
import math
import slack
import random
import threading
from factory import *
from time import sleep
import RPi.GPIO as GPIO
from PyQt5 import QtCore
from PyQt5.QtCore import *
from motorfunctions import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QSlider

# Constants | slack auth | settings file | cycleCounterFile | slack channel name  | font size | button size
slackToken = "xoxb-5867825218247-5875744156982-TuLlFjvAptQvxyraY4ZQ4Vm6"
settingsFile = "settingsCustom.txt"
cycleCounterFile = "cycleCounter.txt"
slackChannel = "testbot"
font = QFont()
font.setPointSize(11)
size = (100, 80)
turntableSpeeds = [0.002, 0.0005, 0.0002]

objDistance = 43  # Distance between object and camera in cm, used for tilt calculations
totHeight = 180  # Total height of the lift
conversionValue = 72000 / totHeight  # Steps per cm

# 6 standard styles for all types of used widgets, format like css
buttonStyle = """
    QPushButton {
        background-color: #505164; /* Background color */
        border: 4px solid #585a6e; /* Border color */
        color: #dddde4; /* Text color */
        padding: 8px 16px; /* Padding around the text */
        border-radius: 15px; /* Rounded corners */
        font-size: 21px; /* Font size */
        font-weight: bold; /* Font weight */
    }

    QPushButton:hover {
        background-color: #585a6e; /* Hover background color */
        border: 4px solid #585a6e; /* Hover border color */
    }

    QPushButton:pressed {
        background-color: #790004; /* Pressed background color */
        border: 4px solid #790004;
    }
    """


emergencyButtonOffStyle = """
        QPushButton {
        background-color : #790004; /* Different background color */
        border : 4px solid #790004;
        color: #dddde4; /* Text color */
        padding: 8px 16px; /* Padding around the text */
        border-radius: 15px; /* Rounded corners */
        font-size: 18px; /* Font size */
        font-weight: bold; /* Font weight */
    }
"""


emergencyButtonOnStyle = """
        QPushButton {
        background-color : #d80006; /* Different background color */
        border : 4px solid #d80006;
        color: #dddde4; /* Text color */
        padding: 8px 16px; /* Padding around the text */
        border-radius: 15px; /* Rounded corners */
        font-size: 18px; /* Font size */
        font-weight: bold; /* Font weight */
    }
"""


labelStyle = """
QLabel {
    color: #dddde4; /* Text color */
    font-size: 16px; /* Font size */
    font-weight: bold; /* Font weight */
}
"""


lineEditStyle = """
QLineEdit {
    background-color: #505164; /* Background color */
    border: 4px solid #585a6e; /* Border color */
    border-radius: 8px; /* Rounded corners */
    padding: 4px 8px; /* Padding inside the line edit */
    font-size: 14px; /* Font size */
    color: #dddde4; /* Text color */
}

QLineEdit:focus {
    border-color: #790004; /* Border color on focus */
}
"""


tableStyle = """
    QTableWidget {
        background-color: #505164; /* Background color for the entire table */
        border: none; /* Remove table border */
        border-radius: 10px; /* Rounded corners */
    }

    QHeaderView::section {
        background-color: #585a6e; /* Header background color */
        color: #dddde4; /* Header text color */
        font-size: 14px; /* Header font size */
        font-weight: bold; /* Header font weight */
        padding: 8px; /* Header section padding */
        border: none; /* Remove header border */
    }

    QTableWidget::item {
        background-color: #343541; /* Entry background color */
        color: #dddde4; /* Entry text color */
        font-size: 14px; /* Entry font size */
        border-bottom: 1px solid #585a6e; /* Item border color */
        padding: 8px; /* Entry padding */
        border-radius: 0px; /* Remove rounded corners */
    }

    QTableWidget::item:selected {
        background-color: #585a6e; /* Selected item background color */
        color: #dddde4; /* Selected item text color */
    }

    QTableCornerButton::section {
        background-color: #585a6e; /* Corner button background color */
}
    """


sliderStylesheet = """
    QSlider {
        border: 4px solid #505164;
        border-radius: 15px;
        background: #505164;
    }

    QSlider::groove:vertical {
        background: #505164;
        border: 4px solid #505164;
        border-radius: 15px;
    }

    QSlider::handle:vertical {
        background: #0078d7;
        border: 1px solid #0078d7;
        height: 30px; /* Increase the height to make it bigger */
        margin: -8px 0;
        border-radius: 9px;
    }
    """


tableSliderStyle = "QScrollBar:vertical { width: 35px; }"


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
    def __init__(self, waitBeforeTime, waitAfterTime, picsPerKeyframe):
        threading.Thread.__init__(self)
        self.__beforeWaitTime = waitBeforeTime
        self.__afterWaitTime = waitAfterTime
        self.__picsPerKeyframe = picsPerKeyframe
        self.__turntableSpeed = sixthScreen.turntableSpeed
        self.__degreesPerRotation = int(64000 / self.__picsPerKeyframe)

    def sendSlackMessage(self, text):
        try:
            client = slack.WebClient(token=slackToken)
            client.chat_postMessage(channel=slackChannel, text=text)
        except:
            print("Oops! Something went wrong with the connection to Slack!")

    # Capture cycle. Takes a picture, rotates the table and repeats.
    def run(self):
        with open(cycleCounterFile, "r") as jsonFile:
            cycleCounter = json.load(jsonFile)

        # Checks if the cycle limit has been reached, after 200 cycles the motors need to be readjusted
        if cycleCounter["CycleCounter"] <= 200:
            firstScreen.setCycleState(True)
            startTime = time.time()

            # Total amount of keyframes
            totKeyframes = secondScreen.keyframeTable.rowCount()
           
            with open(settingsFile, "r") as jsonFile:
                keyframesData = json.load(jsonFile)

            # Loops through all keyframes and moves the height and tilt accordingly. Also checks regurelally for emergency stop
            for i in range(1, totKeyframes + 1):
                if firstScreen.getEmercenyFlag() != True:
                    if keyframesData is not None:
                        if firstScreen.getEmercenyFlag() != True:

                            firstScreen.moveToPosition(
                                keyframesData[f"Keyframe {i}"]["liftHeight"]
                            )
                            firstScreen.angleToPosition(
                                keyframesData[f"Keyframe {i}"]["tiltDegree"]
                            )
                           
                            # Set slider and variables to height of current keyframe
                            firstScreen.setSliderVal(keyframesData[f"Keyframe {i}"]["liftHeight"])
                            firstScreen.setTiltLabelVal(keyframesData[f"Keyframe {i}"]["tiltDegree"])

                            for _ in range(self.__picsPerKeyframe):
                                if not firstScreen.getEmercenyFlag():
                                    sleep(self.__beforeWaitTime)
                                    captureImage()
                                    sleep(self.__afterWaitTime)
                                    motorTableCW(self.__degreesPerRotation, self.__turntableSpeed)
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
            firstScreen.setCycleState(False)
            cycleCounter["CycleCounter"] += 1
           
            # Resets the motors and the counter
            firstScreen.reset()
           
            # Write the updated dictionary to the JSON file
            with open(cycleCounterFile, "w") as jsonFile:
                json.dump(cycleCounter, jsonFile)
           
        else:
            text = "The cycle limit has been reached! Readjust the motors and reset the counter!"

            # Sends message to Slack workspace
            self.sendSlackMessage(text)


class MainWindow(QMainWindow):
    # All important values
    __waitBeforeTime = 1
    __waitAfterTime = 0
    __picsPerKeyframe = 25
    __tiltValue = 0
    __desiredTilt = 0
    __heightValue = 0
    __desiredHeight = 0
    __isCycleBusy = False
    __emergencyFlag = False

    # Constructor
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #343541")

        self.initUI()

    # mostly contains GUI design
    def initUI(self):
        self.setGeometry(100, 100, 600, 400)

        layout = QGridLayout()

        # Creates all the widgets using the factory classes.
        self.slider = sliderFactory.create(0, 72000, 2000, 100, 20, sliderStylesheet, self.update_slider_label)
        self.sliderLabel = labelFactory.create("Height: 0", font, labelStyle)
        self.tiltLabel = labelFactory.create("Tilt", font, labelStyle)
        self.waitBeforeLabel = labelFactory.create(f'Wait Before Time: {self.__waitBeforeTime}', font, labelStyle)
        self.waitAfterLabel = labelFactory.create(f'Wait After Time: {self.__waitAfterTime}', font, labelStyle)
        self.picsPerKeyframeLabel = labelFactory.create(f'Pictures: {self.__picsPerKeyframe}', font, labelStyle)

        self.tiltButtonSub = buttonFactory.create("-", lambda: self.tiltButtonsClicked("-"), buttonStyle, size)
        self.tiltButtonAdd = buttonFactory.create("+", lambda: self.tiltButtonsClicked("+"), buttonStyle, size)
        self.tiltButtons = hboxLayoutFactory.create(self.tiltButtonSub, self.tiltButtonAdd)

        self.waitBeforeButtonSub = buttonFactory.create("-", lambda: self.waitBeforeClicked("-"), buttonStyle, size)
        self.waitBeforeButtonAdd = buttonFactory.create("+", lambda: self.waitBeforeClicked("+"), buttonStyle, size)
        self.waitBeforeButtons = hboxLayoutFactory.create(self.waitBeforeButtonSub, self.waitBeforeButtonAdd)

        self.waitAfterButtonSub = buttonFactory.create("-", lambda: self.waitAfterClicked("-"), buttonStyle, size)
        self.waitAfterButtonAdd = buttonFactory.create("+", lambda: self.waitAfterClicked("+"), buttonStyle, size)
        self.waitAfterButtons = hboxLayoutFactory.create(self.waitAfterButtonSub, self.waitAfterButtonAdd)

        self.picsPerKeyframeButtonSub = buttonFactory.create("-", lambda: self.picsPerKeyframeClicked("-"), buttonStyle, size)
        self.picsPerKeyframeButtonAdd = buttonFactory.create("+", lambda: self.picsPerKeyframeClicked("+"), buttonStyle, size)
        self.picsPerKeyframeButtons = hboxLayoutFactory.create(self.picsPerKeyframeButtonSub, self.picsPerKeyframeButtonAdd)

        self.keyframeButton = buttonFactory.create("KFM", self.keyframeMenuClicked, buttonStyle, size)
        self.turntableButton = buttonFactory.create("TTM", self.turntableMenuClicked, buttonStyle, size)
        self.menuButtons = hboxLayoutFactory.create(self.keyframeButton, self.turntableButton)

        self.moveButton = buttonFactory.create("MOVE", self.moveButtonClicked, buttonStyle, size)
        self.resetLiftButton = buttonFactory.create("RESET", self.reset, buttonStyle, size)
        self.quickAddKeyframeButton = buttonFactory.create("QUICK ADD KEYFRAME", self.quickAddKeyframe, buttonStyle, size)
        self.startCycleButton = buttonFactory.create("START CYCLE", self.cycle, buttonStyle, size)
        self.newZeroButton = buttonFactory.create("SET NEW ZERO", self.newZeroClicked, buttonStyle, size)
        self.emergencyStopButton = buttonFactory.create("EMERGENCY STOP", self.emergencyStopClicked , emergencyButtonOffStyle, size)

        # Adds all the widgets to the layout
        layout.addWidget(self.slider, 0, 0, 5, 1)
        layout.addWidget(self.sliderLabel, 5, 0)
        layout.addWidget(self.tiltLabel, 0, 1)
        layout.addLayout(self.tiltButtons, 1, 1, 1, 1)
        layout.addWidget(self.newZeroButton, 2, 1)
        layout.addWidget(self.waitBeforeLabel, 3, 1)
        layout.addLayout(self.waitBeforeButtons, 4, 1)
        layout.addWidget(self.quickAddKeyframeButton, 2, 2)
        layout.addWidget(self.waitAfterLabel, 3, 2)
        layout.addLayout(self.waitAfterButtons, 4, 2)
        layout.addWidget(self.resetLiftButton, 1, 3)
        layout.addWidget(self.startCycleButton, 2, 3)
        layout.addWidget(self.picsPerKeyframeLabel, 0, 2)
        layout.addLayout(self.picsPerKeyframeButtons, 1, 2, 1, 1)
        layout.addWidget(self.moveButton, 4, 3)
        layout.addLayout(self.menuButtons, 0, 3)
        layout.addWidget(self.emergencyStopButton, 3, 3)

        # Sets the layout to the window
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        layout.setColumnStretch(0, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # Calculates the steps needed to move to a certain position.
    def moveToPosition(self, goToPos):
        currentLiftHeight = self.__heightValue
        stepsNeeded = int(goToPos) - currentLiftHeight
        currentLiftHeight += stepsNeeded
        if stepsNeeded <= 0:
            # Makes sure neededSteps is positive
            stepsNeeded = stepsNeeded * -1
            motorLiftDown(stepsNeeded)
        elif stepsNeeded >= 0:
            motorLiftUp(stepsNeeded)
        self.__heightValue = self.__desiredHeight

    # Calculates the steps needed to move to a certain tilt angle.
    def angleToPosition(self, goToPos):
        currentTiltAngle = firstScreen.getTiltValue()
        stepsNeeded = int(goToPos) - currentTiltAngle
        currentTiltAngle += stepsNeeded
        if stepsNeeded <= 0:
            # Makes sure neededSteps is positive
            stepsNeeded = stepsNeeded * -1
            motorTiltCW(stepsNeeded)
        elif stepsNeeded >= 0:
            motorTiltCCW(stepsNeeded)
        self.__tiltValue = self.__desiredTilt

    # Called when the slider is used, changes the label and the variable for the wanted lift height. /conversion is for conversion from steps to cm
    def update_slider_label(self):
        sliderValue = self.slider.value()
        self.sliderLabel.setText("Height: " + str(int(sliderValue / conversionValue)))
        self.__desiredHeight = sliderValue

    # Move MARC to wanted height and tilt, and sets the variables to those values
    def moveButtonClicked(self):
        if not self.__isCycleBusy:
            self.moveToPosition(self.__desiredHeight)
       
    # Adds a keyframe to the keyframe list via another class function
    def quickAddKeyframe(self):
        thirdScreen.quickAddKeyframe(self.__desiredHeight, self.__tiltValue)

    # Sets the tilt variable to 0 because of inconsistencies in the tilt motor
    def newZeroClicked(self):
        self.__tiltValue = 0
        self.__desiredTilt = 0
        self.tiltLabel.setText("Tilt: " + str(self.__tiltValue))

    # Depending on which button got sent here it adds or subs 20 from the tilt variable. Add button has operator = + and sub has operator = -
    def tiltButtonsClicked(self, operator):
        if self.__isCycleBusy == False:
            if operator == "+":
                self.__desiredTilt += 200
            elif operator == "-":
                self.__desiredTilt -= 200
            self.tiltLabel.setText("Tilt: " + str(self.__desiredTilt))
            self.angleToPosition(self.__desiredTilt)

    # Chnages the wait before time depending on which button got sent here
    def waitBeforeClicked(self, operator):
        if operator == "+":
            self.__waitBeforeTime += 0.5
        elif operator == "-" and self.__waitBeforeTime >= 0.5:
            self.__waitBeforeTime -= 0.5
        self.waitBeforeLabel.setText("Wait Before Time: " + str(self.__waitBeforeTime))

    # Changes the wait after time depending on which button got sent here
    def waitAfterClicked(self, operator):
        if operator == "+":
            self.__waitAfterTime += 0.5
        elif operator == "-" and self.__waitAfterTime >= 0.5:
            self.__waitAfterTime -= 0.5
        self.waitAfterLabel.setText("Wait After Time: " + str(self.__waitAfterTime))

    # Depending on which button got sent here it adds or subs 1 from the pictures per keyframe variable. Add button has operator = + and sub has operator = -. Also refreshes the screen
    def picsPerKeyframeClicked(self, operator):
        if operator == "+":
            self.__picsPerKeyframe += 1
        elif operator == "-" and self.__picsPerKeyframe > 1:
            self.__picsPerKeyframe -= 1
        self.picsPerKeyframeLabel.setText("Pictures: " + str(self.__picsPerKeyframe))

    # Changes screen
    def keyframeMenuClicked(self):
        widget.setCurrentWidget(secondScreen)

    def turntableMenuClicked(self):
        widget.setCurrentWidget(sixthScreen)

    # Sets emergency flag to True or false accordingly and changes style of emergency button
    def emergencyStopClicked(self):
        if self.__emergencyFlag == False:
            self.__emergencyFlag = True
            self.emergencyStopButton.setStyleSheet(emergencyButtonOnStyle)
        else:
            self.__emergencyFlag = False
            self.emergencyStopButton.setStyleSheet(emergencyButtonOffStyle)

    # Checks if MARC isn't busy or in emergency stop mode, if not starts the cycle thread and changes the busy flag
    def cycle(self):
        if self.__isCycleBusy != True and self.__emergencyFlag != True:
            newCycleThread = cycleThread(self.__waitBeforeTime, self.__waitAfterTime, self.__picsPerKeyframe)
            newCycleThread.start()

    # Set state of MARC
    def setCycleState(self, state):
        self.__isCycleBusy = state

    # Returns the emergency flag value
    def getEmercenyFlag(self):
        return self.__emergencyFlag

    # Sets the slider position
    def setSliderVal(self, value):
        self.slider.setSliderPosition(value)
        self.__heightValue = value

    # Returns slider value
    def getSliderValue(self):
        return self.__desiredHeight

    # Returns tilt value
    def getTiltValue(self):
        return self.__tiltValue

    # Sets the tilt text in window
    def setTiltLabelVal(self, val):
        self.__tiltValue = val
        self.tiltLabel.setText("Angle: " + str(val))

    # Resets the height ans til to 0
    def reset(self):
        if not self.__isCycleBusy:
            self.angleToPosition(0)
            self.__tiltValue = 0
            self.setTiltLabelVal(self.__tiltValue)
            self.moveToPosition(0)
            self.__desiredHeight = 0
            self.__heightValue = 0
            self.setSliderVal(self.__heightValue)


class KeyframeListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)  # Adjusted window size

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        centralLayout = QGridLayout()  # Main horizontal layout

        # Creates all the widgets using the factory classes.
        self.keyframeTable = qtableFactory.create((550, 350), tableStyle, tableSliderStyle)
        self.createKeyframeTable()

        self.backButton = buttonFactory.create("BACK", self.back, buttonStyle, size)
        self.addButton = buttonFactory.create("ADD KEYFRAME", self.addKeyframe, buttonStyle, size)
        self.editButton = buttonFactory.create("EDIT KEYFRAME", self.editKeyframe, buttonStyle, size)
        self.deleteButton = buttonFactory.create("DELETE KEYFRAME", self.deleteKeyframe, buttonStyle, size)
        self.keyframeCalculator = buttonFactory.create("CALC KEYFRAMES", self.kfcClicked, buttonStyle, size)

        rightLayout = vboxLayoutFactory.create(self.backButton, self.addButton, self.editButton, self.deleteButton, self.keyframeCalculator)

        centralLayout.addWidget(self.keyframeTable, 0, 0)
        centralLayout.addLayout(rightLayout, 0, 1)

        centralWidget = QWidget()
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

        self.selectedKeyframeIndex = None

    # Loads the json settings file into a local variable for easier use
    def loadKeyframesData(self):
        try:
            with open(self.keyframesDataFile, "r") as jsonFile:
                self.keyframesData = json.load(jsonFile)
        except FileNotFoundError:
            self.keyframesData = {}

    # Saves the locally changed settings into the settings file
    def saveKeyframesData(self):
        with open(self.keyframesDataFile, "w") as jsonFile:
            json.dump(self.keyframesData, jsonFile, indent=4)

    # Function that creates the keyframe displayer
    def createKeyframeTable(self):
        self.keyframeTable.setColumnCount(4)
        self.keyframeTable.setHorizontalHeaderLabels(["Keyframe", "Lift Height (cm)", "Tilt Degree", "Time Added"])

        rowCount = len(self.keyframesData)
        self.keyframeTable.setRowCount(rowCount)

        # Fill the table with the keyframe data
        for row, (keyframe, data) in enumerate(self.keyframesData.items()):
            self.keyframeTable.setItem(row, 0, QTableWidgetItem(keyframe))
            self.keyframeTable.setItem(row, 1, QTableWidgetItem(str(data["liftHeight"] / conversionValue)))
            self.keyframeTable.setItem(row, 2, QTableWidgetItem(str(data["tiltDegree"])))
            self.keyframeTable.setItem(row, 3, QTableWidgetItem(data.get("timeAdded", "")))

        # Make the table read-only
        for row in range(self.keyframeTable.rowCount()):
            for col in range(self.keyframeTable.columnCount()):
                item = self.keyframeTable.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # Set the row height and column width
        for row in range(self.keyframeTable.rowCount()):
            self.keyframeTable.setRowHeight(row, 70)
            self.keyframeTable.setColumnWidth(row, 110)

        # Set the selection mode to select entire rows
        self.keyframeTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.keyframeTable.itemSelectionChanged.connect(self.handleTableSelection)

    # Looks for the selected row and updates the corrosponding variable
    def handleTableSelection(self):
        selectedItems = self.keyframeTable.selectedItems()
        if selectedItems:
            self.selectedKeyframeIndex = self.keyframeTable.indexFromItem(selectedItems[0])

    # Changes screen
    def kfcClicked(self):
        widget.setCurrentWidget(fifthScreen)

    # Dynamically adds keyframes
    def addKeyframe(self):
        widget.setCurrentWidget(thirdScreen)

    # Dynamically edits keyframes
    def editKeyframe(self):
        widget.setCurrentWidget(fourthScreen)

    # Dynamically deletes keyframes TODO fix fast delete tap crash
    def deleteKeyframe(self):
        if self.selectedKeyframeIndex is not None and self.keyframeTable.rowCount() > 0:
            keyframeRow = self.selectedKeyframeIndex.row()
            if keyframeRow < self.keyframeTable.rowCount():
                keyframe = self.keyframeTable.item(keyframeRow, 0).text()

                del self.keyframesData[keyframe]
                self.updateKeyframeNumbers()
                self.saveKeyframesData()
                self.createKeyframeTable()

    # Goes back to the main screen
    def back(self):
        widget.setCurrentWidget(firstScreen)

    # Updates the numbers, so that there are no gaps
    def updateKeyframeNumbers(self):
        currentKeyframes = dict(self.keyframesData)
        self.keyframesData.clear()

        for i, (keyframe, data) in enumerate(currentKeyframes.items()):
            newKeyframeName = f"Keyframe {i + 1}"
            self.keyframesData[newKeyframeName] = data


class NewKeyframeWindow(QMainWindow):
    __desiredHeight = 0
    __desiredTilt = 0

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        window = QGridLayout()

        # create the necessary widgets using the factory classes
        self.heightLabel = labelFactory.create("Desired height: 0", font, labelStyle)

        self.heightBigSubButton = buttonFactory.create("--", lambda: self.heightButtonsBigClicked("-"), buttonStyle, size)
        self.heightBigAddButton = buttonFactory.create("++", lambda: self.heightButtonsBigClicked("+"), buttonStyle, size)
        self.greatHeightButtonsLayout = hboxLayoutFactory.create(self.heightBigSubButton, self.heightBigAddButton)

        self.heightSmallSubButton = buttonFactory.create("-", lambda: self.heightButtonsSmallClicked("-"), buttonStyle, size)
        self.heightSmallAddButton = buttonFactory.create("+", lambda: self.heightButtonsSmallClicked("+"), buttonStyle, size)
        self.smallHeightButtonsLayout = hboxLayoutFactory.create(self.heightSmallSubButton, self.heightSmallAddButton)

        self.tiltLabel = labelFactory.create("Desired Tilt Angle: 0", font, labelStyle)

        self.tiltAddButton = buttonFactory.create("+", lambda: self.tiltButtonsClicked("+"), buttonStyle, size)
        self.tiltSubButton = buttonFactory.create("-", lambda: self.tiltButtonsClicked("-"), buttonStyle, size)
        self.tiltButtonsLayout = hboxLayoutFactory.create(self.tiltSubButton, self.tiltAddButton)

        self.backButton = buttonFactory.create("BACK", self.backButtonClicked, buttonStyle, size)
        self.addButton = buttonFactory.create("ADD KEYFRAME", self.addKeyframeClicked, buttonStyle, size)
        self.navButtonsLayout = hboxLayoutFactory.create(self.backButton, self.addButton)

        window.addWidget(self.heightLabel, 0, 0)
        window.addLayout(self.greatHeightButtonsLayout, 1, 0)
        window.addLayout(self.smallHeightButtonsLayout, 2, 0)
        window.addWidget(self.tiltLabel, 0, 1)
        window.addLayout(self.tiltButtonsLayout, 1, 1)
        window.addLayout(self.navButtonsLayout, 3, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)

    # Loads the json settings file into a local variable for esier use
    def loadKeyframesData(self):
        try:
            with open(self.keyframesDataFile, "r") as jsonFile:
                self.keyframesData = json.load(jsonFile)
        except FileNotFoundError:
            self.keyframesData = {}

    # depending on wich button got sent here it adds or subs 200 from the tilt variable. Add button has operator = + and sub has operator = -
    def tiltButtonsClicked(self, operator):
        if operator == "+":
            self.__desiredTilt += 200
        elif operator == "-":
            self.__desiredTilt -= 200
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__desiredTilt))

    # Depending on which button got sent here it adds or subs 5cm from the height variable. Add button has operator = + and sub has operator = -
    def heightButtonsBigClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight + 4000 <= 72000:
                self.__desiredHeight += 4000
        elif operator == "-":
            if self.__desiredHeight - 4000 >= 0:
                self.__desiredHeight -= 4000
        self.heightLabel.setText(
            "Desired Height: " + str(int(self.__desiredHeight / conversionValue))
        )

        self.updateHeightLabel()

    # Depending on which button got sent here it adds or subs 1cm from the height variable. Add button has operator = + and sub has operator = -
    def heightButtonsSmallClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight + 400 <= 72000:
                self.__desiredHeight += 400
        elif operator == "-":
            if self.__desiredHeight - 400 >= 0:
                self.__desiredHeight -= 400
        self.heightLabel.setText(
            "Desired Height: " + str(int(self.__desiredHeight / conversionValue))
        )

        self.updateHeightLabel()

    # Updates the height label
    def updateHeightLabel(self):
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / conversionValue))

    # Goes back to the main screen
    def backButtonClicked(self):
        widget.setCurrentWidget(secondScreen)

    def addKeyframeClicked(self):
        # calculates next keyrame number and creates the name
        nextKeyframe = secondScreen.keyframeTable.rowCount() + 1
        keyframeName = "Keyframe " + str(nextKeyframe)
        print(nextKeyframe)
        # Gets wanted values from entries
        liftHeight = self.__desiredHeight
        tiltDegree = self.__desiredTilt

        # Adds the kyframe to the last spot
        if keyframeName and liftHeight:
            keyframeData = {
                "liftHeight": int(liftHeight),
                "tiltDegree": int(tiltDegree),
                "timeAdded": QDateTime.currentDateTime().toString(
                    "dd/MM/yyyy hh:mm:ss"
                ),
            }
            secondScreen.keyframesData[keyframeName] = keyframeData
            secondScreen.saveKeyframesData()
            secondScreen.createKeyframeTable()
            secondScreen.keyframeTable.setRowHeight(nextKeyframe - 1, 70)
            for column in range(secondScreen.keyframeTable.columnCount()):
                secondScreen.keyframeTable.setColumnWidth(column, 125)
        widget.setCurrentWidget(secondScreen)

    def quickAddKeyframe(self, desiredHeight, desiredTilt):
        # calculates next keyrame number and creates the name
        nextKeyframe = secondScreen.keyframeTable.rowCount() + 1
        keyframeName = "Keyframe " + str(nextKeyframe)

        # Gets wanted values from entries
        liftHeight = desiredHeight
        tiltDegree = desiredTilt

        # Adds the kyframe to the last spot
        if keyframeName and liftHeight:
            keyframeData = {
                "liftHeight": int(liftHeight),
                "tiltDegree": int(tiltDegree),
                "timeAdded": QDateTime.currentDateTime().toString(
                    "dd/MM/yyyy hh:mm:ss"
                ),
            }
            secondScreen.keyframesData[keyframeName] = keyframeData
            secondScreen.saveKeyframesData()
            secondScreen.createKeyframeTable()
            secondScreen.keyframeTable.setRowHeight(nextKeyframe - 1, 70)
            for column in range(secondScreen.keyframeTable.columnCount()):
                secondScreen.keyframeTable.setColumnWidth(column, 125)


class EditKeyframeWindow(QMainWindow):
    __desiredHeight = 0
    __desiredTilt = 0

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        window = QGridLayout()

        # create the necessary widgets using the factory classes
        self.tiltLabel = labelFactory.create("Desired Tilt Angle: 0", font, labelStyle)

        self.tiltAddButton = buttonFactory.create("+", lambda: self.tiltButtonsClicked("+"), buttonStyle, size)
        self.tiltSubButton = buttonFactory.create("-", lambda: self.tiltButtonsClicked("-"), buttonStyle, size)
        self.tiltButtonsLayout = hboxLayoutFactory.create(self.tiltSubButton, self.tiltAddButton)

        self.heightLabel = labelFactory.create("Desired height: 0", font, labelStyle)

        self.heightSubSmallButton = buttonFactory.create("-", lambda: self.heightButtonsSmallClicked("-"), buttonStyle, size)
        self.heightAddSmallButton = buttonFactory.create("+", lambda: self.heightButtonsSmallClicked("+"), buttonStyle, size)
        self.heightButtonsSmallLayout = hboxLayoutFactory.create(self.heightSubSmallButton, self.heightAddSmallButton)

        self.heightSubBigButton = buttonFactory.create("--", lambda: self.heightButtonsBigClicked("-"), buttonStyle, size)
        self.heightAddBigButton = buttonFactory.create("++", lambda: self.heightButtonsBigClicked("+"), buttonStyle, size)
        self.heightButtonsBigLayout = hboxLayoutFactory.create(self.heightSubBigButton, self.heightAddBigButton)

        self.backButton = buttonFactory.create("BACK", self.backButtonClicked, buttonStyle, size)

        self.editButton = buttonFactory.create("EDIT KEYFRAME", self.editKeyframeClicked, buttonStyle, size)

        self.navButtonsLayout = hboxLayoutFactory.create(self.backButton, self.editButton)

        window.addWidget(self.heightLabel, 0, 0)
        window.addLayout(self.heightButtonsBigLayout, 1, 0)
        window.addLayout(self.heightButtonsSmallLayout, 2, 0)
        window.addWidget(self.tiltLabel, 0, 1)
        window.addLayout(self.tiltButtonsLayout, 1, 1)
        window.addLayout(self.navButtonsLayout, 3, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)

    # Edits the clicked keyframe to the new desired variables
    def editKeyframeClicked(self):
        if secondScreen.selectedKeyframeIndex is not None:
            liftHeight = self.__desiredHeight
            tiltDegree = self.__desiredTilt

            if liftHeight:
                keyframeData = {
                    "liftHeight": int(liftHeight),
                    "tiltDegree": int(tiltDegree),
                    "timeAdded": QDateTime.currentDateTime().toString(
                        "dd/MM/yyyy hh:mm:ss"
                    ),
                }
                # Gets the selected row and pastes the new keyframe on that row
                keyframeRow = secondScreen.selectedKeyframeIndex.row()
                keyframe = secondScreen.keyframeTable.item(keyframeRow, 0).text()
                secondScreen.keyframesData[keyframe] = keyframeData
                secondScreen.saveKeyframesData()
                secondScreen.createKeyframeTable()
        widget.setCurrentWidget(secondScreen)

    # Loads the json settings file into a local variable for esier use
    def loadKeyframesData(self):
        try:
            with open(self.keyframesDataFile, "r") as jsonFile:
                self.keyframesData = json.load(jsonFile)
        except FileNotFoundError:
            self.keyframesData = {}

    def updateHeightLabel(self):
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / conversionValue))

    # Depending on which button got sent here it adds or subs 20 from the tilt variable. Add button has operator = + and sub has operator = -
    def tiltButtonsClicked(self, operator):
        if operator == "+":
            self.__desiredTilt += 200
        elif operator == "-":
            self.__desiredTilt -= 200
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__desiredTilt))

    # Depending on which button got sent here it adds or subs 20 from the tilt variable. Add button has operator = + and sub has operator = -
    def heightButtonsBigClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight + 4000 <= 72000:
                self.__desiredHeight += 4000
        elif operator == "-":
            if self.__desiredHeight - 4000 >= 0:
                self.__desiredHeight -= 4000
        self.heightLabel.setText("Desired Height: " + str(int(self.__desiredHeight / conversionValue)))

        self.updateHeightLabel()

    def heightButtonsSmallClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight + 400 <= 72000:
                self.__desiredHeight += 400
        elif operator == "-":
            if self.__desiredHeight - 400 >= 0:
                self.__desiredHeight -= 400
        self.heightLabel.setText("Desired Height: " + str(int(self.__desiredHeight / conversionValue)))

        self.updateHeightLabel()

    # Goes back to the main screen
    def backButtonClicked(self):
        widget.setCurrentWidget(secondScreen)


class KeyframeCalculator(QMainWindow):
    __objHeight = 30
    __objSize = ""

    def __init__(self):

        super().__init__()

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        layout = QGridLayout()

        # Height slider Widgets
        self.heightSliderLabel = labelFactory.create("Height: 30", font, labelStyle)
        self.heightSlider = sliderFactory.create(30, 160, 1, 100, 20, sliderStylesheet , self.updateHeightSliderLabel)
        self.sizeSliderLabel = labelFactory.create("Size: small", font, labelStyle)
        self.sizeSlider = sliderFactory.create(0, 2, 1, 100, 20, sliderStylesheet, self.updateSizeSliderLabel)
        self.backButton = buttonFactory.create("Back", self.back, buttonStyle, size)
        self.calculateButton = buttonFactory.create("Calculate", self.calculate, buttonStyle, size)

        # Adding all widgets together
        layout.addWidget(self.heightSlider, 0, 0, 5, 1)
        layout.addWidget(self.heightSliderLabel, 5, 0)
        layout.addWidget(self.sizeSlider, 0, 1, 5, 1)
        layout.addWidget(self.sizeSliderLabel, 5, 1)
        layout.addWidget(self.calculateButton, 2, 2)
        layout.addWidget(self.backButton, 3, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # Goes back to the main screen
    def back(self):
        widget.setCurrentWidget(secondScreen)

    # Calculates the keyframes and saves them to the settings file
    def calculate(self):
        oppositeSide = objDistance
        scannerHeight = totHeight
        conversionVal = conversionValue
        size = self.__objSize
        height = self.__objHeight

        if size == 0:
            heightIncr = 4
        elif size == 1:
            heightIncr = 6
        else:
            heightIncr = 8

        keyframes_data = {}  # Dictionary to store keyframe data
        initialHeight = height - (heightIncr * 3)

        # Calculate keyframe data using trigonometry
        for i in range(1, 8):
            newHeight = initialHeight + (i * heightIncr)
            x = scannerHeight - newHeight
            rightSideTriangle = scannerHeight - height - x

            # Check if rightSideTriangle is non-zero to avoid division by zero
            if rightSideTriangle != 0:

                # Calculate the acute angle using sine and handle positive and negative cases
                theta = math.degrees(math.atan(oppositeSide / rightSideTriangle)) * -1

                if theta > 0:
                    keyframeData = {
                        "liftHeight": int(
                            newHeight * conversionVal
                        ),  # Convert to motor steps
                        "tiltDegree": int(
                            (90 - theta) * 100
                        ),  # Scale angle for motor control
                        "timeAdded": QDateTime.currentDateTime().toString(
                            "dd/MM/yyyy hh:mm:ss"
                        ),
                    }
                elif theta < 0:
                    keyframeData = {
                        "liftHeight": int(
                            newHeight * conversionVal
                        ),  # Convert to motor steps
                        "tiltDegree": int(
                            -abs((90 - abs(theta))) * 100
                        ),  # Handle negative angles
                        "timeAdded": QDateTime.currentDateTime().toString(
                            "dd/MM/yyyy hh:mm:ss"
                        ),
                    }

                keyframes_data[f"Keyframe {i}"] = keyframeData
            else:
                # Handle the case where rightSideTriangle is zero so there is no triangle
                keyframeData = {
                    "liftHeight": int(
                        newHeight * conversionVal
                    ),  # Convert to motor steps
                    "tiltDegree": int(0),  # No tilt when rightSideTriangle is zero
                    "timeAdded": QDateTime.currentDateTime().toString(
                        "dd/MM/yyyy hh:mm:ss"
                    ),
                }

                keyframes_data[f"Keyframe {i}"] = keyframeData

        # Write keyframes_data to a JSON file
        with open(settingsFile, "w") as file:
            json.dump(keyframes_data, file, indent=4)

        secondScreen.keyframesData = keyframes_data
        secondScreen.saveKeyframesData()
        secondScreen.createKeyframeTable()
        for row in range(secondScreen.keyframeTable.rowCount()):
            secondScreen.keyframeTable.setRowHeight(row, 70)

    # Updates the label for the size slider
    def updateSizeSliderLabel(self, value):
        size_options = ["Small", "Medium", "Large"]
        self.sizeSliderLabel.setText(f"Size: {size_options[value]}")
        self.__objSize = value

    # Updates the label for the height slider
    def updateHeightSliderLabel(self, value):
        self.heightSliderLabel.setText("Height: " + str(value))
        self.__objHeight = value


class TurntableMenuWindow(QMainWindow):
    turntableSpeed = 0.0009

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        window = QGridLayout()

        self.speedLabel = labelFactory.create(f'Turntable speed: {self.turntableSpeed}', font, labelStyle)

        self.slowButton = buttonFactory.create('Slow', lambda: self.speedButtonsClicked('Slow'), buttonStyle, size)
        self.mediumButton = buttonFactory.create('Medium', lambda: self.speedButtonsClicked('Medium'), buttonStyle, size)
        self.fastButton = buttonFactory.create('Fast', lambda: self.speedButtonsClicked('Fast'), buttonStyle, size)

        self.speedButtonsLayout = hboxLayoutFactory.create(self.slowButton, self.mediumButton, self.fastButton)

        self.backButton = buttonFactory.create("BACK", self.back, buttonStyle, size)

        window.addWidget(self.speedLabel, 0, 1)
        window.addLayout(self.speedButtonsLayout, 1, 1)
        window.addWidget(self.backButton, 2, 1)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)
    
    def speedButtonsClicked(self, speed):
        if speed == 'Slow':
            self.turntableSpeed = turntableSpeeds[0]
        elif speed == 'Medium':
            self.turntableSpeed = turntableSpeeds[1]
        elif speed == 'Fast':
            self.turntableSpeed = turntableSpeeds[2]
            
        self.speedLabel.setText(f'Turntable speed: {self.turntableSpeed}')


    def back(self):
        widget.setCurrentWidget(firstScreen)


app = QApplication(sys.argv)
widget = QStackedWidget()
firstScreen = MainWindow()
widget.addWidget(firstScreen)
secondScreen = KeyframeListWindow()
widget.addWidget(secondScreen)
thirdScreen = NewKeyframeWindow()
widget.addWidget(thirdScreen)
fourthScreen = EditKeyframeWindow()
widget.addWidget(fourthScreen)
fifthScreen = KeyframeCalculator()
widget.addWidget(fifthScreen)
sixthScreen = TurntableMenuWindow()
widget.addWidget(sixthScreen)

sliderFactory = sliderFactory()
labelFactory = labelFactory()
buttonFactory = buttonFactory()
hboxLayoutFactory = hboxLayoutFactory()
vboxLayoutFactory = vboxLayoutFactory()
qtableFactory = qtableFactory()

# setting the page that you want to load when application starts up
widget.setCurrentWidget(firstScreen)
widget.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
widget.showMaximized()
widget.show()
app.exec()