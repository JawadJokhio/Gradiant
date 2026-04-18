import base64
import json
import requests
from google import genai
from google.genai import types
from abc import ABC, abstractmethod
from groq import Groq
from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.exceptions import LLMProviderError

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2500, temperature: float = 0.3) -> str:
        """Generate response from LLM."""
        pass

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Groq API key is missing")
        self.client = Groq(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2500, temperature: float = 0.3) -> str:
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise LLMProviderError(f"Groq generation failed: {str(e)}")

class GroqVisionProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Groq API key is missing")
        self.client = Groq(api_key=api_key)
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def generate(self, system_prompt: str, user_prompt: str, image_base64: str = None, max_tokens: int = 1500, temperature: float = 0.3) -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
            content = [{"type": "text", "text": full_prompt}]
            if image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                })

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise LLMProviderError(f"Groq vision failed: {str(e)}")

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key missing")
        # Initialize the new Google GenAI client
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        try:
            prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text
        except Exception as e:
            raise LLMProviderError(f"Gemini text failed: {str(e)}")

class GeminiVisionProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key missing")
        # Initialize the new Google GenAI client
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def generate(self, system_prompt: str, user_prompt: str, image_base64: str = None, max_tokens: int = 1500, temperature: float = 0.3) -> str:
        try:
            prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
            
            contents = [prompt]
            if image_base64:
                # Use the new Part.from_bytes for the new SDK
                image_bytes = base64.b64decode(image_base64)
                contents.append(
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                )
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text
        except Exception as e:
            raise LLMProviderError(f"Gemini vision failed: {str(e)}")

class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            res = requests.post(self.url, headers=headers, json=data, timeout=30)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMProviderError(f"OpenRouter failed: {str(e)}")

class OpenRouterVisionProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-exp:free"

    def generate(self, system_prompt: str, user_prompt: str, image_base64: str = None, max_tokens: int = 1500, temperature: float = 0.3) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
            content = [{"type": "text", "text": full_prompt}]
            if image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                })
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            res = requests.post(self.url, headers=headers, json=data, timeout=60)
            if res.status_code != 200:
                raise Exception(f"OpenRouter Vision API error: {res.text}")
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMProviderError(f"OpenRouter Vision failed: {str(e)}")

class HFVisionProvider(BaseLLMProvider):
    def __init__(self, client: InferenceClient):
        self.client = client
        self.model = "llava-hf/llava-1.5-7b-hf"

    def generate(self, system_prompt: str, user_prompt: str, image_base64: str = None, max_tokens: int = 1500, temperature: float = 0.3) -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
            content = [{"type": "text", "text": full_prompt}]
            if image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                })
            response = self.client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMProviderError(f"HF Vision generation failed: {str(e)}")

class HFProvider(BaseLLMProvider):
    def __init__(self, client: InferenceClient):
        self.client = client
        self.model = "Qwen/Qwen2.5-72B-Instruct"

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMProviderError(f"HF generation failed: {str(e)}")

class LLMService:
    def __init__(self):
        self.groq_provider = None
        self.groq_vision = None
        self.gemini_provider = None
        self.gemini_vision = None
        self.openrouter_provider = None
        self.openrouter_vision = None
        self.hf_provider = None
        self.hf_vision = None
        
        # 1. Groq (Primary Text/Vision)
        if settings.groq_api_key:
            # Groq keys typically start with "gsk_".
            if settings.groq_api_key.startswith("gsk_"):
                self.groq_provider = GroqProvider(settings.groq_api_key)
                self.groq_vision = GroqVisionProvider(settings.groq_api_key)
            else:
                print("DEBUG: GROQ_API_KEY format looks invalid for Groq (expected prefix: gsk_)")
        
        # 2. Gemini (Production-grade Vision + High Reliability Text)
        if settings.gemini_api_key:
            self.gemini_provider = GeminiProvider(settings.gemini_api_key)
            self.gemini_vision = GeminiVisionProvider(settings.gemini_api_key)

        # 3. OpenRouter (Fallback Text/Vision)
        if settings.openrouter_api_key:
            # OpenRouter keys typically start with "sk-or-v1-".
            if settings.openrouter_api_key.startswith("sk-or-v1-"):
                self.openrouter_provider = OpenRouterProvider(settings.openrouter_api_key)
                self.openrouter_vision = OpenRouterVisionProvider(settings.openrouter_api_key)
            else:
                print("DEBUG: OPENROUTER_API_KEY format looks invalid (expected prefix: sk-or-v1-)")

        # 4. HuggingFace (Global Fallback)
        if settings.hf_api_key and settings.hf_api_key != "your_huggingface_api_key_here":
            hf_client = InferenceClient(token=settings.hf_api_key, base_url="https://router.huggingface.co/v1")
            self.hf_provider = HFProvider(hf_client)
            self.hf_vision = HFVisionProvider(hf_client)

    def _configured_vision_providers(self):
        providers = []
        if self.groq_vision:
            providers.append("Groq")
        if self.hf_vision:
            providers.append("HuggingFace")
        if self.openrouter_vision:
            providers.append("OpenRouter")
        if self.gemini_vision:
            providers.append("Gemini")
        return providers

    @staticmethod
    def _summarize_provider_error(error: Exception) -> str:
        message = str(error)
        lowered = message.lower()

        if "model_decommissioned" in lowered or "decommissioned" in lowered:
            return "configured model is deprecated/decommissioned"
        if "404" in message or "not_found" in lowered or "not found" in lowered:
            return "model not found or unavailable for your account"
        if "401" in message or "unauthorized" in lowered or "authentication" in lowered:
            return "auth failed (invalid/revoked API key)"
        if "invalid_argument" in lowered or "api_key_invalid" in lowered or "api key not valid" in lowered:
            return "invalid API key"
        if "403" in message or "permission" in lowered or "access" in lowered:
            return "access denied (billing/model permission)"
        if "429" in message or "quota" in lowered or "rate limit" in lowered:
            return "quota/rate limit exceeded"
        if "timeout" in lowered:
            return "request timeout"
        return "runtime request failed"

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Sequential Fallback: Groq -> Gemini -> OpenRouter -> HF"""
        # 1. Try Groq
        if self.groq_provider:
            try:
                return self.groq_provider.generate(system_prompt, user_prompt, **kwargs)
            except Exception as e:
                print(f"DEBUG: Groq failed, falling back to Gemini... Error: {str(e)}")

        # 2. Try Gemini
        if self.gemini_provider:
            try:
                return self.gemini_provider.generate(system_prompt, user_prompt, **kwargs)
            except Exception as e:
                print(f"DEBUG: Gemini failed, falling back to OpenRouter... Error: {str(e)}")

        # 3. Try OpenRouter
        if self.openrouter_provider:
            try:
                return self.openrouter_provider.generate(system_prompt, user_prompt, **kwargs)
            except Exception as e:
                print(f"DEBUG: OpenRouter failed, falling back to HF... Error: {str(e)}")

        # 4. Try HuggingFace
        if self.hf_provider:
            try:
                return self.hf_provider.generate(system_prompt, user_prompt, **kwargs)
            except Exception as e:
                print(f"DEBUG: HF Provider failed: {str(e)}")

        return "Intelligence engines offline: All providers failed. Please check your API keys."

    def generate_vision_response(self, system_prompt: str, user_prompt: str, image_base64: str) -> str:
        """Vision Fallback: Groq -> HF -> OpenRouter -> Gemini"""
        configured_providers = self._configured_vision_providers()
        provider_errors = {}

        # 1. Try Groq Vision (Primary)
        if self.groq_vision:
            try:
                return self.groq_vision.generate(system_prompt, user_prompt, image_base64=image_base64)
            except Exception as e:
                provider_errors["Groq"] = self._summarize_provider_error(e)
                print(f"DEBUG: Groq Vision failed, falling back to HF... Error: {str(e)}")

        # 2. Try HF Vision (Fallback)
        if self.hf_vision:
            try:
                return self.hf_vision.generate(system_prompt, user_prompt, image_base64=image_base64)
            except Exception as e:
                provider_errors["HuggingFace"] = self._summarize_provider_error(e)
                print(f"DEBUG: HF Vision failed, falling back to OpenRouter... Error: {str(e)}")

        # 3. Try OpenRouter Vision (Fallback)
        if self.openrouter_vision:
            try:
                return self.openrouter_vision.generate(system_prompt, user_prompt, image_base64=image_base64)
            except Exception as e:
                provider_errors["OpenRouter"] = self._summarize_provider_error(e)
                print(f"DEBUG: OpenRouter Vision failed, falling back to Gemini... Error: {str(e)}")

        # 4. Try Gemini Vision (Fallback)
        if self.gemini_vision:
            try:
                return self.gemini_vision.generate(system_prompt, user_prompt, image_base64=image_base64)
            except Exception as e:
                provider_errors["Gemini"] = self._summarize_provider_error(e)
                print(f"DEBUG: Gemini Vision failed: {str(e)}")

        if not configured_providers:
            return (
                "Vision engines offline: No provider is configured. "
                "Set at least one of GEMINI_API_KEY, OPENROUTER_API_KEY, or HF_API_KEY in .env."
            )

        if provider_errors:
            details = "; ".join(f"{name}: {reason}" for name, reason in provider_errors.items())
            return (
                "Vision engines offline: Configured providers failed at runtime "
                f"({', '.join(configured_providers)}). Details: {details}."
            )

        return (
            "Vision engines offline: Configured providers failed at runtime "
            f"({', '.join(configured_providers)}). Please verify API keys, billing, and model access."
        )
