import psycopg2
from database import get_connection
from auth import AuthManager

class EliteMotorsAgent:
    def __init__(self):
        self.name = 'Elit Motors AI'
        self.auth = AuthManager()
        self.current_user = None

    #auth
    def login(self, username, password):
        #user system login
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT user_id, password_hash, role FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            
            if user and self.auth.check_password(password, user[1]):
                self.current_user = {'id': user[0], 'username': username, 'role': user[2]}
                return f"✅ Hello, {username}! you successfuly logged in system"
            return "❌ Wrong user name or password"
        finally:
            cur.close()
            conn.close()
            
            
    #Add new car
    def add_new_car(self, brand, year, price, quantity=1):
        "Add car only for admin"
        if not self.current_user or self.current_user['role'] != 'admin':
            return "🚫 for this operation need admin access!" 
        
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO cars (brand, year, price, quantity, added_by) VALUES (%s, %s, %s, %s, %s)",
                (brand, year, price, quantity, self.current_user['id'])
            )
            conn.commit()
            return f"🏎️ მანქანა {brand} ({year}) წარმატებით დაემატა ინვენტარში!"
        except Exception as e:
            conn.rollback()
            return f"❌ შეცდომა დამატებისას: {e}"
        finally:
            cur.close()
            conn.close()
            
            
    # --- testing ---
if __name__ == "__main__":
    agent = EliteMotorsAgent()
    
    # 1. try enter
    print(agent.login("admin_giorgi", "pass123"))
    
    # 2. if loggin add car
    if agent.current_user:
        print(agent.add_new_car("Mercedes-AMG GT", 2024, 150000, 1))
    