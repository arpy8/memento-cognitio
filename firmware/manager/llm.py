import os
import binascii
from constants import GEMINI_MODEL, GEMINI_PROMPT

class LLMManager:
    """Handles LLM API interactions"""
    
    def __init__(self, requests_session):
        self.requests = requests_session
        self.api_key = os.getenv("GEMINI_API_KEY")
    
    def _encode_image(self, jpeg_data):
        print("Encoding image...")
        return binascii.b2a_base64(jpeg_data).strip().decode()
    
    def _build_payload(self, b64_image, prompt):
        return {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64_image
                        }
                    },
                    {"text": prompt}
                ]
            }]
        }
    
    def analyze_image(self, jpeg_data, prompt=GEMINI_PROMPT):
        if not self.api_key:
            return "Error: No API Key in settings.toml"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        
        b64_image = self._encode_image(jpeg_data)
        payload = self._build_payload(b64_image, prompt)
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        print("Sending to Gemini...")
        try:
            response = self.requests.post(url, json=payload, headers=headers)
            json_resp = response.json()
            
            if "candidates" in json_resp:
                text = json_resp["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
            else:
                print(json_resp)
                return "No content returned."
                
        except Exception as e:
            error_msg = str(e)[:40]
            print(f"API Error: {error_msg}")
            return f"API Error: {error_msg}"