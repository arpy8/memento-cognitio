import time
from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement


class BluetoothManager:
    """Handles Bluetooth LE communication"""
    
    def __init__(self):
        print("Initializing Bluetooth...")
        try:
            self.ble = BLERadio()
            self.uart = UARTService()
            self.advertisement = ProvideServicesAdvertisement(self.uart)
            self.ble.name = "Memento-Cam"
            print(f"BLE Device Name: {self.ble.name}")
        except Exception as e:
            print(f"BLE Init Error: {e}")
            self.ble = None
    
    def start_advertising(self):
        """Start advertising for connections"""
        if self.ble and not self.ble.connected:
            try:
                self.ble.start_advertising(self.advertisement)
                print("BLE: Advertising started")
            except Exception as e:
                print(f"BLE Advertising Error: {e}")
    
    def wait_for_connection(self, timeout=30):
        """Wait for BLE connection with timeout"""
        if not self.ble:
            print("BLE not initialized")
            return False
        
        print(f"Waiting for BLE connection (timeout: {timeout}s)...")
        start_time = time.monotonic()
        
        while not self.ble.connected:
            if time.monotonic() - start_time > timeout:
                print("BLE: Connection timeout")
                return False
            time.sleep(0.1)
        
        print("BLE: Connected!")
        return True
    
    def send_message(self, message):
        """Send message over Bluetooth if connected"""
        if not self.ble:
            print("BLE not initialized")
            return False
            
        try:
            if self.ble.connected:
                self.uart.write((message + "\n").encode('utf-8'))
                print(f"BLE Sent: {message[:50]}...")
                return True
            else:
                print("BLE: Not connected")
                self.start_advertising()
                return False
        except Exception as e:
            print(f"BLE Send Error: {e}")
            return False
    
    def check_connection(self):
        """Check and maintain BLE connection"""
        if self.ble:
            if not self.ble.connected:
                self.start_advertising()
            return self.ble.connected
        return False