import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

def create_motors_agent(user_role="manager"):
    #DATABASE_URL safe reading
    raw_url = os.getenv("DATABASE_URL")
    
    if not raw_url:
        raise ValueError("Error: DATABASE_URL not found in .env file!")
    
    db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    #Satabase configuration
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

    #Strict instruction (Prompt)
    system_prefix = f"""
        You are the Elite Motors AI Assistant. Current User Role: {user_role}.
        
        STRICT OPERATING RULES:
        1. LANGUAGE: Respond in the SAME language the user uses.
        2. GREETINGS: If the user just says "Hello" or "Hi", simply greet them back politely. 
        Do NOT query the database or show car information unless specifically asked.
        3. SEARCHING: If the user asks about car availability, quantity, or specific details, 
        then immediately use 'sql_db_query' to fetch data from the 'vehicles' table.
        4. NO CLARIFICATION: When a car question is asked, do not ask follow-up questions, 
        just show the database results.
        5. PRIVACY: Only show what is in the database.
        6.Return ONLY the final answer to the user. Do not include your internal reasoning or 'Thought' process in the response.
    """

    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=False,
        handle_parsing_errors=True,
        prefix=system_prefix
    )