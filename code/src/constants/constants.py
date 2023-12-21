from PyQt5.QtGui import QFont
from code.src.constants import factory
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication

# Constants | slack auth | settings file | cycleCounterFile | slack channel name  | font size | button size
slackToken = "xoxb-5867825218247-6345779817859-JFVLFfVIrpV0ufdlhEpTWmPp"
settingsFile = "files/settings.txt"
cycleCounterFile = "files/cycleCounter.txt"
slackChannel = "testbot"
font = QFont()
font.setPointSize(11)
size = (100, 80)
turntableSpeeds = [0.002, 0.0007, 0.0002]

objDistance = 43  # Distance between object and camera in cm, used for tilt calculations
totHeight = 180  # Total height of the lift
conversionValue = 72000 / totHeight  # Steps per cm

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

sliderFactory = factory.sliderFactory()
labelFactory = factory.labelFactory()
buttonFactory = factory.buttonFactory()
hboxLayoutFactory = factory.hboxLayoutFactory()
vboxLayoutFactory = factory.vboxLayoutFactory()
qtableFactory = factory.qtableFactory()