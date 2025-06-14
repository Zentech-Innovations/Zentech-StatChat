import streamlit as st
import openai
import os
import time
import datetime
import json
# UPDATED: We only need to import your single, unified tool file
from app_modules import tool_declaration

ASSISTANT_NAME = "PDF_Q&A_Financial_Assistant"

def get_or_create_assistant(client, system_instruction, model_id):
    assistant_fingerprint = f"{ASSISTANT_NAME}_{model_id}"
    try:
        assistants = client.beta.assistants.list(limit=100)
        for assistant in assistants.data:
            if assistant.name == assistant_fingerprint:
                return assistant

        # Uses the ALL_OPENAI_TOOLS list from your tool_declaration.py
        all_tools = [{"type": "file_search"}] + tool_declaration.ALL_OPENAI_TOOLS
        
        assistant = client.beta.assistants.create(
            name=assistant_fingerprint,
            instructions=system_instruction,
            model=model_id,
            tools=all_tools,
        )
        return assistant
    except Exception as e:
        st.error(f"Error getting or creating OpenAI assistant: {e}")
        return None

def get_deepseek_response(api_key, model_id, system_instruction, pdf_path, user_query, thread_id=None, file_id=None):
    response_payload = {"response_text": "Error: Failed to get response from OpenAI.", "thread_id": thread_id, "file_id": file_id}
    
    try:
        client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        assistant = get_or_create_assistant(client, system_instruction, model_id)
        if not assistant:
            return {"response_text": "Failed to initialize OpenAI Assistant."}

        # ... (File upload and wait logic is unchanged) ...
        if not file_id:
            with open(pdf_path, "rb") as file_data:
                file_object = client.files.create(file=file_data, purpose="assistants")
            file_id = file_object.id
            with st.spinner("Preparing document..."):
                start_time = time.time()
                while True:
                    if time.time() - start_time > 60: return {"response_text": "File processing timed out."}
                    file_status = client.files.retrieve(file_id=file_id)
                    if file_status.status == 'processed': break
                    elif file_status.status == 'failed': return {"response_text": "File processing failed."}
                    time.sleep(2)
        
        response_payload["file_id"] = file_id

        if not thread_id:
            thread = client.beta.threads.create(); thread_id = thread.id
        response_payload["thread_id"] = thread_id

        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_query,
            attachments=[{"file_id": file_id, "tools": [{"type": "file_search"}]}]
        )
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                tool_outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # UPDATED: Checks against the TOOL_IMPLEMENTATIONS from your file
                    if tool_name in tool_declaration.TOOL_IMPLEMENTATIONS:
                        implementation = tool_declaration.TOOL_IMPLEMENTATIONS[tool_name]
                        output = implementation(**tool_args)
                        tool_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
                )
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            response_payload["response_text"] = messages.data[0].content[0].text.value
        else:
            response_payload["response_text"] = f"Run failed with status: {run.status}."
        
        return response_payload

    except Exception as e:
        response_payload["response_text"] = f"An unexpected error occurred: {str(e)}"
        return response_payload