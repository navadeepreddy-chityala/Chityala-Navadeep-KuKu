"""
gemini_client.py
----------------
Google Gemini API client for Nyay (AI Lawyer).

Features:
- Built-in .env file loader (no python-dotenv required)
- Strips accidental quotes or whitespace from keys
- Detects placeholder keys before making failed network calls
- Zero external pip packages required (pure Python standard library)
"""

import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional

DEFAULT_MODEL = "gemini-flash-latest"
FALLBACK_MODELS = ["gemini-flash-latest", "gemini-pro-latest", "gemini-2.5-flash"]


def load_env_file(filepath: Optional[str] = None) -> None:
    """Lightweight .env parser that loads variables into os.environ."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and v and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


# Automatically check for .env on import
load_env_file()


def clean_api_key(key: Optional[str]) -> Optional[str]:
    """Cleans up accidental quotes, whitespace, and detects placeholders."""
    if not key:
        return None
    cleaned = key.strip().strip("'\"").strip()
    # Check if the user accidentally pasted our placeholder
    if cleaned.lower().startswith("your-") or "actual-gemini-key" in cleaned.lower():
        return None
    return cleaned if cleaned else None


class GeminiClient:
    """Lightweight, zero-dependency client for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        load_env_file()
        raw_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.api_key = clean_api_key(raw_key)
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def is_configured(self) -> bool:
        """Returns True if a plausible API key is available."""
        return bool(self.api_key and len(self.api_key) >= 15)

    def set_key(self, key: str, save_to_env: bool = True) -> None:
        """Sets the API key dynamically and optionally persists to .env."""
        cleaned = clean_api_key(key)
        if cleaned:
            self.api_key = cleaned
            os.environ["GEMINI_API_KEY"] = cleaned
            if save_to_env:
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                try:
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={cleaned}\n")
                    print(f"✓ Saved Gemini API key to: {env_path}")
                except Exception as e:
                    print(f"[Notice] Could not write to .env: {e}")

    def generate(
        self,
        contents: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: int = 1500,
    ) -> str:
        """Calls Gemini generateContent endpoint."""
        if not self.is_configured:
            raise ValueError(
                "Gemini API Key missing or invalid. Please provide a valid API key from https://aistudio.google.com/"
            )

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = None

        gemini_contents = []
        extra_system_notes = []

        for msg in contents:
            r = msg.get("role", "user")
            text = msg.get("content", "")
            if r == "system":
                # Collect system prompts rather than converting to 'model'
                extra_system_notes.append(text)
            elif r in ("user", "human"):
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": text}]
                })
            elif r in ("model", "assistant"):
                gemini_contents.append({
                    "role": "model",
                    "parts": [{"text": text}]
                })

        # Ensure conversation starts with user if contents exist
        if gemini_contents and gemini_contents[0]["role"] != "user":
            gemini_contents.insert(0, {"role": "user", "parts": [{"text": "Hello"}]})

        full_system = system_instruction or ""
        if extra_system_notes:
            full_system = (full_system + "\n\n" + "\n\n".join(extra_system_notes)).strip()

        payload = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            }
        }

        if full_system:
            payload["system_instruction"] = {
                "parts": [{"text": full_system}]
            }

        data_bytes = json.dumps(payload).encode("utf-8")

        for candidate_model in models_to_try:
            endpoint = f"{self.base_url}/{candidate_model}:generateContent?key={self.api_key}"
            req = urllib.request.Request(
                endpoint,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    res_body = response.read().decode("utf-8")
                    res_json = json.loads(res_body)
                    candidates = res_json.get("candidates", [])
                    if not candidates:
                        return "No response generated by Gemini."
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                    return "Empty response from Gemini."
            except urllib.error.HTTPError as e:
                error_details = e.read().decode("utf-8", errors="ignore")
                try:
                    err_json = json.loads(error_details)
                    msg = err_json.get("error", {}).get("message", error_details)
                except Exception:
                    msg = error_details
                last_error = f"Gemini API Error ({e.code}): {msg}"
                # If 503 (high demand) or 404 (model not found), try next model
                if e.code in (404, 503):
                    continue
                else:
                    raise RuntimeError(last_error)
            except urllib.error.URLError as e:
                raise RuntimeError(f"Network error connecting to Gemini API: {e.reason}")

        raise RuntimeError(last_error or "All Gemini models failed.")
