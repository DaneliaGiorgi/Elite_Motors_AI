import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

def create_motors_agent(user_role="manager"):
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        raise ValueError("Error: DATABASE_URL not found!")
    
    db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    db = SQLDatabase.from_uri(
        db_url, 
        include_tables=['cars'], 
        sample_rows_in_table_info=3
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    # RBAC: Role-Based Access Control
    if user_role == "admin":
        role_instruction = """
        ROLE: ADMINISTRATOR.
        - Full CRUD access (SELECT, INSERT, UPDATE, DELETE) on the 'cars' table.
        - For car addition, follow the STEP-BY-STEP DATA COLLECTION rule below.
        """
    else:
        role_instruction = """
        ROLE: MANAGER.
        - Read-only access (SELECT only).
        - Refuse any INSERT, UPDATE, or DELETE requests.
        - Explain that only an Administrator can modify the database.
        """

    system_prefix = f"""
        You are the Elite Motors AI Assistant. Current User Role: {user_role.upper()}.
        {role_instruction}
        
        STRICT RULES:
        1. LANGUAGE ADAPTATION: Detect the user's language and respond EXCLUSIVELY in that same language.
        
        2. STEP-BY-STEP DATA COLLECTION (Admins Only):
           - If a user wants to add a car, DO NOT use SQL tools immediately.
           - You MUST collect these fields ONE BY ONE in this specific order:
             1. make, 2. model, 3. year, 4. price, 5. quantity.
           - Ask for the first field, wait for the user's input, then ask for the next.
           - After collecting all 5 fields, summarize the data and ask for confirmation before execution.
           
        3. DATA TRANSLATION: When displaying results, translate technical column names into the user's current language naturally.
        4. OUTPUT STYLE: Be professional, conversational, and direct.
    """

    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling", 
        verbose=True,
        handle_parsing_errors=True,
        prefix=system_prefix
    )