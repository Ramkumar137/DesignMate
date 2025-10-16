import os
import requests
import json
from services.config_loader import get_secret


class GeminiService:
    def __init__(self):
        # Read from env var or config.local.json
        self.api_key = get_secret("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in env")
        # Model and endpoint per Google Generative Language API
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def ask(self, prompt: str, context: str | None = None) -> str:
        """
        Send a prompt to Gemini API and return the response
        """
        try:
            # Log a short fingerprint only, avoid printing full keys
            print(f"Gemini API Key: {self.api_key[:6]}***" if self.api_key else "No API key")
            print(f"API URL: {self.api_url}")
            
            # Prepare the request payload
            content_parts = [{"text": prompt}]
            if context:
                content_parts.insert(0, {"text": f"Context: {context}\n\n"})
            
            payload = {
                "contents": [{
                    "parts": content_parts
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            print(f"Making request to Gemini API with payload: {payload}")
            
            # Make the API call
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            response.raise_for_status()
            data = response.json()
            
            print(f"Response data: {data}")
            
            # Extract the generated text from the response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"]
                elif "finishReason" in candidate:
                    print(f"Finish reason: {candidate['finishReason']}")
                    return "Sorry, the response was filtered or incomplete. Please try rephrasing your question."
            
            print(f"No valid candidates in response: {data}")
            return "Sorry, I couldn't generate a response. Please try again."
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return f"Error connecting to Gemini API: {str(e)}"
        except Exception as e:
            print(f"General error: {str(e)}")
            return f"Error processing request: {str(e)}"