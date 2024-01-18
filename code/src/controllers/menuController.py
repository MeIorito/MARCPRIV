import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from controllers import motorControllers
from menus import editKeyframeMenu, keyframeMenu, newKeyframeMenu, turntableMenu, mainScreen

# This class controls the menu system, and is responsible for creating the menu widgets
# It gives itself to the screens so that they can call the menuController's functions for switching screens
# It is also used a a hub for screens to call each other's functions to prevent circular imports

class menuController():
    widget = QStackedWidget()

    def __init__(self):
        self.tiltMotorController = motorControllers.tiltMotor()
        self.heightMotorController = motorControllers.heightMotor()
        self.tableMotorController = motorControllers.tableMotor(self)
        self.cameraController = motorControllers.camera()

        self.firstScreen = mainScreen.MainWindow(self, self.tiltMotorController, self.heightMotorController, self.cameraController, self.tableMotorController)
        self.secondScreen = keyframeMenu.KeyframeListWindow(self)
        self.thirdScreen = newKeyframeMenu.NewKeyframeWindow(self)
        self.fourthScreen = editKeyframeMenu.EditKeyframeWindow(self)
        self.fifthScreen = turntableMenu.TurntableMenuWindow(self, self.tableMotorController)
        self.widget.addWidget(self.firstScreen)
        self.widget.addWidget(self.secondScreen)
        self.widget.addWidget(self.thirdScreen)
        self.widget.addWidget(self.fourthScreen)
        self.widget.addWidget(self.fifthScreen)
        
        self.widget.setCurrentWidget(self.firstScreen)
        self.widget.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.widget.showMaximized()
        self.widget.show()

    def showMainMenu(self):
        self.widget.setCurrentWidget(self.firstScreen)

    def showKeyframeMenu(self):
        self.widget.setCurrentWidget(self.secondScreen)

    def showNewKeyframeMenu(self):
        self.widget.setCurrentWidget(self.thirdScreen)

    def showEditKeyframeMenu(self):
        self.widget.setCurrentWidget(self.fourthScreen)
    
    def showTurntableMenu(self):
        self.widget.setCurrentWidget(self.fifthScreen)
    
    # def showKeyframeCalcMenu(self):
    #     self.widget.setCurrentWidget(self.sixthScreen)
    
