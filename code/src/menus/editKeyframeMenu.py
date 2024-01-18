import json
from constants import constants
from threads import *
from PyQt5.QtCore import *
from constants import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow

class EditKeyframeWindow(QMainWindow):
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
        self.tiltLabel = constants.labelFactory.create("Desired Tilt Angle: 0", constants.font, constants.labelStyle)

        self.tiltAddButton = constants.buttonFactory.create("+", lambda: self.tiltButtonsClicked("+"), constants.buttonStyle, constants.size)
        self.tiltSubButton = constants.buttonFactory.create("-", lambda: self.tiltButtonsClicked("-"), constants.buttonStyle, constants.size)
        self.tiltButtonsLayout = constants.hboxLayoutFactory.create(self.tiltSubButton, self.tiltAddButton)

        self.heightLabel = constants.labelFactory.create("Desired height: 0", constants.font, constants.labelStyle)

        self.heightSubSmallButton = constants.buttonFactory.create("-", lambda: self.heightButtonsSmallClicked("-"), constants.buttonStyle, constants.size)
        self.heightAddSmallButton = constants.buttonFactory.create("+", lambda: self.heightButtonsSmallClicked("+"), constants.buttonStyle, constants.size)
        self.heightButtonsSmallLayout = constants.hboxLayoutFactory.create(self.heightSubSmallButton, self.heightAddSmallButton)

        self.heightSubBigButton = constants.buttonFactory.create("--", lambda: self.heightButtonsBigClicked("-"), constants.buttonStyle, constants.size)
        self.heightAddBigButton = constants.buttonFactory.create("++", lambda: self.heightButtonsBigClicked("+"), constants.buttonStyle, constants.size)
        self.heightButtonsBigLayout = constants.hboxLayoutFactory.create(self.heightSubBigButton, self.heightAddBigButton)

        self.backButton = constants.buttonFactory.create("BACK", self.backButtonClicked, constants.buttonStyle, constants.size)

        self.editButton = constants.buttonFactory.create("EDIT KEYFRAME", self.editKeyframeClicked, constants.buttonStyle, constants.size)

        self.navButtonsLayout = constants.hboxLayoutFactory.create(self.backButton, self.editButton)

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
        if self.mc.secondScreen.selectedKeyframeIndex is not None:
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
                keyframeRow = self.mc.secondScreen.selectedKeyframeIndex.row()
                keyframe = self.mc.secondScreen.keyframeTable.item(keyframeRow, 0).text()
                self.mc.secondScreen.keyframesData[keyframe] = keyframeData
                self.mc.secondScreen.saveKeyframesData()
                self.mc.secondScreen.createKeyframeTable()
        self.mc.showKeyframeMenu()

    # Loads the json settings file into a local variable for esier use
    def loadKeyframesData(self):
        try:
            with open(self.keyframesDataFile, "r") as jsonFile:
                self.keyframesData = json.load(jsonFile)
        except FileNotFoundError:
            self.keyframesData = {}

    def updateHeightLabel(self):
        self.heightLabel.setText("Desired height: " + str(self.__desiredHeight / constants.conversionValue))

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
        self.heightLabel.setText("Desired Height: " + str(int(self.__desiredHeight / constants.conversionValue)))

        self.updateHeightLabel()

    def heightButtonsSmallClicked(self, operator):
        if operator == "+":
            if self.__desiredHeight + 400 <= 72000:
                self.__desiredHeight += 400
        elif operator == "-":
            if self.__desiredHeight - 400 >= 0:
                self.__desiredHeight -= 400
        self.heightLabel.setText("Desired Height: " + str(int(self.__desiredHeight / constants.conversionValue)))

        self.updateHeightLabel()

    # Goes back to the main screen
    def backButtonClicked(self):
        self.mc.showKeyframeMenu()
