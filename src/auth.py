import bcrypt
import psycopg2
from database import get_connection

class AuthManager:
    @staticmethod
    def hash_password(password):
        """პაროლის დაშიფვრა (Hashing)"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        """პაროლის შემოწმება ვალიდობისთვის"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username, password, role='user'):
        """მომხმარებლის ჩაწერა ბაზაში"""
        hashed_pw = self.hash_password(password)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, role)
            )
            conn.commit()
            print(f"✅ მომხმარებელი '{username}' წარმატებით დარეგისტრირდა!")
        except Exception as e:
            print(f"❌ რეგისტრაციის შეცდომა: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

# მოდი პირდაპირ შენი ადმინ მომხმარებელი შევქმნათ
if __name__ == "__main__":
    auth = AuthManager()
    # შეგიძლია სახელი და პაროლი შეცვალო სურვილისამებრ
    auth.register_user("admin_giorgi", "pass123", role="admin")