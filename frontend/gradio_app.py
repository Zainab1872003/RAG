import gradio as gr
import requests
import json
import os
# Change this line to use environment variable
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def upload_file_gr(file):
    """Upload file to FastAPI backend."""
    if file is None:
        return "No file selected"
    
    try:
        if isinstance(file, str):
            file_path = file
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                files = {"file": (file_name, f)}
                response = requests.post(f"{API_URL}/api/v1/upload/", files=files)
        else:
            return "Error: Unsupported file object type"
        
        if response.status_code == 200:
            return response.json()["message"]
        else:
            error_detail = response.json().get("detail", response.text)
            return f"Error: {error_detail}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def get_files_list():
    """Fetch and format the list of files from backend."""
    try:
        response = requests.get(f"{API_URL}/api/v1/files/")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get("files", [])
            
            if not files:
                return "No files found in the system."
            
            file_list = f"📁 **Total Files: {len(files)}**\n\n"
            
            for filename in files:
                file_extension = os.path.splitext(filename)[1].upper()
                file_list += f"📄 **{filename}** ({file_extension})\n"
            
            return file_list
        else:
            return f"Error fetching files: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to API server. Make sure it's running on port 8000."
    except Exception as e:
        return f"Error: {str(e)}"

def get_files_dropdown():
    """Get files list for dropdown selection."""
    try:
        response = requests.get(f"{API_URL}/api/v1/files/")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get("files", [])
            return files if files else ["No files available"]
        else:
            return ["Error fetching files"]
            
    except Exception as e:
        return ["Error connecting to server"]

def delete_file_gr(filename):
    """Delete a file from the backend."""
    if not filename or filename == "No files available":
        return "❌ Please select a valid file to delete", get_files_list(), get_files_dropdown()
    
    try:
        response = requests.delete(f"{API_URL}/api/v1/files/{filename}")
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("message", f"File {filename} deleted successfully")
            return f"✅ {message}", get_files_list(), get_files_dropdown()
        else:
            error_detail = response.json().get("detail", response.text)
            return f"❌ Error deleting file: {error_detail}", get_files_list(), get_files_dropdown()
            
    except Exception as e:
        return f"❌ Error: {str(e)}", get_files_list(), get_files_dropdown()

def chat_with_documents(message, history, top_k):
    """Chat with your documents using the query endpoint."""
    if not message.strip():
        return history, ""

    try:
        # Prepare request payload
        payload = {
            "question": message,
            "top_k": int(top_k)
        }

        # Send request to query endpoint
        response = requests.post(f"{API_URL}/api/v1/query/", json=payload)

        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "No answer received")
            references = result.get("references", [])

            # Format response with references
            formatted_response = f"**Answer:**\n{answer}\n\n"

            if references:
                formatted_response += "**📚 References:**\n"
                for i, ref in enumerate(references, 1):
                    source = ref.get("source", "Unknown")
                    score = ref.get("score", 0.0)

                    # Build location string from metadata
                    loc_parts = []
                    if ref.get("page") is not None:
                        loc_parts.append(f"Page {ref['page']}")
                    if ref.get("slide") is not None:
                        loc_parts.append(f"Slide {ref['slide']}")
                    if ref.get("sheet"):
                        if ref.get("start_row") and ref.get("end_row"):
                            loc_parts.append(
                                f"Sheet {ref['sheet']} (Rows {ref['start_row']}-{ref['end_row']})"
                            )
                        else:
                            loc_parts.append(f"Sheet {ref['sheet']}")

                    location = " | ".join(loc_parts) if loc_parts else "Location N/A"
                    preview = ref.get("text", "")[:150] + "…"

                    formatted_response += (
                        f"\n**{i}.** 📄 {source} — {location} — "
                        f"Score: {score:.3f}\n"
                        f"*Preview:* {preview}\n"
                    )

            # Add to chat history
            history.append([message, formatted_response])

        elif response.status_code == 404:
            error_msg = "❌ No relevant documents found for your question. Please upload some documents first."
            history.append([message, error_msg])

        else:
            error_detail = response.json().get("detail", response.text)
            error_msg = f"❌ Error: {error_detail}"
            history.append([message, error_msg])

    except requests.exceptions.ConnectionError:
        error_msg = "❌ Error: Cannot connect to API server. Please make sure it's running on port 8000."
        history.append([message, error_msg])
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append([message, error_msg])

    return history, ""

def refresh_all():
    """Refresh files display and dropdown."""
    files_display = get_files_list()
    files_dropdown = get_files_dropdown()
    return files_display, gr.Dropdown(choices=files_dropdown, value=None)

# Custom CSS for better styling
css = """
.chat-container {
    height: 500px;
}
.reference-box {
    background-color: #f8f9fa;
    border-left: 4px solid #007bff;
    padding: 10px;
    margin: 5px 0;
}
"""

# Main Gradio Interface
def create_gradio_app():
    with gr.Blocks(title="📄 Document RAG Chat System", css=css) as demo:
        gr.Markdown("# 📄 Document RAG Chat System")
        gr.Markdown("Upload documents, manage your knowledge base, and chat with your documents using AI!")
        
        with gr.Tab("💬 Chat with Documents"):
            gr.Markdown("### Ask questions about your uploaded documents")
            
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        label="Chat History",
                        height=500,
                        elem_classes="chat-container"
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Question",
                            placeholder="Ask something about your documents...",
                            scale=4
                        )
                        submit_btn = gr.Button("📤 Send", variant="primary", scale=1)
                        
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                    
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ Settings")
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Number of references (top_k)"
                    )
                    
                    gr.Markdown("### 📊 Quick Stats")
                    files_count = gr.Markdown(get_files_list())
                    refresh_chat_btn = gr.Button("🔄 Refresh Files", variant="secondary")
            
            # Chat event handlers
            submit_btn.click(
                chat_with_documents,
                inputs=[msg, chatbot, top_k_slider],
                outputs=[chatbot, msg]
            )
            
            msg.submit(
                chat_with_documents,
                inputs=[msg, chatbot, top_k_slider],
                outputs=[chatbot, msg]
            )
            
            clear_btn.click(lambda: [], outputs=chatbot)
            refresh_chat_btn.click(get_files_list, outputs=files_count)
        
        with gr.Tab("📤 Upload Documents"):
            gr.Markdown("### Upload and process documents for RAG")
            
            upload_file = gr.File(
                label="Upload DOCX/DOC/PDF/Excel/PowerPoint", 
                file_types=[".pdf", ".doc", ".docx", '.xlsx', '.xls', '.pptx', '.ppt']
            )
            upload_btn = gr.Button("🚀 Upload & Embed", variant="primary")
            upload_output = gr.Textbox(label="Upload Status", lines=3)
            
            upload_btn.click(upload_file_gr, inputs=upload_file, outputs=upload_output)
        
        with gr.Tab("📁 Manage Files"):
            gr.Markdown("### View and manage uploaded documents")
            
            refresh_btn = gr.Button("🔄 Refresh Files", variant="secondary")
            
            files_display = gr.Markdown(
                value=get_files_list(),
                label="Files in System"
            )
            
            gr.Markdown("---")
            gr.Markdown("### 🗑️ Delete File")
            gr.Markdown("*Note: This will delete the file and remove all its vectors from the index*")
            
            with gr.Row():
                with gr.Column(scale=3):
                    file_dropdown = gr.Dropdown(
                        choices=get_files_dropdown(),
                        label="Select file to delete",
                        value=None,
                        interactive=True
                    )
                with gr.Column(scale=1):
                    delete_btn = gr.Button("🗑️ Delete File", variant="stop")
            
            delete_output = gr.Textbox(label="Delete Status", lines=2)
            
            # Event handlers for file management
            refresh_btn.click(
                refresh_all,
                outputs=[files_display, file_dropdown]
            )
            
            delete_btn.click(
                delete_file_gr,
                inputs=file_dropdown,
                outputs=[delete_output, files_display, file_dropdown]
            )

    return demo

if __name__ == "__main__":
    demo = create_gradio_app()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)