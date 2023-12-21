import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from menus import editKeyframeMenu, keyframeMenu, newKeyframeMenu, turntableMenu, mainScreen, keyframeCalcMenu

# This class controls the menu system, and is responsible for creating the menu widgets
# It give itself to the screens so that they can call the menuController's functions for switching screens
class menuController():
    widget = QStackedWidget()

    def __init__(self):
        self.firstScreen = mainScreen.MainWindow(self)
        self.secondScreen = keyframeMenu.KeyframeListWindow(self)
        self.thirdScreen = newKeyframeMenu.NewKeyframeWindow(self)
        self.fourthScreen = editKeyframeMenu.EditKeyframeWindow(self)
        self.fifthScreen = turntableMenu.TurntableMenuWindow(self)
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
    
