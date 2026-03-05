from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from langchain_classic.schema import HumanMessage
from pydantic import BaseModel
from factory import create_motors_agent
from security import verify_password, create_access_token, decode_access_token
from database import get_user_by_email, pool#type:ignore

app = FastAPI(title="Elite Motors AI - Secure API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
agent_executor = create_motors_agent()

# Auth Models
class Token(BaseModel):
    access_token: str
    token_type: str

# 1. Authentication
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(status_code=401, detail="Invalid data")
    
    access_token = create_access_token(data={"sub": user[0], "role": user[2]})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid Token")
    return payload

# 2. Chat Endpoint (მიაქვს კონკრეტულ thread_id-ში)
@app.post("/chat")
async def chat(
    message: str, 
    thread_id: str, 
    current_user: dict = Depends(get_current_user)
):
    config = {"configurable": {"thread_id": thread_id}}
    response = agent_executor.invoke({"messages": [HumanMessage(content=message)]}, config)#type:ignore
    return {"response": response["messages"][-1].content}

# 3. History Endpoint (იღებს კონკრეტულ ისტორიას)
@app.get("/chat/history")
async def get_history(
    thread_id: str, 
    current_user: dict = Depends(get_current_user)
):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = agent_executor.get_state(config)#type:ignore
        messages = state.values.get("messages", [])
        formatted_history = [
            {"role": "user" if m.type == "human" else "assistant", "content": m.content} 
            for m in messages
        ]
        return {"history": formatted_history}
    except Exception:
        return {"history": []}

# 4. Threads List (საიდბარისთვის)
@app.get("/chat/threads")
async def get_all_threads(current_user: dict = Depends(get_current_user)):
    user_id = current_user["sub"]
    threads_list = []
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT thread_id 
                    FROM checkpoints 
                    WHERE thread_id LIKE %s
                    ORDER BY thread_id DESC
                """, (f"{user_id}%",))
                
                rows = cur.fetchall()
                for row in rows:
                    t_id = row[0]
                    display_id = t_id.replace(f"{user_id}_", "")[:8]
                    threads_list.append({"id": t_id, "preview": f"Chat {display_id}"})
        return {"threads": threads_list}
    except Exception:
        return {"threads": []}

# 5. Delete Specific Thread (აი აქ იყო შეცდომა!)
@app.delete("/chat/history")
async def delete_history(
    thread_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    აშლის მხოლოდ იმ კონკრეტულ ჩატს, რომელსაც X-ით მივუთითებთ
    """
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                # ვშლით ყველა ცხრილიდან, სადაც ეს thread_id ფიგურირებს
                cur.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
                cur.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (thread_id,))
                cur.execute("DELETE FROM checkpoint_blobs WHERE thread_id = %s", (thread_id,))
        return {"message": f"Thread {thread_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))