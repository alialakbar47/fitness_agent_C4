"""FitFusion AI Fitness Assistant - Streamlit Application."""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

from agent.graph import FitFusionAgent
from agent.config import LLMConfig
from agent.personas import PersonaManager
from database.db_manager import DatabaseManager
from utils.helpers import (
    ExperimentLogger, 
    validate_email, 
    get_persona_emoji,
    format_booking_list
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FitFusion AI Assistant",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #F1F8E9;
        border-left: 4px solid #66BB6A;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'llm_config' not in st.session_state:
        st.session_state.llm_config = LLMConfig()
    if 'persona_manager' not in st.session_state:
        st.session_state.persona_manager = PersonaManager()
    if 'agent' not in st.session_state:
        st.session_state.agent = FitFusionAgent(
            st.session_state.llm_config,
            st.session_state.persona_manager
        )
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    if 'experiment_logger' not in st.session_state:
        st.session_state.experiment_logger = ExperimentLogger()


def login_page():
    """Display login/signup page."""
    st.markdown('<div class="main-header">💪 FitFusion AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your Personal AI Fitness Companion</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        
        if st.button("Login", key="login_button"):
            if username:
                user = st.session_state.db.get_user_by_username(username)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}! 🎉")
                    st.rerun()
                else:
                    st.error("User not found. Please sign up first!")
            else:
                st.warning("Please enter a username.")
    
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username")
        email = st.text_input("Email Address", key="signup_email")
        
        if st.button("Sign Up", key="signup_button"):
            if new_username and email:
                if not validate_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    success, message = st.session_state.db.create_user(new_username, email)
                    if success:
                        st.success(message)
                        st.session_state.logged_in = True
                        st.session_state.username = new_username
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields.")


def settings_sidebar():
    """Display settings in sidebar."""
    st.sidebar.header("⚙️ Configuration")
    
    # Persona selection
    st.sidebar.subheader("🎭 Persona")
    personas = st.session_state.persona_manager.get_all_personas()
    
    persona_options = {k: f"{v}" for k, v in personas.items()}
    current_persona = st.session_state.persona_manager.current_persona
    
    selected_persona = st.sidebar.selectbox(
        "Choose your coach style",
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x],
        index=list(persona_options.keys()).index(current_persona),
        key="persona_select"
    )
    
    if selected_persona != current_persona:
        st.session_state.persona_manager.set_persona(selected_persona)
        st.session_state.agent = FitFusionAgent(
            st.session_state.llm_config,
            st.session_state.persona_manager
        )
    
    # Display persona description
    with st.sidebar.expander("ℹ️ About this persona"):
        st.write(st.session_state.persona_manager.get_persona_description(selected_persona))
    
    st.sidebar.divider()
    
    # Model configuration
    st.sidebar.subheader("🤖 Model Settings")
    
    model_options = LLMConfig.get_available_models()
    current_model = st.session_state.llm_config.model_name
    
    selected_model = st.sidebar.selectbox(
        "Model",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=list(model_options.keys()).index(current_model) if current_model in model_options else 0,
        key="model_select"
    )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.llm_config.temperature,
        step=0.1,
        help="Higher = more creative, Lower = more focused",
        key="temp_slider"
    )
    
    top_p = st.sidebar.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.llm_config.top_p,
        step=0.05,
        help="Nucleus sampling threshold",
        key="top_p_slider"
    )
    
    max_tokens = st.sidebar.select_slider(
        "Max Tokens",
        options=[512, 1024, 2048, 4096],
        value=st.session_state.llm_config.max_tokens,
        help="Maximum response length",
        key="tokens_slider"
    )
    
    # Update configuration
    st.session_state.llm_config.update_config(
        model_name=selected_model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    
    st.sidebar.divider()
    
    # Prompt engineering style
    st.sidebar.subheader("📝 Prompt Style")
    
    prompt_styles = {
        "zero_shot": "Zero-Shot (No examples)",
        "few_shot": "Few-Shot (With examples)",
        "chain_of_thought": "Chain-of-Thought"
    }
    
    current_style = st.session_state.persona_manager.current_prompt_style
    
    selected_style = st.sidebar.selectbox(
        "Prompt Engineering",
        options=list(prompt_styles.keys()),
        format_func=lambda x: prompt_styles[x],
        index=list(prompt_styles.keys()).index(current_style),
        key="prompt_style_select"
    )
    
    if selected_style != current_style:
        st.session_state.persona_manager.set_prompt_style(selected_style)
        st.session_state.agent = FitFusionAgent(
            st.session_state.llm_config,
            st.session_state.persona_manager
        )
    
    st.sidebar.divider()
    
    # User info and actions
    st.sidebar.subheader(f"👤 {st.session_state.username}")
    
    if st.sidebar.button("📅 View My Bookings"):
        bookings = st.session_state.db.get_user_bookings(st.session_state.username)
        with st.sidebar.expander("Your Bookings", expanded=True):
            st.markdown(format_booking_list(bookings))
    
    if st.sidebar.button("🔄 Clear Chat History"):
        st.session_state.conversation_history = []
        st.success("Chat history cleared!")
        st.rerun()
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.conversation_history = []
        st.rerun()


def chat_interface():
    """Main chat interface."""
    st.markdown('<div class="main-header">💪 FitFusion AI Assistant</div>', unsafe_allow_html=True)
    
    # Display current persona
    persona_emoji = get_persona_emoji(st.session_state.persona_manager.current_persona)
    persona_name = st.session_state.persona_manager.get_persona_name()
    st.markdown(f'<div class="sub-header">Currently chatting with: {persona_emoji} {persona_name}</div>', 
                unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        for message in st.session_state.conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f'''
                <div class="chat-message user-message">
                    <strong>You:</strong><br>{content}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="chat-message assistant-message">
                    <strong>{persona_emoji} Assistant:</strong><br>{content}
                </div>
                ''', unsafe_allow_html=True)
    
    # Input area
    st.divider()
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Your message:",
            key="user_input",
            placeholder="Ask me anything about fitness, nutrition, or bookings...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 📤", use_container_width=True)
    
    # Quick action buttons
    st.caption("Quick Actions:")
    quick_cols = st.columns(4)
    
    with quick_cols[0]:
        if st.button("📅 Book Session"):
            user_input = "I want to book a session"
            send_button = True
    
    with quick_cols[1]:
        if st.button("🏋️ Get Workout"):
            user_input = "Create me a workout plan"
            send_button = True
    
    with quick_cols[2]:
        if st.button("🥗 Nutrition Advice"):
            user_input = "Give me nutrition advice"
            send_button = True
    
    with quick_cols[3]:
        if st.button("📊 My Schedule"):
            user_input = "Show me my bookings"
            send_button = True
    
    # Process input
    if send_button and user_input:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Show loading spinner
        with st.spinner(f"{persona_emoji} Thinking..."):
            # Get agent response
            response = st.session_state.agent.run(
                user_input,
                st.session_state.username,
                st.session_state.conversation_history[:-1]  # Exclude the just-added message
            )
        
        # Add assistant response
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Log interaction
        config = {
            "persona": st.session_state.persona_manager.current_persona,
            "prompt_style": st.session_state.persona_manager.current_prompt_style,
            **st.session_state.llm_config.get_config_dict()
        }
        
        st.session_state.experiment_logger.log_interaction(
            user_input,
            response,
            config,
            {"username": st.session_state.username}
        )
        
        # Rerun to display new messages
        st.rerun()


def main():
    """Main application entry point."""
    init_session_state()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        settings_sidebar()
        chat_interface()
    
    # Footer
    st.divider()
    st.caption("FitFusion AI Assistant - Powered by Google Gemini & LangGraph")


if __name__ == "__main__":
    main()
