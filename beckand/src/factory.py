import os
from typing import Annotated, TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from pydantic import BaseModel, Field, validator
from logger import ShowroomLogger

load_dotenv()

class VehicleValidation(BaseModel):
    brand: str = Field(description="Brand and model of the vehicle")
    year: int = Field(gt=1900, lt=2027, description="Manufacturing year")
    mileage: float = Field(ge=0)
    price: float = Field(gt=0)
    quantity: int = Field(ge=1)
    vehicle_type: str = Field(description="sedan, suv, truck, electric")
    engine_volume: float = Field(default=0.0)
    battery_capacity: float = Field(default=0.0)
    max_load: float = Field(default=0.0)

    @validator('vehicle_type')
    def validate_type(cls, v):
        allowed = ['sedan', 'suv', 'truck', 'electric']
        if v.lower() not in allowed:
            raise ValueError(f"Type must be one of {allowed}")
        return v.lower()

#Define the State Schema
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_role: str

def create_motors_agent(user_role: str = "manager"):
    """
    Creates a LangGraph agent that handles SQL queries for the 'vehicles' table.
    Ensures RBAC and step-by-step data collection.
    """
    
    #Database Initialization
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        raise ValueError("DATABASE_URL environment variable is not set")
        
    #Ensure SQLAlchemy compatibility (fix for postgres://)
    db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    #CONNECT TO 'vehicles' TABLE
    db = SQLDatabase.from_uri(db_url, include_tables=['vehicles'])
    
    #Initialize the LLM (Gemini 2.0 Flash)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    
    #Initialize SQL Toolkit and Tools for the 'vehicles' table
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    tool_node = ToolNode(tools)

    #Define the Agent Logic (Node)
    def call_model(state: AgentState):
        messages = state['messages']
        role = state.get('user_role', 'manager')
        
        validation_rules = """
        VALIDATION RULES:
        - Year must be between 1901 and 2026.
        - Price and Quantity must be positive numbers.
        - Vehicle type must be one of: [sedan, suv, truck, electric].
        If the user provides invalid data, point out the specific error in Georgian and ask again.
        """
        
        #Core System Instructions using 'vehicles' table context
        system_prompt = f"""
        You are the Elite Motors AI Assistant. Role: {role.upper()}.
        
        LANGUAGE RULES:
        1. If the user writes in Georgian (either in Georgian script or Latin script), you MUST respond using ONLY the Georgian alphabet (ქართული ანბანი). NEVER use Latin characters to write Georgian words (e.g., No "Gamarjoba", use "გამარჯობა").
        2. If the user writes in English, respond in English.
        3. Always match the user's language but prioritize correct script for the language.
                
        CRITICAL RULE: 
        - Always detect the user's language and respond EXCLUSIVELY in that same language. 
        - If the user writes in Georgian, respond in Georgian. If English, respond in English.
        - This applies to all greetings, questions, and data descriptions.
        
        STRICT DATA COLLECTION RULES:
        1. Collect info ONE BY ONE. Wait for the user's answer before asking the next question.
        2. Do NOT provide examples like (e.g., Audi Q5) in your questions. Just ask the question.
        
        ORDER OF QUESTIONS:
        1. **Vehicle Name**: Ask for the brand and model (to be saved in 'brand' column).
        2. **Year**: Ask for the manufacturing year.
        3. **Mileage**: Ask for the mileage.
        4. **Price**: Ask for the price.
        5. **Quantity**: Ask for the quantity.
        6. **Vehicle Type**: Ask for the type (sedan, suv, truck, electric). 
        7. **Warranty**: 
           -Ask for the warranty period and type.
           - Ask for 'warranty_period' (e.g., 12 months, 2 years).
           - Ask for 'warranty_type' and provide these specific options to the user: [Full, Powertrain, Battery, or Limited]. 
           - If the user provides a different type, politely ask them to choose from the list to ensure database consistency.
        8. **E-Sign**: Ask if it is e-sign eligible.
        9. **CORRECTION LOGIC**:
           - If the user indicates a mistake or asks to change a previous answer (e.g., "change type to truck" or "I made a mistake"):
           - Immediately acknowledge the change and update the value in memory.
           - Resume the flow by returning to the exact question that was pending before the correction.
           - If the 'vehicle_type' is changed, ensure the final set of questions adjusts to include the correct conditional fields (battery_capacity or max_load).
           
        CONDITIONAL LOGIC:
        - If type is 'electric': Ask for 'battery_capacity'. Skip 'engine_volume'.
        - If type is 'truck': Ask for 'max_load'. Skip 'engine_volume'.
        - For all other types: Ask for 'engine_volume'.

        ADMIN CAPABILITIES:
        - As an ADMIN, you have full permission to DELETE vehicles, UPDATE prices, or INSERT new records. 
        - When an Admin asks to delete or update, execute the SQL command immediately or after a single confirmation.

        DATABASE MAPPING:
        Table: 'vehicles'
        Columns: brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible, vehicle_type, battery_capacity, max_load, engine_volume.
        
        Always respond in the user's language. Keep responses professional, brief, and direct.
        {validation_rules}
        """
        
        #Bind tools to the model and invoke
        model_with_tools = llm.bind_tools(tools)
        response = model_with_tools.invoke([("system", system_prompt)] + messages)
        
        #logger
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool in response.tool_calls:
                #The tool is defined here because it’s inside the loop
                ShowroomLogger.log(f"ADMIN ACTION: Executing {tool['name']} with args: {tool['args']}")
        elif response.content:
            ShowroomLogger.log(f"AI Response: {response.content[:50]}...")
            
        return {"messages": [response]}

    #Build the StateGraph
    workflow = StateGraph(AgentState)

    #Define the nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    #Set the entry point
    workflow.set_entry_point("agent")

    #Define conditional routing
    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        last_message = state['messages'][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END # type: ignore

    # Add edges
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    #Add Persistence (Memory)
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)