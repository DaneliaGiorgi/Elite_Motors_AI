import os
import time
from google import genai
from google.genai import types
from agent import EliteMotorsAgent  # Import our agent logic

def start_app():
    """Main function to run the AI Agent interface."""
    agent = EliteMotorsAgent()
    
    # Initialize Gemini Client
    # Assume API_KEY is loaded in agent.py or we can load it here too
    API_KEY = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=API_KEY)

    print("\n" + "="*40)
    print("ELITE MOTORS AI SYSTEM ACTIVATED")
    print("="*40)
    print("Type 'exit' or 'quit' to close the system.\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("System shutting down. Goodbye!")
            break

        # Check for Session Timeout (5 minutes)
        if agent.current_user and (time.time() - agent.last_action_time > agent.session_timeout):
            print("Session expired due to inactivity. Please log in again.")
            agent.current_user = None

        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction="""
                        You are the Elite Motors Sales & Security Assistant. 
                        STRICT RULES:
                        1. RESPONSE LANGUAGE: Always match the user's language (Georgian or English).
                        2. AUTHENTICATION: For car sales or additions, you MUST have an active session.
                        3. LOGIN FEEDBACK: When calling 'verify_admin', you MUST report the EXACT message returned by the tool to the user. 
                        - If it says "Attempt 1/3", tell the user exactly that.
                        - If it says "Account locked", warn them clearly.
                        4. Do not summarize or hide security alerts.
                        5. Be professional and use emojis.
                        """,
                    tools=[agent.add_new_car, agent.get_inventory, agent.sell_car, agent.verify_admin],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                )
            )
            
            if response.text:
                print(f"AI: {response.text}")
                
                # Update timestamp if user is logged in
                if agent.current_user:
                    agent.last_action_time = time.time()
            
        except Exception as e:
            print(f"System Error: {e}")

if __name__ == "__main__":
    start_app()