import json
from constants import constants
from classes import *
from PyQt5.QtCore import *
from constants import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow

class NewKeyframeWindow(QMainWindow):
    __desiredHeight = 0
    __desiredTilt = 0

    def __init__(self, menuController):
        super().__init__()

        self.mc = menuController

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        self.keyframesDataFile = constants.settingsFile
        self.loadKeyframesData()

        window = QGridLayout()

        # create the necessary widgets using the factory classes
        self.heightLabel = constants.labelFactory.create("Desired height: 0", constants.font, constants.labelStyle)

        self.heightBigSubButton = constants.buttonFactory.create("--", lambda: self.heightButtonsBigClicked("-"), constants.buttonStyle, constants.size)
        self.heightBigAddButton = constants.buttonFactory.create("++", lambda: self.heightButtonsBigClicked("+"), constants.buttonStyle, constants.size)
        self.greatHeightButtonsLayout = constants.hboxLayoutFactory.create(self.heightBigSubButton, self.heightBigAddButton)

        self.heightSmallSubButton = constants.buttonFactory.create("-", lambda: self.heightButtonsSmallClicked("-"), constants.buttonStyle, constants.size)
        self.heightSmallAddButton = constants.buttonFactory.create("+", lambda: self.heightButtonsSmallClicked("+"), constants.buttonStyle, constants.size)
        self.smallHeightButtonsLayout = constants.hboxLayoutFactory.create(self.heightSmallSubButton, self.heightSmallAddButton)

        self.tiltLabel = constants.labelFactory.create("Desired Tilt Angle: 0", constants.font, constants.labelStyle)

        self.tiltAddButton = constants.buttonFactory.create("+", lambda: self.tiltButtonsClicked("+"), constants.buttonStyle, constants.size)
        self.tiltSubButton = constants.buttonFactory.create("-", lambda: self.tiltButtonsClicked("-"), constants.buttonStyle, constants.size)
        self.tiltButtonsLayout = constants.hboxLayoutFactory.create(self.tiltSubButton, self.tiltAddButton)

        self.backButton = constants.buttonFactory.create("BACK", self.backButtonClicked, constants.buttonStyle, constants.size)
        self.navButtonsLayout = constants.hboxLayoutFactory.create(self.backButton)

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
            "Desired Height: " + str(int(self.__desiredHeight / constants.conversionValue))
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
            "Desired Height: " + str(int(self.__desiredHeight / constants.conversionValue))
        )

        self.updateHeightLabel()

    # Updates the height label
    def updateHeightLabel(self):
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / constants.conversionValue))

    # Goes back to the main screen
    def backButtonClicked(self):
        self.mc.showKeyframeMenu()

    def quickAddKeyframe(self, desiredHeight, desiredTilt):
        # calculates next keyrame number and creates the name
        nextKeyframe = self.mc.secondScreen.keyframeTable.rowCount() + 1
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
            self.mc.secondScreen.keyframesData[keyframeName] = keyframeData
            self.mc.secondScreen.saveKeyframesData()
            self.mc.secondScreen.createKeyframeTable()
            self.mc.secondScreen.keyframeTable.setRowHeight(nextKeyframe - 1, 70)
            for column in range(secondScreen.keyframeTable.columnCount()):
                self.mc.secondScreen.keyframeTable.setColumnWidth(column, 125)
