import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- Import custom modules using your specified style ---
from app_modules import app_config, ui_landing, chat_utils

# --- Environment & API Key Setup ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GEMINI_API_KEY not found. Please ensure it's set in your .env file.")
    st.stop()

# --- Utility to Load CSS ---
def load_css(css_file_path):
    try:
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file_path}. Create './assets/style.css'")

# --- Main Application Setup ---
if not os.path.exists(app_config.BASE_CHAT_DIR): 
    os.makedirs(app_config.BASE_CHAT_DIR, exist_ok=True) 

st.set_page_config(
    page_title="Statement Q&A Chat", layout="wide",
    initial_sidebar_state="expanded", page_icon="assets/zentech.png" 
)

# Load CSS from external file
load_css("assets/style.css")

# --- Main Application Logic ---
if "active_profile" not in st.session_state or not st.session_state.active_profile:
    if "current_loaded_profile_for_chats" not in st.session_state:
        st.session_state.current_loaded_profile_for_chats = None
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    ui_landing.show_landing_page()
    st.stop()

ACTIVE_PROFILE_KEY = st.session_state.active_profile

if st.session_state.get("current_loaded_profile_for_chats") != ACTIVE_PROFILE_KEY:
    st.session_state.chats = chat_utils.load_chats(ACTIVE_PROFILE_KEY)
    st.session_state.current_loaded_profile_for_chats = ACTIVE_PROFILE_KEY
    st.session_state.active_chat = None 
    st.session_state.pdf_to_display_in_dialog = None

# --- Chatbot UI (if a profile is selected) ---
CURRENT_PROFILE_CONFIG = app_config.PROFILE_CONFIGS[ACTIVE_PROFILE_KEY]
PREDEFINED_CHATS_FOR_PROFILE = CURRENT_PROFILE_CONFIG["predefined_chats"]
QUESTIONS_FOR_PROFILE = CURRENT_PROFILE_CONFIG["questions"]

if "pdf_to_display_in_dialog" not in st.session_state:
    st.session_state.pdf_to_display_in_dialog = None


# --- Session State Initialization & Predefined Chat Setup for Current Profile ---
if "chats" not in st.session_state:
    st.session_state.chats = chat_utils.load_chats()

for title, pdf_path_config in PREDEFINED_CHATS_FOR_PROFILE.items():
    if not (
        pdf_path_config
        and os.path.exists(pdf_path_config)
        and pdf_path_config.lower().endswith(".pdf")
    ):
        continue

    if title not in st.session_state.chats:
        st.session_state.chats[title] = {
            "pdf_path": pdf_path_config,
            "messages": [],
            "gemini_cache_name": None,
            "gemini_cache_model": None,
            "cache_creation_failed": False,
        }
        chat_utils.save_chat(ACTIVE_PROFILE_KEY, title, st.session_state.chats[title])
    else:
        st.session_state.chats[title].setdefault("cache_creation_failed", False)
        if st.session_state.chats[title].get("pdf_path") != pdf_path_config:
            st.session_state.chats[title]["pdf_path"] = pdf_path_config
            st.session_state.chats[title]["messages"] = []
            st.session_state.chats[title]["gemini_cache_name"] = None
            st.session_state.chats[title]["gemini_cache_model"] = None
            st.session_state.chats[title]["cache_creation_failed"] = False
            chat_utils.save_chat(ACTIVE_PROFILE_KEY, title, st.session_state.chats[title])

valid_predefined_titles_for_profile = [
    title
    for title, path in PREDEFINED_CHATS_FOR_PROFILE.items()
    if path and os.path.exists(path) and path.lower().endswith(".pdf") and title in st.session_state.chats
]

if not st.session_state.get("active_chat") or st.session_state.active_chat not in valid_predefined_titles_for_profile:
    if valid_predefined_titles_for_profile:
        st.session_state.active_chat = valid_predefined_titles_for_profile[0]
    else:
        all_valid_loaded_chats = [
            t for t, data in st.session_state.chats.items()
            if data.get("pdf_path") and os.path.exists(data["pdf_path"]) and data["pdf_path"].lower().endswith(".pdf")
        ]
        st.session_state.active_chat = next(iter(all_valid_loaded_chats), None)
    st.session_state.pdf_to_display_in_dialog = None 

# --- Sidebar UI ---
with st.sidebar:
    side_col1, side_col2 = st.columns([1,6])
    with side_col1:
        if st.button("🏠", use_container_width=True):
            st.session_state.active_profile = None
            st.session_state.active_chat = None
            st.rerun()
   
    with side_col2:
        st.markdown("## 📄 Talk to Your Statement ")

    sorted_chat_titles_for_profile = []
    for title_key in PREDEFINED_CHATS_FOR_PROFILE.keys():
        if title_key in st.session_state.chats:
            chat_data_for_sort = st.session_state.chats[title_key]
            pdf_path_for_sort = chat_data_for_sort.get("pdf_path")
            if (
                pdf_path_for_sort
                and os.path.exists(pdf_path_for_sort)
                and pdf_path_for_sort.lower().endswith(".pdf")
            ):
                sorted_chat_titles_for_profile.append(title_key)


    other_chat_titles = [
        title_key
        for title_key in st.session_state.chats.keys()
        if title_key not in sorted_chat_titles_for_profile and \
           st.session_state.chats[title_key].get("pdf_path") and \
           os.path.exists(st.session_state.chats[title_key]["pdf_path"]) and \
           st.session_state.chats[title_key]["pdf_path"].lower().endswith(".pdf")
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
                key="chat_selector_dropdown"
            )
            if selected_chat_title != st.session_state.active_chat:
                st.session_state.active_chat = selected_chat_title
                st.session_state.pdf_to_display_in_dialog = None
                st.rerun()

            col1, col2= st.columns([1,1]) 

            with col1:
                active_chat_for_delete_button = st.session_state.get("active_chat")
                if active_chat_for_delete_button and active_chat_for_delete_button in st.session_state.chats :
                    if st.button(f"🗑️ Clear Chat", key=f"delete_{active_chat_for_delete_button}",\
                        help=f"Delete chat for: {active_chat_for_delete_button}", use_container_width=True):

                        chat_to_delete_data = st.session_state.chats.get(active_chat_for_delete_button)
                        cache_name_to_delete = None
                        if chat_to_delete_data:
                            cache_name_to_delete = chat_to_delete_data.get("gemini_cache_name")

                        if cache_name_to_delete:
                            try:
                                client_del = genai.Client(api_key=GOOGLE_API_KEY)
                                client_del.caches.delete(name=cache_name_to_delete)
                            except Exception as e_del:
                                st.warning(f"Could not delete cache {os.path.basename(cache_name_to_delete)}: {e_del}")

                        if active_chat_for_delete_button in st.session_state.chats:
                            del st.session_state.chats[active_chat_for_delete_button]
                        try:
                            profile_chat_dir_of_deleted = chat_utils.get_profile_chat_dir(ACTIVE_PROFILE_KEY)
                            os.remove(os.path.join(profile_chat_dir_of_deleted, f"{active_chat_for_delete_button}.json"))
                        except FileNotFoundError:
                            pass

                        new_active_chat_options = [
                            t for t in PREDEFINED_CHATS_FOR_PROFILE.keys()
                            if t in st.session_state.chats and os.path.exists(st.session_state.chats[t]["pdf_path"])
                        ]
                        if not new_active_chat_options:
                            new_active_chat_options = [
                                t for t, data in st.session_state.chats.items()
                                if data.get("pdf_path") and os.path.exists(data["pdf_path"])
                            ]
                        st.session_state.active_chat = new_active_chat_options[0] if new_active_chat_options else None
                        st.session_state.pdf_to_display_in_dialog = None 
                        st.rerun()
                elif not active_chat_for_delete_button : 
                    st.markdown("<p style='text-align: center; font-size: small;'>No active chat to clear.</p>", unsafe_allow_html=True)

            with col2:
                if st.button("📄 View PDF", key="view_selected_pdf_button_sidebar", use_container_width=True):
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
    if QUESTIONS_FOR_PROFILE:
        with st.container(border=True, height=380):
            for i, question in enumerate(QUESTIONS_FOR_PROFILE):
                if st.button(
                    question, key=f"question_button_{ACTIVE_PROFILE_KEY}_{i}", use_container_width=True
                ):
                    st.session_state.question_from_button = question
                    st.session_state.process_button_question = True
                    if st.session_state.active_chat: st.rerun()
    else:
        st.markdown("No predefined questions for this profile.")

# --- PDF Dialog ---
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
                st.markdown(_pdf_path_for_dialog_display, unsafe_allow_html=True)
            view_pdf_in_dialog_function_content()    
    else:
        st.session_state.pdf_to_display_in_dialog = None


# --- Main Chat Area ---
if not st.session_state.active_chat:
    st.info("👉 Select a statement from the sidebar to begin, or ensure valid PDFs are configured for the current profile.")
    if not any(os.path.exists(p) for p in PREDEFINED_CHATS_FOR_PROFILE.values() if p):
        st.stop()
else:
    chat_title = st.session_state.active_chat
    current_chat_data = st.session_state.chats.get(chat_title)

    if not current_chat_data or not current_chat_data.get("pdf_path") or not os.path.exists(current_chat_data.get("pdf_path")):
        valid_titles_in_profile = [
            title for title in PREDEFINED_CHATS_FOR_PROFILE.keys()
            if title in st.session_state.chats and \
            st.session_state.chats[title].get("pdf_path") and \
            os.path.exists(st.session_state.chats[title]["pdf_path"])
        ]
        if valid_titles_in_profile:
            st.session_state.active_chat = valid_titles_in_profile[0]
        else:
            all_valid_chats = [
                t for t, data in st.session_state.chats.items()
                if data.get("pdf_path") and os.path.exists(data["pdf_path"])
            ]
            st.session_state.active_chat = all_valid_chats[0] if all_valid_chats else None
        st.rerun()
        st.stop()
    chat_pdf_path = current_chat_data["pdf_path"]
    current_chat_messages = current_chat_data["messages"]

    st.markdown(f"### Chat: {chat_title}")

    pdf_basename_for_display = os.path.basename(chat_pdf_path)
    st.caption(
        f"⚡ Model: {app_config.FIXED_MODEL_ID} | 📄 Statement: {pdf_basename_for_display}"
    )

    if not os.path.exists(chat_pdf_path):
        st.error(f"The PDF for '{chat_title}' could not be found at {chat_pdf_path}. Please select another statement.")
        st.stop()

    for msg in current_chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    input_for_processing = None

    if st.session_state.get("process_button_question", False):
        if "question_from_button" in st.session_state:
            input_for_processing = st.session_state.question_from_button
            del st.session_state.question_from_button
        st.session_state.process_button_question = False

    chat_field_input = st.chat_input("Ask a question to your statement", key=f"chat_input_{ACTIVE_PROFILE_KEY}_{chat_title}")

    if chat_field_input:
        input_for_processing = chat_field_input

    if input_for_processing:
        user_query = input_for_processing

        current_chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
        
        gemini_api_formatted_conversation = []
        for msg in current_chat_messages:
            role_for_api = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_api_formatted_conversation.append(
                {"role": role_for_api, "parts": [{"text": msg["content"]}]}
            )

        with st.spinner("Thinking..."):
            response = None
            answer_text = "Error: Could not retrieve a valid response from the model."
            use_fallback_for_this_run = False 
            cache_name_for_generation = None
            uploaded_file_for_cache_ref = None

            try:
                client = genai.Client(api_key=GOOGLE_API_KEY)

                _stored_cache_name_from_session = current_chat_data.get("gemini_cache_name")
                _stored_cache_model_from_session = current_chat_data.get("gemini_cache_model")
                _cache_creation_failed_persistently = current_chat_data.get("cache_creation_failed", False)

                # --- Phase 1: Validate existing cache ---
                if _stored_cache_name_from_session and not _cache_creation_failed_persistently: 
                    try:
                        cache_info = client.caches.get(name=_stored_cache_name_from_session)
                        if cache_info.model == app_config.MODEL_TO_USE_FOR_API and \
                        _stored_cache_model_from_session == app_config.MODEL_TO_USE_FOR_API:
                            cache_name_for_generation = _stored_cache_name_from_session
                        else: 
                            try: client.caches.delete(name=_stored_cache_name_from_session)
                            except Exception: pass 
                            current_chat_data["gemini_cache_name"] = None
                            current_chat_data["gemini_cache_model"] = None
                            current_chat_data["cache_creation_failed"] = False 
                            chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, current_chat_data)
                    
                    except genai.errors.ClientError as e_client_get:
                        current_chat_data["gemini_cache_name"] = None
                        current_chat_data["gemini_cache_model"] = None
                        current_chat_data["cache_creation_failed"] = False 
                        chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, current_chat_data)
                    except Exception as e_other_get:
                        current_chat_data["gemini_cache_name"] = None
                        current_chat_data["gemini_cache_model"] = None
                        current_chat_data["cache_creation_failed"] = False 
                        chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, current_chat_data)

                # --- Phase 2: Create cache if no valid one is ready AND not persistently failed before ---
                _cache_creation_failed_flag_for_phase2 = current_chat_data.get("cache_creation_failed", False)
                if not cache_name_for_generation and not _cache_creation_failed_flag_for_phase2:
                    if not os.path.exists(chat_pdf_path):
                        st.error(f"PDF file not found for processing: {chat_pdf_path}")
                        raise FileNotFoundError(f"PDF file not found: {chat_pdf_path}")

                    st.toast(f"Processing and caching {pdf_basename_for_display} for Q&A. This may take a moment...", icon="⏳")
                    try:
                        uploaded_file_for_cache_ref = client.files.upload(file=chat_pdf_path)
                        new_cache = client.caches.create(
                            model=app_config.MODEL_TO_USE_FOR_API,
                            config=types.CreateCachedContentConfig(
                                display_name=f"{pdf_basename_for_display}_cache_{app_config.FIXED_MODEL_ID.replace('.', '_')}",
                                system_instruction=app_config.DETAILED_SYSTEM_INSTRUCTION,
                                contents=[uploaded_file_for_cache_ref],
                                ttl="3600s",
                            ),
                        )
                        cache_name_for_generation = new_cache.name
                        current_chat_data["gemini_cache_name"] = cache_name_for_generation
                        current_chat_data["gemini_cache_model"] = app_config.MODEL_TO_USE_FOR_API
                        current_chat_data["cache_creation_failed"] = False 
                        chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, current_chat_data)
                    except Exception as e_create:
                        use_fallback_for_this_run = True 
                        current_chat_data["cache_creation_failed"] = True 
                        current_chat_data["gemini_cache_name"] = None 
                        current_chat_data["gemini_cache_model"] = None
                        chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, current_chat_data)
    
                    finally:
                        if uploaded_file_for_cache_ref:
                            try: client.files.delete(name=uploaded_file_for_cache_ref.name)
                            except Exception: pass

                # --- Phase 3: Generate content ---
                should_use_fallback_definitively = use_fallback_for_this_run or \
                    (_cache_creation_failed_persistently and not cache_name_for_generation)
                
                if should_use_fallback_definitively:
                    if not os.path.exists(chat_pdf_path):
                        raise FileNotFoundError(f"PDF file not found for direct processing: {chat_pdf_path}")

                    uploaded_file_for_fallback = client.files.upload(
                        file=chat_pdf_path
                    )
                    contents_for_fallback = [
                        {"role": "user", "parts": [{"text": app_config.DETAILED_SYSTEM_INSTRUCTION}]}, 
                        uploaded_file_for_fallback,                                        
                    ]
                    contents_for_fallback.extend(gemini_api_formatted_conversation)
                    response = client.models.generate_content(
                        model=app_config.MODEL_TO_USE_FOR_API,
                        contents=contents_for_fallback, 
                        config=types.GenerateContentConfig(temperature=0.1)
                    )

                elif cache_name_for_generation:
                    response = client.models.generate_content(
                        model=app_config.MODEL_TO_USE_FOR_API,
                        contents=gemini_api_formatted_conversation, 
                        config=types.GenerateContentConfig(
                            cached_content=cache_name_for_generation, temperature=0.1
                        ),
                    )
                else: 
                    st.error("Unexpected state: No cache prepared and not explicitly falling back. Defaulting to error.")


                # --- Response Parsing --- 
                if response and response.candidates:
                    if response.candidates[0].content and response.candidates[0].content.parts:
                        answer_text = "".join(
                            part.text
                            for part in response.candidates[0].content.parts
                            if hasattr(part, "text")
                        )
                    elif response.candidates[0].finish_reason != types.Candidate.FinishReason.FINISH_REASON_UNSPECIFIED and \
                         response.candidates[0].finish_reason != types.Candidate.FinishReason.STOP :
                        try:
                            finish_reason_name = types.Candidate.FinishReason(response.candidates[0].finish_reason).name
                        except ValueError:
                            finish_reason_name = f"UNKNOWN_REASON_({response.candidates[0].finish_reason})"
                        answer_text = f"Could not generate content. Reason: {finish_reason_name}."
                        if response.candidates[0].safety_ratings:
                                answer_text += f" Safety Ratings: {response.candidates[0].safety_ratings}"
                elif response and response.prompt_feedback:
                    answer_text = f"Could not generate content. Prompt Feedback: {response.prompt_feedback}"

                elif response and response.prompt_feedback:
                    answer_text = f"Could not generate content. Prompt Feedback: {response.prompt_feedback}"

            except FileNotFoundError as e_fnf:
                answer_text = str(e_fnf)
            except Exception as e_outer:
                answer_text = "An unexpected error occurred"

            current_chat_messages.append({"role": "assistant", "content": answer_text})
            with st.chat_message("assistant"):
                st.markdown(answer_text)

            st.session_state.chats[chat_title]["messages"] = current_chat_messages
            chat_utils.save_chat(ACTIVE_PROFILE_KEY, chat_title, st.session_state.chats[chat_title])
            st.rerun()
