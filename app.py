import streamlit as st
import requests
from PIL import Image
import json

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

img = Image.open("logo.png")
new_size = (100,100)
img= img.resize(new_size)
st.image(img)
st.title("Malla Bot!")
st.caption("Ask Your Favorite Tunisian AI anything! 🇹🇳")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg['role']).markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ekteb li theb...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    payload ={
        "model": "llama3.2",
        "prompt":f"User: {prompt}"
    }

    with st.spinner("mmm dkika nkhamem..."):
        try:
            response=requests.post(api_endpoint, json=payload, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
        else:
            full_response= ""

            with st.chat_message("assistant"):
                placeholder= st.empty()
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    text_chunk= ""

                    try:
                        parsed=json.loads(line)
                        if isinstance(parsed, dict):

                            text_chunk= parsed.get("response") or parsed.get("text") or parsed.get("token") or ""
                        else:
                            text_chunk=str(parsed)
                    except Exception:

                        raw=line
                        if raw.startswith("data: "):
                            raw=raw[len("data: "):]
                        text_chunk= raw

                    full_response+= text_chunk
                    placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
                
