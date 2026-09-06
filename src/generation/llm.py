"""
llm.py

Unified LLM wrapper for generating responses using Groq.
Supports models like llama-3.3-70b-versatile and llama-3.1-8b-instant.
"""

import os
from typing import List, Dict, Optional

from src.logger import get_logger

logger = get_logger(__name__)

# Default recommended Groq model (top quality + free tier)
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


class GroqLLM:
    """
    Client for Groq's ultra-fast LPU inference engine.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_GROQ_MODEL,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        api_key: Optional[str] = None
    ):
        """
        Args:
            model_name: Groq model identifier (e.g. 'llama-3.3-70b-versatile')
            temperature: Sampling temperature (0.1 keeps answers strictly factual)
            max_tokens: Maximum token limit for the generated response
            api_key: Optional explicit key; defaults to os.getenv('GROQ_API_KEY')
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key or self.api_key.startswith("your-"):
            raise ValueError(
                "GROQ_API_KEY is not set or contains placeholder text. "
                "Please add your key from https://console.groq.com/keys to your .env file."
            )

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            logger.info(f"GroqLLM initialized with model '{self.model_name}'")
        except ImportError:
            raise ImportError(
                "The 'groq' package is not installed. "
                "Run: pip install groq"
            )

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Sends chat messages to Groq and returns the generated text response.

        Args:
            messages: List of chat messages:
                      [{"role": "system", "content": ...}, {"role": "user", "content": ...}]

        Returns:
            The completion string from the model.
        """
        logger.info(f"Calling Groq ({self.model_name}) with {len(messages)} messages...")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            answer = response.choices[0].message.content
            logger.info(f"Groq response generated successfully ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"Groq API call failed: {e}", exc_info=True)
            raise
