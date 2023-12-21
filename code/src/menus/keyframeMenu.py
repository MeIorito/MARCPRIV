import json
from constants import constants
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow


class KeyframeListWindow(QMainWindow):

    def __init__(self, menuController):
        super().__init__()

        self.mc = menuController

        self.setStyleSheet("background-color: #343541;")
        self.setGeometry(100, 100, 800, 400)  # Adjusted window size

        self.keyframesDataFile = constants.settingsFile
        self.loadKeyframesData()

        centralLayout = QGridLayout()  # Main horizontal layout

        # Creates all the widgets using the factory classes.
        self.keyframeTable = constants.qtableFactory.create((550, 350), constants.tableStyle, constants.tableSliderStyle)
        self.createKeyframeTable()

        self.backButton = constants.buttonFactory.create("BACK", self.back, constants.buttonStyle, constants.size)
        self.addButton = constants.buttonFactory.create("ADD KEYFRAME", self.addKeyframe, constants.buttonStyle, constants.size)
        self.editButton = constants.buttonFactory.create("EDIT KEYFRAME", self.editKeyframe, constants.buttonStyle, constants.size)
        self.deleteButton = constants.buttonFactory.create("DELETE KEYFRAME", self.deleteKeyframe, constants.buttonStyle, constants.size)
        self.keyframeCalculator = constants.buttonFactory.create("CALC KEYFRAMES", self.kfcClicked, constants.buttonStyle, constants.size)

        rightLayout = constants.vboxLayoutFactory.create(self.backButton, self.addButton, self.editButton, self.deleteButton, self.keyframeCalculator)

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
            self.keyframeTable.setItem(row, 1, QTableWidgetItem(str(data["liftHeight"] / constants.conversionValue)))
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
        pass

    # Dynamically adds keyframes
    def addKeyframe(self):
        self.mc.showNewKeyframeMenu()

    # Dynamically edits keyframes
    def editKeyframe(self):
        self.mc.showEditKeyframeMenu()

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
        self.mc.showMainMenu()

    # Updates the numbers, so that there are no gaps
    def updateKeyframeNumbers(self):
        currentKeyframes = dict(self.keyframesData)
        self.keyframesData.clear()

        for i, (keyframe, data) in enumerate(currentKeyframes.items()):
            newKeyframeName = f"Keyframe {i + 1}"
            self.keyframesData[newKeyframeName] = data
