import sys
from PyQt5.QtWidgets import QApplication
# Create this here because it needs to be created before the controllers are imported 
app = QApplication(sys.argv)

from controllers import menuController

# Create the menu controller and start the application
mc = menuController.menuController()

# # calibrateCameraLift()
# # calibrateTilthead()

app.exec()