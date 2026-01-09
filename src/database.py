import psycopg2 # type: ignore

print("--- File runing! ---")
# database configuration
DB_CONFIG = {
    "dbname": "postgres", 
    "user": "macbookpro15", 
    "password": "123", # usually emptuy
    "host": "localhost",
    "port": "5432"
}

def get_connection():
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
    """Creates tables: users and cars"""
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
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(users_sql)
        cur.execute(cars_sql)
        conn.commit()
        print("✅ The database is ready: the users and cars tables have been created!")
    except Exception as e:
        print(f"❌ Error while creating tables: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
        
def delete_car_by_id(car_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        conn.commit()
        print(f"✅ Car ID {car_id} successufuly deleted.")
    except Exception as e:
        print(f"❌ Error while deleting.: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
    delete_car_by_id(1)