import bcrypt # type: ignore
from database import get_connection

def set_password():
    conn = get_connection()
    cur = conn.cursor()
    
    password = "giorgi123"
    # ვქმნით ჰეშს იმავე ბიბლიოთეკით, რომლითაც აგენტი ამოწმებს
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cur.execute(
        "UPDATE users SET password_hash = %s, failed_attempts = 0, locked_until = NULL WHERE username = 'giorgi'",
        (hashed,)
    )
    conn.commit()
    print(f"✅ Password for 'giorgi' updated successfully to: {password}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    set_password()