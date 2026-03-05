import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

#Load environment variables from .env
load_dotenv()

#Get the connection string safely
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    print("Error: DATABASE_URL not found in environment variables.")
    exit(1)

#Format the URL for SQLAlchemy/psycopg2
db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)

try:
    #Initialize the database engine
    engine = create_engine(db_url)

    with engine.connect() as conn:
        #Get current database name
        db_query = conn.execute(text("SELECT current_database();")).fetchone()
        current_db = db_query[0] if db_query else "Unknown"

        #List all public tables
        tables_query = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)).fetchall()

    print(f"\n--- Connected to Database: {current_db} ---")
    print("Tables found:")
    
    if not tables_query:
        print("- No tables found in the public schema.")
    else:
        for t in tables_query:
            print(f"- {t[0]}")

except Exception as e:
    print(f"Connection failed: {e}")