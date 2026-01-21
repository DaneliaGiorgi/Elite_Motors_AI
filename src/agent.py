import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from database import get_connection
from auth import AuthManager

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

    def verify_admin(self, username: str, password: str):
        """Verifies identity using AuthManager and handles brute-force protection."""
        print(f"\n[System]: Verifying credentials for user: {username}...")
        
        # We delegate the entire login process to AuthManager
        # It handles password hashing, failed attempts, and lockout logic
        result = self.auth.login_user(username, password)

        if isinstance(result, dict) and "token" in result:
            # If result is a dict, login was successful
            self.current_user = {
                'username': result["username"], 
                'role': result["role"],
                'token': result["token"]
            }
            self.last_action_time = time.time()
            return f"Access granted. Session token issued for {username}. You can now perform admin tasks."
        
        else:
            # If result is a string, it contains the error message (e.g., "Account locked")
            self.current_user = None
            return f"{result}"

    def add_new_car(self, brand: str, year: int, price: float, quantity: int = 1):
        """Adds a new car record. Secured by JWT validation."""
        
        # 1. Check if the agent has an active session
        if not self.current_user:
            return "Access Denied: Please log in as an admin first."
        
        # 2. Validate the token and check for expiration
        verification = self.auth.verify_token(self.current_user['token'])
        if isinstance(verification, str) and verification.startswith("Error"):
            self.current_user = None 
            return f"Session Invalid: {verification}"
        
        #Conect to db
        conn = get_connection()
        cur = conn.cursor()
        try:
            #Use the 'user_id' from token (if needed) or just proceed as admin
            cur.execute(
                "INSERT INTO cars (brand, year, price, quantity) VALUES (%s, %s, %s, %s)",
                (brand, year, price, quantity)
            )
            #Commit the changes
            conn.commit()
            return f"Success! {brand} ({year}) has been added to the inventory."
        except Exception as e:
            return f"Database Error: {e}"
        finally:
            #Close cursor and connection
            cur.close()
            conn.close()

    def sell_car(self, brand: str):
        """Decrements car quantity. Secured by Session Token validation."""
        
        if not self.current_user:
            return "Authentication Required: Please log in to process sales."
        
        verification = self.auth.verify_token(self.current_user['token'])
        if isinstance(verification, str) and verification.startswith("Error"):
            self.current_user = None
            return f"{verification}"
        
        #Get connection to db
        conn = get_connection()
        cur = conn.cursor()
        try:
            #search
            cur.execute("SELECT car_id, brand, quantity FROM cars WHERE brand ILIKE %s LIMIT 1", (f"%{brand}%",))
            car = cur.fetchone()
            
            if not car:
                return f"Sorry, '{brand}' was not found in our database."
            
            car_id, db_brand, qty = car 
            print(f"[DEBUG]: Found {db_brand} (ID: {car_id}) with quantity: {qty}")

            if qty > 0:
                #Refresh
                cur.execute("UPDATE cars SET quantity = quantity - 1 WHERE car_id = %s", (car_id,))
                
                # check how many rows were changed in the database.
                if cur.rowcount == 0:
                    return f"Error: Database found the car but failed to update it (ID: {car_id})."

                conn.commit()
                
                #Reload the data
                cur.execute("SELECT quantity FROM cars WHERE car_id = %s", (car_id,))
                new_qty_row = cur.fetchone()
                
                if new_qty_row:
                    actual_qty = new_qty_row[0]
                    return f"Success! One {db_brand} sold. New quantity in DB: {actual_qty}"
                else:
                    return "Error: Could not retrieve new quantity after update."
            else:
                return f"Out of Stock: {db_brand} is currently at 0."
                
        except Exception as e:
            return f"Sales Error: {e}"
        finally:
            #Close cursor and connection
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
            summary = f"📋 Elite Motors Inventory Report:\n"
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

