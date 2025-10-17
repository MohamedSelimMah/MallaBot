import streamlit as st
import requests
from PIL import Image
import json

# ===== Clarifai API configuration =====
API_URL = "https://api.clarifai.com/v2/users/openai/apps/chat-completion/models/gpt-4-turbo/versions/182136408b4b4002a920fd500839f2c8/outputs"
API_KEY = "56cdc5d57f90447cba9600f6397e0184"  # ← your Clarifai key

# ===== Page setup =====
st.set_page_config(
    page_title="MALLA BOT 🌶️",
    page_icon="🌶️",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'mailto:mahjoubselim07@gmail.com',
        'About': "🇹🇳 Made by ZeroOne — Malla Bot, the friendly Tunisian AI."
    }
)

# ===== Logo =====
try:
    img = Image.open("weebsu.png")
    st.image(img.resize((120, 120)))
except:
    st.warning("⚠️ Logo not found (weebsu.png).")

st.title("🌶️ MALLA BOT — Friendly Tunisian AI Chatbot")

# ===== Sidebar controls =====
with st.sidebar:
    st.header("⚙️ Settings")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max Response Length", 50, 500, 200, 10)
    new_chat = st.button("🆕 New Chat")

# ===== Reset chat when “New Chat” clicked =====
if new_chat:
    st.session_state.messages = []
    st.experimental_rerun()

# ===== Initialize chat history =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== Display chat messages =====
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ===== Handle user input =====
if prompt := st.chat_input("💬 Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # ----- Prepare Clarifai payload -----
    payload = {
        "inputs": [
            {
                "data": {
                    "text": {
                        "raw": prompt
                    }
                }
            }
        ]
    }

    headers = {
        "Authorization": f"Key {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        output = response.json()["outputs"][0]["data"]["text"]["raw"]
    except Exception as e:
        output = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": output})
    st.chat_message("assistant").write(output)
