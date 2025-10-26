# FitFusion AI Fitness Assistant

A conversational AI fitness assistant powered by Google Gemini 2.0, LangGraph ReAct architecture, and Streamlit.

## Features

- **Two AI Personas**: Drill Sergeant Coach (🎖️) and Helpful Assistant (😊)
- **8 Functional Tools**: Session booking, fitness plans, nutrition advice, user context
- **ReAct Agent**: Reasoning + Acting workflow with LangGraph
- **Flexible Time Parsing**: Natural language understanding ("book at 3", "tomorrow at 9pm")
- **SQLite Database**: Persistent storage for users, bookings, and feedback
- **Experiment Logging**: Track all interactions and configurations

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API Key ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/alialakbar47/fitness_agent_C4.git
cd fitness_agent_C4
```

2. **Set up environment variables**

```bash
# Create .env file with your API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

3. **Run with Docker**

```bash
docker-compose up --build
```

4. **Access the application**
   Open http://localhost:8501 in your browser

## Usage

**Sign up/Login** → **Select Persona** → **Chat naturally**

Example interactions:

- "Book yoga for next Monday at 3pm"
- "Show me my bookings"
- "Create a workout plan for muscle gain"
- "Give me nutrition advice for weight loss"

## Configuration

Customize in the sidebar:

- **Persona**: Drill Sergeant (strict) or Helpful Assistant (friendly)
- **Model**: Gemini 2.0 Flash, Gemini Exp 1206, or Gemini 2.0 Flash Thinking
- **Temperature**: 0.3-0.9 (recommended: 0.7)
- **Top P**: 0.25-0.95 (recommended: 0.95)
- **Prompt Style**: Few-shot (recommended), Chain-of-thought, or Zero-shot

## Project Structure

```
HW4/
├── agent/              # ReAct agent logic
│   ├── graph.py       # LangGraph workflow
│   ├── tools.py       # 8 functional tools
│   ├── config.py      # LLM configuration
│   └── personas.py    # Persona management
├── prompts/            # System prompts & examples
├── database/           # SQLite schema & manager
├── utils/              # Helpers & experiment logger
├── app.py              # Streamlit interface
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Container orchestration
```

## Technologies

- **LLM**: Google Gemini 2.0 Flash (Experimental)
- **Agent Framework**: LangGraph 0.2+
- **Web Framework**: Streamlit 1.39.0
- **Database**: SQLite
- **Deployment**: Docker + Docker Compose

## Key Features Explained

### ReAct Agent Architecture

The agent follows a Thought → Action → Observation → Answer loop:

1. **Thought**: Agent reasons about the user's request
2. **Action**: Calls appropriate tools (booking, fitness plans, etc.)
3. **Observation**: Receives tool results
4. **Answer**: Responds to user in persona's style

### Flexible Time Parsing

Understands natural language:

- "3" → 15:00 (if afternoon context)
- "3pm" → 15:00
- "tomorrow at 9" → next day at 09:00
- "2025-11-03 14:00" → exact datetime

### Anti-Hallucination Mechanisms

- Explicit instructions forbidding made-up booking IDs
- Validation layer detecting hallucination attempts
- Current date injection to prevent past date bookings
- Clear error handling when tools fail

## License

MIT License

## Author

Ali Alakbar
