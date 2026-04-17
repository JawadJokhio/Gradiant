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

class HFVisionProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        if not api_key or api_key == "your_hf_api_key_here":
            raise ValueError("HuggingFace API key is missing")
        self.api_key = api_key
        self.base_url = "https://router.huggingface.co/v1"
        self.model = "CohereLabs/aya-vision-32b:cohere"  # Best free vision model via HF router

    def generate(self, system_prompt: str, user_prompt: str, image_base64: str = None, max_tokens: int = 1500, temperature: float = 0.3) -> str:
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        user_content = [{"type": "text", "text": f"{system_prompt}\n\n{user_prompt}"}]
        if image_base64:
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}})
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": user_content}],
            "max_tokens": max_tokens
        }
        try:
            r = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMProviderError(f"HF Vision generation failed: {str(e)}")


class HFProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("HuggingFace API key is missing")
        self.client = InferenceClient(token=api_key)

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        try:
            prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
            return self.client.text_generation(
                prompt,
                model="Qwen/Qwen2.5-72B-Instruct",
                max_new_tokens=max_tokens
            )
        except Exception as e:
            raise LLMProviderError(f"HF generation failed: {str(e)}")


class LLMService:
    def __init__(self):
        self.groq_provider = None
        self.hf_provider = None
        self.vision_provider = None
        
        if settings.groq_api_key:
            self.groq_provider = GroqProvider(settings.groq_api_key)
        
        if settings.hf_api_key and settings.hf_api_key != "your_huggingface_api_key_here":
            self.hf_provider = HFProvider(settings.hf_api_key)
            self.vision_provider = HFVisionProvider(settings.hf_api_key)

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Try Groq first, then HF fallback."""
        if self.groq_provider:
            try:
                return self.groq_provider.generate(system_prompt, user_prompt, **kwargs)
            except LLMProviderError as e:
                print(f"Groq fallback triggered: {e}")
                
        if self.hf_provider:
            try:
                return self.hf_provider.generate(system_prompt, user_prompt, **kwargs)
            except LLMProviderError as e:
                print(f"HF fallback failed: {e}")
                pass
                
        if not self.groq_provider and not self.hf_provider:
            return "Intelligence engines offline: Please check your API keys in the .env file."
            
        return "Intelligence engines offline: Expected providers failed."

    def generate_vision_response(self, system_prompt: str, user_prompt: str, image_base64: str) -> str:
        """Only use Groq for vision right now."""
        if self.vision_provider:
            return self.vision_provider.generate(system_prompt, user_prompt, image_base64=image_base64)
        raise LLMProviderError("Vision provider offline or API keys missing.")
