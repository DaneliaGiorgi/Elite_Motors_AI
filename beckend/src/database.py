import psycopg
from psycopg_pool import ConnectionPool

# მონაცემები შენი კომპიუტერის მიხედვით
DB_CONFIG = "postgresql://macbookpro15:1234@localhost:5432/postgres"

# ეს არის მთავარი ობიექტი
pool = ConnectionPool(conninfo=DB_CONFIG)

def get_user_by_email(email: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username, password_hash, role FROM users WHERE username = %s", (email,))
                return cur.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def create_tables():
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(50), last_name VARCHAR(50),
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        failed_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP WITH TIME ZONE
    );"""
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(users_sql)
                print("✅ Tables checked/created.")
    except Exception as e:
        print(f"Init Error: {e}")

if __name__ == "__main__":
    create_tables()