import os
import requests
from dotenv import load_dotenv
from agent import EliteMotorsAgent
from database import get_connection

# .env ფაილის ჩატვირთვა
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
# ვიყენებთ შენს სიაში არსებულ Gemini 2.5 Flash მოდელს
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

motor_agent = EliteMotorsAgent()

def chat_with_ai(user_input: str):
    # 1. ვიღებთ რეალურ მონაცემებს ბაზიდან
    inventory = motor_agent.get_inventory()
    
    # DEBUG პრინტი, რომ ვნახოთ რატომ გვიწერს "relation cars does not exist"
    print("\n" + "="*40)
    print(f"DEBUG - მონაცემთა ბაზის პასუხი: {inventory}")
    print("="*40 + "\n")

    # 2. ვამზადებთ ინსტრუქციას AI-სთვის
    prompt = f"""
    შენ ხარ Elite Motors-ის დამხმარე ასისტენტი. 
    აი ჩვენი ამჟამინდელი ინვენტარი:
    {inventory}

    მომხმარებლის კითხვა: {user_input}
    უპასუხე ქართულ ენაზე, მეგობრულად და პროფესიონალურად.
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
            return f"შეცდომა API-სთან: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"სისტემური შეცდომა: {str(e)}"
    
    
    
def get_inventory(self):
    """ბაზიდან მონაცემების წამოღება 'vehicles' ცხრილიდან."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # ახლა უკვე ვიცით, რომ ცხრილს 'vehicles' ჰქვია
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
    # ტესტ-კითხვა
    response = chat_with_ai("რა მანქანები გყავთ გაყიდვაში?")
    print("\nAI-ს პასუხი:")
    print(response)