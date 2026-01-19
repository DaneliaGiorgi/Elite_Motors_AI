import bcrypt # type: ignore
from database import get_connection

class AuthManager:
    """Handles user registration and secure password validation."""
    
    @staticmethod
    def hash_password(password):
        """Hashes a plain-text password using bcrypt."""
        #Added sybols to password
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        """Verifies if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username, password, role='user'):
        """Registers a new user into the database with a hashed password."""
        #Use hash_password funtion
        hashed_pw = self.hash_password(password)
        #Get connetion to db
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, role)
            )
            print(f"User '{username}' successfully registered!")
        except Exception as e:
            print(f"Registration Error: {e}")
        finally:
            #Close connetion to db
            cur.close()
            conn.close()