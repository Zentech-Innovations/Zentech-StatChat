import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os
from google import genai
import plotly.io as pio
from . import app_config, chat_utils

def render_sidebar_content():
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    is_processing = st.session_state.processing

    active_profile_key = st.session_state.active_profile
    current_profile_config = app_config.PROFILE_CONFIGS[active_profile_key]
    predefined_chats_for_profile = current_profile_config["predefined_chats"]
    questions_for_profile = current_profile_config["questions"]

    side_col1, side_col2 = st.columns([1,6])
    with side_col1:
        if st.button("🏠", use_container_width=True, help="Go to Profile Selection", disabled=is_processing):
            st.session_state.active_profile = None
            st.session_state.active_chat = None
            st.rerun()

    with side_col2:
        st.markdown("## 📄 Talk to Your Statement ")

    with st.container(border=True):
        available_model_names = list(app_config.AVAILABLE_MODELS.keys())
        if "selected_model_name" not in st.session_state or st.session_state.selected_model_name not in available_model_names:
            st.session_state.selected_model_name = app_config.DEFAULT_MODEL_NAME

        selected_model_name_from_ui = st.selectbox(
            "Choose a model:",
            options=available_model_names,
            index=available_model_names.index(st.session_state.selected_model_name),
            key="model_selector_sidebar",
            disabled=is_processing
        )

        if selected_model_name_from_ui != st.session_state.selected_model_name:
            st.session_state.selected_model_name = selected_model_name_from_ui
            st.toast(f"Model changed to: {st.session_state.selected_model_name}", icon="🤖")

    current_selected_model_name = st.session_state.selected_model_name
    if "GPT" in current_selected_model_name:
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY not found. Please set it in your .env file.")

    elif "Gemini" in current_selected_model_name:
        if not os.getenv("GEMINI_API_KEY"):
            st.error("GEMINI_API_KEY not found. Please set it in your .env file.")

    st.markdown("---")

    sorted_chat_titles_for_profile = [
        title
        for title, path in predefined_chats_for_profile.items()
        if path and os.path.exists(path) and path.lower().endswith(".pdf") and title in st.session_state.chats
    ]
    other_chat_titles = [
        title
        for title in st.session_state.chats.keys()
        if title not in sorted_chat_titles_for_profile and \
           st.session_state.chats[title].get("pdf_path") and \
           os.path.exists(st.session_state.chats[title]["pdf_path"]) and \
           st.session_state.chats[title]["pdf_path"].lower().endswith(".pdf")
    ]
    combined_titles_to_display = sorted_chat_titles_for_profile + sorted(other_chat_titles)

    if combined_titles_to_display:
        current_active_chat_index = 0
        if st.session_state.active_chat and st.session_state.active_chat in combined_titles_to_display:
            current_active_chat_index = combined_titles_to_display.index(st.session_state.active_chat)
        elif combined_titles_to_display:
            st.session_state.active_chat = combined_titles_to_display[0]
            st.session_state.pdf_to_display_in_dialog = None

        with st.container(border=True):
            selected_chat_title = st.selectbox(
                "Select a Statement:",
                options=combined_titles_to_display,
                index=current_active_chat_index,
                key="chat_selector_dropdown",
                disabled=is_processing
            )
            if selected_chat_title != st.session_state.active_chat:
                st.session_state.active_chat = selected_chat_title
                st.session_state.pdf_to_display_in_dialog = None
                st.rerun()

            col1, col2= st.columns([1,1])

            with col1:
                active_chat_for_delete_button = st.session_state.get("active_chat")
                if active_chat_for_delete_button and active_chat_for_delete_button in st.session_state.chats :
                    if st.button(f"🗑️ Clear Chat", key=f"delete_{active_chat_for_delete_button}", help=f"Delete all messages in: {active_chat_for_delete_button}", use_container_width=True, disabled=is_processing):
                        
                        chat_to_delete_data = st.session_state.chats.get(active_chat_for_delete_button)
                        if chat_to_delete_data:
                            cache_name_to_delete = chat_to_delete_data.get("gemini_cache_name")
                            if cache_name_to_delete and os.getenv("GEMINI_API_KEY"):
                                try:
                                    client_del = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                                    client_del.caches.delete(name=cache_name_to_delete)
                                    st.toast(f"Gemini cache for chat deleted.", icon="🗑️")
                                except Exception as e_del:
                                    st.warning(f"Could not delete Gemini cache: {e_del}")

                        del st.session_state.chats[active_chat_for_delete_button]
                        
                        try:
                            profile_chat_dir = chat_utils.get_profile_chat_dir(active_profile_key)
                            file_to_delete = os.path.join(profile_chat_dir, f"{active_chat_for_delete_button}.json")
                            if os.path.exists(file_to_delete):
                                os.remove(file_to_delete)
                        except Exception:
                            pass
                        
                        st.session_state.active_chat = None
                        st.rerun()

            with col2:
                if st.button("📄 View PDF", key="view_selected_pdf_button_sidebar", use_container_width=True, disabled=is_processing):
                    active_chat_for_view = st.session_state.get("active_chat")
                    if active_chat_for_view and active_chat_for_view in st.session_state.chats:
                        chat_data = st.session_state.chats[active_chat_for_view]
                        pdf_path_to_show = chat_data.get("pdf_path")
                        if pdf_path_to_show and os.path.exists(pdf_path_to_show):
                            st.session_state.pdf_to_display_in_dialog = pdf_path_to_show
                            st.rerun()
                    else:
                        st.toast("No PDF selected to view.", icon="ℹ️")
    else:
        st.markdown("No chats available for this profile.")

    st.markdown("---")
    st.markdown("## ❓ Select a Question")
    if questions_for_profile:
        with st.container(border=True, height=380):
            for i, question in enumerate(questions_for_profile):
                if st.button(
                    question, key=f"question_button_{active_profile_key}_{i}", use_container_width=True,
                    disabled=is_processing
                ):
                    st.session_state.process_button_question = True
                    st.session_state.question_from_button = question
                    st.rerun()
    else:
        st.markdown("No predefined questions for this profile.")

def display_pdf_modal():
    if st.session_state.get("pdf_to_display_in_dialog"):
        _pdf_path_for_dialog_display = st.session_state.pdf_to_display_in_dialog
        st.session_state.pdf_to_display_in_dialog = None
        if _pdf_path_for_dialog_display and os.path.exists(_pdf_path_for_dialog_display):
            if hasattr(st, 'dialog'):
                @st.dialog(title=" ", width="large")
                def view_pdf_in_dialog_function_content():
                    with open(_pdf_path_for_dialog_display, "rb") as f:
                        binary_content = f.read()
                    pdf_viewer(input=binary_content, height=1000)
                    st.markdown(os.path.basename(_pdf_path_for_dialog_display), unsafe_allow_html=True)
                view_pdf_in_dialog_function_content()

def display_chat_history(current_chat_messages):
    for msg in current_chat_messages:
        with st.chat_message(msg["role"]):
            content_type = msg.get("type", "text")

            if content_type == "chart":
                try:
                    fig = pio.from_json(msg["content"])
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not display chart from history: {e}")
            else:
                st.markdown(msg["content"])