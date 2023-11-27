import sys
import json
import time
import math
import slack
import random
import threading
from constants import constants
from classes import *
from time import sleep
from PyQt5 import QtCore
from PyQt5.QtCore import *
from constants import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QSlider

class TurntableMenuWindow(QMainWindow):
    turntableSpeed = 0.0009

    def __init__(self, menuController):
        super().__init__()

        self.mc = menuController

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)

        window = QGridLayout()

        self.speedLabel = constants.labelFactory.create(f'Turntable speed: {self.turntableSpeed}', constants.font, constants.labelStyle)

        self.slowButton = constants.buttonFactory.create('Slow', lambda: self.speedButtonsClicked('Slow'), constants.buttonStyle, constants.size)
        self.mediumButton = constants.buttonFactory.create('Medium', lambda: self.speedButtonsClicked('Medium'), constants.buttonStyle, constants.size)
        self.fastButton = constants.buttonFactory.create('Fast', lambda: self.speedButtonsClicked('Fast'), constants.buttonStyle, constants.size)

        self.speedButtonsLayout = constants.hboxLayoutFactory.create(self.slowButton, self.mediumButton, self.fastButton)

        self.backButton = constants.buttonFactory.create("BACK", self.back, constants.buttonStyle, constants.size)

        window.addWidget(self.speedLabel, 0, 1)
        window.addLayout(self.speedButtonsLayout, 1, 1)
        window.addWidget(self.backButton, 2, 1)

        widget = QWidget()
        widget.setLayout(window)
        self.setCentralWidget(widget)
    
    def speedButtonsClicked(self, speed):
        if speed == 'Slow':
            self.turntableSpeed = constants.turntableSpeeds[0]
        elif speed == 'Medium':
            self.turntableSpeed = constants.turntableSpeeds[1]
        elif speed == 'Fast':
            self.turntableSpeed = constants.turntableSpeeds[2]
            
        self.speedLabel.setText(f'Turntable speed: {self.turntableSpeed}')


    def back(self):
        self.mc.showMainMenu()
