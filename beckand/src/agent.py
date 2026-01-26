import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from database import get_connection
from auth import AuthManager
from database import get_user_by_email
from security import verify_password
import time

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
API_KEY = os.getenv("GOOGLE_API_KEY")

class EliteMotorsAgent:
    """AI Agent that connects natural language to database operations with professional security."""
    
    def __init__(self):
        self.auth = AuthManager()
        self.current_user = None # Stores username, role, and token
        self.last_action_time = 0
        self.session_timeout = 300  # 5 minutes in seconds

    def verify_admin(self, email: str, password: str):
        user = get_user_by_email(email)
        
        if not user:
            return "user not found"

        # The tuple retrieved from PostgreSQL contains the following data
        # user[0] -> user_id
        # user[1] -> name
        # user[2] -> last_name
        # user[3] -> username (email)
        # user[4] -> password_hash
        
        if verify_password(password, user[4]): #use index 4
            self.current_user = email
            self.last_action_time = time.time()
            return f"autorization successful! Hi {user[1]}"
        else:
            return "incorect password"

    def add_new_car(self, brand: str, year: int, price: float, quantity: int = 1):
        """Adds a new car record. Secured by an active session."""
    
        #We check whether the user is authenticated (self.current_user stores the email)
        if not self.current_user:
            return "Access Denied: Please log in as an admin first."
        
        # Note: If the JWT token is not stored in a separate variable,
        # here we simply check whether the agent has an active session.
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Add car in PostgreSQL
            cur.execute(
                "INSERT INTO cars (brand, year, price, quantity) VALUES (%s, %s, %s, %s)",
                (brand, year, price, quantity)
            )
            return f"Success! {brand} ({year}) has been added to the inventory."
        except Exception as e:
            return f"Database Error: {e}"
        finally:
            cur.close()
            conn.close()

    def sell_car(self, car_id: int, quantity: int = 1):
        if not self.current_user:
            return "Access Denied: Please log in first."

        conn = get_connection()
        cur = conn.cursor()
        try:
            #check whether the quantity is sufficient
            cur.execute("SELECT quantity FROM cars WHERE car_id = %s", (car_id,))
            res = cur.fetchone()
            
            if not res or res[0] < quantity:
                return "Error: Not enough stock!"

            #decrease the quantity
            cur.execute(
                "UPDATE cars SET quantity = quantity - %s WHERE car_id = %s",
                (quantity, car_id)
            )
            return f"Success! Sold {quantity} car(s)."
        except Exception as e:
            return f"Database Error: {e}"
        finally:
            cur.close()
            conn.close()
            
    def get_inventory(self):
        """Public function: Retrieves all cars from the showroom."""
        #Conect to database
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT brand, year, price, quantity FROM cars")
            cars = cur.fetchall()
            
            if not cars:
                return "The showroom is currently empty."
            
            total_units = sum(car[3] for car in cars)
            summary = f"Elite Motors Inventory Report:\n"
            summary += f"• Total Models: {len(cars)}\n"
            summary += f"• Total Units in Stock: {total_units}\n"
            summary += "------------------------------\n"
            
            for car in cars:
                summary += f"{car[0]} ({car[1]}) - ${car[2]:,.2f} | Stock: {car[3]}\n"
            return summary
        except Exception as e:
            return f"Database error: {e}"
        finally:
            #Close cursor and connection
            cur.close()
            conn.close()

