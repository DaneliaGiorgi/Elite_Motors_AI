import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

def create_motors_agent(user_role="manager"):
    #Secure database connection configuration
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        raise ValueError("Error: DATABASE_URL not found in .env file!")
    
    db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    #Create SQLDatabase by role
    #If role is 'manager', agent is allowed to perform SELECT operations only
    db = SQLDatabase.from_uri(
        db_url, 
        include_tables=['vehicles'],
        sample_rows_in_table_info=3
    )

    #Model configuration
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    #Role based system prompt
    role_instruction = ""
    
    if user_role == "admin":
        role_instruction = """
        ROLE: ADMINISTRATOR (Full Access).
        - You can ADD, DELETE, and UPDATE records in the 'vehicles' table.
        - If the user asks to "Add a car", "Change price", or "Delete", perform the SQL action.
        """
    else:
        role_instruction = """
        ROLE: MANAGER (Read-Only).
        - You can ONLY read data using SELECT.
        - NEVER attempt to INSERT, UPDATE, or DELETE. If asked, politely refuse.
        """

    system_prefix = f"""
        You are the Elite Motors AI Assistant. Current User Role: {user_role.upper()}.
        {role_instruction}
        
        STRICT OPERATING RULES:
        1. MULTILINGUAL ADAPTATION: Identify the user's language and respond EXCLUSIVELY in that language. 
           (e.g., if the user speaks Spanish, you must translate everything to Spanish).
        2. DATABASE TRANSLATION: When displaying car details, translate the database column names 
           (Brand, Year, Price, Mileage, etc.) into the user's language naturally.
        3. GREETINGS: Respond to greetings in the same language they were given.
        4. EXECUTION: Use tools immediately for any car-related requests.
        5. NO CLARIFICATION: Show database results directly without follow-up questions.
        6. FINAL ANSWER: Return ONLY the final, translated output. Do not show internal reasoning.
    """

    #Create agent
    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling", 
        verbose=False,
        handle_parsing_errors=True,
        prefix=system_prefix
    )