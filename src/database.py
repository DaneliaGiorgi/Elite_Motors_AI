import psycopg2

print("--- ფაილი გაეშვა! ---")
# database configuration
DB_CONFIG = {
    "dbname": "postgres", 
    "user": "macbookpro15", 
    "password": "", # usually emptuy
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """ქმნის და აბრუნებს კავშირს ბაზასთან"""
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """ქმნის ცხრილებს: users და cars"""
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
        print("✅ ბაზა მომზადებულია: ცხრილები users და cars შეიქმნა!")
    except Exception as e:
        print(f"❌ შეცდომა ცხრილების შექმნისას: {e}")
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
        print(f"✅ ავტომობილი ID-ით {car_id} წარმატებით წაიშალა.")
    except Exception as e:
        print(f"❌ შეცდომა წაშლისას: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_tables()