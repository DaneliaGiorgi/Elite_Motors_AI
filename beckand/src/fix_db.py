import psycopg2
import os

DB_URL = os.getenv("DATABASE_URL") 

def fix_database(): 
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("Connection established. Creating/Fixing 'users' table...")

        #Create the table if it does not exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'manager',
                failed_attempts INTEGER DEFAULT 0 NOT NULL,
                locked_until TIMESTAMP WITH TIME ZONE
            );
        """)
        
        #Enforce the column size
        cur.execute("ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255);")
        
        #Clean up old data
        cur.execute("TRUNCATE TABLE users RESTART IDENTITY;")
        
        conn.commit()
        print("SUCCESS: Table 'users' is created and ready!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()#type: ignore
        conn.close()#type: ignore

if __name__ == "__main__":
    fix_database()