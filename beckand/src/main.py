import sys
import time
from auth import AuthManager
from factory import create_motors_agent
from security import ACCESS_TOKEN_EXPIRE_MINUTES

def start_app():
    auth = AuthManager()
    
    print("\n" + "="*45)
    print("      ELITE MOTORS AI - SECURE INTERFACE      ")
    print("="*45 + "\n")

    #NEW: Choice for Portfolio Demo
    print("[1] Login")
    print("[2] Register (New Role)")
    choice = input("\nSelect Option (1/2): ").strip()

    if choice == "2":
        print("\n--- REGISTRATION MODE ---")
        name = input("Enter First Name: ").strip()
        last_name = input("Enter Last Name: ").strip()
        username = input("Enter Email/Username: ").strip()
        password = input("Enter Password: ").strip()
        role = input("Enter Role (admin/manager): ").strip().lower()
        
        if role not in ['admin', 'manager']:
            print("[SYSTEM]: Invalid role. Defaulting to 'manager'.")
            role = 'manager'
            
        auth.register_user(name, last_name, username, password, role)
        print("\n[SYSTEM]: Account created! Proceeding to auto-login...")
        
        #Authorization is automatically performed with the same data
    else:
        #Standard Login Phase
        username = input("\nEnter Username: ").strip()
        password = input("Enter Password: ").strip()
    
    #Authentication (Existing Logic) 
    auth_result = auth.login_user(username, password)

    if isinstance(auth_result, str):
        print(f"\n[AUTH ERROR]: {auth_result}")
        return

    token = auth_result["token"]
    user_role = auth_result["role"]
    
    print(f"\n[SYSTEM]: Access Granted. Session active for {ACCESS_TOKEN_EXPIRE_MINUTES} minutes.")
    print(f"[SYSTEM]: Hello {username}! Access Level: {user_role.upper()}\n")

    #Agent Initialization
    try:
        agent_executor = create_motors_agent(user_role=user_role)
        print("Connected to Elite Motors Database...\n")
    except Exception as e:
        print(f"[CRITICAL ERROR]: Failed to initialize Agent: {e}")
        return

    #Secure Interaction Loop
    while True:
        decoded_token = auth.verify_token(token)
        
        if isinstance(decoded_token, str):
            print(f"\n[SECURITY]: {decoded_token} Re-authentication required.")
            break

        user_input = input(f"{username} ({user_role}): ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye', 'გამოსვლა']:
            print("\nSession ended. Closing secure connection...")
            break
        
        if not user_input:
            continue

        try:
            response = agent_executor.invoke({"input": user_input})
            output = response.get("output", "")
            
            if str(output).strip():
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