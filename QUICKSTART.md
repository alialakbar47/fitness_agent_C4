# Quick Start Guide - FitFusion AI Assistant

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### Step 2: Configure Environment

1. Create a `.env` file in the project root:
   ```bash
   GOOGLE_API_KEY=paste_your_api_key_here
   ```

### Step 3: Run with Docker

```bash
# Start the application
docker-compose up

# Access at: http://localhost:8501
```

That's it! 🎉

---

## 📝 First Time Usage

### 1. Sign Up

- Enter a username (e.g., "john_doe")
- Enter your email
- Click "Sign Up"

### 2. Choose Your Coach

In the sidebar, select one of three personas:

- 🎖️ **Drill Sergeant** - Strict and commanding
- 😊 **Helpful Assistant** - Friendly and supportive
- 💪 **Motivational Coach** - High-energy and inspiring

### 3. Start Chatting!

Try these example queries:

**Book a Session:**

```
"I want to book a personal training session for tomorrow at 2pm"
```

**Get a Workout:**

```
"Create me a beginner workout plan for weight loss"
```

**Nutrition Advice:**

```
"I'm vegetarian and want to build muscle, what should I eat?"
```

**View Schedule:**

```
"Show me all my bookings"
```

---

## ⚙️ Quick Settings Guide

### Model Settings (Sidebar)

**Model:**

- `gemini-1.5-flash` - Fast (recommended)
- `gemini-1.5-pro` - More intelligent
- `gemini-pro` - Balanced

**Temperature:** (0.0 - 1.0)

- 0.0 = Consistent, factual
- 0.7 = Balanced (recommended)
- 1.0 = Creative, varied

**Prompt Style:**

- `Few-Shot` - Best results (recommended)
- `Zero-Shot` - No examples
- `Chain-of-Thought` - Detailed reasoning

---

## 🎯 Common Tasks

### Book a Session

```
"Book a group class for Friday at 6pm"
```

### Cancel Booking

```
"Cancel my booking #42"
or
"Show my bookings and cancel the Tuesday one"
```

### Get Fitness Plan

```
"I'm intermediate level, want to gain muscle, have a full gym,
need a 60 minute workout"
```

### Submit Feedback

```
"I want to leave feedback: The trainer was amazing! 5 stars"
```

---

## 🛠️ Troubleshooting

### "Error: API Key not found"

- Make sure `.env` file exists
- Check `GOOGLE_API_KEY=` has your actual key
- Restart: `docker-compose restart`

### Application won't start

```bash
# Check if port 8501 is available
docker-compose down
docker-compose up
```

### Database issues

```bash
# Reset database
rm -rf data/
docker-compose restart
```

### Clear chat history

Click "🔄 Clear Chat History" in the sidebar

---

## 📊 Experiment Tracking

All your interactions are logged for analysis!

View logs:

```bash
cat logs/experiment_logs.json
```

Export logs from the UI or programmatically:

```python
from utils.helpers import ExperimentLogger
logger = ExperimentLogger()
stats = logger.get_statistics()
print(stats)
```

---

## 🎓 Tips for Best Results

1. **Be Specific**: "Book Tuesday 2pm" vs "Book sometime next week"
2. **Use Natural Language**: The agent understands conversation
3. **Try Different Personas**: Each has unique strengths
4. **Experiment with Settings**: Temperature affects creativity
5. **Check Examples**: See few-shot examples in `prompts/examples.py`

---

## 🆘 Need Help?

- 📖 Full documentation: See `README.md`
- 🔍 Technical details: See `REFLECTION.md`
- 💬 Chat with the assistant: Ask "What can you help me with?"

---

## 🎯 Next Steps

1. ✅ Sign up and create your account
2. ✅ Try all three personas
3. ✅ Book a session
4. ✅ Get a fitness plan
5. ✅ Experiment with settings
6. ✅ Review your logs

**Enjoy your FitFusion experience! 💪**
