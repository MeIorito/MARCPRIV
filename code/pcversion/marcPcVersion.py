# Note that this is a PC only version. Meant for testing the visuals and logic of the program without the need of a Raspberry Pi.

import sys
import json
import time
import math
import slack
import random
import threading
from time import sleep

# import RPi.GPIO as GPIO
from PyQt6 import QtCore
from PyQt6.QtCore import *

# from motorfunctions import all
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QSlider

# Constants | slack auth | settings file | font size
slackToken = "xoxb-5867825218247-5875744156982-TuLlFjvAptQvxyraY4ZQ4Vm6"
settingsFile = "code\settings.txt"
cycleCounterFile = 'code\cycleCounter.txt'
font = QFont()
font.setPointSize(11)
size = (100, 80)
# Measure the distance between the object and the camare when leveled, this is for calculating keyframes
objDistance = 45
totHeight = 180
conversionValue = 400

# 4 standard styles for all types of used widgets, format like css
buttonStyle = """
    QPushButton {
        background-color: #505164; /* Background color */
        border: 4px solid #585a6e; /* Border color */
        color: #dddde4; /* Text color */
        padding: 8px 16px; /* Padding around the text */
        border-radius: 15px; /* Rounded corners */
        font-size: 18px; /* Font size */
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
        font-size: 16px; /* Entry font size */
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
        color: #ffffff; /* Corner button text color */
        font-size: 14px; /* Corner button font size */
        font-weight: bold; /* Corner button font weight */
        padding: 8px; /* Corner button section padding */
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
    __marc_berichten = [
        "Scan voltooid! Tijd voor de grote onthulling.",
        "Ta-da! De 3D-scan is gereed voor inspectie.",
        "Missie volbracht! Wat denk je van het resultaat?",
        "Goed nieuws! De scan is klaar om te bekijken.",
        "Bing! De scan is afgerond. Laten we kijken wat ik heb vastgelegd.",
        "Het scannen is voltooid. Benieuwd naar het eindresultaat?",
        "Klaar om te zien wat ik heb gemaakt? De scan is compleet!",
        "Het wachten is voorbij! Bekijk snel de 3D-beelden.",
        "MARC heeft zijn magie weer laten zien. Het resultaat is hier!",
        "De 3D-scan is gereed. Wat vind je ervan?",
    ]

    # Constructor, needs the wait times for the cycle
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
        if cycleCounter["CycleCounter"] < 200:
            startTime = time.time()
            firstScreen.setCycleState(True)
            # Total amount of keyframes
            totKeyframes = secondScreen.keyframeTable.rowCount()
            with open(settingsFile, "r") as jsonFile:
                keyframesData = json.load(jsonFile)

            # TODO Implementeer later de onderstaande berkeningen
            # amountOfTurns = int(amountCounter.get())
            # currentMode = turntableMode.get()
            # degreesPerRotation = int(32000/amountOfTurns)

            # Loops through all keyframes and moves the height and tilt accordingly
            for i in range(1, totKeyframes + 1):
                if firstScreen.getEmercenyFlag() != True:
                    keyframe = keyframesData[f"Keyframe {i}"]

                    if keyframe["liftHeight"] is not None:
                        if firstScreen.getEmercenyFlag() != True:
                            print("Camera gaat naar gewilde positie!")
                            sleep(5)
                            print("tilt van camera gaat naar gewilde positie!")
                            sleep(5)
                            for x in range(self.__picsPerKeyframe):
                                if firstScreen.getEmercenyFlag() != True:
                                    print("Tafel draait!")
                                    # sleep(2)
                                    sleep(self.__beforeWaitTime)
                                    print("Maakt foto!")
                                    # sleep(self.__afterWaitTime)
                                else:
                                    text = "The emergency button has been pressed!"
                                    print("The emergency button has been pressed!")
                                    break
                        else:
                            break
                        #     # if currentMode != 'Disabled':
                        #     for j in range(amountOfTurns):
                        #         if GPIO.input(EMERGENCY) != False:
                        #             print("Emergency triggered")
                        #             break
                        #         motorTableCW(degreesPerRotation)
                        #         sleep(beforeWaitTime)
                        #         captureImage()
                        #         sleep(afterWaitTime)
                        # else:
                        #     sleep(beforeWaitTime)
                        #     captureImage()
                        #     sleep(afterWaitTime)

                        # Set slider to height of current keyframe
                        firstScreen.setSliderVal(keyframe["liftHeight"])
                        firstScreen.setTiltLabelVal(keyframe["tiltDegree"])
                        text = (
                            str(random.choice(self.__marc_berichten))
                            + " Het kostte: "
                            + str(round(time.time() - startTime, 2))
                            + " seconden"
                        )
                else:
                    text = "The emergency button has been pressed!"
                    break
            # Sends message to Slack workspace
            try:
                client = slack.WebClient(token=slackToken)
                client.chat_postMessage(channel="#testbot", text=text)
            except:
                print("Er is wat fout gegaan met de verbinding met Slack!")
            # Updates busy flag
            cycleCounter["CycleCounter"] += 1
            with open(cycleCounterFile, "w") as jsonFile:
                json.dump(cycleCounter, jsonFile, indent=4)
            firstScreen.setCycleState(False)


class MainWindow(QMainWindow):
    # All important values
    __sliderValue = 0
    __waitBeforeTime = 0
    __waitAfterTime = 2
    __picsPerKeyframe = 20
    __tiltValue = 0
    __isCycleBusy = False
    __emergencyFlag = False

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
        self.menuButtons = self.setupMenuButtons(buttonStyle, size)

        self.moveButton = self.setupButton("MOVE", self.moveButtonClicked, buttonStyle, size)
        self.resetLiftButton = self.setupButton("RESET", self.reset, buttonStyle, size)
        self.quickAddKeyframeButton = self.setupButton("QUICK ADD KEYFRAME", self.quickAddKeyframe, buttonStyle, size)
        self.startCycleButton = self.setupButton("START CYCLE", self.cycle, buttonStyle, size)
        self.newZeroButton = self.setupButton("SET NEW ZERO", self.newZeroClicked, buttonStyle, size)
        self.emergencyStopButton = self.setupEmergencyStopButton(buttonStyle, size)

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

    def setupMenuButtons(self, style, size):
        self.keyframeButton = self.setupButton("KFM", self.keyframeMenuClicked, style, size)
        self.turntableButton = self.setupButton("TTM", self.turntableMenuClicked, style, size)

        menuButtonsLayout = QHBoxLayout()
        menuButtonsLayout.addWidget(self.keyframeButton)
        menuButtonsLayout.addWidget(self.turntableButton)

        return menuButtonsLayout

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


    def moveToPosition(self, goToPos):
        curLiftHeight = self.__sliderValue
        stepsNeeded = int(goToPos) - curLiftHeight
        curLiftHeight += stepsNeeded
        if stepsNeeded <= 0:
            stepsNeeded = stepsNeeded - stepsNeeded * 2
            print(str(stepsNeeded))
            # motorLiftDown(stepsNeeded)
        elif stepsNeeded >= 0:
            # motorLiftUp(stepsNeeded)
            print(str(stepsNeeded))

    def angleToPosition(self, goToPos):
        curTiltAngle = self.__tiltValue
        stepsNeeded = int(goToPos) - curTiltAngle
        curTiltAngle += stepsNeeded
        if stepsNeeded <= 0:
            stepsNeeded = stepsNeeded - stepsNeeded * 2
            print(str(stepsNeeded))
            # motorTiltCW(stepsNeeded)
        elif stepsNeeded >= 0:
            # motorTiltCCW(stepsNeeded)
            print(str(stepsNeeded))

    # Called when the slider is used, changes the label and the variable for the lift height
    def update_slider_label(self, value):
        self.sliderLabel.setText("Height: " + str(int(value / 400)))
        self.__sliderValue = value

    def moveButtonClicked(self):
        # TODO: Implement logic for the MOVE button
        print("LIFT HEIGHT SET TO:", self.__sliderValue, "CM")

    # Called when the reset button is clicked, points to other function
    def quickAddKeyframe(self):
        thirdScreen.quickAddKeyframe(self.__sliderValue, self.__tiltValue)

    # Depending on which button got sent here it adds or subs 20 from the tilt variable. Add button has operator = + and sub has operator = -
    def tiltButtonsClicked(self, operator):
        if operator == "+":
            self.__tiltValue += 200
        elif operator == "-":
            self.__tiltValue -= 200
        self.tiltLabel.setText("Desired Tilt Angle: " + str(self.__tiltValue))

    # Depending on what the source and operator are, the correct value is added or subbed from the right time variable. Also refreshes the screen
    def timeButtonsClicked(self, source, operator):
        if source == "waitBefore" and operator == "+":
            self.__waitBeforeTime += 0.5
        elif source == "waitBefore" and operator == "-":
            self.__waitBeforeTime -= 0.5
        elif source == "waitAfter" and operator == "+":
            self.__waitAfterTime += 0.5
        elif source == "waitAfter" and operator == "-":
            self.__waitAfterTime -= 0.5
        print(self.__waitAfterTime, " : ", self.__waitBeforeTime)
        self.waitBeforeLabel.setText("Wait Before Time: " + str(self.__waitBeforeTime))
        self.waitAfterLabel.setText("Wait After Time: " + str(self.__waitAfterTime))

    # Depending on which button got sent here it adds or subs 1 from the pictures per keyframe variable. Add button has operator = + and sub has operator = -. Also refreshes the screen
    def picsPerKeyframeClicked(self, operator):
        if operator == "+":
            self.__picsPerKeyframe += 1
        elif operator == "-":
            self.__picsPerKeyframe -= 1
        self.picsPerKeyframeLabel.setText("Pictures: " + str(self.__picsPerKeyframe))

    # Changes screen
    def keyframeMenuClicked(self):
        widget.setCurrentWidget(secondScreen)

    def turntableMenuClicked(self):
        widget.setCurrentWidget(sixthScreen)

    def emergencyStopClicked(self):
        if self.__emergencyFlag == False:
            self.__emergencyFlag = True
            self.emergencyStopButton.setStyleSheet(
                buttonStyle
                + """
                QPushButton#emergencyStopButton {
                    background-color : #d80006; /* Different background color */
                    border : 4px solid #d80006;
                }
            """
            )
        else:
            self.__emergencyFlag = False
            self.emergencyStopButton.setStyleSheet(
                buttonStyle
                + """
                QPushButton#emergencyStopButton {
                    background-color : #790004; /* Different background color */
                    border : 4px solid #790004;
                }
            """
            )

    # Checks if scanner isn't busy or in emergency stop mode, if not starts the cycle thread and changes the busy flag
    def cycle(self):
        if self.__isCycleBusy != True and self.__emergencyFlag != True:
            newCycleThread = cycleThread(
                self.__waitBeforeTime, self.__waitAfterTime, self.__picsPerKeyframe
            )
            newCycleThread.start()

    def setCycleState(self, state):
        self.__isCycleBusy = state

    def getEmercenyFlag(self):
        return self.__emergencyFlag

    # Sets the slider position
    def setSliderVal(self, value):
        self.slider.setSliderPosition(value)

    def newZeroClicked(self):
        self.__tiltValue = 0
        self.tiltLabel.setText("Angle: " + str(self.__tiltValue))

    def setTiltLabelVal(self, val):
        self.__tiltValue = val
        self.tiltLabel.setText("Desired Tilt Angle: " + str(val))

    # Not working yet
    def closeEvent(self, event):
        print("Ik doe nog even snel iets!!")
        event.accept()

    def reset(self):
        print("Lift aan het resetten!")
        self.moveToPosition(0)
        self.angleToPosition(0)


class KeyframeListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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

        for row in range(self.keyframeTable.rowCount()):
            self.keyframeTable.setRowHeight(row, 70)
            self.keyframeTable.setColumnWidth(row, 110)

        self.keyframeTable.verticalScrollBar().setStyleSheet(tableSliderStyle)

        # Right side: Buttons and entry fields
        rightLayout = QVBoxLayout()  # Vertical layout for buttons and entry fields

        self.backButton = self.setupButton("BACK", self.back, buttonStyle, size)
        self.addButton = self.setupButton("ADD KEYFRAME", self.addKeyframe, buttonStyle, size)
        self.editButton = self.setupButton("EDIT KEYFRAME", self.editKeyframe, buttonStyle, size)
        self.deleteButton = self.setupButton("DELETE KEYFRAME", self.deleteKeyframe, buttonStyle, size)
        self.keyframeCalculator = self.setupButton("CALC KEYFRAMES", self.kfcClicked, buttonStyle, size)

        rightLayout.addWidget(self.backButton)
        rightLayout.addWidget(self.addButton)
        rightLayout.addWidget(self.editButton)
        rightLayout.addWidget(self.deleteButton)
        rightLayout.addWidget(self.keyframeCalculator)

        # Add the QTableWidget and the right side layout to the main horizontal layout
        centralLayout.addWidget(self.keyframeTable, 0, 0)
        centralLayout.addLayout(rightLayout, 0, 1)

        centralWidget = QWidget()
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

        self.selectedKeyframeIndex = None


    def setupButton(self, text, slot, style, size):
        button = QPushButton(text)
        button.clicked.connect(slot)
        button.setStyleSheet(style)
        button.setMinimumSize(size[0], size[1])
        return button

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
            ["Keyframe", "Lift Height", "Tilt Degree", "Time Added"]
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

    # Dynamically adds keyframes
    def addKeyframe(self):
        widget.setCurrentWidget(thirdScreen)

    # Dynamically edits keyframes
    def editKeyframe(self):
        widget.setCurrentWidget(fourthScreen)

    # Dynamically deletes keyframes TODO find better solution 
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

    def kfcClicked(self):
        widget.setCurrentWidget(fithScreen)

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

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_increment)
        self.button_pressed = False

        self.setWindowTitle("Keyframe List")
        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        self.keyframesDataFile = settingsFile
        self.loadKeyframesData()

        window = QGridLayout()

        self.heightLabel = self.setupLabel("Desired height: 0", font, labelStyle)
        self.greatHeightButtonsLayout = self.setupHeightButtons(buttonStyle, size, 4000)
        self.smallHeightButtonsLayout = self.setupHeightButtons(buttonStyle, size, 400)
        self.tiltLabel = self.setupLabel("Desired Tilt Angle: 0", font, labelStyle)
        self.tiltButtonsLayout = self.setupTiltButtons(buttonStyle, size)
        self.backButton = self.setupButton("BACK", self.backButtonClicked, buttonStyle, size)
        self.addButton = self.setupButton("ADD KEYFRAME", self.addKeyframeClicked, buttonStyle, size)

        self.navButtonsLayout = QHBoxLayout()
        self.navButtonsLayout.addWidget(self.backButton)
        self.navButtonsLayout.addWidget(self.addButton)

        window.addWidget(self.heightLabel, 0, 0)
        window.addLayout(self.greatHeightButtonsLayout, 1, 0)
        window.addLayout(self.smallHeightButtonsLayout, 2, 0)
        window.addWidget(self.tiltLabel, 0, 1)
        window.addLayout(self.tiltButtonsLayout, 1, 1)
        window.addLayout(self.navButtonsLayout, 3, 0, 1, 2)


        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)

    # generic function for setting up labels
    def setupLabel(self, text, font, style):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(font)
        label.setStyleSheet(style)
        return label

    # generic function for setting up buttons
    def setupButton(self, text, slot, style, size):
        button = QPushButton(text)
        button.clicked.connect(slot)
        button.setStyleSheet(style)
        button.setMinimumSize(size[0], size[1])
        return button

    # function for setting up tilt buttons
    def setupHeightButtons(self, style, size, changeValue):
        heightAddButton = self.setupButton(
            f'+ {changeValue/conversionValue}', lambda: self.heightButtonsClicked("+", changeValue), style, size
        )
        heightSubButton = self.setupButton(
            f'- {changeValue/conversionValue}', lambda: self.heightButtonsClicked("-", changeValue), style, size
        )

        heightButtonsLayout = QHBoxLayout()
        heightButtonsLayout.addWidget(heightSubButton)
        heightButtonsLayout.addWidget(heightAddButton)

        return heightButtonsLayout

    def setupTiltButtons(self, style, size):
        tiltAddButton = self.setupButton("+", lambda: self.tiltButtonsClicked("+"), style, size)
        tiltSubButton = self.setupButton("-", lambda: self.tiltButtonsClicked("-"), style, size)

        tiltButtonsLayout = QHBoxLayout()
        tiltButtonsLayout.addWidget(tiltSubButton)
        tiltButtonsLayout.addWidget(tiltAddButton)

        return tiltButtonsLayout

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

    def heightButtonsClicked(self, operator, changeValue):
        if operator == "+":
            if self.__desiredHeight + changeValue <= 72000:
                self.__desiredHeight += changeValue
        elif operator == "-":
            if self.__desiredHeight - changeValue >= 0:
                self.__desiredHeight -= changeValue
        self.heightLabel.setText(
            "Desired Height: " + str(int(self.__desiredHeight / conversionValue))
        )

        self.updateHeightLabel()

    def updateHeightLabel(self):
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / 400))

    def reset_increment(self):
        # Reset the button press state
        self.button_pressed = False
        self.counter = 0
        self.increment_amount = 400
        self.timer.stop()

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
        if keyframeName and liftHeight and tiltDegree:
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
                secondScreen.keyframeTable.setColumnWidth(column, 110)
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
                secondScreen.keyframeTable.setColumnWidth(column, 110)


class EditKeyframeWindow(QMainWindow):
    __desiredHeight = 0
    __desiredTilt = 0

    def __init__(self):
        super().__init__()

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_increment)
        self.button_pressed = False

        self.setWindowTitle("Keyframe List")
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
            current_time = time.time()
            if not self.button_pressed:
                self.button_pressed = True
                self.previous_press = current_time
                self.counter = 1
                self.increment_amount = 400
                self.__desiredHeight += self.increment_amount
                self.heightLabel.setText(f"Value: {self.__desiredHeight}")
                self.timer.start(3000)  # Start a 5-second timer
            else:
                time_difference = current_time - self.previous_press
                if time_difference <= 3:
                    self.counter += 1
                    if self.counter >= 8:
                        self.increment_amount = 2000
                    self.__desiredHeight += self.increment_amount
                    self.heightLabel.setText(f"Value: {self.__desiredHeight}")
                    print("Incrementing by", self.increment_amount)
                else:
                    self.reset_increment()
        elif operator == "-":
            self.__desiredHeight -= 2000
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / 400))

    def backButtonClicked(self):
        widget.setCurrentWidget(secondScreen)

    def reset_increment(self):
        self.button_pressed = False
        self.timer.stop()
        self.counter = 0
        self.increment_amount = 1


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
        self.heightSliderLabel = self.setupLabel("Height: 30", font, labelStyle)
        self.heightSlider = self.setupSlider(30, 160, 1, 100, self.updateHeightSliderLabel)
        self.sizeSliderLabel = self.setupLabel("Size: small", font, labelStyle)
        self.sizeSlider = self.setupSlider(0, 2, 1, 100, self.updateSizeSliderLabel)
        self.backButton = self.setupButton("Back", self.back, buttonStyle, size)
        self.calculateButton = self.setupButton("Calculate", self.calculate, buttonStyle, size)

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

    def setupSlider(self, min, max, pageStep, width, slot):
        slider = QSlider()
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setPageStep(pageStep)
        slider.setFixedWidth(width)
        slider.setStyleSheet(sliderStylesheet)
        slider.valueChanged.connect(slot)
        return slider

    # generic function for setting up labels
    def setupLabel(self, text, font, style):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(font)
        label.setStyleSheet(style)
        return label

    # generic function for setting up buttons
    def setupButton(self, text, slot, style, size):
        button = QPushButton(text)
        button.clicked.connect(slot)
        button.setStyleSheet(style)
        button.setMinimumSize(size[0], size[1])
        return button

    def back(self):
        widget.setCurrentWidget(secondScreen)

    def calculate(self):
        oppositeSide = objDistance
        scannerHeight = totHeight
        conversionVal = conversionValue
        size = self.__objSize
        height = self.__objHeight

        if size == 0:
            heightIncr = 8
        elif size == 1:
            heightIncr = 10
        else:
            heightIncr = 12

        keyframes_data = {}  # Dictionary to store keyframe data
        initialHeight = height - (heightIncr * 3)

        # Calculate keyframe data using trigonometry
        for i in range(1, 8):
            newHeight = initialHeight + i * heightIncr
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


class TurntableMenuWindow(QMainWindow):
    turntableSpeed = "Medium"

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Turntable Menu")
        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        window = QGridLayout()

        self.speedLabel = self.setupLabel(f'Turntable speed: {self.turntableSpeed}', font, labelStyle)
        self.speedButtonsLayout = self.setupSpeedButtons(buttonStyle, size)
        self.backButton = self.setupButton("BACK", self.back, buttonStyle, size)

        window.addWidget(self.speedLabel, 0, 1)
        window.addLayout(self.speedButtonsLayout, 1, 1)
        window.addWidget(self.backButton, 2, 1)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)

    # generic function for setting up labels
    def setupLabel(self, text, font, style):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(font)
        label.setStyleSheet(style)
        return label
    
    # generic function for setting up buttons
    def setupButton(self, text, slot, style, size):
        button = QPushButton(text)
        button.clicked.connect(slot)
        button.setStyleSheet(style)
        button.setMinimumSize(size[0], size[1])
        return button
    
    # function for setting up speed options. Slow, medium and fast
    def setupSpeedButtons(self, style, size):
        slowButton = self.setupButton('Slow', lambda: self.speedButtonsClicked('Slow'), style, size)
        mediumButton = self.setupButton('Medium', lambda: self.speedButtonsClicked('Medium'), style, size)
        fastButton = self.setupButton('Fast', lambda: self.speedButtonsClicked('Fast'), style, size)

        speedButtonsLayout = QHBoxLayout()
        speedButtonsLayout.addWidget(slowButton)
        speedButtonsLayout.addWidget(mediumButton)
        speedButtonsLayout.addWidget(fastButton)

        return speedButtonsLayout
    
    def speedButtonsClicked(self, speed):
        self.turntableSpeed = speed
        self.speedLabel.setText(f'Turntable speed: {self.turntableSpeed}')

    def back(self):
        widget.setCurrentWidget(firstScreen)

app = QApplication(sys.argv)
widget = QStackedWidget()
firstScreen = MainWindow()

widget.addWidget(firstScreen)
secondScreen = KeyframeListWindow()
thirdScreen = NewKeyframeWindow()
fourthScreen = EditKeyframeWindow()
fithScreen = KeyframeCalculator()
sixthScreen = TurntableMenuWindow()
widget.addWidget(fourthScreen)
widget.addWidget(thirdScreen)
widget.addWidget(secondScreen)
widget.addWidget(fithScreen)
widget.addWidget(sixthScreen)
widget.setCurrentWidget(firstScreen)
widget.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
widget.show()
app.exec()