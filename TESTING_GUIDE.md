# Testing Guide - FitFusion AI Assistant

This guide provides comprehensive test scenarios to validate the FitFusion AI Assistant functionality.

---

## 🧪 Test Scenario Categories

1. Authentication & User Management
2. Booking Operations
3. Fitness Planning
4. Nutrition Consulting
5. Multi-Step Interactions
6. Persona Variations
7. Configuration Testing
8. Error Handling

---

## 1️⃣ Authentication & User Management

### Test 1.1: New User Sign Up

**Steps:**

1. Open application at http://localhost:8501
2. Go to "Sign Up" tab
3. Enter username: "test_user"
4. Enter email: "test@example.com"
5. Click "Sign Up"

**Expected Result:**

- ✅ Success message displayed
- ✅ Automatically logged in
- ✅ Redirected to chat interface
- ✅ Username shown in sidebar

### Test 1.2: Existing User Login

**Steps:**

1. Logout if logged in
2. Go to "Login" tab
3. Enter username: "test_user"
4. Click "Login"

**Expected Result:**

- ✅ Welcome message displayed
- ✅ Successfully logged in
- ✅ Previous chat history empty (first time)

### Test 1.3: Invalid Login

**Steps:**

1. Logout if logged in
2. Try to login with username: "nonexistent_user"

**Expected Result:**

- ❌ Error message: "User not found"
- ❌ Not logged in

---

## 2️⃣ Booking Operations

### Test 2.1: Check Availability

**Query:**

```
"What times are available for personal training tomorrow?"
```

**Expected Behavior:**

- ✅ Agent calls `check_availability`
- ✅ Returns list of available time slots
- ✅ Response includes date and times

**Validation:**

- Check that times are in HH:MM format
- Verify date is correct

### Test 2.2: Simple Booking

**Query:**

```
"Book me a personal training session for tomorrow at 2pm"
```

**Expected Behavior:**

- ✅ Agent checks availability (optional but good)
- ✅ Agent calls `book_session` with correct parameters
- ✅ Returns booking confirmation with ID
- ✅ Persona-appropriate response

**Validation:**

- Note the booking ID
- Verify service_type is "personal_training"
- Check date/time format

### Test 2.3: Book Group Class

**Query:**

```
"I want to join a group class on Friday at 6pm"
```

**Expected Behavior:**

- ✅ Correct service_type: "group_class"
- ✅ Booking confirmed
- ✅ Booking ID provided

### Test 2.4: Book Nutrition Consultation

**Query:**

```
"Schedule a nutrition consult for next Monday at 10am"
```

**Expected Behavior:**

- ✅ service_type: "nutrition_consult"
- ✅ Booking successful

### Test 2.5: View All Bookings

**Query:**

```
"Show me all my bookings"
or
"What do I have scheduled?"
```

**Expected Behavior:**

- ✅ Agent calls `view_bookings`
- ✅ Lists all bookings with details
- ✅ Shows booking IDs, dates, times, statuses

**Validation:**

- All previous bookings should appear
- Status should be "confirmed"

### Test 2.6: Cancel Booking

**Query:**

```
"Cancel my booking with ID [use actual ID from previous test]"
or
"Cancel booking #42"
```

**Expected Behavior:**

- ✅ Agent calls `cancel_booking` with correct ID
- ✅ Cancellation confirmed
- ✅ Status changed to "cancelled"

**Validation:**

- View bookings again - should show as cancelled

### Test 2.7: Multi-Step Booking

**Query:**

```
"I want to book a session but first show me what times are available tomorrow"
```

**Expected Behavior:**

1. ✅ Shows available times first
2. ✅ Waits for user to choose
3. ✅ Then books the selected time

---

## 3️⃣ Fitness Planning

### Test 3.1: Beginner Weight Loss Plan

**Query:**

```
"Create me a beginner workout plan for weight loss. I don't have any equipment."
```

**Expected Behavior:**

- ✅ Calls `get_fitness_plan("beginner", "weight_loss", "none", "45min")`
- ✅ Returns structured workout with:
  - Warm-up exercises
  - Main workout exercises
  - Cool-down exercises
  - Sets and reps
- ✅ Appropriate for no equipment

**Validation:**

- All exercises should be bodyweight
- Appropriate intensity for beginners

### Test 3.2: Intermediate Muscle Gain

**Query:**

```
"I'm intermediate level and want to build muscle. I have dumbbells at home. Give me a 60-minute workout."
```

**Expected Behavior:**

- ✅ Calls `get_fitness_plan("intermediate", "muscle_gain", "basic", "60min")`
- ✅ Includes dumbbell exercises
- ✅ Focus on strength training
- ✅ Higher intensity than beginner

### Test 3.3: Advanced with Full Gym

**Query:**

```
"I'm advanced and have access to a full gym. I want to improve endurance. 45 minutes."
```

**Expected Behavior:**

- ✅ Calls `get_fitness_plan("advanced", "endurance", "full_gym", "45min")`
- ✅ Uses gym equipment
- ✅ High-intensity endurance focused
- ✅ Advanced exercises

### Test 3.4: Vague Fitness Request

**Query:**

```
"Give me a workout plan"
```

**Expected Behavior:**

- ✅ Agent asks clarifying questions:
  - Fitness level?
  - Goals?
  - Equipment available?
- OR
- ✅ Makes reasonable assumptions and generates plan

---

## 4️⃣ Nutrition Consulting

### Test 4.1: Omnivore Weight Loss

**Query:**

```
"I eat everything and want to lose weight. What should I eat?"
```

**Expected Behavior:**

- ✅ Calls `get_nutrition_advice("omnivore", "weight_loss", "none")`
- ✅ Provides meal plan with:
  - Breakfast options
  - Lunch options
  - Dinner options
  - Snacks
  - Macro recommendations

### Test 4.2: Vegetarian Muscle Gain

**Query:**

```
"I'm vegetarian and trying to build muscle. Help me with my diet."
```

**Expected Behavior:**

- ✅ Calls `get_nutrition_advice("vegetarian", "muscle_gain", "none")`
- ✅ No meat in recommendations
- ✅ High protein vegetarian sources
- ✅ Caloric surplus advice

### Test 4.3: Vegan with Restrictions

**Query:**

```
"I'm vegan and allergic to nuts. What should I eat for endurance training?"
```

**Expected Behavior:**

- ✅ Calls `get_nutrition_advice("vegan", "endurance", "nuts")`
- ✅ All vegan recommendations
- ✅ No nut-based foods
- ✅ Endurance-focused nutrition

### Test 4.4: Keto Diet

**Query:**

```
"I'm on a keto diet and want to maintain my weight. Give me meal ideas."
```

**Expected Behavior:**

- ✅ Calls `get_nutrition_advice("keto", "maintenance", "none")`
- ✅ Low-carb, high-fat meals
- ✅ Keto-appropriate foods only

---

## 5️⃣ Multi-Step Interactions

### Test 5.1: Book and View

**Query:**

```
"Book me a training session tomorrow at 10am and then show me all my bookings"
```

**Expected Behavior:**

1. ✅ Books the session first
2. ✅ Then views all bookings
3. ✅ New booking appears in the list

### Test 5.2: View and Cancel

**Query:**

```
"Show my schedule and cancel the Tuesday session"
```

**Expected Behavior:**

1. ✅ Shows all bookings
2. ✅ Identifies Tuesday session
3. ✅ Cancels it
4. ✅ Confirms cancellation

### Test 5.3: Context-Aware Recommendation

**Query:**

```
"Based on my booking history, recommend a workout for me"
```

**Expected Behavior:**

1. ✅ Calls `get_user_context` first
2. ✅ Analyzes booking patterns
3. ✅ Generates appropriate fitness plan
4. ✅ References user's history in response

### Test 5.4: Complete Fitness Journey

**Conversation:**

```
User: "I want to start getting fit"
Agent: [Asks questions or provides guidance]
User: "I'm a beginner, want to lose weight"
Agent: [Generates workout plan]
User: "What should I eat?"
Agent: [Provides nutrition advice]
User: "Book me a trainer session for next week"
Agent: [Books session]
```

**Expected Behavior:**

- ✅ Maintains conversation context
- ✅ References previous information
- ✅ Coherent multi-turn dialogue

---

## 6️⃣ Persona Variations

Run the same query with all three personas and compare responses.

### Test 6.1: Simple Booking Request

**Query:** "Book me a training session tomorrow at 2pm"

**Expected Responses:**

**Drill Sergeant:**

- ✅ Direct, commanding tone
- ✅ "Get it done" attitude
- ✅ Short, efficient response
- Example: "Booking confirmed at 1400 hours, soldier! ID: 42. Don't be late!"

**Helpful Assistant:**

- ✅ Friendly, supportive tone
- ✅ Detailed explanation
- ✅ Encouraging language
- Example: "Great! I've booked your personal training session for tomorrow at 2pm. Your booking ID is 42. Looking forward to your session! 😊"

**Motivational Coach:**

- ✅ High-energy, enthusiastic tone
- ✅ Pumped up language
- ✅ Celebrates the action
- Example: "YES! Let's DO THIS! 💪 Your training session is LOCKED IN for tomorrow at 2pm! Booking ID: 42. You're taking action and that's AMAZING! Get ready to crush it!"

### Test 6.2: Skipped Workout Confession

**Query:** "I skipped my workout yesterday"

**Expected Responses:**

**Drill Sergeant:**

- ✅ Tough love response
- ✅ Accountability focused
- Example: "Unacceptable! No excuses! Get up RIGHT NOW and do 50 burpees to make up for it. Then book your next session!"

**Helpful Assistant:**

- ✅ Understanding and supportive
- ✅ Problem-solving approach
- Example: "That's okay, we all have off days! What kept you from working out? Let's figure out how to make sure it doesn't happen again. Want to schedule your next session now?"

**Motivational Coach:**

- ✅ Turns setback into comeback
- ✅ Inspiring and forward-looking
- Example: "Hey, you know what? Even champions have off days! But you're here NOW, and that shows your commitment! Let's turn this around - TODAY is your comeback day! Ready to show yourself what you're made of?"

---

## 7️⃣ Configuration Testing

### Test 7.1: Temperature Variations

Use the same query with different temperature settings:

**Query:** "Give me a workout motivation quote"

**Temperature 0.0:**

- ✅ Consistent, same response each time
- ✅ Factual and straightforward

**Temperature 0.5:**

- ✅ Some variation
- ✅ Balanced creativity

**Temperature 0.7 (Recommended):**

- ✅ Good variety
- ✅ Natural and engaging

**Temperature 1.0:**

- ✅ High variety
- ✅ More creative/unpredictable

### Test 7.2: Prompt Style Comparison

Same query, different prompt styles:

**Query:** "Book a training session and get me a workout plan"

**Zero-Shot:**

- ✅ Should work but may be less accurate
- ✅ Tool usage around 85-90%

**Few-Shot (Recommended):**

- ✅ Best accuracy (95-98%)
- ✅ Follows examples
- ✅ Proper tool chaining

**Chain-of-Thought:**

- ✅ Detailed reasoning shown
- ✅ More verbose
- ✅ Good for understanding process

### Test 7.3: Model Comparison

**Query:** "Create a complex fitness and nutrition plan for an intermediate athlete"

**gemini-1.5-flash:**

- ✅ Fast response (1-2s)
- ✅ Good quality
- ✅ Recommended for production

**gemini-1.5-pro:**

- ✅ Slower (2-4s)
- ✅ Superior quality
- ✅ Better for complex tasks

**gemini-pro:**

- ✅ Balanced (1.5-3s)
- ✅ Good quality
- ✅ Stable and reliable

---

## 8️⃣ Error Handling

### Test 8.1: Invalid Date Format

**Query:** "Book me for tomorrow at 25:00"

**Expected Behavior:**

- ✅ Catches invalid time
- ✅ Asks for correction
- ✅ Doesn't crash

### Test 8.2: Invalid Service Type

**Query:** "Book me a massage session"

**Expected Behavior:**

- ✅ Recognizes invalid service
- ✅ Suggests valid options (personal_training, group_class, nutrition_consult)

### Test 8.3: Canceling Non-Existent Booking

**Query:** "Cancel booking ID 99999"

**Expected Behavior:**

- ✅ Error message: "Booking not found"
- ✅ Graceful handling

### Test 8.4: Empty/Vague Input

**Query:** "Help"

**Expected Behavior:**

- ✅ Provides guidance on what assistant can do
- ✅ Lists available services
- ✅ Asks clarifying question

---

## 9️⃣ Feedback System

### Test 9.1: Submit Feedback

**Query:**

```
"I want to leave feedback: The workout plan was excellent! 5 stars"
```

**Expected Behavior:**

- ✅ Calls `submit_feedback`
- ✅ Extracts rating (5)
- ✅ Stores feedback text
- ✅ Confirmation message

---

## 🔟 Context & Memory

### Test 10.1: Remember User Info

**Conversation:**

```
User: "My name is John and I'm a beginner"
[chat continues]
User: "What workout would you recommend for me?"
```

**Expected Behavior:**

- ✅ Remembers user mentioned being a beginner
- ✅ Uses that context in recommendation

### Test 10.2: Reference Previous Booking

**Conversation:**

```
User: "Book me for tomorrow at 2pm"
Agent: [Books session with ID 42]
User: "Actually, cancel that"
```

**Expected Behavior:**

- ✅ Understands "that" refers to booking 42
- ✅ Cancels the correct booking

---

## 📊 Test Results Template

Use this template to record test results:

```
Test: [Test Number and Name]
Date: [Date]
Persona: [Persona Used]
Configuration:
  - Model: [Model Name]
  - Temperature: [Value]
  - Prompt Style: [Style]

Query: "[Actual query used]"

Response: "[Agent's response]"

Tools Called:
  1. [tool_name(params)]
  2. [tool_name(params)]

Result: ✅ PASS / ❌ FAIL

Notes: [Any observations]

Issues Found: [List any issues]
```

---

## 🎯 Success Criteria

A successful test should demonstrate:

- ✅ Correct tool selection
- ✅ Accurate parameter extraction
- ✅ Appropriate persona voice
- ✅ Proper error handling
- ✅ Context awareness
- ✅ Natural language understanding

---

## 📝 Recommended Testing Order

1. **Setup Tests** (Authentication)
2. **Basic Tool Tests** (One tool at a time)
3. **Multi-Step Tests** (Tool chaining)
4. **Persona Tests** (All three personas)
5. **Configuration Tests** (Settings variations)
6. **Error Tests** (Edge cases)
7. **Integration Tests** (Complete workflows)

---

## 🔍 Experiment Tracking

All tests are automatically logged to `logs/experiment_logs.json`

To analyze results:

```python
from utils.helpers import ExperimentLogger
logger = ExperimentLogger()

# Get test statistics
stats = logger.get_statistics()
print(f"Total tests: {stats['total_interactions']}")
print(f"Persona breakdown: {stats['persona_usage']}")
```

---

## ✅ Testing Checklist

- [ ] All 8 tools tested individually
- [ ] All 3 personas tested
- [ ] All prompt styles tested
- [ ] Temperature variations tested
- [ ] Model comparison completed
- [ ] Multi-step scenarios validated
- [ ] Error handling verified
- [ ] Context awareness confirmed
- [ ] Documentation reviewed
- [ ] Results logged and analyzed

---

**Happy Testing! 🧪💪**
