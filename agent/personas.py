"""Persona configurations and system prompt management."""

from typing import Dict
from prompts.system_prompts import get_base_prompt, AVAILABLE_PERSONAS


class PersonaManager:
    """Manages persona selection and prompt generation."""
    
    def __init__(self):
        self.available_personas = AVAILABLE_PERSONAS
        self.current_persona = "helpful_assistant"
        self.current_prompt_style = "few_shot"
    
    def set_persona(self, persona: str):
        """Set the active persona."""
        if persona in self.available_personas:
            self.current_persona = persona
        else:
            raise ValueError(f"Unknown persona: {persona}. Choose from: {list(self.available_personas.keys())}")
    
    def set_prompt_style(self, style: str):
        """Set the prompt engineering style."""
        valid_styles = ["zero_shot", "few_shot", "chain_of_thought"]
        if style in valid_styles:
            self.current_prompt_style = style
        else:
            raise ValueError(f"Unknown style: {style}. Choose from: {valid_styles}")
    
    def get_system_prompt(self) -> str:
        """Get the complete system prompt for the current configuration."""
        return get_base_prompt(self.current_persona, self.current_prompt_style)
    
    def get_persona_name(self) -> str:
        """Get the display name of the current persona."""
        return self.available_personas[self.current_persona]
    
    def get_all_personas(self) -> Dict[str, str]:
        """Get all available personas with display names."""
        return self.available_personas
    
    def get_persona_description(self, persona: str) -> str:
        """Get a brief description of a persona."""
        descriptions = {
            "drill_sergeant": "Strict, no-nonsense coach who pushes you to your limits with military-style discipline.",
            "helpful_assistant": "Friendly and supportive guide who patiently helps you achieve your goals.",
            "motivational_coach": "High-energy cheerleader who pumps you up and celebrates every victory!"
        }
        return descriptions.get(persona, "Unknown persona")
