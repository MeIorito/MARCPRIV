import threading

class infiniteTurnThread(threading.Thread):
    def __init__(self, turnTableScreen, tableMotorController):
        threading.Thread.__init__(self)
        self.tts = turnTableScreen
        self.tc = tableMotorController

    def run(self):
        while self.tts.turnSignal == "ON":
            self.tc.moveMotorUp(200, float(self.tts.turntableSpeed))