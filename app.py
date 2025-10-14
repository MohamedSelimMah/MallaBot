import streamlit as st
import requests

api_endpoint = "http://localhost:11434/api/generate"

st.set_page_config(
    page_title="MALLA BOT",
    page_icon="🌶️",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'mailto:mahjoubselim07@gmail.com',
        'About':"I hope you enjoyed the experience 🇹🇳 made by ZeroOne"
    }
)

st.title("Malla Bot!")
st.caption("Ask Your Favorite Tunisian AI anything! 🇹🇳")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ekteb li theb...")

