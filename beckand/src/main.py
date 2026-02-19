import os
from factory import create_motors_agent

def start_app():
    #Based on the design, this is where user authentication should occur
    print("\n" + "="*40)
    print("      ELITE MOTORS AI CONTROL PANEL      ")
    print("="*40 + "\n")

    #Authorization simulation (later, the data will come from a JWT)
    print("System Authorization Required:")
    username = input("Enter Username: ").strip()
    user_role = input("Enter Role (admin/manager): ").strip().lower()

    if user_role not in ['admin', 'manager']:
        print("\n[AUTH ERROR]: Access Denied. Invalid Role.")
        return

    #Dynamic role-based agent initialization
    try:
        agent_executor = create_motors_agent(user_role=user_role)
        print(f"\n[SYSTEM]: Hello {username}! Access Level: {user_role.upper()}")
        print("Connected to Elite Motors Database...\n")
    except Exception as e:
        print(f"[CRITICAL ERROR]: Failed to initialize Agent: {e}")
        return

    while True:
        user_input = input(f"{username} ({user_role}): ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'გამოსვლა']:
            print("\nSession ended. Closing connection...")
            break
        
        if not user_input:
            continue

        try:
            #Call agent
            response = agent_executor.invoke({"input": user_input})
            output = response.get("output", "")
            
            #Answer
            if str(output).strip():
                print(f"\nAI Assistant: {output}\n")
            else:
                print("\nAI Assistant: The system was unable to generate a response. Please clarify your question.\n")

        except Exception as e:
            #If an administrator attempts to run an invalid SQL query, it will be caught here
            print(f"\n[EXECUTION ERROR]: {e}\n")

if __name__ == "__main__":
    start_app()