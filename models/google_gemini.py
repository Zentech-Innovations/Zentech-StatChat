#  models/gemini_interactions.py
import streamlit as st
import os
import json
from google import genai
from google.genai import types
from app_modules import app_config, tool_declaration

def generate_gemini_response(
    client: genai.Client,
    current_chat_messages: list,
    user_query: str,
    current_chat_data: dict,
    chat_pdf_path: str,
    system_instruction_str: str,
    gemini_tool_config: types.Tool
):
    api_conversation_history = []
    uploaded_file_for_api_content = None

    _stored_cache_name_from_session = current_chat_data.get("gemini_cache_name")
    _stored_cache_model_from_session = current_chat_data.get("gemini_cache_model")
    _cache_creation_failed_persistently = current_chat_data.get("cache_creation_failed", False)

    cache_name_for_generation = None

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
        except Exception:
            current_chat_data["gemini_cache_name"] = None
            current_chat_data["gemini_cache_model"] = None
            current_chat_data["cache_creation_failed"] = False

    should_use_fallback_definitively = (_cache_creation_failed_persistently and not cache_name_for_generation) or \
                                       (not cache_name_for_generation and current_chat_data.get("cache_creation_failed", False) and not _stored_cache_name_from_session)

    if should_use_fallback_definitively:
        if not os.path.exists(chat_pdf_path):
            st.error(f"PDF file not found for direct processing: {chat_pdf_path}")
            return "Error: PDF file for chat not found.", current_chat_data

        uploaded_file_for_api_content = client.files.upload(file=chat_pdf_path)
        api_conversation_history = [
            types.Content(role="user", parts=[types.Part(text=system_instruction_str)]),
            uploaded_file_for_api_content
        ]
        for msg in current_chat_messages[:-1]:
            role_for_api = "model" if msg["role"] == "assistant" else msg["role"]
            if not (msg["role"] == "user" and msg["content"] == system_instruction_str):
                api_conversation_history.append(types.Content(role=role_for_api, parts=[types.Part(text=msg["content"])]))
        api_conversation_history.append(types.Content(role="user", parts=[types.Part(text=user_query)]))

    else:
        if not cache_name_for_generation:
            api_conversation_history.append(types.Content(role="user", parts=[types.Part(text=system_instruction_str)]))

        for msg in current_chat_messages:
            role_for_api = "model" if msg["role"] == "assistant" else msg["role"]
            is_first_system_instruction = (
                len(api_conversation_history) == 1 and
                api_conversation_history[0].role == "user" and
                api_conversation_history[0].parts[0].text == system_instruction_str
            )
            if msg["role"] == "user" and msg["content"] == system_instruction_str and is_first_system_instruction:
                continue
            api_conversation_history.append(types.Content(role=role_for_api, parts=[types.Part(text=msg["content"])]))

    # --- Actual API Call Logic ---
    answer_text = "Error: Could not retrieve a valid response from the model."
    use_fallback_for_this_run = False
    uploaded_file_for_cache_ref = None

    try:
        MAX_FUNCTION_CALLS = 5
        num_function_calls = 0

        while num_function_calls < MAX_FUNCTION_CALLS:
            if not cache_name_for_generation and not should_use_fallback_definitively and not use_fallback_for_this_run:
                if not current_chat_data.get("cache_creation_failed", False):
                    if not os.path.exists(chat_pdf_path):
                        st.error(f"PDF file not found for cache processing: {chat_pdf_path}")
                        use_fallback_for_this_run = True
                        current_chat_data["cache_creation_failed"] = True
                    else:
                        st.toast(f"Processing and caching {os.path.basename(chat_pdf_path)} for Q&A. This may take a moment...", icon="⏳")
                        uploaded_file_for_cache_ref = None
                        try:
                            uploaded_file_for_cache_ref = client.files.upload(file=chat_pdf_path)
                            create_cache_config = types.CreateCachedContentConfig(
                                display_name=f"{os.path.basename(chat_pdf_path)}_cache_{app_config.FIXED_MODEL_ID.replace('.', '_')}",
                                system_instruction=system_instruction_str,
                                contents=[uploaded_file_for_cache_ref],
                                tools=[gemini_tool_config],
                                ttl="3600s",
                            )
                            new_cache = client.caches.create(
                                model=app_config.MODEL_TO_USE_FOR_API,
                                config=create_cache_config
                            )
                            cache_name_for_generation = new_cache.name
                            current_chat_data["gemini_cache_name"] = cache_name_for_generation
                            current_chat_data["gemini_cache_model"] = app_config.MODEL_TO_USE_FOR_API
                            current_chat_data["cache_creation_failed"] = False


                            temp_history_for_new_cache = []
                            for msg_hist in current_chat_messages:
                                role_hist = "model" if msg_hist["role"] == "assistant" else msg_hist["role"]
                                if not (msg_hist["role"] == "user" and msg_hist["content"] == system_instruction_str):
                                    temp_history_for_new_cache.append(types.Content(role=role_hist, parts=[types.Part(text=msg_hist["content"])]))
                            api_conversation_history = temp_history_for_new_cache

                        except Exception as e_create:
                            use_fallback_for_this_run = True
                            current_chat_data["cache_creation_failed"] = True
                            current_chat_data["gemini_cache_name"] = None
                            current_chat_data["gemini_cache_model"] = None
                        finally:
                            if uploaded_file_for_cache_ref:
                                try: client.files.delete(name=uploaded_file_for_cache_ref.name)
                                except Exception: pass
                else:
                    use_fallback_for_this_run = True

            if should_use_fallback_definitively or use_fallback_for_this_run:
                if not uploaded_file_for_api_content:
                    if not os.path.exists(chat_pdf_path):
                        st.error(f"PDF file not found for fallback processing: {chat_pdf_path}")
                        return f"Error: PDF file not found for fallback processing: {chat_pdf_path}", current_chat_data
                    uploaded_file_for_api_content = client.files.upload(file=chat_pdf_path)

                temp_history_for_fallback = [
                    types.Content(role="user", parts=[types.Part(text=system_instruction_str)]),
                    uploaded_file_for_api_content
                ]
                for msg_hist in current_chat_messages[:-1]:
                    role_hist = "model" if msg_hist["role"] == "assistant" else msg_hist["role"]
                    if not (msg_hist["role"] == "user" and msg_hist["content"] == system_instruction_str):
                        temp_history_for_fallback.append(types.Content(role=role_hist, parts=[types.Part(text=msg_hist["content"])]))
                temp_history_for_fallback.append(types.Content(role="user", parts=[types.Part(text=user_query)]))
                api_conversation_history = temp_history_for_fallback


            gen_config_args = {"temperature": 0.1}
            final_fallback_for_this_api_call = should_use_fallback_definitively or use_fallback_for_this_run

            if cache_name_for_generation and not final_fallback_for_this_api_call:
                gen_config_args["cached_content"] = cache_name_for_generation
            else:
                gen_config_args["tools"] = [gemini_tool_config]

            effective_gen_config = types.GenerateContentConfig(**gen_config_args)

            if not api_conversation_history:
                answer_text = "Error: Internal problem, API conversation history is empty."
                break

            response = client.models.generate_content(
                model=app_config.MODEL_TO_USE_FOR_API,
                contents=api_conversation_history,
                config=effective_gen_config
            )

            if not response.candidates:
                answer_text = "No response candidates from model."
                if response.prompt_feedback:
                    answer_text += f" Prompt Feedback: {response.prompt_feedback}"
                break

            candidate = response.candidates[0]

            if candidate.content and candidate.content.parts:
                api_conversation_history.append(candidate.content)

            function_call_to_execute = None
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call and part.function_call.name:
                        function_call_to_execute = part.function_call
                        break

            if function_call_to_execute:
                fc_name = function_call_to_execute.name
                fc_args_struct = function_call_to_execute.args

                if fc_name in tool_declaration.TOOL_IMPLEMENTATIONS:
                    tool_function = tool_declaration.TOOL_IMPLEMENTATIONS[fc_name]
                    args_dict = {key: value for key, value in fc_args_struct.items()}
                    try:
                        tool_output_json_str = tool_function(**args_dict)
                        tool_response_payload = {"content": tool_output_json_str}
                    except Exception as e_tool_exec:
                        tool_response_payload = {"content": json.dumps({"error": f"Failed to execute tool {fc_name}: {str(e_tool_exec)}"})}

                    api_conversation_history.append(
                        types.Content(
                            parts=[types.Part(
                                function_response=types.FunctionResponse(
                                    name=fc_name,
                                    response=tool_response_payload
                                )
                            )],
                            role="function"
                        )
                    )
                    num_function_calls += 1
                else:
                    answer_text = f"Error: The model tried to use an unavailable tool: {fc_name}."
                    break
            else:
                if candidate.content and candidate.content.parts:
                    answer_text = "".join(part.text for part in candidate.content.parts if hasattr(part, "text"))
                elif candidate.finish_reason not in [types.Candidate.FinishReason.STOP, types.Candidate.FinishReason.FINISH_REASON_UNSPECIFIED, types.Candidate.FinishReason.MAX_TOKENS]:
                    try: finish_reason_name = types.Candidate.FinishReason(candidate.finish_reason).name
                    except ValueError: finish_reason_name = f"UNKNOWN_REASON_({candidate.finish_reason})"
                    answer_text = f"Could not generate content. Reason: {finish_reason_name}."
                    if candidate.safety_ratings:
                        answer_text += f" Safety Ratings: {candidate.safety_ratings}"
                elif response.prompt_feedback:
                    answer_text = f"Could not generate content. Prompt Feedback: {response.prompt_feedback}"
                else:
                    answer_text = "Received an empty response or response with no text parts from the model."
                break

        if num_function_calls >= MAX_FUNCTION_CALLS:
            answer_text = "Exceeded maximum function call attempts. Please try rephrasing."

    except FileNotFoundError as e_fnf:
        answer_text = str(e_fnf)
    except Exception as e_outer:
        answer_text = f"An unexpected error occurred: {str(e_outer)}"
        st.exception(e_outer)

    if uploaded_file_for_api_content:
        try:
            client.files.delete(name=uploaded_file_for_api_content.name)
        except Exception:
            pass

    return answer_text, current_chat_data