import sys
from typing import Any, cast
from langchain_core.runnables import RunnableConfig
import time
from auth import AuthManager
from factory import create_motors_agent
from security import ACCESS_TOKEN_EXPIRE_MINUTES

def start_app():
    auth = AuthManager()
    
    print("\n" + "="*45)
    print("      ELITE MOTORS AI - SECURE INTERFACE      ")
    print("="*45 + "\n")

    #Login or Registration
    print("[1] Login")
    print("[2] Register (New Role)")
    choice = input("\nSelect Option (1/2): ").strip()

    if choice == "2":
        print("\n--- REGISTRATION MODE ---")
        name = input("Enter First Name: ").strip()
        last_name = input("Enter Last Name: ").strip()
        username_input = input("Enter Email/Username: ").strip()
        password_input = input("Enter Password: ").strip()
        role_input = input("Enter Role (admin/manager): ").strip().lower()
        
        if role_input not in ['admin', 'manager']:
            print("[SYSTEM]: Invalid role. Defaulting to 'manager'.")
            role_input = 'manager'
            
        auth.register_user(name, last_name, username_input, password_input, role_input)
        print("\n[SYSTEM]: Account created! Proceeding to auto-login...")
        
        #Authenticate immediately after registration
        auth_result = auth.login_user(username_input, password_input)
    else:
        #Standard Login Phase
        username_input = input("\nEnter Username: ").strip()
        password_input = input("Enter Password: ").strip()
        auth_result = auth.login_user(username_input, password_input)

    #Validate Authentication Results
    if isinstance(auth_result, str):
        print(f"\n[AUTH ERROR]: {auth_result}")
        return

    #these variables are safely bound
    token = auth_result["token"]
    user_role = auth_result["role"]
    username = username_input # Use the input from login/reg
    
    print(f"\n[SYSTEM]: Access Granted. Session active for {ACCESS_TOKEN_EXPIRE_MINUTES} minutes.")
    print(f"[SYSTEM]: Hello {username}! Access Level: {user_role.upper()}\n")

    #Agent Initialization
    try:
        agent_executor = create_motors_agent(user_role=user_role)
        #Type cast config for Pylance safety
        config = cast(RunnableConfig, {"configurable": {"thread_id": username}})
        print("Connected to Elite Motors Database (LangGraph Active)...\n")
    except Exception as e:
        print(f"[CRITICAL ERROR]: Failed to initialize Agent: {e}")
        return

    #Secure Interaction Loop (The only loop needed)
    while True:
        #Token validation for session security
        decoded_token = auth.verify_token(token)
        
        if isinstance(decoded_token, str):
            print("\n" + "!"*45)
            print("  SESSION EXPIRED (Security Timeout)        ")
            print("  Your test session has ended.              ")
            print("  Please log in again to continue.          ")
            print("!"*45 + "\n")
            break

        user_input = input(f"{username} ({user_role}): ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye', 'გამოსვლა']:
            print("\nSession ended. Closing secure connection...")
            break
        
        if not user_input:
            continue

        try:
            #LangGraph State Input
            input_data = {
                "messages": [("user", user_input)],
                "user_role": user_role
            }
            
            #Agent Execution
            response: Any = agent_executor.invoke(input_data, config=config) # type: ignore
            
            if "messages" in response:
                output = response["messages"][-1].content
                if output.strip():
                    print(f"\nAI Assistant: {output}\n")
                else:
                    print("\nAI Assistant: System returned an empty response.\n")
        except Exception as e:
            print(f"\n[EXECUTION ERROR]: {e}\n")
        
        time.sleep(0.6)

if __name__ == "__main__":
    try:
        start_app()
    except KeyboardInterrupt:
        print("\n\nSystem shutdown by user. Securely exiting...")
        sys.exit(0)