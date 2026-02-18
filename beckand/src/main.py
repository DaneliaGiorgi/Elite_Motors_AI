import os
from factory import create_motors_agent

def start_app():
    #Role assignment (you can change it to 'admin' if needed)
    user_role = "manager"
    agent_executor = create_motors_agent(user_role=user_role)

    print("\n" + "="*40)
    print(f"ELITE MOTORS AI - READY | Role: {user_role.upper()}")
    print("="*40 + "\n")

    while True:
        user_input = input("User: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'გამოსვლა']:
            break
        
        if not user_input:
            continue

        try:
            #Call agent
            response = agent_executor.invoke({"input": user_input})
            
            #Retrieving the response
            output = response.get("output", "")
            
            if isinstance(output, list) and output:
                output = output[0].get("text", str(output))
            
            #Show the final answer
            if str(output).strip():
                print(f"\nAI: {output}\n")
            else:
                print("\nAI: Apologies, data retrieval failed. Please rephrase your question.\n")

        except Exception as e:
            print(f"\n[ERROR]: Something went wrong: {e}\n")

if __name__ == "__main__":
    start_app()