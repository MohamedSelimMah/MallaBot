import streamlit as st
import requests
from PIL import Image
import json
import datetime

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
try:
    img = Image.open("logo.png")
    img = img.resize((90, 90))
    st.image(img)
except:
    st.warning("Logo image not found. Using default icon.")
    
st.title("Malla Bot!")
st.caption("Ask Your Favorite Tunisian AI anything! 🇹🇳")

# --- INITIALIZE STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_name: [messages]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None  # no chat yet

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="chat-header">', unsafe_allow_html=True)
    st.subheader("Chat Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # NEW CHAT BUTTON
    if st.button("New Chat"):
        st.session_state.current_chat = None
        st.rerun()
    
    # CHAT HISTORY
    st.divider()
    st.subheader("Chat History")
    chat_names = list(st.session_state.chats.keys())
    
    if chat_names:
        current_index = 0
        if st.session_state.current_chat in chat_names:
            current_index = chat_names.index(st.session_state.current_chat)

        selected_chat = st.selectbox("Select a chat:", chat_names, index=current_index, label_visibility="collapsed")
        if selected_chat != st.session_state.current_chat:
            st.session_state.current_chat = selected_chat
            st.rerun()
    else:
        st.info("No chat history yet!")
    
    # Delete current chat functionality
    if st.session_state.chats and st.session_state.current_chat:
        st.divider()
        if st.button("🗑️ Delete Current Chat", use_container_width=True, type="secondary"):
            del st.session_state.chats[st.session_state.current_chat]
            if st.session_state.chats:
                st.session_state.current_chat = list(st.session_state.chats.keys())[0]
            else:
                st.session_state.current_chat = None
            st.rerun()

    # API CONFIGURATION
    with st.expander("🔧 API Configuration", expanded=False):
        api_endpoint = st.text_input(
            "Ollama API Endpoint",
            value="http://localhost:11434/api/generate",
            help="Change if using a remote Ollama instance"
        )
        
        # Health check
        if st.button("Test Connection", use_container_width=True):
            try:
                health_url = api_endpoint.replace("/generate", "/tags")
                test_response = requests.get(health_url, timeout=10)
                if test_response.status_code == 200:
                    st.success("✅ Connected successfully!")
                else:
                    st.error("❌ Connection failed")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

    # MODEL PARAMETERS
    with st.expander("⚙️ Model Parameters", expanded=False):
        temperature = st.slider(
            "Temperature", 
            0.0, 1.5, 0.7, 0.1,
            help="Lower = more deterministic, Higher = more creative"
        )
        
        max_tokens = st.number_input(
            "Max Tokens", 
            min_value=50, 
            max_value=4000, 
            value=500, 
            step=50,
            help="Maximum length of response"
        )
        
        top_p = st.slider(
            "Top P", 
            0.1, 1.0, 0.9, 0.1,
            help="Nucleus sampling probability threshold"
        )

    # SYSTEM PROMPT
    with st.expander("🤖 System Prompt", expanded=False):
        system_prompt = st.text_area(
            "System Instructions",
            value="You are Malla Bot, a helpful Tunisian AI assistant that provides clear, concise responses with a friendly tone.",
            height=100,
            label_visibility="collapsed"
        )

    # EXPORT FUNCTIONALITY
    if st.session_state.chats and st.session_state.current_chat:
        with st.expander("💾 Export Chat", expanded=False):
            if st.button("Export as JSON", use_container_width=True):
                chat_data = {
                    "chat_name": st.session_state.current_chat,
                    "export_date": datetime.datetime.now().isoformat(),
                    "parameters": {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "top_p": top_p
                    },
                    "messages": st.session_state.chats[st.session_state.current_chat]
                }
                
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(chat_data, indent=2),
                    file_name=f"malla_bot_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

    # DANGER ZONE - Clear all chats
    if st.session_state.chats:
        with st.expander("🚨 Danger Zone", expanded=False):
            if st.button("Clear All Chats", use_container_width=True, type="secondary"):
                st.session_state.chats = {}
                st.session_state.current_chat = None
                st.rerun()

# --- MAIN CHAT AREA ---

# Welcome message for new chats
if st.session_state.current_chat is None and not st.session_state.chats:
    st.info("👋 Welcome ! Start a conversation by typing below the title of the chat.")

# Display current chat name
if st.session_state.current_chat:
    st.subheader(f"💬 {st.session_state.current_chat}")

# --- GET CURRENT CHAT MESSAGES ---
messages = []
if st.session_state.current_chat:
    messages = st.session_state.chats.get(st.session_state.current_chat, [])

# Display previous messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
prompt = st.chat_input("Ekteb li theb...")

if prompt:
    # Create a new chat if none exists
    if st.session_state.current_chat is None:
        chat_name = prompt[:30] + "..." if len(prompt) > 30 else prompt
        st.session_state.current_chat = chat_name
        st.session_state.chats[chat_name] = []
        messages = st.session_state.chats[chat_name]
        st.rerun()

    # Append user message
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare payload for Ollama
    payload = {
        "model": "llama3.2",  # Fixed model name
        "prompt": prompt,
        "system": system_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "stream": True
    }

    # Display thinking message and get response
    with st.spinner("mmm dkika nkhamem..."):
        try:
            response = requests.post(api_endpoint, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            full_response = ""
            with st.chat_message("assistant"):
                placeholder = st.empty()
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            parsed = json.loads(line)
                            # Check if this is the final response
                            if parsed.get("done", False):
                                break
                            # Get the response text
                            text_chunk = parsed.get("response", "")
                        except json.JSONDecodeError:
                            # If not JSON, use the line as is
                            text_chunk = line
                        
                        full_response += text_chunk
                        # Display with cursor effect
                        placeholder.markdown(full_response + "▌")
                
                # Final display without cursor
                placeholder.markdown(full_response)
            
            # Save assistant's response
            messages.append({"role": "assistant", "content": full_response})
            st.session_state.chats[st.session_state.current_chat] = messages
                
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please try again.")
            # Remove the user message since we couldn't get a response
            messages.pop()
            
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to Ollama API. Make sure it's running on localhost:11434")
            messages.pop()
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {e}")
            messages.pop()
            
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)}")
            messages.pop()

# Footer
st.markdown("---")
st.caption("Made with ❤️ by ZeroOne | 🇹🇳 Tunisian AI Assistant")