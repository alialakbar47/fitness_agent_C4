from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
import re
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

# Initialize database manager
db = DatabaseManager()


def _parse_flexible_datetime(date_time_str: str) -> tuple:
    """
    Parse flexible datetime formats and return standardized datetime.
    
    Handles formats like:
    - "2024-10-27 3" or "2024-10-27 3pm" -> "2024-10-27 15:00:00"
    - "2024-10-27 3:00" -> "2024-10-27 03:00:00"
    - "2024-10-27 15:00" -> "2024-10-27 15:00:00"
    - "tomorrow at 3" -> next day at 15:00
    - "next monday at 10am" -> next monday at 10:00
    
    Returns:
        (success, datetime_obj or error_message)
    """
    try:
        # Clean up the input
        date_time_str = date_time_str.strip().lower()
        
        # Handle relative dates (tomorrow, today, next week, etc.)
        date_part = None
        time_part = None
        
        # Extract date and time parts
        if ' at ' in date_time_str:
            parts = date_time_str.split(' at ')
            date_part = parts[0].strip()
            time_part = parts[1].strip()
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_time_str):
            # Has a date in YYYY-MM-DD format
            match = re.match(r'(\d{4}-\d{2}-\d{2})\s+(.+)', date_time_str)
            if match:
                date_part = match.group(1)
                time_part = match.group(2)
            else:
                date_part = date_time_str
        else:
            # Try to parse the whole thing as a date-time
            time_part = date_time_str
        
        # Parse the date part
        if date_part:
            if date_part == 'today':
                base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_part == 'tomorrow':
                base_date = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif re.match(r'\d{4}-\d{2}-\d{2}', date_part):
                base_date = datetime.strptime(date_part, '%Y-%m-%d')
            else:
                return False, f"Could not parse date: {date_part}"
        else:
            base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Parse the time part
        if time_part:
            # Remove common words
            time_part = time_part.replace('at', '').strip()
            
            # Check for AM/PM
            is_pm = 'pm' in time_part or 'p.m' in time_part
            is_am = 'am' in time_part or 'a.m' in time_part
            time_part = re.sub(r'[ap]\.?m\.?', '', time_part).strip()
            
            # Try to extract hour and minute
            if ':' in time_part:
                # Format: "3:00", "15:30"
                parts = time_part.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
            elif time_part.isdigit():
                # Format: "3", "15"
                hour = int(time_part)
                minute = 0
            else:
                # Try to extract just numbers
                numbers = re.findall(r'\d+', time_part)
                if numbers:
                    hour = int(numbers[0])
                    minute = int(numbers[1]) if len(numbers) > 1 else 0
                else:
                    return False, f"Could not parse time: {time_part}"
            
            # Handle AM/PM conversion
            if is_pm and hour < 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
            
            # Handle 24-hour format where hour < 12 without am/pm might be PM for afternoon times
            # If user says "3" and it's afternoon context, assume PM
            if not is_am and not is_pm and 1 <= hour <= 11:
                # If it's a common afternoon/evening time, assume PM
                current_hour = datetime.now().hour
                if current_hour >= 12:  # It's afternoon/evening now
                    hour += 12
            
            if hour < 0 or hour > 23:
                return False, f"Invalid hour: {hour}. Must be 0-23"
            if minute < 0 or minute > 59:
                return False, f"Invalid minute: {minute}. Must be 0-59"
            
            result_datetime = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            result_datetime = base_date
        
        return True, result_datetime
        
    except Exception as e:
        return False, f"Error parsing datetime: {str(e)}"


def check_availability(service_type: str, date: str) -> Dict[str, Any]:
    """
    Check available time slots for services.
    
    Args:
        service_type: Type of service (personal_training, group_class, nutrition_consult)
        date: Date in YYYY-MM-DD format
    
    Returns:
        Dictionary with available slots
    """
    try:
        # Validate service type
        valid_services = ['personal_training', 'group_class', 'nutrition_consult']
        if service_type not in valid_services:
            return {
                "status": "error",
                "message": f"Invalid service type. Choose from: {', '.join(valid_services)}"
            }
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid date format. Use YYYY-MM-DD"
            }
        
        available_slots = db.get_available_slots(service_type, date)
        
        return {
            "status": "success",
            "service_type": service_type,
            "date": date,
            "available_slots": available_slots,
            "count": len(available_slots)
        }
    except Exception as e:
        logger.error(f"Error in check_availability: {e}")
        return {"status": "error", "message": str(e)}


def book_session(username: str, service_type: str, date_time: str, notes: str = "") -> Dict[str, Any]:
    """
    Create a booking record.
    
    Args:
        username: Username of the person booking
        service_type: Type of service (personal_training, group_class, nutrition_consult)
        date_time: Date and time in flexible formats:
                  - "YYYY-MM-DD HH:MM" (e.g., "2024-10-27 14:00")
                  - "YYYY-MM-DD H" (e.g., "2024-10-27 3" -> assumes 3 PM if afternoon context)
                  - "YYYY-MM-DD Hpm/am" (e.g., "2024-10-27 3pm")
                  - "tomorrow at 3pm"
                  - "today at 15:00"
        notes: Optional notes for the booking
    
    Returns:
        Dictionary with booking confirmation
    """
    try:
        # Validate service type
        valid_services = ['personal_training', 'group_class', 'nutrition_consult']
        if service_type not in valid_services:
            return {
                "status": "error",
                "message": f"Invalid service type. Choose from: {', '.join(valid_services)}"
            }
        
        # Parse datetime with flexible format support
        success, result = _parse_flexible_datetime(date_time)
        if not success:
            return {
                "status": "error",
                "message": f"Invalid date/time format. {result}. Please provide a valid date and time."
            }
        
        date_time_obj = result
        date_time_formatted = date_time_obj.strftime('%Y-%m-%d %H:%M:00')
        
        # Check if time is in the future
        if date_time_obj < datetime.now():
            return {
                "status": "error",
                "message": "Cannot book sessions in the past"
            }
        
        # Create booking
        success, message = db.create_booking(username, service_type, date_time_formatted, notes)
        
        if success:
            return {
                "status": "success",
                "message": message,
                "booking_details": {
                    "username": username,
                    "service_type": service_type,
                    "date_time": date_time_formatted,
                    "notes": notes
                }
            }
        else:
            return {"status": "error", "message": message}
    except Exception as e:
        logger.error(f"Error in book_session: {e}")
        return {"status": "error", "message": str(e)}


def view_bookings(username: str) -> Dict[str, Any]:
    """
    Retrieve user's bookings.
    
    Args:
        username: Username to query bookings for
    
    Returns:
        Dictionary with list of bookings
    """
    try:
        bookings = db.get_user_bookings(username)
        
        if not bookings:
            return {
                "status": "success",
                "message": f"No bookings found for {username}",
                "bookings": []
            }
        
        # Format bookings for display
        formatted_bookings = []
        for booking in bookings:
            formatted_bookings.append({
                "id": booking['id'],
                "service_type": booking['service_type'],
                "date_time": booking['date_time'],
                "status": booking['status'],
                "notes": booking['notes'],
                "created_at": booking['created_at']
            })
        
        return {
            "status": "success",
            "username": username,
            "bookings": formatted_bookings,
            "count": len(formatted_bookings)
        }
    except Exception as e:
        logger.error(f"Error in view_bookings: {e}")
        return {"status": "error", "message": str(e)}


def cancel_booking(booking_id: int) -> Dict[str, Any]:
    """
    Cancel a booking.
    
    Args:
        booking_id: ID of the booking to cancel
    
    Returns:
        Dictionary with cancellation confirmation
    """
    try:
        success, message = db.cancel_booking(booking_id)
        
        return {
            "status": "success" if success else "error",
            "message": message,
            "booking_id": booking_id
        }
    except Exception as e:
        logger.error(f"Error in cancel_booking: {e}")
        return {"status": "error", "message": str(e)}


def submit_feedback(username: str, feedback_text: str, rating: int) -> Dict[str, Any]:
    """
    Store user feedback.
    
    Args:
        username: Username submitting feedback
        feedback_text: Feedback content
        rating: Rating from 1-5
    
    Returns:
        Dictionary with submission confirmation
    """
    try:
        success, message = db.submit_feedback(username, feedback_text, rating)
        
        return {
            "status": "success" if success else "error",
            "message": message,
            "rating": rating
        }
    except Exception as e:
        logger.error(f"Error in submit_feedback: {e}")
        return {"status": "error", "message": str(e)}


def get_fitness_plan(fitness_level: str, goals: str, equipment_available: str, 
                     duration: str) -> Dict[str, Any]:
    """
    Generate workout routines based on goals.
    
    Args:
        fitness_level: beginner, intermediate, advanced
        goals: weight_loss, muscle_gain, endurance, general_fitness
        equipment_available: none, basic (dumbbells), full_gym
        duration: 30min, 45min, 60min
    
    Returns:
        Dictionary with structured workout plan
    """
    try:
        # Validate inputs
        valid_levels = ['beginner', 'intermediate', 'advanced']
        valid_goals = ['weight_loss', 'muscle_gain', 'endurance', 'general_fitness']
        valid_equipment = ['none', 'basic', 'full_gym']
        valid_durations = ['30min', '45min', '60min']
        
        if fitness_level not in valid_levels:
            return {"status": "error", "message": f"Invalid fitness level. Choose from: {', '.join(valid_levels)}"}
        if goals not in valid_goals:
            return {"status": "error", "message": f"Invalid goal. Choose from: {', '.join(valid_goals)}"}
        if equipment_available not in valid_equipment:
            return {"status": "error", "message": f"Invalid equipment option. Choose from: {', '.join(valid_equipment)}"}
        if duration not in valid_durations:
            return {"status": "error", "message": f"Invalid duration. Choose from: {', '.join(valid_durations)}"}
        
        # Generate workout plan based on parameters
        plan = {
            "status": "success",
            "fitness_level": fitness_level,
            "goals": goals,
            "equipment": equipment_available,
            "duration": duration,
            "workout_plan": _generate_workout_structure(fitness_level, goals, equipment_available, duration)
        }
        
        return plan
    except Exception as e:
        logger.error(f"Error in get_fitness_plan: {e}")
        return {"status": "error", "message": str(e)}


def _generate_workout_structure(level: str, goal: str, equipment: str, duration: str) -> Dict:
    """Helper function to generate workout structure."""
    
    # Base structure
    plan = {
        "warm_up": [],
        "main_workout": [],
        "cool_down": []
    }
    
    # Warm-up (same for all)
    plan["warm_up"] = [
        "5 minutes light cardio (jogging in place, jumping jacks)",
        "Dynamic stretching (arm circles, leg swings, torso twists)"
    ]
    
    # Main workout based on parameters
    if goal == "weight_loss":
        if equipment == "none":
            plan["main_workout"] = [
                "Burpees: 3 sets of 10-15 reps",
                "Mountain climbers: 3 sets of 20 reps",
                "Jump squats: 3 sets of 15 reps",
                "High knees: 3 sets of 30 seconds",
                "Plank: 3 sets of 30-60 seconds"
            ]
        elif equipment == "basic":
            plan["main_workout"] = [
                "Dumbbell thrusters: 3 sets of 12 reps",
                "Renegade rows: 3 sets of 10 reps per arm",
                "Dumbbell swings: 3 sets of 15 reps",
                "Walking lunges with dumbbells: 3 sets of 12 per leg",
                "Russian twists: 3 sets of 20 reps"
            ]
        else:  # full_gym
            plan["main_workout"] = [
                "Treadmill intervals: 20 minutes (1 min fast, 2 min moderate)",
                "Rowing machine: 3 sets of 500m",
                "Battle ropes: 3 sets of 30 seconds",
                "Box jumps: 3 sets of 12 reps",
                "Kettlebell swings: 3 sets of 20 reps"
            ]
    
    elif goal == "muscle_gain":
        if equipment == "none":
            plan["main_workout"] = [
                "Push-ups: 4 sets of 12-15 reps",
                "Pike push-ups: 3 sets of 10 reps",
                "Bulgarian split squats: 4 sets of 12 per leg",
                "Diamond push-ups: 3 sets of 10 reps",
                "Plank to push-up: 3 sets of 10 reps"
            ]
        elif equipment == "basic":
            plan["main_workout"] = [
                "Dumbbell bench press: 4 sets of 8-12 reps",
                "Dumbbell rows: 4 sets of 10 reps per arm",
                "Goblet squats: 4 sets of 12 reps",
                "Dumbbell shoulder press: 3 sets of 10 reps",
                "Bicep curls: 3 sets of 12 reps"
            ]
        else:  # full_gym
            plan["main_workout"] = [
                "Barbell bench press: 4 sets of 8-10 reps",
                "Barbell squats: 4 sets of 8-10 reps",
                "Deadlifts: 3 sets of 6-8 reps",
                "Pull-ups: 3 sets to failure",
                "Dips: 3 sets of 10-12 reps"
            ]
    
    elif goal == "endurance":
        if equipment == "none":
            plan["main_workout"] = [
                "Running: 20-30 minutes steady pace",
                "Bodyweight squats: 3 sets of 25 reps",
                "Push-ups: 3 sets of 20 reps",
                "Lunges: 3 sets of 20 per leg",
                "Plank hold: 3 sets of 60 seconds"
            ]
        elif equipment == "basic":
            plan["main_workout"] = [
                "Dumbbell step-ups: 3 sets of 20 per leg",
                "Farmer's walk: 3 sets of 1 minute",
                "Dumbbell clean and press: 3 sets of 15 reps",
                "Dumbbell lunges: 3 sets of 20 per leg",
                "Dumbbell swings: 3 sets of 25 reps"
            ]
        else:  # full_gym
            plan["main_workout"] = [
                "Elliptical: 25 minutes moderate intensity",
                "Rowing machine: 4 sets of 1000m",
                "Cycling: 20 minutes intervals",
                "Jump rope: 5 sets of 2 minutes",
                "Stair climber: 15 minutes"
            ]
    
    else:  # general_fitness
        plan["main_workout"] = [
            "Circuit training (3 rounds):",
            "- Squats: 15 reps",
            "- Push-ups: 12 reps",
            "- Lunges: 10 per leg",
            "- Plank: 30 seconds",
            "- Jumping jacks: 30 seconds"
        ]
    
    # Cool-down
    plan["cool_down"] = [
        "5 minutes light walking or slow cycling",
        "Static stretching (hold each for 30 seconds):",
        "- Hamstring stretch",
        "- Quad stretch",
        "- Shoulder stretch",
        "- Chest stretch",
        "- Lower back stretch"
    ]
    
    # Add notes based on level
    if level == "beginner":
        plan["notes"] = "Start with lighter weights and focus on form. Rest 60-90 seconds between sets."
    elif level == "intermediate":
        plan["notes"] = "Challenge yourself with moderate weights. Rest 45-60 seconds between sets."
    else:  # advanced
        plan["notes"] = "Use heavy weights with proper form. Rest 30-45 seconds between sets for intensity."
    
    return plan


def get_nutrition_advice(dietary_preferences: str, fitness_goals: str, 
                         restrictions: str = "none") -> Dict[str, Any]:
    """
    Provide meal recommendations.
    
    Args:
        dietary_preferences: omnivore, vegetarian, vegan, keto, paleo
        fitness_goals: weight_loss, muscle_gain, endurance, maintenance
        restrictions: Comma-separated list of allergies/restrictions or "none"
    
    Returns:
        Dictionary with meal plan suggestions
    """
    try:
        # Validate inputs
        valid_diets = ['omnivore', 'vegetarian', 'vegan', 'keto', 'paleo']
        valid_goals = ['weight_loss', 'muscle_gain', 'endurance', 'maintenance']
        
        if dietary_preferences not in valid_diets:
            return {"status": "error", "message": f"Invalid dietary preference. Choose from: {', '.join(valid_diets)}"}
        if fitness_goals not in valid_goals:
            return {"status": "error", "message": f"Invalid fitness goal. Choose from: {', '.join(valid_goals)}"}
        
        # Generate nutrition plan
        nutrition_plan = {
            "status": "success",
            "dietary_preferences": dietary_preferences,
            "fitness_goals": fitness_goals,
            "restrictions": restrictions,
            "meal_plan": _generate_meal_plan(dietary_preferences, fitness_goals, restrictions),
            "hydration": "Drink at least 8-10 glasses of water daily, more if exercising intensely",
            "supplements": _get_supplement_recommendations(fitness_goals)
        }
        
        return nutrition_plan
    except Exception as e:
        logger.error(f"Error in get_nutrition_advice: {e}")
        return {"status": "error", "message": str(e)}


def _generate_meal_plan(diet: str, goal: str, restrictions: str) -> Dict:
    """Helper function to generate meal plans."""
    
    meals = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snacks": []
    }
    
    # Meal suggestions based on diet and goal
    if diet == "omnivore":
        if goal == "weight_loss":
            meals["breakfast"] = ["Oatmeal with berries and almond butter", "Greek yogurt with nuts and honey", "Veggie omelet with whole grain toast"]
            meals["lunch"] = ["Grilled chicken salad with olive oil", "Turkey and avocado wrap", "Quinoa bowl with roasted vegetables"]
            meals["dinner"] = ["Baked salmon with steamed broccoli", "Lean beef stir-fry with vegetables", "Grilled chicken breast with sweet potato"]
            meals["snacks"] = ["Apple slices with peanut butter", "Carrot sticks with hummus", "Mixed nuts (1 oz)"]
        elif goal == "muscle_gain":
            meals["breakfast"] = ["Scrambled eggs with turkey bacon and avocado", "Protein pancakes with banana", "Greek yogurt parfait with granola"]
            meals["lunch"] = ["Chicken breast with brown rice and vegetables", "Beef and quinoa bowl", "Tuna sandwich on whole grain bread"]
            meals["dinner"] = ["Steak with sweet potato and asparagus", "Salmon with pasta and vegetables", "Chicken thighs with rice and beans"]
            meals["snacks"] = ["Protein shake", "Cottage cheese with fruit", "Hard-boiled eggs"]
    
    elif diet == "vegetarian":
        if goal == "weight_loss":
            meals["breakfast"] = ["Smoothie bowl with chia seeds", "Whole grain toast with avocado", "Greek yogurt with berries"]
            meals["lunch"] = ["Lentil soup with side salad", "Veggie burger with side salad", "Chickpea salad wrap"]
            meals["dinner"] = ["Tofu stir-fry with vegetables", "Eggplant parmesan with side salad", "Bean chili with side salad"]
            meals["snacks"] = ["Hummus with vegetables", "Trail mix", "Fruit salad"]
        elif goal == "muscle_gain":
            meals["breakfast"] = ["Protein smoothie with banana and spinach", "Scrambled eggs with cheese and toast", "Protein oatmeal with nuts"]
            meals["lunch"] = ["Quinoa and black bean bowl", "Veggie wrap with extra hummus", "Lentil curry with rice"]
            meals["dinner"] = ["Tofu and tempeh stir-fry with rice", "Vegetarian lasagna", "Bean burrito bowl"]
            meals["snacks"] = ["Protein bar", "Nut butter on rice cakes", "Edamame"]
    
    elif diet == "vegan":
        if goal == "weight_loss":
            meals["breakfast"] = ["Oatmeal with plant-based milk and berries", "Smoothie with plant protein", "Whole grain toast with avocado"]
            meals["lunch"] = ["Buddha bowl with tahini dressing", "Lentil soup", "Mixed greens salad with chickpeas"]
            meals["dinner"] = ["Tofu stir-fry with brown rice", "Vegetable curry with quinoa", "Stuffed bell peppers"]
            meals["snacks"] = ["Fresh fruit", "Vegetables with guacamole", "Roasted chickpeas"]
        elif goal == "muscle_gain":
            meals["breakfast"] = ["Tofu scramble with nutritional yeast", "Protein oatmeal with hemp seeds", "Smoothie with vegan protein powder"]
            meals["lunch"] = ["Tempeh sandwich with avocado", "Quinoa and bean bowl", "Lentil and rice curry"]
            meals["dinner"] = ["Seitan stir-fry with vegetables", "Black bean and sweet potato burrito", "Chickpea pasta with marinara"]
            meals["snacks"] = ["Plant-based protein shake", "Nut butter on whole grain crackers", "Trail mix with dried fruit"]
    
    elif diet == "keto":
        meals["breakfast"] = ["Bacon and eggs with avocado", "Keto smoothie with MCT oil", "Bulletproof coffee with cheese omelet"]
        meals["lunch"] = ["Caesar salad with grilled chicken (no croutons)", "Bunless burger with cheese and bacon", "Zucchini noodles with pesto and chicken"]
        meals["dinner"] = ["Ribeye steak with butter and asparagus", "Salmon with cauliflower rice", "Chicken thighs with broccoli and cheese sauce"]
        meals["snacks"] = ["Cheese cubes", "Pepperoni slices", "Macadamia nuts", "Celery with cream cheese"]
    
    else:  # paleo
        meals["breakfast"] = ["Scrambled eggs with vegetables", "Sweet potato hash with ground beef", "Almond flour pancakes with berries"]
        meals["lunch"] = ["Grilled chicken with mixed greens", "Tuna salad over lettuce", "Beef and vegetable soup"]
        meals["dinner"] = ["Grass-fed steak with roasted vegetables", "Baked salmon with asparagus", "Chicken stir-fry with cauliflower rice"]
        meals["snacks"] = ["Mixed nuts", "Fresh fruit", "Hard-boiled eggs", "Vegetable sticks with guacamole"]
    
    # Add macro recommendations
    if goal == "weight_loss":
        meals["macros"] = "Aim for slight caloric deficit: 40% protein, 30% carbs, 30% fats"
    elif goal == "muscle_gain":
        meals["macros"] = "Aim for caloric surplus: 30% protein, 40% carbs, 30% fats"
    elif goal == "endurance":
        meals["macros"] = "Balanced macros: 25% protein, 50% carbs, 25% fats"
    else:  # maintenance
        meals["macros"] = "Balanced maintenance: 30% protein, 40% carbs, 30% fats"
    
    return meals


def _get_supplement_recommendations(goal: str) -> List[str]:
    """Helper function for supplement recommendations."""
    
    base_supplements = ["Multivitamin", "Vitamin D", "Omega-3 fatty acids"]
    
    if goal == "muscle_gain":
        return base_supplements + ["Whey/plant protein powder", "Creatine monohydrate", "BCAAs"]
    elif goal == "weight_loss":
        return base_supplements + ["Green tea extract", "Fiber supplement", "Protein powder"]
    elif goal == "endurance":
        return base_supplements + ["Electrolyte supplements", "B-complex vitamins", "Iron (if deficient)"]
    else:
        return base_supplements


def get_user_context(username: str) -> Dict[str, Any]:
    """
    Fetch user history and preferences.
    
    Args:
        username: Username to get context for
    
    Returns:
        Dictionary with user profile summary
    """
    try:
        context = db.get_user_context(username)
        
        if "error" in context:
            return {"status": "error", "message": context["error"]}
        
        # Format context for display
        summary = {
            "status": "success",
            "username": username,
            "member_since": context["user"]["created_at"],
            "total_bookings": context["total_bookings"],
            "active_bookings": context["active_bookings"],
            "recent_bookings": context["bookings"][:5],  # Last 5 bookings
            "feedback_count": len(context["feedback"])
        }
        
        return summary
    except Exception as e:
        logger.error(f"Error in get_user_context: {e}")
        return {"status": "error", "message": str(e)}


# Tool registry for LangGraph
TOOLS = {
    "check_availability": check_availability,
    "book_session": book_session,
    "view_bookings": view_bookings,
    "cancel_booking": cancel_booking,
    "submit_feedback": submit_feedback,
    "get_fitness_plan": get_fitness_plan,
    "get_nutrition_advice": get_nutrition_advice,
    "get_user_context": get_user_context
}


# Tool descriptions for LLM
TOOL_DESCRIPTIONS = """
Available Tools:

1. check_availability(service_type, date)
   - Check available time slots for services
   - service_type: "personal_training", "group_class", or "nutrition_consult"
   - date: Date in YYYY-MM-DD format
   - Returns: List of available time slots

2. book_session(username, service_type, date_time, notes)
   - Create a booking record
   - username: User making the booking
   - service_type: Type of service
   - date_time: Date and time in flexible formats:
     * "YYYY-MM-DD HH:MM" (e.g., "2024-10-27 14:00")
     * "YYYY-MM-DD H" (e.g., "2024-10-27 3" -> interprets as 3 PM if afternoon)
     * "YYYY-MM-DD Hpm" or "YYYY-MM-DD Ham" (e.g., "2024-10-27 3pm")
     * "tomorrow at 3pm", "today at 15:00"
   - notes: Optional notes (default: "")
   - Returns: Confirmation with booking ID

3. view_bookings(username)
   - Retrieve user's bookings
   - username: User to query bookings for
   - Returns: List of all bookings with details

4. cancel_booking(booking_id)
   - Cancel a booking
   - booking_id: ID of the booking to cancel
   - Returns: Cancellation confirmation

5. submit_feedback(username, feedback_text, rating)
   - Store user feedback
   - username: User submitting feedback
   - feedback_text: Feedback content
   - rating: Rating from 1-5
   - Returns: Success confirmation

6. get_fitness_plan(fitness_level, goals, equipment_available, duration)
   - Generate workout routines based on goals
   - fitness_level: "beginner", "intermediate", or "advanced"
   - goals: "weight_loss", "muscle_gain", "endurance", or "general_fitness"
   - equipment_available: "none", "basic", or "full_gym"
   - duration: "30min", "45min", or "60min"
   - Returns: Structured workout plan

7. get_nutrition_advice(dietary_preferences, fitness_goals, restrictions)
   - Provide meal recommendations
   - dietary_preferences: "omnivore", "vegetarian", "vegan", "keto", or "paleo"
   - fitness_goals: "weight_loss", "muscle_gain", "endurance", or "maintenance"
   - restrictions: Comma-separated allergies/restrictions or "none"
   - Returns: Meal plan suggestions

8. get_user_context(username)
   - Fetch user history and preferences
   - username: User to get context for
   - Returns: User profile summary with bookings and feedback
"""
