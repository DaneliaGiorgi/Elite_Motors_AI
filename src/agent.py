import os
import bcrypt # type: ignore
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
    """AI Agent that connects natural language to database operations."""
    
    def __init__(self):
        self.auth = AuthManager()
        self.current_user = None
        self.last_action_time = 0
        self.session_timeout = 300  # 5 minutes in seconds

    def verify_admin(self, username: str, password: str):
        """Checks the database to verify if the user is an admin."""
        #Get connection to db
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT password_hash, role FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            
            if user:
                db_password_hash, role = user
                
                #Convert the entered password to bytes
                password_bytes = password.encode('utf-8')
                
                #The hash retrieved from the database must also be in bytes (it sometimes comes as a string)
                if isinstance(db_password_hash, str):
                    db_password_hash = db_password_hash.encode('utf-8')

                #Compare by bcrypt
                if bcrypt.checkpw(password_bytes, db_password_hash):
                    if role == 'admin':
                        self.current_user = {'username': username, 'role': 'admin'}
                        self.last_action_time = time.time()
                        return f"Access granted for {username}."
                    return "Error: You don't have admin privileges."
                
            return "Error: Wrong username or password."
        except Exception as e:
            return f"Auth error: {e}"
        finally:
            #Close connection to db
            cur.close()
            conn.close()

    def add_new_car(self, brand: str, year: int, price: int, quantity: int = 1):
        """Database function: Adds a new car record."""
        if not self.current_user or self.current_user['role'] != 'admin':
            return "Please log in as an admin (provide your username and password)."
        #Get connection to db
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO cars (brand, year, price, quantity) VALUES (%s, %s, %s, %s)",
                (brand, year, price, quantity)
            )
            #Save changes in db
            conn.commit()
            return f"Success! {brand} ({year}) added to inventory."
        except Exception as e:
            return f"Database Error: {e}"
        finally:
            #Close connection to db
            cur.close()
            conn.close()

    def sell_car(self, brand: str):
        """Decreases the car quantity by 1 without deleting it."""
        if not self.current_user or self.current_user['role'] != 'admin':
            return "This action requires administrator privileges."
        
        #Get connection to db    
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            #We use car_id as specified when creating the database
            cur.execute("SELECT car_id, quantity FROM cars WHERE brand ILIKE %s LIMIT 1", (brand,))
            car = cur.fetchone()
            
            if not car:
                return f"Sorry, {brand} Not found in the database."
            
            car_id, qty = car 
            if qty > 0:
                #Decrement the quantity, and at the end we must pass (car_id,)
                cur.execute("UPDATE cars SET quantity = quantity - 1 WHERE car_id = %s", (car_id,))
                #Save changes in db
                conn.commit() 
                
                if qty == 1:
                    return f"{brand} Sold. This was the last item; the stock is now empty!"
                else:
                    return f"One {brand} Sold. Remaining: {qty - 1} unit."
            else:
                return f"Sorry, {brand} stock is already empty."
                
        except Exception as e:
            return f"Error during sale: {e}"
        finally:
            #Close connection to db
            cur.close()
            conn.close()
        
    def get_inventory(self):
        """Retrieves cars and calculates total units in stock."""
        #Get connection to db
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT brand, year, price, quantity FROM cars")
            #Fetch all from db
            cars = cur.fetchall()
            
            if not cars:
                return "Showroom is empty."
            
            total_units = sum(car[3] for car in cars)
            summary = f"Information from the showroom:\n"
            summary += f"- Unique record: {len(cars)}\n"
            summary += f"- Total quantity: {total_units}\n\n"
            
            for car in cars:
                summary += f"- {car[0]} ({car[1]}): ${car[2]}, quantity: {car[3]}\n"
            return summary
        except Exception as e:
            return f"Database error: {e}"
        finally:
            #Close connection to db
            cur.close()
            conn.close()

if __name__ == "__main__":
    agent = EliteMotorsAgent()
    client = genai.Client(api_key=API_KEY)

    print("AI agent is activated. Type exit to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break

        #Check session time (5 minute)
        if agent.current_user and (time.time() - agent.last_action_time > agent.session_timeout):
            print("Session has ended. Please log in again.")
            agent.current_user = None

        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction="""
                    You are the Elite Motors Sales & Security Assistant.
                    STRICT OPERATIONAL RULES:
                    1. LANGUAGE: Always respond to the user in the same language they use (e.g., if they speak Georgian, respond in Georgian).
                    2. AUTHENTICATION: If a user wants to add, sell, or modify car data, you MUST verify their identity. 
                    3. PROMPT ACTION: As soon as a user provides a username and password, IMMEDIATELY call the 'verify_admin' tool with those credentials. Do not ask for confirmation; just execute the tool.
                    4. SEQUENCE: 
                    - Step A: Get credentials.
                    - Step B: Call 'verify_admin'.
                    - Step C: If 'verify_admin' returns success, proceed to the requested task (e.g., call 'sell_car').
                    5. PERSISTENCE: If 'verify_admin' fails, explain why and ask for credentials again.
                    6. Use emojis in your responses to make the conversation friendly.
                    """,
                    tools=[agent.add_new_car, agent.get_inventory, agent.sell_car, agent.verify_admin],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                )
            )
            
            if response.text:
                print(f"AI: {response.text}")
                #update the timestamp on every activity
                if agent.current_user:
                    agent.last_action_time = time.time()
            
        except Exception as e:
            print(f"AI Error: {e}")