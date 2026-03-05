import streamlit as st
import requests
import uuid

# 1. გვერდის კონფიგურაცია
st.set_page_config(page_title="Elite Motors AI", layout="wide")

BASE_URL = "http://127.0.0.1:8000"

# 2. სესიის ინიციალიზაცია
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "threads" not in st.session_state:
    st.session_state.threads = []
if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None

# 3. დამხმარე ფუნქციები
def generate_thread_id():
    """ქმნის უნიკალურ ID-ს მომხმარებლის პრეფიქსით ბაზაში ფილტრაციისთვის"""
    prefix = st.session_state.user_email if st.session_state.user_email else "guest"
    return f"{prefix}_{uuid.uuid4()}"

def fetch_all_threads():
    """ბექენდიდან ყველა საუბრის სიის წამოღება საიდბარისთვის"""
    if st.session_state.token:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            response = requests.get(f"{BASE_URL}/chat/threads", headers=headers)
            if response.status_code == 200:
                st.session_state.threads = response.json().get("threads", [])
        except Exception as e:
            st.error(f"Error fetching history: {e}")

def load_chat(thread_id):
    """კონკრეტული ჩატის მესიჯების ჩატვირთვა"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        response = requests.get(f"{BASE_URL}/chat/history", params={"thread_id": thread_id}, headers=headers)
        if response.status_code == 200:
            st.session_state.messages = response.json().get("history", [])
            st.session_state.current_thread_id = thread_id
            st.rerun()
    except Exception as e:
        st.error(f"Error loading chat: {e}")

def delete_thread(thread_id):
    """კონკრეტული ჩატის წაშლა ბაზიდან"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        res = requests.delete(f"{BASE_URL}/chat/history", params={"thread_id": thread_id}, headers=headers)
        if res.status_code == 200:
            # თუ მიმდინარე ჩატს ვშლით, ეკრანს ვასუფთავებთ
            if st.session_state.current_thread_id == thread_id:
                st.session_state.messages = []
                st.session_state.current_thread_id = generate_thread_id()
            fetch_all_threads()
            st.rerun()
    except Exception as e:
        st.error(f"Delete failed: {e}")

# 4. Login Screen
def login_screen():
    st.title("Login - Elite Motors AI")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            res = requests.post(f"{BASE_URL}/login", data={"username": email, "password": password})
            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.session_state.user_email = email
                st.session_state.current_thread_id = generate_thread_id()
                fetch_all_threads()
                st.rerun()
            else:
                st.error("Invalid credentials")

# 5. Chat Screen
def chat_screen():
    with st.sidebar:
        st.title("Elite Motors")
        if st.button("+ New Chat", use_container_width=True):
            st.session_state.current_thread_id = generate_thread_id()
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.subheader("Recent Chats")
        
        # ისტორიის ჩვენება საიდბარში
        for t in st.session_state.threads:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                # ღილაკი ჩატის გადასართავად
                if st.button(f"🗨️ {t['preview']}", key=t['id'], use_container_width=True):
                    load_chat(t['id'])
            with col2:
                # წაშლის ღილაკი
                if st.button("X", key=f"del_{t['id']}"):
                    delete_thread(t['id'])

        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # მთავარი ჩატის არეალი
    if not st.session_state.messages:
        st.title("How can I help you today?")
        st.info("Start a conversation to see it in your history.")
    else:
        st.title("Elite Motors AI")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # მესიჯის გაგზავნა
    if prompt := st.chat_input("Message Elite Motors AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        # თუ რაღაც მიზეზით thread_id არ გვაქვს, ვქმნით
        if not st.session_state.current_thread_id:
            st.session_state.current_thread_id = generate_thread_id()

        try:
            res = requests.post(
                f"{BASE_URL}/chat", 
                params={"message": prompt, "thread_id": st.session_state.current_thread_id},
                headers=headers
            )
            if res.status_code == 200:
                ai_res = res.json()["response"]
                st.session_state.messages.append({"role": "assistant", "content": ai_res})
                fetch_all_threads() # განვაახლოთ სია საიდბარისთვის
                st.rerun()
            else:
                st.error("Session expired or error occurred.")
        except Exception as e:
            st.error(f"Connection error: {e}")

# 6. Flow Control
if st.session_state.token is None:
    login_screen()
else:
    # თუ ჩატში ვართ, მაგრამ სიები ჯერ არ წამოგვიღია (მაგ. რეფრეშისას)
    if not st.session_state.threads and st.session_state.token:
        fetch_all_threads()
    chat_screen()