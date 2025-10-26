# 💪 FitFusion AI Fitness Assistant

A ReAct-style AI fitness assistant built with LangGraph that combines booking management, fitness planning, and nutrition consulting with persona-based interactions.

## 🎯 Project Overview

FitFusion AI Assistant is an intelligent conversational agent that helps users with:

- **Session Booking**: Schedule personal training, group classes, and nutrition consultations
- **Fitness Planning**: Get customized workout plans based on goals and fitness level
- **Nutrition Advice**: Receive personalized meal recommendations
- **Progress Tracking**: View booking history and user context

The assistant features three distinct personas with configurable LLM settings and supports multiple prompt engineering approaches.

## 🏗️ Architecture

### Technology Stack

- **Framework**: LangGraph for ReAct agent implementation
- **LLM**: Google Gemini API (gemini-1.5-flash, gemini-1.5-pro, gemini-pro)
- **Database**: SQLite (serverless, file-based)
- **Frontend**: Streamlit web interface
- **Containerization**: Docker & Docker Compose

### Project Structure

```
fitfusion-agent/
├── app.py                      # Main Streamlit application
├── agent/
│   ├── graph.py               # LangGraph ReAct workflow
│   ├── personas.py            # Persona management
│   ├── tools.py               # 8 agent tools
│   └── config.py              # LLM configuration
├── database/
│   ├── db_manager.py          # SQLite operations
│   └── schema.sql             # Database schema
├── prompts/
│   ├── system_prompts.py      # Persona system prompts
│   └── examples.py            # Few-shot examples
├── utils/
│   └── helpers.py             # Utility functions
├── data/                       # SQLite database (auto-created)
├── logs/                       # Experiment logs (auto-created)
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or extract the project**

   ```bash
   cd c:\Users\thekn\Desktop\HW4
   ```

2. **Set up environment variables**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your Google API key
   # GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. **Build and run with Docker**

   ```bash
   # Build the Docker image
   docker-compose build

   # Start the application
   docker-compose up
   ```

4. **Access the application**
   - Open your browser to: `http://localhost:8501`
   - The application will be ready to use!

### Running Without Docker (Alternative)

If you prefer to run locally without Docker:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
# Windows PowerShell:
$env:GOOGLE_API_KEY="your_api_key_here"
# Linux/Mac:
export GOOGLE_API_KEY="your_api_key_here"

# Run the application
streamlit run app.py
```

## 🎭 Features

### Three Distinct Personas

1. **🎖️ Drill Sergeant Coach**

   - Strict, no-nonsense approach
   - Direct commands and high expectations
   - Military-style discipline and motivation
   - Example: "Drop and give me 20! No excuses!"

2. **😊 Helpful Assistant**

   - Friendly and supportive tone
   - Patient explanations and guidance
   - Encouraging without being pushy
   - Example: "Let's work together on achieving your goals!"

3. **💪 Motivational Coach**
   - High-energy and enthusiastic
   - Inspirational language and metaphors
   - Celebrates every achievement
   - Example: "You're unstoppable! Let's crush these goals!"

### Eight Powerful Tools

1. **check_availability** - Check available time slots
2. **book_session** - Schedule appointments
3. **view_bookings** - See user's bookings
4. **cancel_booking** - Cancel appointments
5. **submit_feedback** - Collect user feedback
6. **get_fitness_plan** - Generate workout routines
7. **get_nutrition_advice** - Provide meal plans
8. **get_user_context** - Fetch user history

### Configurable LLM Settings

- **Model Selection**: Choose between Gemini models

  - gemini-1.5-flash (Fast, efficient)
  - gemini-1.5-pro (More capable)
  - gemini-pro (Stable)

- **Temperature**: 0.0 to 1.0 (creativity vs focus)
- **Top P**: 0.0 to 1.0 (nucleus sampling)
- **Max Tokens**: 512, 1024, 2048, 4096 (response length)

### Prompt Engineering Styles

- **Zero-Shot**: No examples, pure reasoning
- **Few-Shot**: Includes example interactions
- **Chain-of-Thought**: Step-by-step reasoning

## 📊 Database Schema

### Users Table

```sql
id INTEGER PRIMARY KEY
username TEXT UNIQUE
email TEXT
created_at TIMESTAMP
```

### Bookings Table

```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY
service_type TEXT (personal_training, group_class, nutrition_consult)
date_time TIMESTAMP
status TEXT (confirmed, cancelled)
notes TEXT
```

### Feedback Table

```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY
feedback_text TEXT
rating INTEGER (1-5)
created_at TIMESTAMP
```

## 🔄 ReAct Agent Flow

The agent follows the ReAct (Reasoning + Acting) pattern:

```
1. Thought: Agent reasons about user request
2. Action: Selects and calls appropriate tool
3. Observation: Receives tool result
4. [Repeat 1-3 if needed]
5. Answer: Provides final response to user
```

**Example:**

```
User: "Book me a training session tomorrow at 10am"

Thought: User wants to book a session. I should check availability first.
Action: check_availability("personal_training", "2024-10-27")
Observation: {"available_slots": ["09:00", "10:00", "11:00"...]}

Thought: 10:00 is available. Now I can book it.
Action: book_session("john_doe", "personal_training", "2024-10-27 10:00")
Observation: {"status": "success", "booking_id": 42}

Answer: Your training session is locked in for tomorrow at 10am! Booking ID: 42.
```

## 🧪 Experiment Tracking

All interactions are logged to `logs/experiment_logs.json` with:

- User query
- Agent response
- Configuration (persona, model, temperature, etc.)
- Timestamp and metadata

This enables comparison of:

- Different personas
- Various LLM settings
- Prompt engineering approaches

## 📝 Usage Examples

### Booking a Session

```
User: "I want to book a personal training session for next Monday at 2pm"
Assistant: [Checks availability, books session, confirms]
```

### Getting a Workout Plan

```
User: "Create me a beginner workout plan, I have dumbbells at home"
Assistant: [Generates customized workout with warm-up, exercises, cool-down]
```

### Nutrition Advice

```
User: "I'm vegetarian and trying to build muscle, what should I eat?"
Assistant: [Provides meal plan with breakfast, lunch, dinner suggestions]
```

### Viewing Schedule

```
User: "Show me my upcoming appointments"
Assistant: [Retrieves and displays all bookings]
```

### Canceling Bookings

```
User: "Cancel my Tuesday session"
Assistant: [Shows bookings, identifies Tuesday session, cancels it]
```

## 🐳 Docker Commands

```bash
# Build the image
docker-compose build

# Start the application
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up --build

# Remove all containers and volumes
docker-compose down -v
```

## 📂 Data Persistence

- **Database**: Stored in `data/fitfusion.db` (persisted via Docker volume)
- **Logs**: Stored in `logs/experiment_logs.json` (persisted via Docker volume)

Both directories are mounted as volumes, so data persists even when containers are stopped.

## 🔧 Configuration

### Environment Variables (.env)

```bash
GOOGLE_API_KEY=your_api_key_here
DATABASE_PATH=data/fitfusion.db
LOG_LEVEL=INFO
LOG_PATH=logs/experiment_logs.json
```

### Port Configuration

- Default: `http://localhost:8501`
- Change in `docker-compose.yml`: `ports: - "YOUR_PORT:8501"`

## 🧠 LangGraph Implementation

The agent uses a state graph with four main nodes:

1. **Reason Node**: LLM generates thoughts and decides actions
2. **Act Node**: Executes selected tool
3. **Observe Node**: Processes tool results
4. **Respond Node**: Generates final answer

Conditional edges control flow:

- Continue reasoning → Tool execution → Observation → Reason again
- Ready to answer → Respond → End

Maximum 5 iterations to prevent infinite loops.

## 🎨 UI Features

- **Clean, modern fitness-themed design**
- **Responsive layout** with sidebar configuration
- **Real-time chat interface** with message history
- **Quick action buttons** for common tasks
- **Collapsible settings panel**
- **Emoji-enhanced UI** for better UX

## 📊 Experiment Analysis

Access experiment logs programmatically:

```python
from utils.helpers import ExperimentLogger

logger = ExperimentLogger()

# Get recent logs
logs = logger.get_logs(limit=10)

# Get statistics
stats = logger.get_statistics()
print(f"Total interactions: {stats['total_interactions']}")
print(f"Persona usage: {stats['persona_usage']}")

# Export logs
logger.export_logs("my_experiments.json")
```

## 🔍 Testing Scenarios

Recommended test cases:

1. **Simple Booking**: "Book a group class tomorrow"
2. **Multi-step Booking**: "Check what's available Friday afternoon and book the 3pm slot"
3. **Fitness Planning**: "I'm a beginner who wants to lose weight, create me a plan"
4. **Nutrition Query**: "What should I eat post-workout if I'm vegan?"
5. **Schedule Management**: "Show my bookings and cancel the one on Tuesday"
6. **Context Retrieval**: "What have I booked in the past?"

## 🛠️ Troubleshooting

### API Key Issues

- Ensure `GOOGLE_API_KEY` is set in `.env` file
- Verify the key is valid at [Google AI Studio](https://makersuite.google.com/)

### Docker Issues

- Check Docker is running: `docker ps`
- View logs: `docker-compose logs -f`
- Rebuild: `docker-compose up --build`

### Database Issues

- Database is auto-created on first run
- Located at `data/fitfusion.db`
- To reset: Delete the file and restart

### Port Already in Use

- Change port in `docker-compose.yml`
- Or stop conflicting service: `docker-compose down`

## 📚 Assignment Requirements Checklist

- ✅ LangGraph ReAct agent with manual loop implementation
- ✅ 8 functional tools (booking, fitness, nutrition)
- ✅ 3 distinct personas with different communication styles
- ✅ SQLite database with user, bookings, and feedback tables
- ✅ Configurable LLM settings (model, temperature, top_p, max_tokens)
- ✅ Three prompt engineering styles (zero-shot, few-shot, CoT)
- ✅ Streamlit web interface with chat and settings
- ✅ Experiment logging and tracking
- ✅ Docker containerization
- ✅ Comprehensive documentation

## 🎓 Key Insights

### Best Persona for Different Tasks:

- **Booking Management**: Helpful Assistant (clear, step-by-step)
- **Fitness Planning**: Motivational Coach (inspiring, energetic)
- **Nutrition Advice**: Drill Sergeant (disciplined, no-nonsense)

### Optimal Configuration:

- **Temperature**: 0.7 for balanced creativity and accuracy
- **Model**: gemini-1.5-flash for speed, gemini-1.5-pro for complex queries
- **Prompt Style**: Few-shot for consistent tool usage

## 📄 License

This project is created for educational purposes as part of a university assignment.

## 👤 Author

Created for HW4 - AI Agents Assignment

## 🙏 Acknowledgments

- Google Gemini API for LLM capabilities
- LangGraph for agent framework
- Streamlit for web interface
- SQLite for database management

---

**Note**: This is a demonstration project for educational purposes. For production use, implement proper authentication, input validation, error handling, and security measures.
