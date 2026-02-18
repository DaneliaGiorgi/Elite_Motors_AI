import os
import requests
from dotenv import load_dotenv
from agent import EliteMotorsAgent
from database import get_connection

#Loading .env file
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
#Use Gemini 2.5 Flash model
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

motor_agent = EliteMotorsAgent()

def chat_with_ai(user_input: str):
    #Fetching real data from the database
    inventory = motor_agent.get_inventory()
    
    # DEBUG Print it to see why it’s showing "relation cars does not exist"
    print("\n" + "="*40)
    print(f"DEBUG - მონაცემთა ბაზის პასუხი: {inventory}")
    print("="*40 + "\n")

    #Instuction for AI
    prompt = f"""
    You are Elite Motors asistent. 
    Here is our current inventory:
    {inventory}

    Question from user: {user_input}
    Answer in Georgian, in a friendly and professional manner.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(URL, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error API: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"System Error: {str(e)}"
    
    
    
def get_inventory(self):
    """Retrieving data from the 'vehicles' table in the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT brand, year, price, quantity FROM vehicles")
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
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Elite Motors AI Engine is running...")