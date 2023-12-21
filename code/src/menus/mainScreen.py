from classes import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from constants import constants
from classes import cycle
from controllers import motorfunctions
from PyQt5.QtWidgets import QMainWindow

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

    # Constructor with menuController as parameter
    def __init__(self, menuController):
        super().__init__()

        self.mc = menuController

        self.setStyleSheet("background-color: #343541")
        self.setGeometry(100, 100, 600, 400)

        layout = QGridLayout()

        # Creates all the widgets using the factory classes wich are imported from constants
        self.slider = constants.sliderFactory.create(0, 72000, 2000, 100, 20, constants.sliderStylesheet, self.update_slider_label)
        self.sliderLabel = constants.labelFactory.create("Height: 0", constants.font, constants.labelStyle)
        self.tiltLabel = constants.labelFactory.create("Tilt: 0", constants.font, constants.labelStyle)
        self.waitBeforeLabel = constants.labelFactory.create(f'Wait Before Time: {self.__waitBeforeTime}', constants.font, constants.labelStyle)
        self.waitAfterLabel = constants.labelFactory.create(f'Wait After Time: {self.__waitAfterTime}', constants.font, constants.labelStyle)
        self.picsPerKeyframeLabel = constants.labelFactory.create(f'Pictures: {self.__picsPerKeyframe}', constants.font, constants.labelStyle)

        self.tiltButtonSub = constants.buttonFactory.create("-", lambda: self.tiltButtonsClicked("-"), constants.buttonStyle, constants.size)
        self.tiltButtonAdd = constants.buttonFactory.create("+", lambda: self.tiltButtonsClicked("+"), constants.buttonStyle, constants.size)
        self.tiltButtons = constants.hboxLayoutFactory.create(self.tiltButtonSub, self.tiltButtonAdd)

        self.waitBeforeButtonSub = constants.buttonFactory.create("-", lambda: self.waitBeforeClicked("-"), constants.buttonStyle, constants.size)
        self.waitBeforeButtonAdd = constants.buttonFactory.create("+", lambda: self.waitBeforeClicked("+"), constants.buttonStyle, constants.size)
        self.waitBeforeButtons = constants.hboxLayoutFactory.create(self.waitBeforeButtonSub, self.waitBeforeButtonAdd)

        self.waitAfterButtonSub = constants.buttonFactory.create("-", lambda: self.waitAfterClicked("-"), constants.buttonStyle, constants.size)
        self.waitAfterButtonAdd = constants.buttonFactory.create("+", lambda: self.waitAfterClicked("+"), constants.buttonStyle, constants.size)
        self.waitAfterButtons = constants.hboxLayoutFactory.create(self.waitAfterButtonSub, self.waitAfterButtonAdd)

        self.picsPerKeyframeButtonSub = constants.buttonFactory.create("-", lambda: self.picsPerKeyframeClicked("-"), constants.buttonStyle, constants.size)
        self.picsPerKeyframeButtonAdd = constants.buttonFactory.create("+", lambda: self.picsPerKeyframeClicked("+"), constants.buttonStyle, constants.size)
        self.picsPerKeyframeButtons = constants.hboxLayoutFactory.create(self.picsPerKeyframeButtonSub, self.picsPerKeyframeButtonAdd)

        self.keyframeButton = constants.buttonFactory.create("KFM", self.keyframeMenuClicked, constants.buttonStyle, constants.size)
        self.turntableButton = constants.buttonFactory.create("TTM", self.turntableMenuClicked, constants.buttonStyle, constants.size)
        self.menuButtons = constants.hboxLayoutFactory.create(self.keyframeButton, self.turntableButton)

        self.moveButton = constants.buttonFactory.create("MOVE", self.moveButtonClicked, constants.buttonStyle, constants.size)
        self.resetLiftButton = constants.buttonFactory.create("RESET", self.reset, constants.buttonStyle, constants.size)
        self.quickAddKeyframeButton = constants.buttonFactory.create("QUICK ADD KEYFRAME", self.quickAddKeyframe, constants.buttonStyle, constants.size)
        self.startCycleButton = constants.buttonFactory.create("START CYCLE", self.cycle, constants.buttonStyle, constants.size)
        self.newZeroButton = constants.buttonFactory.create("RESET TILT", self.resetTiltButtonClicked, constants.buttonStyle, constants.size)
        self.emergencyStopButton = constants.buttonFactory.create("EMERGENCY STOP", self.emergencyStopClicked , constants.emergencyButtonOffStyle, constants.size)

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
            motorfunctions.motorLiftDown(stepsNeeded)
        elif stepsNeeded >= 0:
            motorfunctions.motorLiftUp(stepsNeeded)
        self.__heightValue = self.__desiredHeight

    # Calculates the steps needed to move to a certain tilt angle.
    def angleToPosition(self, goToPos):
        currentTiltAngle = self.__tiltValue
        stepsNeeded = int(goToPos) - currentTiltAngle
        currentTiltAngle += stepsNeeded
        if stepsNeeded <= 0:
            # Makes sure neededSteps is positive
            stepsNeeded = stepsNeeded * -1
            motorfunctions.motorTiltCW(stepsNeeded)
        elif stepsNeeded >= 0:
            motorfunctions.motorTiltCCW(stepsNeeded)
        self.__tiltValue = self.__desiredTilt

    # Called when the slider is used, changes the label and the variable for the wanted lift height. /conversion is for conversion from steps to cm
    def update_slider_label(self):
        sliderValue = self.slider.value()
        self.sliderLabel.setText("Height: " + str(int(sliderValue / constants.conversionValue)))
        self.__desiredHeight = sliderValue

    # Move MARC to wanted height and tilt, and sets the variables to those values
    def moveButtonClicked(self):
        if not self.__isCycleBusy:
            self.moveToPosition(self.__desiredHeight)
       
    # Adds a keyframe to the keyframe list via another class function
    def quickAddKeyframe(self):
        self.mc.thirdScreen.quickAddKeyframe(self.__desiredHeight, self.__tiltValue)

    def resetTiltButtonClicked(self):
        motorfunctions.calibrateTilthead()
        self.__tiltValue = 0
        self.__desiredTilt = 0
        self.setTiltLabelVal(self.__tiltValue)

    # Depending on which button got sent here it adds or subs 20 from the tilt variable. Add button has operator = + and sub has operator = -
    def tiltButtonsClicked(self, operator):
        if self.__isCycleBusy == False:
            if operator == "+" and self.__desiredTilt <= 12000:
                self.__desiredTilt += 200
            elif operator == "-" and self.__desiredTilt >= -5400:
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
        self.mc.showKeyframeMenu()

    def turntableMenuClicked(self):
        self.mc.showTurntableMenu()

    # Sets emergency flag to True or false accordingly and changes style of emergency button
    def emergencyStopClicked(self):
        if self.__emergencyFlag == False:
            self.__emergencyFlag = True
            self.emergencyStopButton.setStyleSheet(constants.emergencyButtonOnStyle)
        else:
            self.__emergencyFlag = False
            self.emergencyStopButton.setStyleSheet(constants.emergencyButtonOffStyle)

    # Checks if MARC isn't busy or in emergency stop mode, if not starts the cycle thread and changes the busy flag
    def cycle(self):
        if self.__isCycleBusy != True and self.__emergencyFlag != True:
            newCycleThread = cycle.cycleThread(self.mc, self.__waitBeforeTime, self.__waitAfterTime, self.__picsPerKeyframe)
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
            motorfunctions.calibrateTilthead()
            self.__tiltValue = 0
            self.__desiredTilt = 0
            self.setTiltLabelVal(self.__tiltValue)
            motorfunctions.calibrateCameraLift()
            self.__heightValue = 0
            self.__desiredHeight = 0
            self.setSliderVal(self.__heightValue)
