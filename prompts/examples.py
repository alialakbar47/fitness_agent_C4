"""Few-shot examples for ReAct prompting."""


FEW_SHOT_EXAMPLES = """
=== EXAMPLE INTERACTIONS ===

Example 1: Booking with Availability Check
-------------------------------------------
User: "I want to book a group class tomorrow at 2pm"

Thought: User wants to book a group class. I should first check if 2pm (14:00) is available tomorrow. Let me check the date - if today is 2024-10-26, tomorrow is 2024-10-27.
Action: check_availability("group_class", "2024-10-27")
Observation: {"status": "success", "available_slots": ["09:00", "10:00", "14:00", "15:00", "16:00"]}
Thought: Great! 14:00 (2pm) is available. Now I can book it for the user. I need their username from the session context.
Action: book_session("sarah_johnson", "group_class", "2024-10-27 14:00", "")
Observation: {"status": "success", "message": "Booking confirmed! Booking ID: 123"}
Answer: Perfect! Your group class is booked for tomorrow at 2pm. Booking ID: 123. See you there!


Example 2: Fitness Plan Generation
------------------------------------
User: "I'm new to working out and want to lose weight. I don't have any equipment."

Thought: User is a beginner who wants to lose weight and has no equipment. I should create a beginner-level workout plan focused on weight loss with bodyweight exercises. I'll set duration to 45min as a good starting point.
Action: get_fitness_plan("beginner", "weight_loss", "none", "45min")
Observation: {"status": "success", "workout_plan": {"warm_up": ["5 minutes light cardio", "Dynamic stretching"], "main_workout": ["Burpees: 3 sets of 10-15 reps", "Mountain climbers: 3 sets of 20 reps", ...], "cool_down": ["5 minutes walking", "Static stretching"]}}
Thought: I have a comprehensive workout plan. Let me present it in an encouraging way since the user is a beginner.
Answer: Here's your beginner-friendly weight loss workout plan! Start with a 5-minute warm-up, then do: Burpees (3 sets of 10-15 reps), Mountain climbers (3 sets of 20 reps), Jump squats (3 sets of 15 reps), High knees (3 sets of 30 seconds), and Plank holds (3 sets of 30-60 seconds). Finish with a 5-minute cool-down. Remember: focus on form over speed, and you've got this!


Example 3: Nutrition Advice
----------------------------
User: "What should I eat? I'm vegetarian and trying to build muscle"

Thought: User wants nutrition advice. They're vegetarian with a goal of muscle gain. No specific restrictions mentioned, so I'll use "none".
Action: get_nutrition_advice("vegetarian", "muscle_gain", "none")
Observation: {"status": "success", "meal_plan": {"breakfast": ["Protein smoothie with banana and spinach", "Scrambled eggs with cheese and toast"], "lunch": ["Quinoa and black bean bowl", "Veggie wrap with extra hummus"], "dinner": ["Tofu and tempeh stir-fry with rice", "Vegetarian lasagna"], "macros": "Aim for caloric surplus: 30% protein, 40% carbs, 30% fats"}}
Thought: Good nutrition plan for vegetarian muscle building. I should present the meal options clearly and emphasize protein.
Answer: For building muscle on a vegetarian diet, here's your meal plan: Breakfast - Protein smoothie with banana and spinach or scrambled eggs with cheese. Lunch - Quinoa and black bean bowl or veggie wrap with extra hummus. Dinner - Tofu and tempeh stir-fry with rice or vegetarian lasagna. Aim for a caloric surplus with 30% protein, 40% carbs, 30% fats. Key tip: Make sure you're getting enough protein throughout the day!


Example 4: Viewing and Cancelling Bookings
--------------------------------------------
User: "Show me my upcoming sessions and cancel the one on Tuesday"

Thought: User wants to see their bookings and cancel one. Let me first retrieve all their bookings.
Action: view_bookings("mike_chen")
Observation: {"status": "success", "bookings": [{"id": 45, "service_type": "personal_training", "date_time": "2024-10-29 10:00:00", "status": "confirmed"}, {"id": 47, "service_type": "nutrition_consult", "date_time": "2024-10-31 14:00:00", "status": "confirmed"}]}
Thought: I can see two bookings. October 29 is a Tuesday and that's the personal training session (ID: 45). User wants to cancel that one.
Action: cancel_booking(45)
Observation: {"status": "success", "message": "Booking 45 has been cancelled successfully."}
Answer: Here are your bookings: 1) Personal Training on Tuesday Oct 29 at 10am, 2) Nutrition Consult on Thursday Oct 31 at 2pm. I've cancelled your Tuesday session as requested. You still have your nutrition consultation on Thursday!


Example 5: Multi-Step with User Context
-----------------------------------------
User: "Recommend a workout based on my history"

Thought: User wants a personalized recommendation. I should first check their context to understand their history and preferences.
Action: get_user_context("alex_rodriguez")
Observation: {"status": "success", "total_bookings": 15, "active_bookings": 2, "recent_bookings": [{"service_type": "personal_training", "date_time": "2024-10-20 09:00:00"}, {"service_type": "group_class", "date_time": "2024-10-18 18:00:00"}]}
Thought: User has good engagement with 15 total bookings, regularly doing personal training and group classes. They seem intermediate level. Let me create a workout assuming they have gym access and want general fitness.
Action: get_fitness_plan("intermediate", "general_fitness", "full_gym", "60min")
Observation: {"status": "success", "workout_plan": {...comprehensive 60-min plan...}}
Thought: Perfect! I have a plan that matches their active lifestyle.
Answer: Based on your consistent training history (15 sessions!), here's an intermediate 60-minute workout perfect for you: [details of workout plan]. Keep up the great work!


Example 6: Handling Errors Gracefully
---------------------------------------
User: "Book me for next Monday at 25:00"

Thought: User wants to book a session but the time "25:00" is invalid (hours go from 00-23). I should inform them of the error and help them correct it.
Answer: I'd love to help you book that session, but 25:00 isn't a valid time format. Did you mean 1:00 (13:00)? Our available hours are from 9am to 8pm. Let me know what time works for you!


Example 7: No Tool Needed
--------------------------
User: "What services does FitFusion offer?"

Thought: This is a general information question about our services. I don't need to call any tools - I can answer directly based on what I know.
Answer: FitFusion offers three great services: Personal Training (one-on-one sessions with expert trainers), Group Classes (fun, energetic workouts with others), and Nutrition Consultations (personalized meal planning and dietary advice). Which one interests you?

=== END OF EXAMPLES ===
"""


def get_few_shot_examples() -> str:
    """Return the few-shot examples."""
    return FEW_SHOT_EXAMPLES
