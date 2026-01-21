import psycopg2 # type: ignore

# Database configuration settings
DB_CONFIG = {
    "dbname": "postgres", 
    "user": "macbookpro15", 
    "password": "1234", 
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )
    # Autocommit is set to True to apply changes immediately without manual commit
    conn.autocommit = True  
    return conn

def create_tables():
    """Initializes the database schema and handles migrations (security updates)."""
    
    #SQL to create the users table with security and lockout columns
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        failed_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP WITH TIME ZONE
    );
    """
    
    #SQL to create the cars table with a Foreign Key linked to the user who added it
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
    
    #Connect to the database and execute queries
    conn = get_connection()
    cur = conn.cursor()
    try:
        #Create tables if they do not exist
        cur.execute(users_sql)
        cur.execute(cars_sql)
        
        #Migration: Add security columns to an existing table if they are missing
        #This prevents data loss while updating the database structure
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_attempts INTEGER DEFAULT 0;")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;")
        
        print("✅ Database initialized: Tables created and security columns verified.")
    except Exception as e:
        print(f"Initialization Error: {e}")
    finally:
        #close the cursor and connection to free up resources
        cur.close()
        conn.close()

if __name__ == "__main__":
    #Execute table creation logic when script is run directly
    create_tables()