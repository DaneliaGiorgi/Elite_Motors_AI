import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from database import get_connection
from security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

#Load secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

class AuthManager:
    """Handles user registration, authentication, and brute-force protection."""
    
    @staticmethod
    def hash_password(password):
        """Hashes a plain-text password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        """Verifies if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def register_user(self, name, last_name, username, password, role='manager'):
        hashed_pw = self.hash_password(password)
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Added first_name and last_name to columns and values
            cur.execute(
                """INSERT INTO users (name, last_name, username, password_hash, role, failed_attempts) 
                VALUES (%s, %s, %s, %s, %s, 0)""",
                (name, last_name, username, hashed_pw, role)
            )
            conn.commit()
            print(f"User '{username}' successfully registered!")
        except Exception as e:
            print(f"Registration Error: {e}")
        finally:
            cur.close()
            conn.close()

    def login_user(self, username, password):
        """Authenticates user and manages login attempts and account locking."""
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            #Fetch user data and security info
            cur.execute(
                "SELECT password_hash, role, failed_attempts, locked_until FROM users WHERE username = %s", 
                (username,)
            )
            user = cur.fetchone()

            if not user:
                return "Error: User not found."

            pw_hash, role, attempts, locked_until = user
            attempts = attempts if attempts is not None else 0
            

            #Check if the account is currently locked
            if locked_until:
                now = datetime.now(timezone.utc)
                if now < locked_until:
                    remaining_seconds = (locked_until - now).total_seconds()
                    remaining_minutes = int(max(0, remaining_seconds // 60))
                    return f"Error: Account locked. Try again in {remaining_minutes} minutes."
                

            #Verify password
            if self.check_password(password, pw_hash):
                # Successful login: reset failed attempts
                cur.execute(
                    "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = %s",
                    (username,)
                )
                token = self.generate_token(username, role)
                return {"token": token, "username": username, "role": role}
            
            else:
                #Failed attempt logic
                new_attempts = attempts + 1
                if new_attempts >= 3:
                    #Lock account for 15 minutes after 3 failed attempts
                    lock_time = datetime.now(timezone.utc) + timedelta(minutes=15)
                    cur.execute(
                        "UPDATE users SET failed_attempts = %s, locked_until = %s WHERE username = %s",
                        (new_attempts, lock_time, username)
                    )
                    conn.commit()
                    return "Error: Too many failed attempts. Account locked for 15 minutes."
                else:
                    cur.execute(
                        "UPDATE users SET failed_attempts = %s WHERE username = %s",
                        (new_attempts, username)
                    )
                    conn.commit()
                    return f"Error: Invalid password. Attempt {new_attempts}/3."

        except Exception as e:
            print(f"DEBUG: AuthManager error -> {e}")
            return f"Login Error: {str(e)}"        
        finally:
            cur.close()
            conn.close()
            
    @staticmethod
    def cleanup_old_users():
        """Optional: Deletes non-admin users to keep the portfolio DB clean."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            #Delete all admin users
            cur.execute("DELETE FROM users WHERE username != 'admin@elite.com'")
            conn.commit()
        except Exception as e:
            print(f"Cleanup Error: {e}")
        finally:
            cur.close()
            conn.close()

    @staticmethod       
    def generate_token(username, role):
        """Creates a secure JWT token that expires in 1 hour."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            'username': username,
            'role': role,
            "exp": int(expire.timestamp()) 
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token):
        """Verifies the JWT token and returns the payload if valid."""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return "Error: Token has expired."
        except jwt.InvalidTokenError:
            return "Error: Invalid token."


if __name__ == "__main__":
    auth = AuthManager()
    
    email = "test1@gmail.com"
    new_password = "test123"
    
    # Hash the password
    hashed_pw = auth.hash_password(new_password)
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        #Attempt to update existing user
        cur.execute("""
            UPDATE users 
            SET password_hash = %s, 
                failed_attempts = 0, 
                locked_until = NULL 
            WHERE username = %s
        """, (hashed_pw, email))
        
        conn.commit()
        
        if cur.rowcount == 0:
            print(f"Warning: User '{email}' not found. Registering as new...")
            #Fixed: Passing all 5 required arguments (first_name, last_name, username, password, role)
            auth.register_user("System", "Admin", email, new_password, role="admin")
        else:
            print(f"SUCCESS: User '{email}' has been FORCE UPDATED.")
            print(f"New Password is: {new_password}")

    except Exception as e:
        print(f"Critical DB Error: {e}")
    finally:
        cur.close()
        conn.close()