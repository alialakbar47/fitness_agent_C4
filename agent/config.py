"""LLM Configuration Manager for Google Gemini."""

import os
import google.generativeai as genai
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMConfig:
    """Manages LLM configuration and API settings."""
    
    def __init__(self):
        # Default configuration
        self.model_name = "gemini-2.0-flash-exp"
        self.temperature = 0.7
        self.top_p = 0.95
        self.max_tokens = 2048
        
        # Initialize API
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize Google Generative AI API."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
            return
        
        try:
            genai.configure(api_key=api_key)
            logger.info("Google Generative AI API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API: {e}")
    
    def update_config(self, model_name: Optional[str] = None,
                     temperature: Optional[float] = None,
                     top_p: Optional[float] = None,
                     max_tokens: Optional[int] = None):
        """Update LLM configuration parameters."""
        if model_name is not None:
            self.model_name = model_name
        if temperature is not None:
            self.temperature = max(0.0, min(1.0, temperature))
        if top_p is not None:
            self.top_p = max(0.0, min(1.0, top_p))
        if max_tokens is not None:
            self.max_tokens = max_tokens
        
        logger.info(f"Config updated: model={self.model_name}, temp={self.temperature}, "
                   f"top_p={self.top_p}, max_tokens={self.max_tokens}")
    
    def get_model(self):
        """Get configured Gemini model instance."""
        try:
            generation_config = {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_output_tokens": self.max_tokens,
            }
            
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config
            )
            
            return model
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return None
    
    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction/prompt
        
        Returns:
            Generated response text
        """
        try:
            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "max_output_tokens": self.max_tokens,
                    },
                    system_instruction=system_instruction
                )
            else:
                model = self.get_model()
            
            if model is None:
                return "Error: Failed to initialize model"
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens
        }
    
    @staticmethod
    def get_available_models() -> Dict[str, str]:
        """Get available Gemini models."""
        return {
            "gemini-2.0-flash-exp": "Gemini 2.0 Flash",
            "gemini-2.5-flash-exp": "Gemini 2.5 Flash",
            "gemini-2.0-pro-exp": "Gemini 2.0 Pro",
            "gemini-2.0-flash-lite-exp": "Gemini 2.0 Flash Lite"
        }
