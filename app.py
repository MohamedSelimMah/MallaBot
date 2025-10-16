import streamlit as st
import requests
from PIL import Image
import json

api_endpoint = "http://localhost:11434/api/generate"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="MALLA BOT",
    page_icon="🌶️",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'mailto:mahjoubselim07@gmail.com',
        'About': "I hope you enjoyed the experience 🇹🇳 made by ZeroOne"
    }
)

# --- LOGO + TITLE ---
img = Image.open("logo.png")
img = img.resize((90, 90))
st.image(img)
st.title("Malla Bot!")
st.caption("Ask Your Favorite Tunisian AI anything! 🇹🇳")

# --- INITIALIZE STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_name: [messages]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None  # no chat yet

# --- SIDEBAR ---
with st.sidebar:
    # NEW CHAT BUTTON
    if st.button("New Chat"):
        st.session_state.current_chat = None

    # CHAT HISTORY
    st.subheader("Chat History")
    chat_names = list(st.session_state.chats.keys())
    if chat_names:
        current_index = 0
        if st.session_state.current_chat in chat_names:
            current_index = chat_names.index(st.session_state.current_chat)

        selected_chat = st.selectbox("Select a chat:", chat_names, index=current_index)
        if selected_chat != st.session_state.current_chat:
            st.session_state.current_chat = selected_chat

    # MODEL PARAMETERS
    with st.expander("Model Parameters", expanded=False):
        temperature = st.slider("Temperature (Creativity)", 0.0, 1.5, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", min_value=50, max_value=2000, value=200, step=50)

# --- GET CURRENT CHAT MESSAGES ---
messages = st.session_state.chats.get(st.session_state.current_chat, [])

# Display previous messages
for msg in messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# --- CHAT INPUT ---
prompt = st.chat_input("Ekteb li theb...")

if prompt:
    # Create a new chat if none exists
    if st.session_state.current_chat is None:
        chat_name = prompt[:30] + "..." if len(prompt) > 30 else prompt
        st.session_state.current_chat = chat_name
        st.session_state.chats[chat_name] = []
        messages = st.session_state.chats[chat_name]

    # Append user message
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    payload = {
        "model": "llama3.2",
        "prompt": f"User: {prompt}",
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    with st.spinner("mmm dkika nkhamem..."):
        try:
            response = requests.post(api_endpoint, json=payload, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
        else:
            full_response = ""
            with st.chat_message("assistant"):
                placeholder = st.empty()
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    # Handle JSON or raw text
                    try:
                        parsed = json.loads(line)
                        text_chunk = parsed.get("response") or parsed.get("text") or parsed.get("token") or ""
                    except Exception:
                        text_chunk = line.decode("utf-8") if isinstance(line, bytes) else line
                        if text_chunk.startswith("data: "):
                            text_chunk = text_chunk[len("data: "):]

                    full_response += text_chunk
                    placeholder.markdown(full_response)

            messages.append({"role": "assistant", "content": full_response})
