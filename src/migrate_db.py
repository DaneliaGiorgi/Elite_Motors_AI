from database import get_connection

def migrate():
    """update database schema without losing data."""
    #Connect to database
    conn = get_connection()
    cur = conn.cursor()
    
    print("🔍 Checking for database updates...")
    
    try:
        #Add failed_attempts column
        cur.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='users' AND column_name='failed_attempts') THEN
                    ALTER TABLE users ADD COLUMN failed_attempts INT DEFAULT 0;
                    RAISE NOTICE 'Column failed_attempts added.';
                END IF;
            END $$;
        """)

        #Add locked_until column
        cur.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='users' AND column_name='locked_until') THEN
                    ALTER TABLE users ADD COLUMN locked_until TIMESTAMP WITH TIME ZONE;
                    RAISE NOTICE 'Column locked_until added.';
                END IF;
            END $$;
        """)
        
        # Commit changes
        conn.commit()
        print("Migration successful! Database is now up to date.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
