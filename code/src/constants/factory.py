from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from abc import ABC, abstractmethod

# Parent class for all factories
class Factory(ABC):

    def create(self):
        pass

# Child classes for each type of widget
# Each child class has a static method that creates a widget and returns it
# This is done so that the widget can be created without having to create an instance of the factory

class sliderFactory(Factory):
    @staticmethod
    def create(min, max, step, width, interval, style, function):
        slider = QSlider()
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setPageStep(step)
        slider.setFixedWidth(width)
        slider.setTickInterval(interval)
        slider.setStyleSheet(style)
        slider.valueChanged.connect(function)
        return slider
    

class labelFactory(Factory):
    @staticmethod
    def create(text, font, style):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(font)
        label.setStyleSheet(style)
        return label
    

class buttonFactory(Factory):
    @staticmethod
    def create(text, function, style, size):
        button = QPushButton(text)
        button.clicked.connect(function)
        button.setStyleSheet(style)
        button.setMinimumSize(size[0], size[1])
        return button
    
class hboxLayoutFactory(Factory):
    @staticmethod
    def create(*widgets):
        layout = QHBoxLayout()

        for widget in widgets:
            layout.addWidget(widget)

        return layout
    

class vboxLayoutFactory(Factory):
    @staticmethod
    def create(*widgets):
        layout = QVBoxLayout()

        for widget in widgets:
            layout.addWidget(widget)
        
        return layout
    
class qtableFactory(Factory):
    @staticmethod
    def create(size, tableStyle, scrollbarStyle):
        table = QTableWidget()
        table.setFixedSize(size[0], size[1])
        table.setStyleSheet(tableStyle)
        table.verticalScrollBar().setStyleSheet(scrollbarStyle)

        return table