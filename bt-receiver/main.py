"""
Memento Cognitio Bluetooth Receiver
Version 1.0.0

Copyright (c) 2026 Arpit Sengar

MIT License — Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.

Project: Memento Cognitio – AI-powered visual cognition device
"""

import io
import wave
import asyncio
import datetime
from pathlib import Path
from pydub import playback
from piper import PiperVoice
from pydub import AudioSegment 
from bleak import BleakScanner, BleakClient


UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  
UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

DEVICE_NAME = "Memento-Cam"
SCAN_TIMEOUT = 10.0

BASE_DIR = Path(__file__).parent.resolve()
TTS_MODEL = BASE_DIR / "tts_models" / "en_US-libritts_r-medium.onnx"
TTS_VOICE = PiperVoice.load(TTS_MODEL)


def convert_to_speech(text, play=True):
    if not text:
        return None
    
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, "wb") as wav_file:
        TTS_VOICE.synthesize_wav(text, wav_file)
    
    wav_buffer.seek(0)
    
    if play:
        audio_segment = AudioSegment.from_file(wav_buffer, format="wav")
        playback.play(audio_segment)
    
    return wav_buffer

class MementoReceiver:
    def __init__(self):
        self.client = None
        self.message_buffer = ""
        self.message_count = 0
        self.audio_history = []
    
    async def find_device(self):
        print(f"Scanning for '{DEVICE_NAME}'...")
        print("Make sure your Memento camera is powered on!\n")
        
        device = await BleakScanner.find_device_by_name(
            DEVICE_NAME, 
            timeout=SCAN_TIMEOUT
        )
        
        if device:
            print(f"Found device: {device.name}")
            print(f"  Address: {device.address}\n")
            return device
        else:
            print(f"Device '{DEVICE_NAME}' not found after {SCAN_TIMEOUT}s")
            print("\nTroubleshooting:")
            print("  1. Check if the camera is powered on")
            print("  2. Make sure Bluetooth is enabled on your laptop")
            print("  3. Try moving the camera closer")
            print("  4. Restart the camera and try again")
            return None
    
    def handle_notification(self, sender, data):
        """Handle incoming BLE notifications"""
        try:
            text = data.decode('utf-8')
            self.message_buffer += text
            
            if '\n' in self.message_buffer:
                messages = self.message_buffer.split('\n')
                
                for msg in messages[:-1]:
                    if msg.strip():
                        self.message_count += 1
                        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                        
                        print("=" * 60)
                        print(f"Message #{self.message_count} | {timestamp}")
                        print("-" * 60)
                        print(msg.strip())
                        print("=" * 60)
                        print()
                        
                        audio_buffer = convert_to_speech(msg.strip(), play=True)
                        self.audio_history.append({
                            'timestamp': timestamp,
                            'message': msg.strip(),
                            'audio': audio_buffer
                        })
                
                self.message_buffer = messages[-1]
                
        except Exception as e:
            print(f"Error processing notification: {e}")
    
    async def connect_and_listen(self, device):
        """Connect to device and listen for messages"""
        print("Connecting to Memento camera...")
        
        try:
            async with BleakClient(device) as client:
                self.client = client
                print(f"Connected successfully!\n")
                
                await client.start_notify(
                    UART_RX_CHAR_UUID, 
                    self.handle_notification
                )
                
                print("Listening for messages from camera...")
                print("Press Ctrl+C to stop\n")
                
                while True:
                    if not client.is_connected:
                        print("\n✗ Connection lost!")
                        break
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"\n✗ Connection error: {e}")
        finally:
            print("\nDisconnected from camera")
    
    async def run(self):
        """Main run loop with automatic reconnection"""
        print("=" * 60)
        print("Memento Camera Bluetooth Receiver")
        print("=" * 60)
        print()
        
        while True:
            device = await self.find_device()
            
            if device:
                await self.connect_and_listen(device)
                
                print("\nAttempting to reconnect in 3 seconds...")
                print("Press Ctrl+C to exit\n")
                await asyncio.sleep(3)
            else:
                print(f"\nRetrying in 3 seconds...")
                print("Press Ctrl+C to exit\n")
                await asyncio.sleep(3)


async def main():
    receiver = MementoReceiver()
    
    try:
        await receiver.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        print(f"Total messages received: {receiver.message_count}")


if __name__ == "__main__":
    asyncio.run(main())