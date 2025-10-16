import streamlit as st
from openai import OpenAI
from PIL import Image

# --- INITIALIZE OPENAI CLIENT ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# --- SESSION STATE INIT ---
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_name: [messages]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "new_chat_trigger" not in st.session_state:
    st.session_state.new_chat_trigger = False

# --- SIDEBAR ---
with st.sidebar:
    # NEW CHAT BUTTON
    if st.button("New Chat"):
        st.session_state.current_chat = None
        st.session_state.new_chat_trigger = True

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
            st.session_state.new_chat_trigger = False

    # MODEL PARAMETERS
    with st.expander("Model Parameters", expanded=False):
        temperature = st.slider("Temperature (Creativity)", 0.0, 1.5, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", min_value=50, max_value=2000, value=300, step=50)

# --- CHAT HANDLING ---
if st.session_state.new_chat_trigger:
    messages = []
else:
    messages = st.session_state.chats.get(st.session_state.current_chat, [])

# Display previous chat messages
for msg in messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# --- CHAT INPUT ---
prompt = st.chat_input("Ekteb li theb...")

if prompt:
    if st.session_state.new_chat_trigger:
        st.session_state.new_chat_trigger = False

    # Create new chat if needed
    if st.session_state.current_chat is None:
        chat_name = prompt[:30] + "..." if len(prompt) > 30 else prompt
        st.session_state.current_chat = chat_name
        st.session_state.chats[chat_name] = []
        messages = st.session_state.chats[chat_name]

    # Add user message
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Generate assistant reply
    with st.spinner("mmm dkika nkhamem..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Fast, cheap, and smart
                messages=[
                    {"role": "system", "content": "You are Malla Bot, a friendly and funny Tunisian AI 🇹🇳. Speak in a casual, humorous tone."},
                    *[{"role": m["role"], "content": m["content"]} for m in messages],
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            full_response = ""
            with st.chat_message("assistant"):
                placeholder = st.empty()
                for chunk in response:
                    text_chunk = chunk.choices[0].delta.get("content", "")
                    full_response += text_chunk
                    placeholder.markdown(full_response)

            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {e}")
