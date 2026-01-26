import os
import wifi

class WiFiManager:
    """Handles WiFi connection"""
    
    @staticmethod
    def connect():
        print("Connecting to WiFi...")
        try:
            ssid = os.getenv("CIRCUITPY_WIFI_SSID")
            password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
            
            wifi.radio.connect(ssid, password)
            print(f"Connected to {ssid}!")
            print(f"DNS: {wifi.radio.ipv4_dns}")
            return True
            
        except Exception as e:
            print(f"WiFi Error: {e}")
            return False