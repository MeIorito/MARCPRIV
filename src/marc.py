import sys
import json
import time
import math
import slack
import random
import threading
from time import sleep
import RPi.GPIO as GPIO
from PyQt5 import QtCore
from PyQt5.QtCore import *
from motorfunctions import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QSlider

# Constants | slack auth | settings file | font size
slackToken = "xoxb-5867825218247-5875744156982-TuLlFjvAptQvxyraY4ZQ4Vm6"
settingsFile = "settingsCustom.txt"
cycleCounterFile = "cycleCounter.txt"
font = QFont()
font.setPointSize(11)
size = (100, 80)

objDistance = 43 # Distance between object and camera
totHeight = 180 # Total height of the lift
conversionValue = 72000 / totHeight # Steps per cm

# 4 standard styles for all types of used widgets, format like css
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
    # Messages for the slack bot to send (Can delete an customize) chatGPT generated
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

    # Constructor, needs the wait times, pictures per keyframe and rotations for the cycle
    def __init__(self, waitBeforeTime, waitAfterTime, picsPerKeyframe):
        threading.Thread.__init__(self)
        self.__beforeWaitTime = waitBeforeTime
        self.__afterWaitTime = waitAfterTime
        self.__picsPerKeyframe = picsPerKeyframe
        self.__degreesPerRotation = int(32000 / self.__picsPerKeyframe)

    # Capture cycle
    def run(self):
        with open(cycleCounterFile, "r") as jsonFile:
            cycleCounter = json.load(jsonFile)

        # Checks if the cycle limit has been reached, after 200 cycles the motors need to be readjusted
        if cycleCounter["CycleCounter"] <= 3:
            startTime = time.time()
            firstScreen.setCycleState(True)

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
                            for _ in range(self.__picsPerKeyframe):
                                if not firstScreen.getEmercenyFlag():
                                    sleep(self.__beforeWaitTime)
                                    #captureImage()
                                    sleep(self.__afterWaitTime)
                                    motorTableCW(self.__degreesPerRotation)
                                else:
                                    text = "The emergency button has been pressed!"
                                    break
                        else:
                            break
                        # Set slider and variables to height of current keyframe
                        firstScreen.setSliderVal(
                            keyframesData[f"Keyframe {i}"]["liftHeight"]
                        )
                        firstScreen.setTiltLabelVal(
                            keyframesData[f"Keyframe {i}"]["tiltDegree"]
                        )
                        text = (
                            str(random.choice(self.__marcMessages))
                            + " It took: "
                            + str(round(time.time() - startTime, 2))
                            + " seconds"
                        )
                else:
                    text = "The emergency button has been pressed!"
                    break
            firstScreen.reset()
            # Sends message to Slack workspace
            try:
                client = slack.WebClient(token=slackToken)
                client.chat_postMessage(channel="#testbot", text=text)
            except:
                print("Oops! Something went wrong with the connection to Slack!")
            # Updates busy flag
            firstScreen.setCycleState(False)
            cycleCounter["cycleCounter"] += 1
        else:
            text = "The cycle limit has been reached! Readjust the motors and reset the counter!"
            # Sends message to Slack workspace
            try:
                client = slack.WebClient(token=slackToken)
                client.chat_postMessage(channel="#testbot", text=text)
            except:
                print("Oops! Something went wrong with the connection to Slack!")


class MainWindow(QMainWindow):
    # All important values
    __sliderValue = 0
    __waitBeforeTime = 0
    __waitAfterTime = 2
    __picsPerKeyframe = 20
    __tiltValue = 0
    __desiredTilt = 0
    __heightValue = 0
    __isCycleBusy = False
    __emergencyFlag = False

    # Constructor, mostly contains GUI design
    # Constructor, mostly contains GUI design
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #343541")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Your Application")
        self.setGeometry(100, 100, 600, 400)

        layout = QGridLayout()

        self.slider = self.setupSlider()
        self.sliderLabel = self.setupLabel("Height: 0", font, labelStyle)
        self.tiltLabel = self.setupLabel("Desired Tilt Angle: 0", font, labelStyle)
        self.waitBeforeLabel = self.setupLabel("Wait Before Time: 0", font, labelStyle)
        self.waitAfterLabel = self.setupLabel("Wait After Time: 2", font, labelStyle)
        self.picsPerKeyframeLabel = self.setupLabel("Pictures: 20", font, labelStyle)

        self.tiltButtons = self.setupTiltButtons(buttonStyle, size)
        self.waitBeforeButtons = self.setupTimeButtons("waitBefore", buttonStyle, size)
        self.waitAfterButtons = self.setupTimeButtons("waitAfter", buttonStyle, size)
        self.picsPerKeyframeButtons = self.setupPicsPerKeyframeButtons(buttonStyle, size)

        self.moveButton = self.setupButton("MOVE", self.moveButtonClicked, buttonStyle, size)
        self.resetLiftButton = self.setupButton("RESET", self.reset, buttonStyle, size)
        self.startCycleButton = self.setupButton("START CYCLE", self.cycle, buttonStyle, size)
        self.keyframeButton = self.setupButton("KEYFRAME MENU", self.keyframeMenuClicked, buttonStyle, size)
        self.newZeroButton = self.setupButton("SET NEW ZERO", self.newZeroClicked, buttonStyle, size)
        self.emergencyStopButton = self.setupEmergencyStopButton(buttonStyle, size)

        layout.addWidget(self.slider, 0, 0, 5, 1)
        layout.addWidget(self.sliderLabel, 5, 0)
        layout.addWidget(self.tiltLabel, 0, 1)
        layout.addLayout(self.tiltButtons, 1, 1, 1, 1)
        layout.addWidget(self.newZeroButton, 2, 1)
        layout.addWidget(self.waitBeforeLabel, 3, 1)
        layout.addLayout(self.waitBeforeButtons, 4, 1)
        layout.addWidget(self.waitAfterLabel, 3, 2)
        layout.addLayout(self.waitAfterButtons, 4, 2)
        layout.addWidget(self.resetLiftButton, 1, 3)
        layout.addWidget(self.startCycleButton, 2, 3)
        layout.addWidget(self.picsPerKeyframeLabel, 0, 2)
        layout.addLayout(self.picsPerKeyframeButtons, 1, 2, 1, 1)
        layout.addWidget(self.moveButton, 4, 3)
        layout.addWidget(self.keyframeButton, 0, 3)
        layout.addWidget(self.emergencyStopButton, 3, 3)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        layout.setColumnStretch(0, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def setupSlider(self):
        slider = QSlider()
        slider.setMinimum(0)
        slider.setMaximum(72000)
        slider.setPageStep(2000)
        slider.setFixedWidth(100)
        slider.setTickInterval(20)
        slider.setStyleSheet(sliderStylesheet)
        slider.valueChanged.connect(self.update_slider_label)
        return slider

    def setupLabel(self, text, font, style):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(font)
        label.setStyleSheet(style)
        return label

    def setupButtonStyle(self):
        return """
            QPushButton {
                background-color: #0066cc;
                border: none;
                color: white;
                font-size: 14px;
            }
        """

    def setupButton(self, text, slot, style, size):
        button = QPushButton(text)
        button.clicked.connect(slot)
        button.setStyleSheet(style)
        button.setMinimumSize(size[0], size[1])
        return button

    def setupTiltButtons(self, style, size):
        tiltAddButton = self.setupButton("+", lambda: self.tiltButtonsClicked("+"), style, size)
        tiltSubButton = self.setupButton("-", lambda: self.tiltButtonsClicked("-"), style, size)

        tiltButtonsLayout = QHBoxLayout()
        tiltButtonsLayout.addWidget(tiltAddButton)
        tiltButtonsLayout.addWidget(tiltSubButton)

        return tiltButtonsLayout

    def setupTimeButtons(self, time_type, style, size):
        addButton = self.setupButton("+", lambda: self.timeButtonsClicked(time_type, "+"), style, size)
        subButton = self.setupButton("-", lambda: self.timeButtonsClicked(time_type, "-"), style, size)

        timeButtonsLayout = QHBoxLayout()
        timeButtonsLayout.addWidget(addButton)
        timeButtonsLayout.addWidget(subButton)

        return timeButtonsLayout

    def setupPicsPerKeyframeButtons(self, style, size):
        addButton = self.setupButton("+", lambda: self.picsPerKeyframeClicked("+"), style, size)
        subButton = self.setupButton("-", lambda: self.picsPerKeyframeClicked("-"), style, size)

        picsPerKeyframeButtonsLayout = QHBoxLayout()
        picsPerKeyframeButtonsLayout.addWidget(addButton)
        picsPerKeyframeButtonsLayout.addWidget(subButton)

        return picsPerKeyframeButtonsLayout

    def setupEmergencyStopButton(self, style, size):
        emergencyStopButton = QPushButton("EMERGENCY STOP")
        emergencyStopButton.setStyleSheet(style + """
            QPushButton#emergencyStopButton {
                background-color: #790004;
                border: 4px solid #790004;
            }
        """)
        emergencyStopButton.setMinimumSize(size[0], size[1])
        emergencyStopButton.setObjectName("emergencyStopButton")
        emergencyStopButton.clicked.connect(self.emergencyStopClicked)
        return emergencyStopButton

    # Calculates the steps needed to move to a certain position.
    def moveToPosition(self, goToPos):
        curLiftHeight = self.__heightValue
        stepsNeeded = int(goToPos) - curLiftHeight
        curLiftHeight += stepsNeeded
        if stepsNeeded <= 0:
            # Makes sure neededSteps is positive
            stepsNeeded = stepsNeeded * -1
            motorLiftDown(stepsNeeded)
        elif stepsNeeded >= 0:
            motorLiftUp(stepsNeeded)

    def angleToPosition(self, goToPos):
        curTiltAngle = firstScreen.getTiltValue()
        stepsNeeded = int(goToPos) - curTiltAngle
        curTiltAngle += stepsNeeded
        if stepsNeeded <= 0:
            # Makes sure neededSteps is positive
            stepsNeeded = stepsNeeded * -1
            motorTiltCW(stepsNeeded)
        elif stepsNeeded >= 0:
            motorTiltCCW(stepsNeeded)

    # Called when the slider is used, changes the label and the variable for the wanted lift height. /400 is for conversion from steps to cm
    def update_slider_label(self, value):
        self.sliderLabel.setText("Height: " + str(int(value / 400)))
        self.__sliderValue = value

    # Move MARC to wanted height and tilt, and sets the variables to those values
    def moveButtonClicked(self):
        self.angleToPosition(self.__desiredTilt)
        self.__tiltValue = self.__desiredTilt
        self.moveToPosition(self.__sliderValue)
        self.__heightValue = self.__sliderValue

    # Sets the tilt variable to 0 because of inconsistencies in the tilt motor
    def newZeroClicked(self):
        self.__tiltValue = 0
        self.__desiredTilt = 0
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__tiltValue))

    # Depending on which button got sent here it adds or subs 20 from the tilt variable. Add button has operator = + and sub has operator = -
    def tiltButtonsClicked(self, operator):
        if operator == "+":
            self.__desiredTilt += 100
        elif operator == "-":
            self.__desiredTilt -= 100
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__desiredTilt))

    # Depending on what the source and operator are, the correct value is added or subbed from the right time variable. Also refreshes the screen
    def timeButtonsClicked(self, source, operator):
        if source == "waitBefore" and operator == "+":
            self.__waitBeforeTime += 0.5
        elif source == "waitBefore" and operator == "-" and self.__waitBeforeTime > 0:
            self.__waitBeforeTime -= 0.5
        elif source == "waitAfter" and operator == "+":
            self.__waitAfterTime += 0.5
        elif source == "waitAfter" and operator == "-" and self.__waitAfterTime > 0:
            self.__waitAfterTime -= 0.5
        self.waitBeforeLabel.setText("Wait Before Time: " + str(self.__waitBeforeTime))
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

    # Sets emergency flag to True or false accordingly and changes style of emergency button
    def emergencyStopClicked(self):
        self.__emergencyFlag = not self.__emergencyFlag
        color = "#d80006" if self.__emergencyFlag else "#790004"
        self.emergencyStopButton.setStyleSheet(
            buttonStyle
            + f"""
            QPushButton#emergencyStopButton {{
                background-color: {color};
                border: 4px solid {color};
            }}
        """
        )

    # Checks if MARC isn't busy or in emergency stop mode, if not starts the cycle thread and changes the busy flag
    def cycle(self):
        if self.__isCycleBusy != True and self.__emergencyFlag != True:
            newCycleThread = cycleThread(
                self.__waitBeforeTime, self.__waitAfterTime, self.__picsPerKeyframe
            )
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
        return self.__sliderValue

    # Returns tilt value
    def getTiltValue(self):
        return self.__tiltValue

    # Sets the tilt text in window
    def setTiltLabelVal(self, val):
        self.__tiltValue = val
        self.tiltLabel.setText("Angle: " + str(val))

    # Resets the height ans til to 0
    def reset(self):
        self.angleToPosition(0)
        self.__tiltValue = 0
        self.setTiltLabelVal(self.__tiltValue)
        self.moveToPosition(0)
        self.__sliderValue = 0
        self.__heightValue = 0
        self.setSliderVal(self.__heightValue)


class KeyframeListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 500, 300)

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        layout = QVBoxLayout()

        self.keyframeTable = QTableWidget()
        self.keyframeTable.setFixedSize(600, 250)
        self.keyframeTable.setStyleSheet(tableStyle)
        layout.addWidget(self.keyframeTable)

        self.createKeyframeTable()

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        buttonLayout = QHBoxLayout()
        self.backButton = QPushButton("Back")
        self.addButton = QPushButton("Add Keyframe")
        self.editButton = QPushButton("Edit Keyframe")
        self.deleteButton = QPushButton("Delete Keyframe")
        self.calcButton = QPushButton("Calculate Keyframes")

        # Reduce spacing between buttons
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonLayout.setSpacing(1)

        self.backButton.setMinimumSize(40, 80)
        self.backButton.setStyleSheet(buttonStyle)
        self.addButton.setMinimumSize(40, 80)
        self.addButton.setStyleSheet(buttonStyle)
        self.editButton.setMinimumSize(40, 80)
        self.editButton.setStyleSheet(buttonStyle)
        self.deleteButton.setMinimumSize(40, 80)
        self.deleteButton.setStyleSheet(buttonStyle)
        self.calcButton.setMinimumSize(40, 80)
        self.calcButton.setStyleSheet(buttonStyle)

        buttonLayout.addWidget(self.backButton)
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.editButton)
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addWidget(self.calcButton)
        layout.addLayout(buttonLayout)

        entryFieldsLayout = QHBoxLayout()  # Horizontal layout for entry fields

        self.liftHeightEdit = QLineEdit()
        self.tiltDegreeEdit = QLineEdit()
        self.liftHeightEdit.setStyleSheet(lineEditStyle)
        self.tiltDegreeEdit.setStyleSheet(lineEditStyle)
        self.liftHeightEdit.setMinimumHeight(45)
        self.tiltDegreeEdit.setMinimumHeight(45)

        # Reduce spacing between entry fields and buttons
        entryFieldsLayout.setContentsMargins(0, 0, 0, 0)
        entryFieldsLayout.setSpacing(1)

        entryFieldsLayout.addWidget(self.liftHeightEdit)
        entryFieldsLayout.addWidget(self.tiltDegreeEdit)

        layout.addLayout(entryFieldsLayout)  # Add the entry fields layout

        fill = QHBoxLayout()

        self.fillLabel = QLabel(" ")

        fill.addWidget(self.fillLabel)
        fill.addWidget(self.fillLabel)
        fill.addWidget(self.fillLabel)
        fill.addWidget(self.fillLabel)

        layout.addLayout(fill)

        self.selectedKeyframeIndex = None

        self.backButton.clicked.connect(self.back)
        self.addButton.clicked.connect(self.addKeyframe)
        self.editButton.clicked.connect(self.editKeyframe)
        self.deleteButton.clicked.connect(self.deleteKeyframe)
        self.calcButton.clicked.connect(self.calculateKeyframes)

        self.setWindowTitle("Keyframe List")
        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)  # Adjusted window size

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        centralLayout = QGridLayout()  # Main horizontal layout

        # Left side: QTableWidget
        self.keyframeTable = QTableWidget()
        self.keyframeTable.setFixedSize(550, 350)  # Adjusted table size
        self.keyframeTable.setStyleSheet(tableStyle)
        self.createKeyframeTable()

        for x in range(self.keyframeTable.rowCount()):
            self.keyframeTable.setRowHeight(x, 70)

        for x in range(self.keyframeTable.columnCount()):
            self.keyframeTable.setColumnWidth(x, 125)

        self.keyframeTable.verticalScrollBar().setStyleSheet(tableSliderStyle)

        # Right side: Buttons and entry fields
        rightLayout = QVBoxLayout()  # Vertical layout for buttons and entry fields

        self.backButton = QPushButton("Back")
        self.addButton = QPushButton("Add Keyframe")
        self.editButton = QPushButton("Edit Keyframe")
        self.deleteButton = QPushButton("Delete Keyframe")
        self.keyframeCalcButton = QPushButton("Calculate Keyframes")

        rightLayout.addWidget(self.backButton)
        rightLayout.addWidget(self.addButton)
        rightLayout.addWidget(self.editButton)
        rightLayout.addWidget(self.deleteButton)
        rightLayout.addWidget(self.keyframeCalcButton)

        # Add the QTableWidget and the right side layout to the main horizontal layout
        centralLayout.addWidget(self.keyframeTable, 0, 0)
        centralLayout.addLayout(rightLayout, 0, 1)

        for i in range(rightLayout.count()):
            widget = rightLayout.itemAt(i).widget()
            if widget is not None:
                widget.setFixedWidth(200)
                widget.setMinimumSize(100, 80)
                widget.setStyleSheet(buttonStyle)

        # Set the central widget
        centralWidget = QWidget()
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)
        self.showMaximized()

        self.selectedKeyframeIndex = None

        self.backButton.clicked.connect(self.back)
        self.addButton.clicked.connect(self.addKeyframe)
        self.editButton.clicked.connect(self.editKeyframe)
        self.deleteButton.clicked.connect(self.deleteKeyframe)
        self.keyframeCalcButton.clicked.connect(self.calculateKeyframes)

    # Loads the json settings file into a local variable for esier use
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
        self.keyframeTable.setHorizontalHeaderLabels(
            ["Keyframe", "Lift Height (cm)", "Tilt Degree", "Time Added"]
        )

        rowCount = len(self.keyframesData)
        self.keyframeTable.setRowCount(rowCount)

        for row, (keyframe, data) in enumerate(self.keyframesData.items()):
            self.keyframeTable.setItem(row, 0, QTableWidgetItem(keyframe))
            self.keyframeTable.setItem(
                row, 1, QTableWidgetItem(str(data["liftHeight"] / 400))
            )
            self.keyframeTable.setItem(
                row, 2, QTableWidgetItem(str(data["tiltDegree"]))
            )
            self.keyframeTable.setItem(
                row, 3, QTableWidgetItem(data.get("timeAdded", ""))
            )

        for row in range(self.keyframeTable.rowCount()):
            for col in range(self.keyframeTable.columnCount()):
                item = self.keyframeTable.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.keyframeTable.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.keyframeTable.itemSelectionChanged.connect(self.handleTableSelection)

    # Looks for the selected row and updates the corrosponding variable
    def handleTableSelection(self):
        selectedItems = self.keyframeTable.selectedItems()
        if selectedItems:
            self.selectedKeyframeIndex = self.keyframeTable.indexFromItem(
                selectedItems[0]
            )

    def calculateKeyframes(self):
        widget.setCurrentWidget(fifthScreen)

    # Dynamically adds keyframes
    def addKeyframe(self):
        widget.setCurrentWidget(thirdScreen)

    # Dynamically edits keyframes
    def editKeyframe(self):
        widget.setCurrentWidget(fourthScreen)

    # Dynamically deletes keyframes
    def deleteKeyframe(self):
        if self.selectedKeyframeIndex is not None:
            keyframeRow = self.selectedKeyframeIndex.row()
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

        for i, (keyframe, data) in enumerate(sorted(currentKeyframes.items())):
            newKeyframeName = f"Keyframe {i + 1}"
            self.keyframesData[newKeyframeName] = data

    def clearInputFields(self):
        self.liftHeightEdit.clear()
        self.tiltDegreeEdit.clear()


class NewKeyframeWindow(QMainWindow):
    __desiredHeight = 0
    __desiredTilt = 0

    def __init__(self):
        super().__init__()

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_increment)
        self.button_pressed = False

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        window = QGridLayout()

        # tilt widgets
        self.tiltLabel = QLabel("Desired Tilt Angle: 0")
        self.tiltLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tiltLabel.setStyleSheet(labelStyle)
        self.tiltLabel.setFont(font)

        self.tiltAddButton = QPushButton("+")
        self.tiltAddButton.clicked.connect(lambda: self.tiltButtonsClicked("+"))
        self.tiltSubButton = QPushButton("-")
        self.tiltSubButton.clicked.connect(lambda: self.tiltButtonsClicked("-"))

        # height widgets
        self.heightLabel = QLabel("Desired Height: 0")
        self.heightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heightLabel.setStyleSheet(labelStyle)
        self.heightLabel.setFont(font)

        self.heightAddButton = QPushButton("+")
        self.heightAddButton.clicked.connect(lambda: self.heightButtonsClicked("+"))
        self.heightSubButton = QPushButton("-")
        self.heightSubButton.clicked.connect(lambda: self.heightButtonsClicked("-"))

        # Tilt buttons
        self.tiltButtonsLayout = QHBoxLayout()
        self.tiltButtonsLayout.addWidget(self.tiltAddButton)
        self.tiltButtonsLayout.addWidget(self.tiltSubButton)

        # Height buttons
        self.heightButtonsLayout = QHBoxLayout()
        self.heightButtonsLayout.addWidget(self.heightAddButton)
        self.heightButtonsLayout.addWidget(self.heightSubButton)

        self.backButton = QPushButton("BACK")
        self.backButton.clicked.connect(self.backButtonClicked)

        self.addButton = QPushButton("ADD KEYFRAME")
        self.addButton.clicked.connect(self.addKeyframeClicked)

        self.heightLabel.setMaximumHeight(100)
        self.tiltLabel.setMaximumHeight(100)

        self.navButtonsLayout = QHBoxLayout()
        self.navButtonsLayout.addWidget(self.backButton)
        self.navButtonsLayout.addWidget(self.addButton)

        window.addWidget(self.heightLabel, 0, 0)
        window.addLayout(self.heightButtonsLayout, 1, 0)
        window.addWidget(self.tiltLabel, 0, 1)
        window.addLayout(self.tiltButtonsLayout, 1, 1)
        window.addLayout(self.navButtonsLayout, 2, 0, 1, 2)

        for layout in (
            self.heightButtonsLayout,
            self.tiltButtonsLayout,
            self.navButtonsLayout,
        ):
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.setMinimumSize(100, 80)
                    widget.setStyleSheet(buttonStyle)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)
        self.showMaximized()

    # Loads the json settings file into a local variable for esier use
    def loadKeyframesData(self):
        try:
            with open(self.keyframesDataFile, "r") as jsonFile:
                self.keyframesData = json.load(jsonFile)
        except FileNotFoundError:
            self.keyframesData = {}

    def tiltButtonsClicked(self, operator):
        if operator == "+":
            self.__desiredTilt += 200
        elif operator == "-":
            self.__desiredTilt -= 200
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__desiredTilt))

    def heightButtonsClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight < 72000:
                current_time = time.time()

                if not self.button_pressed:
                    # First button press
                    self.button_pressed = True
                    self.previous_press = current_time
                    self.counter = 1
                    self.increment_amount = 400
                    self.__desiredHeight += self.increment_amount
                    self.updateHeightLabel()

                    # Start a 3-second timer for multi-press
                    self.timer.start(3000)
                else:
                    # Subsequent button presses
                    time_difference = current_time - self.previous_press

                    if time_difference <= 3:
                        self.counter += 1

                        if self.counter >= 8:
                            self.increment_amount = 2000

                        self.__desiredHeight += self.increment_amount
                        self.updateHeightLabel()
                    else:
                        self.reset_increment()
        elif operator == "-":
            if self.__desiredHeight > 0:
                self.__desiredHeight -= 2000

        self.updateHeightLabel()

    def updateHeightLabel(self):
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / 400))

    def backButtonClicked(self):
        widget.setCurrentWidget(secondScreen)

    def reset_increment(self):
        self.button_pressed = False
        self.timer.stop()
        self.counter = 0
        self.increment_amount = 1

    def addKeyframeClicked(self):
        # calculates next keyrame number and creates the name
        nextKeyframe = secondScreen.keyframeTable.rowCount() + 1
        keyframeName = "Keyframe " + str(nextKeyframe)

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

        # tilt widgets
        self.tiltLabel = QLabel("Desired Tilt Angle: 0")
        self.tiltLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tiltLabel.setStyleSheet(labelStyle)
        self.tiltLabel.setFont(font)

        self.tiltAddButton = QPushButton("+")
        self.tiltAddButton.clicked.connect(lambda: self.tiltButtonsClicked("+"))
        self.tiltSubButton = QPushButton("-")
        self.tiltSubButton.clicked.connect(lambda: self.tiltButtonsClicked("-"))

        # height widgets
        self.heightLabel = QLabel("Desired Height: 0")
        self.heightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heightLabel.setStyleSheet(labelStyle)
        self.heightLabel.setFont(font)

        self.heightAddButton = QPushButton("+")
        self.heightAddButton.clicked.connect(lambda: self.heightButtonsClicked("+"))
        self.heightSubButton = QPushButton("-")
        self.heightSubButton.clicked.connect(lambda: self.heightButtonsClicked("-"))

        # Tilt buttons
        self.tiltButtonsLayout = QHBoxLayout()
        self.tiltButtonsLayout.addWidget(self.tiltAddButton)
        self.tiltButtonsLayout.addWidget(self.tiltSubButton)

        # Height buttons
        self.heightButtonsLayout = QHBoxLayout()
        self.heightButtonsLayout.addWidget(self.heightAddButton)
        self.heightButtonsLayout.addWidget(self.heightSubButton)

        self.backButton = QPushButton("BACK")
        self.backButton.clicked.connect(self.backButtonClicked)

        self.editButton = QPushButton("EDIT KEYFRAME")
        self.editButton.clicked.connect(self.editKeyframeClicked)
        self.heightLabel.setMaximumHeight(100)
        self.tiltLabel.setMaximumHeight(100)

        self.navButtonsLayout = QHBoxLayout()
        self.navButtonsLayout.addWidget(self.backButton)
        self.navButtonsLayout.addWidget(self.editButton)

        window.addWidget(self.heightLabel, 0, 0)
        window.addLayout(self.heightButtonsLayout, 1, 0)
        window.addWidget(self.tiltLabel, 0, 1)
        window.addLayout(self.tiltButtonsLayout, 1, 1)
        window.addLayout(self.navButtonsLayout, 2, 0, 1, 2)

        for layout in (
            self.heightButtonsLayout,
            self.tiltButtonsLayout,
            self.navButtonsLayout,
        ):
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.setMinimumSize(100, 80)
                    widget.setStyleSheet(buttonStyle)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)
        self.showMaximized()

    def editKeyframeClicked(self):
        if secondScreen.selectedKeyframeIndex is not None:
            liftHeight = self.__desiredHeight
            tiltDegree = self.__desiredTilt

            if liftHeight and tiltDegree:
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

    def loadKeyframesData(self):
        try:
            with open(self.keyframesDataFile, "r") as jsonFile:
                self.keyframesData = json.load(jsonFile)
        except FileNotFoundError:
            self.keyframesData = {}

    def tiltButtonsClicked(self, operator):
        if operator == "+":
            self.__desiredTilt += 200
        elif operator == "-":
            self.__desiredTilt -= 200
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__desiredTilt))

    def heightButtonsClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight < 72000:
                self.__desiredHeight += 2000
        elif operator == "-":
            if self.__desiredHeight > 0:
                self.__desiredHeight -= 2000
        self.heightLabel.setText(
            "Desired Height: " + str(int(self.__desiredHeight / 400))
        )

    def backButtonClicked(self):
        widget.setCurrentWidget(secondScreen)


class KeyframeCalculator(QMainWindow):
    __objHeight = 30
    __objSize = ""

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Keyframe Calculator")
        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        layout = QGridLayout()

        # Height slider Widgets
        self.heightSliderLabel = QLabel("Height: 30")
        self.heightSliderLabel.setFont(font)
        self.heightSliderLabel.setStyleSheet(labelStyle)

        self.heightSlider = QSlider()
        self.heightSlider.setMinimum(30)
        self.heightSlider.setMaximum(140)
        self.heightSlider.setPageStep(1)
        self.heightSlider.setFixedWidth(100)
        self.heightSlider.setStyleSheet(sliderStylesheet)
        self.heightSlider.valueChanged.connect(self.updateHeightSliderLabel)

        # Size slider Widgets
        self.sizeSliderLabel = QLabel("Size: Small")
        self.sizeSliderLabel.setFont(font)
        self.sizeSliderLabel.setStyleSheet(labelStyle)

        self.sizeSlider = QSlider()
        self.sizeSlider.setMinimum(0)
        self.sizeSlider.setMaximum(2)
        self.sizeSlider.setPageStep(1)
        self.sizeSlider.setFixedWidth(100)
        self.sizeSlider.setStyleSheet(sliderStylesheet)
        self.sizeSlider.valueChanged.connect(self.updateSizeSliderLabel)

        self.backButton = QPushButton("Back")
        self.backButton.setStyleSheet(buttonStyle)
        self.backButton.setMinimumSize(80, 80)
        self.backButton.clicked.connect(self.back)
        self.calculateButton = QPushButton("Calculate")
        self.calculateButton.setStyleSheet(buttonStyle)
        self.calculateButton.setMinimumSize(80, 80)
        self.calculateButton.clicked.connect(self.calculate)

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

    def back(self):
        widget.setCurrentWidget(secondScreen)

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

    def updateSizeSliderLabel(self, value):
        size_options = ["Small", "Medium", "Large"]
        self.sizeSliderLabel.setText(f"Size: {size_options[value]}")
        self.__objSize = value

    def updateHeightSliderLabel(self, value):
        self.heightSliderLabel.setText("Height: " + str(value))
        self.__objHeight = value


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
widget.setCurrentWidget(
    firstScreen
)  # setting the page that you want to load when application starts up.
widget.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
widget.showMaximized()
widget.show()
app.exec()