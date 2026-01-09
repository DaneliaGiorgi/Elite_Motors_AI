import bcrypt # type: ignore
from database import get_connection

class AuthManager:
    @staticmethod
    def hash_password(password):
        """Password hashing (Hashing)"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        """Password validation check"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username, password, role='user'):
        """Saving the user to the database"""
        hashed_pw = self.hash_password(password)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, role)
            )
            conn.commit()
            print(f"✅ User '{username}' Successfully registered!")
        except Exception as e:
            print(f"❌ registration Error: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

# create your admin user directly
if __name__ == "__main__":
    auth = AuthManager()
    # change the username and password
    auth.register_user("admin_giorgi", "pass123", role="admin")