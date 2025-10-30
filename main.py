import streamlit as st
import fitz  # PyMuPDF
import tempfile
import os
from bot import chat
import time

# Configure Streamlit page
st.set_page_config(
    page_title="PDF Reader",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: white;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
    }
    
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    .upload-section {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px dashed #ddd;
        text-align: center;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file using PyMuPDF"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_file_path = tmp_file.name

        # Extract text using PyMuPDF
        doc = fitz.open(tmp_file_path)
        full_text = ""
        total_pages = doc.page_count
        for page_num in range(total_pages):  # PyMuPDF uses 0-based indexing
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text.strip():
                full_text += f"Page {page_num + 1}:\n{page_text}\n\n"
        doc.close()

        # Clean up temporary file
        os.unlink(tmp_file_path)
        return full_text.strip()

    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📄 PDF Reader</h1>
        <p>Upload a PDF and chat with its content using AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.markdown("### 📁 Upload PDF")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF file to start chatting with its content"
        )
        
        if uploaded_file is not None:
            st.success("✅ PDF uploaded successfully!")
            st.markdown(f"**File:** {uploaded_file.name}")
            st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
            
            # Extract text and store in session state
            if 'pdf_text' not in st.session_state or st.session_state.get('current_file') != uploaded_file.name:
                with st.spinner("Extracting text from PDF..."):
                    pdf_text = extract_text_from_pdf(uploaded_file)
                    if pdf_text:
                        st.session_state.pdf_text = pdf_text
                        st.session_state.current_file = uploaded_file.name
                        st.session_state.chat_history = []
                        st.markdown('<p class="status-success">✅ Text extracted successfully!</p>', unsafe_allow_html=True)
                    else:
                        st.error("Failed to extract text from PDF")
        else:
            st.info("👆 Please upload a PDF file to get started")
    
    # Main content area
    if 'pdf_text' in st.session_state and st.session_state.pdf_text:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 💬 Chat with your PDF")
            
            # Chat input
            user_input = st.text_input(
                "Ask a question about the PDF content:",
                placeholder="e.g., What is the main topic of this document?",
                key="chat_input"
            )
            
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                send_button = st.button("Send", type="primary", use_container_width=True)
            
            # Clear chat button
            with col_btn2:
                if st.button("Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Process user input
            if send_button and user_input:
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": time.time()
                })
                
                # Generate AI response
                with st.spinner("AI is thinking..."):
                    try:
                        prompt = f"Act as an assistant and answer this question: {user_input} from the given data: {st.session_state.pdf_text}"
                        ai_response = chat(prompt)
                        
                        # Add AI response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": ai_response,
                            "timestamp": time.time()
                        })
                        
                    except Exception as e:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Sorry, I encountered an error: {str(e)}",
                            "timestamp": time.time()
                        })
                
                # Clear input
                st.rerun()
        
        with col2:
            st.markdown("### 📊 Document Info")
            st.markdown(f"**Current File:** {st.session_state.current_file}")
            
            # Show extracted text preview
            st.markdown("### 📝 Text Preview")
            text_preview = st.session_state.pdf_text[:500] + "..." if len(st.session_state.pdf_text) > 500 else st.session_state.pdf_text
            st.text_area("", value=text_preview, height=200, disabled=True)
        
        # Display chat history
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.markdown("### 💭 Conversation History")
            
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">👤 You: {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)
    
    else:
        # Welcome screen when no PDF is uploaded
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 3rem;">
                <h2>Welcome to PDF Reader! 🤖</h2>
                <p style="font-size: 1.2em; color: #666; margin: 2rem 0;">
                    Upload a PDF file using the sidebar to start chatting with its content.
                </p>
                <div style="background: #f0f2f6; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
                    <h3>Features:</h3>
                    <ul style="text-align: left; display: inline-block;">
                        <li>📄 Extract text from any PDF</li>
                        <li>💬 Ask questions about the content</li>
                        <li>🤖 Get AI-powered responses</li>
                        <li>📚 View conversation history</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()