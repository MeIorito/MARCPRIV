from controllers import motorfunctions
import threading

class infiniteTurnThread(threading.Thread):
    def __init__(self, turnTableScreen):
        threading.Thread.__init__(self)
        self.tts = turnTableScreen

    def run(self):
        print("HOI")
        while self.tts.turnSignal == "ON":
            motorfunctions.motorTableCW(200, float(self.tts.turntableSpeed))