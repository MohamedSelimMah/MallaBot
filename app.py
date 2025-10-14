import streamlit as st
import requests

api_endpoint = "http://localhost:11434/api/generate"

st.set_page_config (page_title="MALLA BOT",page_icon="🌶️")
st.title("Malla Bot!")
st.caption("ask Your Favorite Tunisian AI anything ! 🇹🇳")
    
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt= st.chat_input("Ekteb li theb...")

if prompt:
    st.session_state.messages.append({"role": "user","content":prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = requests.post(
            api_endpoint,
            json={
                "model": "llama3.2",
                "prompt": prompt
            },
            stream=False
        )
        data = response.json()
        bot_message = data.get("response","No response from Malla Bot")
    except Exception as e:
        bot_message = f"Error connecting to the model: {e}"

    st.session_state.messages.append({"role": "assistant","content":bot_message})

    with st.chat_message("assistant"):
        st.markdown(bot_message)


    if st.button("new chat"):
        st.session_state.messages = []
        st.experimental_rerun()