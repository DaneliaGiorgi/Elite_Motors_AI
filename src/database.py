import psycopg2 # type: ignore

# Database configuration settings
DB_CONFIG = {
    "dbname": "postgres", 
    "user": "macbookpro15", 
    "password": "", 
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    # Explicitly passing arguments to satisfy Pylance type checking
    conn = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )
    conn.autocommit = True  
    return conn

def create_tables():
    """Initializes the database schema by creating users and cars tables."""
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'user'
    );
    """
    
    cars_sql = """
    CREATE TABLE IF NOT EXISTS cars (
        car_id SERIAL PRIMARY KEY,
        brand VARCHAR(50) NOT NULL,
        year INTEGER NOT NULL,
        price DECIMAL(12, 2) NOT NULL,
        quantity INTEGER DEFAULT 1,
        added_by INTEGER REFERENCES users(user_id)
    );
    """
    #Get connetion to db
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(users_sql)
        cur.execute(cars_sql)
        print("Database initialized: Tables are ready.")
    except Exception as e:
        print(f"Initialization Error: {e}")
    finally:
        #Close connetion to db
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_tables()