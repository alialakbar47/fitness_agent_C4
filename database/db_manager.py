import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for FitFusion Assistant."""
    
    def __init__(self, db_path: str = "data/fitfusion.db"):
        """Initialize database manager and create tables."""
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables if they don't exist."""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    
    # ==================== User Operations ====================
    
    def create_user(self, username: str, email: str) -> Tuple[bool, str]:
        """
        Create a new user.
        
        Returns:
            (success, message): Tuple of success status and message
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                (username, email)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"User created: {username}")
            return True, f"User '{username}' created successfully!"
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' already exists."
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, f"Error creating user: {str(e)}"
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    # ==================== Booking Operations ====================
    
    def create_booking(self, username: str, service_type: str, 
                      date_time: str, notes: str = "") -> Tuple[bool, str]:
        """
        Create a new booking.
        
        Args:
            username: Username of the person booking
            service_type: Type of service (personal_training, group_class, nutrition_consult)
            date_time: Date and time in ISO format
            notes: Optional notes
        
        Returns:
            (success, message): Tuple of success status and message
        """
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False, f"User '{username}' not found. Please sign up first."
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO bookings (user_id, service_type, date_time, notes)
                   VALUES (?, ?, ?, ?)""",
                (user['id'], service_type, date_time, notes)
            )
            
            booking_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Booking created: ID {booking_id} for {username}")
            return True, f"Booking confirmed! Booking ID: {booking_id}"
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return False, f"Error creating booking: {str(e)}"
    
    def get_user_bookings(self, username: str) -> List[Dict]:
        """Get all bookings for a user."""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return []
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT * FROM bookings 
                   WHERE user_id = ? 
                   ORDER BY date_time DESC""",
                (user['id'],)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching bookings: {e}")
            return []
    
    def get_booking_by_id(self, booking_id: int) -> Optional[Dict]:
        """Get a specific booking by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error fetching booking: {e}")
            return None
    
    def cancel_booking(self, booking_id: int) -> Tuple[bool, str]:
        """Cancel a booking."""
        try:
            booking = self.get_booking_by_id(booking_id)
            if not booking:
                return False, f"Booking ID {booking_id} not found."
            
            if booking['status'] == 'cancelled':
                return False, "Booking is already cancelled."
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
                (booking_id,)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"Booking cancelled: ID {booking_id}")
            return True, f"Booking {booking_id} has been cancelled successfully."
        except Exception as e:
            logger.error(f"Error cancelling booking: {e}")
            return False, f"Error cancelling booking: {str(e)}"
    
    def get_available_slots(self, service_type: str, date: str) -> List[str]:
        """
        Get available time slots for a service on a given date.
        
        Args:
            service_type: Type of service
            date: Date in YYYY-MM-DD format
        
        Returns:
            List of available time slots
        """
        # Define business hours
        time_slots = [
            "09:00", "10:00", "11:00", "12:00", 
            "13:00", "14:00", "15:00", "16:00", 
            "17:00", "18:00", "19:00", "20:00"
        ]
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get booked slots for the date
            cursor.execute(
                """SELECT date_time FROM bookings 
                   WHERE service_type = ? 
                   AND date(date_time) = date(?)
                   AND status = 'confirmed'""",
                (service_type, date)
            )
            
            booked = [row['date_time'] for row in cursor.fetchall()]
            conn.close()
            
            # Filter out booked slots
            available = []
            for slot in time_slots:
                slot_datetime = f"{date} {slot}:00"
                if slot_datetime not in booked:
                    available.append(slot)
            
            return available
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return time_slots  # Return all slots on error
    
    # ==================== Feedback Operations ====================
    
    def submit_feedback(self, username: str, feedback_text: str, 
                       rating: int) -> Tuple[bool, str]:
        """Submit user feedback."""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False, f"User '{username}' not found."
            
            if not (1 <= rating <= 5):
                return False, "Rating must be between 1 and 5."
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO feedback (user_id, feedback_text, rating)
                   VALUES (?, ?, ?)""",
                (user['id'], feedback_text, rating)
            )
            
            feedback_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Feedback submitted: ID {feedback_id} by {username}")
            return True, "Thank you for your feedback!"
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return False, f"Error submitting feedback: {str(e)}"
    
    def get_user_feedback(self, username: str) -> List[Dict]:
        """Get all feedback from a user."""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return []
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT * FROM feedback 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC""",
                (user['id'],)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching feedback: {e}")
            return []
    
    # ==================== Context Operations ====================
    
    def get_user_context(self, username: str) -> Dict:
        """Get comprehensive user context including bookings and feedback."""
        user = self.get_user_by_username(username)
        if not user:
            return {"error": f"User '{username}' not found"}
        
        bookings = self.get_user_bookings(username)
        feedback = self.get_user_feedback(username)
        
        return {
            "user": user,
            "bookings": bookings,
            "feedback": feedback,
            "total_bookings": len(bookings),
            "active_bookings": len([b for b in bookings if b['status'] == 'confirmed'])
        }
