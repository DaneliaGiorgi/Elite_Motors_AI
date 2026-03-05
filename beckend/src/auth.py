import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
# მხოლოდ ამათ ვაიმპორტებთ, get_connection აქ აღარ გვინდა!
from database import get_user_by_email, pool 
from security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Load secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

class AuthManager:
    """Handles user registration, authentication, and brute-force protection."""
    
    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def register_user(self, name, last_name, username, password, role='manager'):
        hashed_pw = self.hash_password(password)
        try:
            # get_connection()-ის ნაცვლად ვიყენებთ pool-ს
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO users (name, last_name, username, password_hash, role, failed_attempts) 
                        VALUES (%s, %s, %s, %s, %s, 0)""",
                        (name, last_name, username, hashed_pw, role)
                    )
            print(f"User '{username}' successfully registered!")
        except Exception as e:
            print(f"Registration Error: {e}")

    def login_user(self, username, password):
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT password_hash, role, failed_attempts, locked_until FROM users WHERE username = %s", 
                        (username,)
                    )
                    user = cur.fetchone()

                    if not user:
                        return "Error: User not found."

                    pw_hash, role, attempts, locked_until = user
                    attempts = attempts if attempts is not None else 0

                    if locked_until:
                        now = datetime.now(timezone.utc)
                        if now < locked_until:
                            remaining_minutes = int((locked_until - now).total_seconds() // 60)
                            return f"Error: Account locked. Try again in {remaining_minutes} minutes."

                    if self.check_password(password, pw_hash):
                        cur.execute(
                            "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = %s",
                            (username,)
                        )
                        token = self.generate_token(username, role)
                        return {"token": token, "username": username, "role": role}
                    else:
                        new_attempts = attempts + 1
                        if new_attempts >= 3:
                            lock_time = datetime.now(timezone.utc) + timedelta(minutes=15)
                            cur.execute(
                                "UPDATE users SET failed_attempts = %s, locked_until = %s WHERE username = %s",
                                (new_attempts, lock_time, username)
                            )
                            return "Error: Too many failed attempts. Account locked for 15 minutes."
                        else:
                            cur.execute(
                                "UPDATE users SET failed_attempts = %s WHERE username = %s",
                                (new_attempts, username)
                            )
                            return f"Error: Invalid password. Attempt {new_attempts}/3."
        except Exception as e:
            return f"Login Error: {str(e)}"        

    @staticmethod
    def cleanup_old_users():
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM users WHERE username != 'admin@elite.com'")
        except Exception as e:
            print(f"Cleanup Error: {e}")

    @staticmethod       
    def generate_token(username, role):
        if not isinstance(SECRET_KEY, str):
            raise ValueError("SECRET_KEY missing.")
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {'username': username, 'role': role, "exp": int(expire.timestamp())}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])#type: ignore
        except Exception as e:
            return f"Error: {str(e)}"

# Main script (Update/Register logic)
if __name__ == "__main__":
    auth = AuthManager()
    email = "test1@gmail.com"
    new_password = "test123"
    hashed_pw = auth.hash_password(new_password)
    
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users 
                    SET password_hash = %s, failed_attempts = 0, locked_until = NULL 
                    WHERE username = %s
                """, (hashed_pw, email))
                
                if cur.rowcount == 0:
                    auth.register_user("System", "Admin", email, new_password, role="admin")
                else:
                    print(f"SUCCESS: User '{email}' updated.")
    except Exception as e:
        print(f"Critical DB Error: {e}")