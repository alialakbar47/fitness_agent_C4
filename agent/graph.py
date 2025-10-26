"""LangGraph workflow definition for ReAct agent."""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import re
import logging
from agent.config import LLMConfig
from agent.personas import PersonaManager
from agent.tools import TOOLS

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State definition for the agent graph."""
    messages: List[Dict[str, str]]  # Chat history
    current_user: str  # Current username
    thought: str  # Current reasoning
    action: str  # Tool to execute
    action_input: Dict[str, Any]  # Tool parameters
    observation: str  # Tool result
    final_answer: str  # Response to user
    iteration_count: int  # Loop counter
    max_iterations: int  # Maximum loops allowed


class FitFusionAgent:
    """ReAct-style agent for FitFusion using LangGraph."""
    
    def __init__(self, llm_config: LLMConfig, persona_manager: PersonaManager):
        self.llm_config = llm_config
        self.persona_manager = persona_manager
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("act", self.tool_node)
        workflow.add_node("observe", self.observe_node)
        workflow.add_node("respond", self.respond_node)
        
        # Set entry point
        workflow.set_entry_point("reason")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "reason",
            self.should_continue,
            {
                "continue": "act",
                "respond": "respond",
                "end": END
            }
        )
        
        workflow.add_edge("act", "observe")
        workflow.add_edge("observe", "reason")
        workflow.add_edge("respond", END)
        
        return workflow.compile()
    
    def reason_node(self, state: AgentState) -> AgentState:
        """
        Reasoning node - LLM generates thought and decides action.
        """
        try:
            # Check iteration limit
            if state["iteration_count"] >= state["max_iterations"]:
                logger.warning("Max iterations reached")
                state["final_answer"] = "I apologize, but I'm having trouble processing this request. Could you rephrase it?"
                return state
            
            # Build prompt with conversation history
            system_prompt = self.persona_manager.get_system_prompt()
            
            # Format conversation history
            history = ""
            for msg in state["messages"]:
                role = msg["role"]
                content = msg["content"]
                history += f"{role}: {content}\n"
            
            # Add previous thought/observation if exists
            if state.get("observation"):
                history += f"\nPrevious Tool Result (Observation): {state['observation']}\n"
                history += "Important: Review the observation above carefully before deciding your next action.\n"
            
            # Generate reasoning
            user_message = state["messages"][-1]["content"] if state["messages"] else ""
            
            prompt = f"""{history}

Now continue with your ReAct reasoning. 

CRITICAL INSTRUCTIONS:
1. If you just received an Observation with tool results, READ IT CAREFULLY
2. The Observation contains the actual data - use it in your Answer
3. Start with "Thought:" to show reasoning
4. Use "Action:" ONLY if you need to call another tool
5. Use "Answer:" when you have enough information to respond to the user

Current user: {state['current_user']}
User's question: {user_message}

Remember: If the Observation shows results, include them in your Answer. Don't ignore tool results!
"""
            
            response = self.llm_config.generate_response(prompt, system_prompt)
            
            # Parse response
            thought, action, action_input, answer = self._parse_response(response)
            
            state["thought"] = thought
            state["action"] = action
            state["action_input"] = action_input
            state["final_answer"] = answer
            state["iteration_count"] += 1
            
            logger.info(f"Reasoning iteration {state['iteration_count']}: thought='{thought[:50]}...'")
            
        except Exception as e:
            logger.error(f"Error in reason_node: {e}")
            state["final_answer"] = "I apologize, but I encountered an error. Please try again."
        
        return state
    
    def tool_node(self, state: AgentState) -> AgentState:
        """
        Tool execution node - executes the selected tool with improved parameter handling.
        """
        try:
            action = state["action"]
            action_input = state["action_input"]
            
            if action not in TOOLS:
                state["observation"] = f"Error: Unknown tool '{action}'. Available tools: {', '.join(TOOLS.keys())}"
                return state
            
            # Map positional parameters to named parameters
            if any(k.startswith('param_') for k in action_input.keys()):
                action_input = self._map_positional_params(action, action_input, state["current_user"])
            
            # Add username from state if needed and not provided
            if action in ['view_bookings', 'get_user_context', 'book_session', 'submit_feedback']:
                if 'username' not in action_input and state["current_user"]:
                    action_input['username'] = state["current_user"]
            
            logger.info(f"Executing tool: {action} with params: {action_input}")
            
            # Execute tool
            tool_func = TOOLS[action]
            result = tool_func(**action_input)
            
            # Format observation with clear structure
            if isinstance(result, dict):
                if result.get("status") == "success":
                    state["observation"] = f"SUCCESS: {str(result)}"
                else:
                    state["observation"] = f"RESULT: {str(result)}"
            else:
                state["observation"] = str(result)
            
            logger.info(f"Tool result: {state['observation'][:100]}...")
            
        except TypeError as e:
            logger.error(f"Parameter error in tool_node: {e}")
            state["observation"] = f"Error: Missing or incorrect parameters for {action}. Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error in tool_node: {e}")
            state["observation"] = f"Error executing tool: {str(e)}"
        
        return state
    
    def _map_positional_params(self, action: str, params: Dict[str, Any], current_user: str) -> Dict[str, Any]:
        """Map positional parameters to named parameters based on tool signature."""
        # Define parameter mappings for each tool
        param_mappings = {
            'view_bookings': ['username'],
            'get_user_context': ['username'],
            'check_availability': ['service_type', 'date'],
            'book_session': ['username', 'service_type', 'date_time', 'notes'],
            'cancel_booking': ['booking_id'],
            'submit_feedback': ['username', 'feedback_text', 'rating'],
            'get_fitness_plan': ['fitness_level', 'goals', 'equipment_available', 'duration'],
            'get_nutrition_advice': ['dietary_preferences', 'fitness_goals', 'restrictions']
        }
        
        if action not in param_mappings:
            return params
        
        expected_params = param_mappings[action]
        mapped_params = {}
        
        # Extract positional parameters in order
        positional = []
        for i in range(len(params)):
            if f'param_{i}' in params:
                positional.append(params[f'param_{i}'])
        
        # Map to named parameters
        for i, value in enumerate(positional):
            if i < len(expected_params):
                mapped_params[expected_params[i]] = value
        
        # Add any explicitly named parameters
        for key, value in params.items():
            if not key.startswith('param_'):
                mapped_params[key] = value
        
        # Auto-fill username if needed
        if 'username' in expected_params and 'username' not in mapped_params:
            mapped_params['username'] = current_user
        
        return mapped_params
    
    def observe_node(self, state: AgentState) -> AgentState:
        """
        Observation node - processes tool output.
        This is mainly a pass-through but could add processing.
        """
        # Could add observation processing here if needed
        return state
    
    def respond_node(self, state: AgentState) -> AgentState:
        """
        Response node - generates final answer if not already set.
        """
        if not state.get("final_answer"):
            # Generate final response based on conversation
            system_prompt = self.persona_manager.get_system_prompt()
            
            history = ""
            for msg in state["messages"]:
                history += f"{msg['role']}: {msg['content']}\n"
            
            if state.get("observation"):
                history += f"\nObservation: {state['observation']}\n"
            
            prompt = f"""{history}

Now provide your final answer to the user in your persona's style.
Start your response with "Answer: "
"""
            
            response = self.llm_config.generate_response(prompt, system_prompt)
            
            # Extract answer
            if "Answer:" in response:
                state["final_answer"] = response.split("Answer:")[1].strip()
            else:
                state["final_answer"] = response.strip()
        
        return state
    
    def should_continue(self, state: AgentState) -> str:
        """
        Routing function to decide next step.
        """
        # Check if we have a final answer
        if state.get("final_answer"):
            return "respond"
        
        # Check if we have an action to execute
        if state.get("action") and state["action"] != "":
            return "continue"
        
        # Check iteration limit
        if state["iteration_count"] >= state["max_iterations"]:
            return "respond"
        
        # Default: continue reasoning
        return "continue"
    
    def _parse_response(self, response: str) -> tuple:
        """
        Parse LLM response to extract thought, action, and answer.
        
        Returns:
            (thought, action, action_input, answer)
        """
        thought = ""
        action = ""
        action_input = {}
        answer = ""
        
        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action:|Answer:)|$)", response, re.DOTALL | re.IGNORECASE)
        if thought_match:
            thought = thought_match.group(1).strip()
        
        # Extract Answer (final response)
        answer_match = re.search(r"Answer:\s*(.+?)$", response, re.DOTALL | re.IGNORECASE)
        if answer_match:
            answer = answer_match.group(1).strip()
            return thought, action, action_input, answer
        
        # Extract Action
        action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response, re.DOTALL | re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip()
            params_str = action_match.group(2).strip()
            
            # Parse parameters
            try:
                action_input = self._parse_parameters(params_str)
            except Exception as e:
                logger.error(f"Error parsing parameters: {e}")
                action_input = {}
        
        return thought, action, action_input, answer
    
    def _parse_parameters(self, params_str: str) -> Dict[str, Any]:
        """Parse function parameters from string with improved robustness."""
        params = {}
        
        if not params_str:
            return params
        
        # Split by comma (but not within quotes)
        parts = re.split(r',\s*(?=(?:[^"\']*["\'][^"\']*["\'])*[^"\']*$)', params_str)
        
        # Common parameter name mappings for tools
        param_names = {
            'view_bookings': ['username'],
            'get_user_context': ['username'],
            'check_availability': ['service_type', 'date'],
            'book_session': ['username', 'service_type', 'date_time', 'notes'],
            'cancel_booking': ['booking_id'],
            'submit_feedback': ['username', 'feedback_text', 'rating'],
            'get_fitness_plan': ['fitness_level', 'goals', 'equipment_available', 'duration'],
            'get_nutrition_advice': ['dietary_preferences', 'fitness_goals', 'restrictions']
        }
        
        param_index = 0
        for part in parts:
            part = part.strip()
            if '=' in part:
                # Named parameter
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
            else:
                # Positional parameter - try to infer name
                value = part
                key = f"param_{param_index}"
                param_index += 1
            
            # Clean up value
            value = value.strip('"\'')
            
            # Try to convert to appropriate type
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit() and value.count('.') <= 1:
                try:
                    value = float(value)
                except:
                    pass
            
            params[key] = value
        
        return params
    
    def run(self, user_message: str, current_user: str, 
            conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Run the agent on a user message.
        
        Args:
            user_message: User's input
            current_user: Current username
            conversation_history: Previous messages
        
        Returns:
            Agent's response
        """
        # Initialize state
        if conversation_history is None:
            conversation_history = []
        
        # Add current message
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        initial_state = {
            "messages": conversation_history,
            "current_user": current_user,
            "thought": "",
            "action": "",
            "action_input": {},
            "observation": "",
            "final_answer": "",
            "iteration_count": 0,
            "max_iterations": 5
        }
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Get final answer
            answer = final_state.get("final_answer", "I'm sorry, I couldn't process that request.")
            
            # Add to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            return answer
        
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return "I apologize, but I encountered an error processing your request."
