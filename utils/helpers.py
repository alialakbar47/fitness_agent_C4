"""Utility functions and helpers."""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ExperimentLogger:
    """Logs experiments and interactions for analysis."""
    
    def __init__(self, log_path: str = "logs/experiment_logs.json"):
        self.log_path = log_path
        
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                json.dump([], f)
    
    def log_interaction(self, 
                       user_query: str,
                       agent_response: str,
                       configuration: Dict[str, Any],
                       metadata: Dict[str, Any] = None):
        """
        Log a single interaction.
        
        Args:
            user_query: User's input
            agent_response: Agent's response
            configuration: Current LLM/persona configuration
            metadata: Additional metadata (tools used, reasoning steps, etc.)
        """
        try:
            # Read existing logs
            with open(self.log_path, 'r') as f:
                logs = json.load(f)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query,
                "agent_response": agent_response,
                "configuration": configuration,
                "metadata": metadata or {}
            }
            
            # Append and save
            logs.append(log_entry)
            
            with open(self.log_path, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info(f"Logged interaction at {log_entry['timestamp']}")
        
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
    
    def get_logs(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve logs.
        
        Args:
            limit: Maximum number of logs to retrieve (most recent first)
        
        Returns:
            List of log entries
        """
        try:
            with open(self.log_path, 'r') as f:
                logs = json.load(f)
            
            # Return most recent first
            logs = list(reversed(logs))
            
            if limit:
                logs = logs[:limit]
            
            return logs
        
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return []
    
    def export_logs(self, output_path: str):
        """Export logs to a file."""
        try:
            logs = self.get_logs()
            
            with open(output_path, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info(f"Logs exported to {output_path}")
        
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
    
    def clear_logs(self):
        """Clear all logs."""
        try:
            with open(self.log_path, 'w') as f:
                json.dump([], f)
            
            logger.info("Logs cleared")
        
        except Exception as e:
            logger.error(f"Error clearing logs: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from logs."""
        try:
            logs = self.get_logs()
            
            if not logs:
                return {"total_interactions": 0}
            
            # Calculate statistics
            personas = {}
            models = {}
            prompt_styles = {}
            
            for log in logs:
                config = log.get("configuration", {})
                
                # Count persona usage
                persona = config.get("persona", "unknown")
                personas[persona] = personas.get(persona, 0) + 1
                
                # Count model usage
                model = config.get("model_name", "unknown")
                models[model] = models.get(model, 0) + 1
                
                # Count prompt style usage
                style = config.get("prompt_style", "unknown")
                prompt_styles[style] = prompt_styles.get(style, 0) + 1
            
            return {
                "total_interactions": len(logs),
                "persona_usage": personas,
                "model_usage": models,
                "prompt_style_usage": prompt_styles,
                "date_range": {
                    "start": logs[-1]["timestamp"] if logs else None,
                    "end": logs[0]["timestamp"] if logs else None
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {"error": str(e)}


def format_datetime(dt_str: str, format: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime string for display."""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime(format)
    except:
        return dt_str


def format_booking_list(bookings: List[Dict]) -> str:
    """Format booking list for display."""
    if not bookings:
        return "No bookings found."
    
    formatted = []
    for booking in bookings:
        status_emoji = "✅" if booking['status'] == 'confirmed' else "❌"
        service_emoji = {
            'personal_training': '🏋️',
            'group_class': '👥',
            'nutrition_consult': '🥗'
        }.get(booking['service_type'], '📅')
        
        formatted.append(
            f"{status_emoji} {service_emoji} **{booking['service_type'].replace('_', ' ').title()}**\n"
            f"   📅 {format_datetime(booking['date_time'])}\n"
            f"   🆔 Booking ID: {booking['id']}"
        )
    
    return "\n\n".join(formatted)


def validate_email(email: str) -> bool:
    """Simple email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def get_service_emoji(service_type: str) -> str:
    """Get emoji for service type."""
    emojis = {
        'personal_training': '🏋️',
        'group_class': '👥',
        'nutrition_consult': '🥗'
    }
    return emojis.get(service_type, '📅')


def get_persona_emoji(persona: str) -> str:
    """Get emoji for persona."""
    emojis = {
        'drill_sergeant': '🎖️',
        'helpful_assistant': '😊',
        'motivational_coach': '💪'
    }
    return emojis.get(persona, '🤖')
