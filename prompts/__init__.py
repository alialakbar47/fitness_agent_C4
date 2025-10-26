"""Initialize prompts package."""

from prompts.system_prompts import get_base_prompt, AVAILABLE_PERSONAS
from prompts.examples import get_few_shot_examples

__all__ = [
    'get_base_prompt',
    'AVAILABLE_PERSONAS',
    'get_few_shot_examples'
]
