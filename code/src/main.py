import sys
from controllers import motorfunctions
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

from controllers import menuController

mc = menuController.menuController()

app.exec()