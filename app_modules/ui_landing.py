# app_modules/ui_landing.py
import streamlit as st
from .app_config import PROFILE_CONFIGS
from .chat_utils import load_chats

# --- Landing Page Function ---
def show_landing_page():
    with st.container():
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            landing_image_path = "assets/zentech.png"
            st.image(landing_image_path, use_container_width=True)
    st.title("🔍 Welcome to Your Financial Document Analyzer")

    cols = st.columns(len(PROFILE_CONFIGS))
    for i, (profile_key, config) in enumerate(PROFILE_CONFIGS.items()):
        with cols[i]:
            if st.button(config["button_label"], key=f"profile_btn_{profile_key}",\
                use_container_width=True, help=f"Open {config['page_title']}"):

                st.session_state.active_profile = profile_key
                st.session_state.active_chat = None
                st.session_state.pdf_to_display_in_dialog = None
                st.session_state.chats = load_chats(profile_key)
                st.session_state.current_loaded_profile_for_chats = profile_key
                st.rerun()