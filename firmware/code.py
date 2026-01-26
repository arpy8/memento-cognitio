"""
Memento Cognitio Firmware
Version 1.0.0

Copyright (c) 2026 Arpit Sengar

MIT License — Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.

Project: Memento Cognitio – AI-powered visual cognition device
"""

import ssl
import time
import wifi
import displayio
import terminalio
import socketpool

import adafruit_requests
import adafruit_pycamera
import adafruit_imageload
from adafruit_display_text import label

from manager import BluetoothManager, WiFiManager, BuzzerManager, LLMManager
from constants import PROMPT_MODES, MESSAGE_DISPLAY_TIME, ERROR_DISPLAY_TIME


class MementoCognitioApp:
    """Main application """
    
    def __init__(self):
        self.pycam = adafruit_pycamera.PyCamera()
        self.pycam.resolution = 5

        self.buzzer = BuzzerManager(self.pycam)
        
        self.bluetooth = BluetoothManager()
        self.bluetooth.start_advertising()
        
        self.display_fullscreen_text("Waiting for BLE", text_color=0xFFFF00)
        
        if self.bluetooth.wait_for_connection(timeout=30):
            self.display_fullscreen_text("BLE Connected", text_color=0x0000FF)
            self.buzzer.play_success_beep()
            time.sleep(2)
        else:
            self.display_fullscreen_text("BLE Timeout\nContinuing...", text_color=0xFFA500)
            time.sleep(2)
        
        if not WiFiManager.connect():
            self.display_error("WiFi Failed!")
            raise Exception("WiFi connection failed")
        
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        self.llm = LLMManager(requests)
    
    def display_startup_image(self, image_path="/splash.bmp"):
        try:            
            bitmap, palette = adafruit_imageload.load(
                image_path,
                bitmap=displayio.Bitmap,
                palette=displayio.Palette
            )
            
            display_width = self.pycam.display.width
            display_height = self.pycam.display.height
            image_width = bitmap.width
            image_height = bitmap.height
            
            x_offset = (display_width - image_width) // 2
            y_offset = (display_height - image_height) // 2
            
            group = displayio.Group()
            
            bg_bitmap = displayio.Bitmap(display_width, display_height, 1)
            bg_palette = displayio.Palette(1)
            bg_palette[0] = 0x000000  # Black
            bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
            group.append(bg_sprite)
            
            tile_grid = displayio.TileGrid(
                bitmap, 
                pixel_shader=palette,
                x=x_offset,
                y=y_offset
            )
            group.append(tile_grid)
            
            self.pycam.display.root_group = group
            self.pycam.display.refresh()
            
            print(f"Displayed startup image: {image_path}")
            
        except Exception as e:
            print(f"Could not load startup image: {e}")
            self.display_fullscreen_text("Memento Cognitio", text_color=0x00FF00)
            
    def display_fullscreen_text(self, text, bg_color=0x000000, text_color=0xFFFFFF, scale=2, max_chars_per_line=20):
        """Display text on black background filling the entire screen"""
        group = displayio.Group()
        
        bitmap = displayio.Bitmap(self.pycam.display.width, self.pycam.display.height, 1)
        palette = displayio.Palette(1)
        palette[0] = bg_color
        
        bg_sprite = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)
        group.append(bg_sprite)
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        wrapped_text = "\n".join(lines)
        
        text_area = label.Label(
            terminalio.FONT,
            text=wrapped_text,
            color=text_color,
            scale=scale,
            anchor_point=(0.5, 0.5),
            anchored_position=(self.pycam.display.width // 2, self.pycam.display.height // 2)
        )
        
        group.append(text_area)
        
        self.pycam.display.root_group = group
        self.pycam.display.refresh()
    
    def display_error(self, message):
        """Display error message on black background"""
        self.display_fullscreen_text(message, bg_color=0x000000, text_color=0xFF0000, scale=2)
        self.buzzer.play_error_beep()
    
    def process_capture(self, button_name="shutter"):
        """Handle image capture and AI analysis"""
        print("Button Pressed! Capturing...")       
        self.buzzer.play_button_press()
        self.display_fullscreen_text(PROMPT_MODES[button_name][1], text_color=0xFFFF00, scale=2)
        
        try:
            image_data = self.pycam.capture_into_jpeg()
            
            result_text = self.llm.analyze_image(image_data, prompt=PROMPT_MODES[button_name][0])
            print(f"Gemini says: {result_text}")
            
            self.buzzer.play_success_beep()
            
            if self.bluetooth.send_message(result_text):
                self.buzzer.play_bluetooth_beep()
            
            self.display_fullscreen_text(result_text, text_color=0x00FFFF, scale=2 if len(result_text.split()) < 20 else 1, max_chars_per_line=20 if len(result_text.split()) < 20 else 40)
            time.sleep(MESSAGE_DISPLAY_TIME)
            self.display_fullscreen_text("", text_color=0xFFFF00)
            
        except Exception as e:
            print(f"Crash: {e}")
            self.display_error("Error!")
            time.sleep(ERROR_DISPLAY_TIME)
        
        finally:
            self.pycam.live_preview_mode()
    
    def run(self):
        """Main application loop"""
        print("Memento Cognitio Ready")
        self.display_startup_image()
        self.buzzer.play_startup_beep()
        
        self.pycam.live_preview_mode()
        
        while True:
            self.bluetooth.check_connection()
            
            self.pycam.keys_debounce()
            self.pycam.blit(self.pycam.continuous_capture())
            
            if self.pycam.shutter.short_count > 0:
                self.process_capture(button_name="shutter")

            elif self.pycam.up.rose > 0:
                self.process_capture(button_name="up")

            elif self.pycam.down.rose > 0:
                self.process_capture(button_name="down")

            elif self.pycam.left.rose > 0:
                self.process_capture(button_name="left")

            elif self.pycam.right.rose > 0:
                self.process_capture(button_name="right")

            elif self.pycam.select.rose > 0:
                self.process_capture(button_name="select")

            elif self.pycam.ok.rose > 0:
                self.process_capture(button_name="ok")


if __name__ == "__main__":
    app = MementoCognitioApp()
    app.run()