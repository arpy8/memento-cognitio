import time

class BuzzerManager:
    """Handles buzzer sounds using PyCamera's built-in methods"""
    
    def __init__(self, pycam):
        self.pycam = pycam

    def play_startup_beep(self):
        self.pycam.tone(440, 0.1)
        self.pycam.tone(554, 0.1)
        self.pycam.tone(659, 0.1)
        self.pycam.tone(880, 0.3)
        time.sleep(1)
        
    def play_button_press(self):
        self.pycam.tone(1000, 0.05)
        time.sleep(0.05)

    def play_success_beep(self):
        self.pycam.tone(1000, 0.05)
        time.sleep(0.05)
        self.pycam.tone(1200, 0.05)
        time.sleep(0.05)
        self.pycam.tone(1000, 0.05)
    
    def play_bluetooth_beep(self):
        self.pycam.tone(800, 0.05)
        time.sleep(0.05)
        self.pycam.tone(800, 0.05)
            
    def play_error_beep(self):
        self.pycam.tone(400, 0.3)