import streamlit as st
import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app_modules import app_config, ui_landing, chat_utils,tool_declaration, ui_components
from models import google_gemini as gemini, openai_chatgpt as openai

# --- Environment & API Key Setup ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GEMINI_API_KEY not found. This is required. Please set it in your .env file.")
    st.stop()

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found. This is required. Please set it in your .env file.")
    st.stop()

# --- Utility to Load CSS ---
def load_css(css_file_path):
    try:
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file_path}. Create './assets/style.css'")

# --- Main Application Setup  ---
if not os.path.exists(app_config.BASE_CHAT_DIR):
    os.makedirs(app_config.BASE_CHAT_DIR, exist_ok=True)

st.set_page_config(
    page_title="Statement Q&A Chat", layout="wide",
    initial_sidebar_state="expanded", page_icon="assets/zensys.png"
)
load_css("assets/style.css")

# --- Main Application Logic ---
if "active_profile" not in st.session_state or not st.session_state.active_profile:
    st.session_state.current_loaded_profile_for_chats = None
    st.session_state.chats = {}
    st.session_state.selected_model_name = app_config.DEFAULT_MODEL_NAME
    st.session_state.processing = False
    ui_landing.show_landing_page()
    st.stop()

ACTIVE_PROFILE_KEY = st.session_state.active_profile

if st.session_state.get("current_loaded_profile_for_chats") != ACTIVE_PROFILE_KEY:
    st.session_state.chats = chat_utils.load_chats(ACTIVE_PROFILE_KEY)
    st.session_state.current_loaded_profile_for_chats = ACTIVE_PROFILE_KEY
    st.session_state.active_chat = None
    st.session_state.pdf_to_display_in_dialog = None

CURRENT_PROFILE_CONFIG = app_config.PROFILE_CONFIGS[ACTIVE_PROFILE_KEY]
PREDEFINED_CHATS_FOR_PROFILE = CURRENT_PROFILE_CONFIG["predefined_chats"]

if "pdf_to_display_in_dialog" not in st.session_state:
    st.session_state.pdf_to_display_in_dialog = None

if "chats" not in st.session_state:
    st.session_state.chats = chat_utils.load_chats(ACTIVE_PROFILE_KEY)

for title, pdf_path_config in PREDEFINED_CHATS_FOR_PROFILE.items():
    if not (pdf_path_config and os.path.exists(pdf_path_config) and pdf_path_config.lower().endswith(".pdf")):
        continue

    if title not in st.session_state.chats:
        st.session_state.chats[title] = {
            "pdf_path": pdf_path_config, "messages": [],
            "gemini_cache_name": None, "gemini_cache_model": None, "cache_creation_failed": False,
            "openai_thread_id": None, "openai_file_id": None,
        }
        chat_utils.save_chat(ACTIVE_PROFILE_KEY, title, st.session_state.chats[title])
    else:
        st.session_state.chats[title].setdefault("cache_creation_failed", False)
        st.session_state.chats[title].setdefault("openai_thread_id", None)
        st.session_state.chats[title].setdefault("openai_file_id", None)
        if st.session_state.chats[title].get("pdf_path") != pdf_path_config:
            st.session_state.chats[title] = {
                "pdf_path": pdf_path_config, "messages": [],
                "gemini_cache_name": None, "gemini_cache_model": None, "cache_creation_failed": False,
                "openai_thread_id": None, "openai_file_id": None,
            }
            chat_utils.save_chat(ACTIVE_PROFILE_KEY, title, st.session_state.chats[title])

if not st.session_state.get("active_chat"):
    valid_predefined_titles = [t for t, p in PREDEFINED_CHATS_FOR_PROFILE.items() if p and os.path.exists(p) and t in st.session_state.chats]
    st.session_state.active_chat = valid_predefined_titles[0] if valid_predefined_titles else None

with st.sidebar:
    ui_components.render_sidebar_content() 

ui_components.display_pdf_modal()

if not st.session_state.active_chat:
    st.info("👉 Select a statement from the sidebar to begin.")
    if not any(os.path.exists(p) for p in PREDEFINED_CHATS_FOR_PROFILE.values() if p and isinstance(p, str)):
        st.warning("No valid PDF documents configured for the current profile. Please check profile settings.")
    st.stop()
else:
    chat_title = st.session_state.active_chat
    if chat_title not in st.session_state.chats or not os.path.exists(st.session_state.chats[chat_title].get('pdf_path', '')):
        st.error(f"Selected chat '{chat_title}' is invalid or its PDF is missing. Please select another chat.")
        st.session_state.active_chat = None 
        st.rerun()

    current_chat_data = st.session_state.chats[chat_title]
    chat_pdf_path = current_chat_data["pdf_path"]
    current_chat_messages = current_chat_data["messages"]

    displayed_model_name = st.session_state.get("selected_model_name", app_config.DEFAULT_MODEL_NAME)
    pdf_basename_for_display = os.path.basename(chat_pdf_path)
    st.markdown(f"### Chat: {chat_title}")
    st.caption(f"⚡ Model: {displayed_model_name} | 📄 Statement: {pdf_basename_for_display}")

    ui_components.display_chat_history(current_chat_messages)

    input_for_processing = None
    if st.session_state.get("process_button_question", False):
        if "question_from_button" in st.session_state:
            input_for_processing = st.session_state.question_from_button
            del st.session_state.question_from_button
        st.session_state.process_button_question = False

    chat_field_input = st.chat_input(
        "Ask a question to your statement",
        key=f"chat_input_{ACTIVE_PROFILE_KEY}_{chat_title}",
        disabled=st.session_state.get("processing", False)
    )
    
    if chat_field_input:
        input_for_processing = chat_field_input

    if input_for_processing:
        st.session_state.processing = True
        st.session_state.query_to_process = str(input_for_processing)
        current_chat_messages.append({"role": "user", "content": st.session_state.query_to_process})
        st.rerun()

if st.session_state.get("processing", False):
    user_query = st.session_state.query_to_process
    
    with st.spinner(f"Thinking with {displayed_model_name}..."):
        selected_model_name = st.session_state.selected_model_name
        api_model_id = app_config.AVAILABLE_MODELS[selected_model_name]
        answer_text = "Error: Model not recognized."
        effective_system_instruction = app_config.UNIFIED_SYSTEM_INSTRUCTION

        if "Google" in selected_model_name:
            client = genai.Client(api_key=GOOGLE_API_KEY)
            gemini_tool_config = types.Tool(function_declarations=tool_declaration.ALL_GEMINI_TOOLS)
            
            answer_text, updated_chat_data = gemini.generate_gemini_response(
                client=client,
                current_chat_messages=list(current_chat_messages), user_query=user_query,
                current_chat_data=dict(current_chat_data), chat_pdf_path=chat_pdf_path,
                system_instruction_str=effective_system_instruction, 
                gemini_tool_config=gemini_tool_config
            )
            st.session_state.chats[chat_title].update(updated_chat_data)

        elif "OpenAI" in selected_model_name:
            openai_result = openai.get_openai_response(
                api_key=OPENAI_API_KEY,
                model_id=api_model_id,
                system_instruction=effective_system_instruction, 
                pdf_path=chat_pdf_path,
                user_query=user_query,
                thread_id=current_chat_data.get("openai_thread_id"),
                file_id=current_chat_data.get("openai_file_id")
            )
            raw_answer_text = openai_result["response_text"]
            cleaned_answer_text = re.sub(r'【\d+:\d+†.*?】', '', raw_answer_text).strip()
            answer_text = cleaned_answer_text
            st.session_state.chats[chat_title]["openai_thread_id"] = openai_result["thread_id"]
            st.session_state.chats[chat_title]["openai_file_id"] = openai_result["file_id"]

        current_chat_messages.append({"role": "assistant", "content": answer_text})
        st.session_state.chats[chat_title]["messages"] = current_chat_messages
        
        chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, st.session_state.chats[chat_title])
        
        del st.session_state.query_to_process
        st.session_state.processing = False
        st.rerun()

if "figure_to_display" in st.session_state and st.session_state.figure_to_display is not None:
    fig = st.session_state.figure_to_display
    
    chat_title = st.session_state.active_chat
    current_chat_messages = st.session_state.chats[chat_title].get("messages", [])
    current_chat_messages.append({
        "role": "assistant",
        "type": "chart",
        "content": fig.to_json() 
    })
    
    chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, st.session_state.chats[chat_title])
    
    del st.session_state.figure_to_display
    st.rerun()

footer_html = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    opacity: 50%;
    width: 100%;
    text-align: center;
    padding-top: 5px;
    padding-bottom: 5px;
    z-index: 9999; 
}
</style>
<div class="footer">
    <p>
        <b>Disclaimer:</b> StatChat can make mistakes, so double-check it. 
    </p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)