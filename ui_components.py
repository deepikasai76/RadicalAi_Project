"""
UI Components
Handles sidebar, navigation, and common UI elements.
"""

import os
import streamlit as st
import tempfile

# Render the sidebar with configuration and document management
# Sidebar is a container that contains the configuration and document management
def render_sidebar(vector_store, conversation_buffer):
    """Render the sidebar with configuration and document management."""
    with st.sidebar:
        # ⚙️ Configuration
        st.markdown("## ⚙️ Configuration")
        
        # 🔑 AI Provider Configuration
        st.markdown("### 🤖 AI Provider Configuration")
        
        # AI Provider Selection
        from modules.ai_provider import AIProviderManager
        ai_manager = AIProviderManager()
        available_providers = ai_manager.get_available_providers()
        
        # If there are available providers, show the provider selection dropdown
        if available_providers:
            selected_provider = st.selectbox(
                "Choose AI Provider:",
                available_providers,
                index=0,
                help="Select which AI service to use for Q&A and quiz generation"
            )
            
            # Show model selection for Ollama
            if selected_provider == "ollama" and "ollama" in ai_manager.providers:
                ollama_provider = ai_manager.providers["ollama"]
                available_models = ollama_provider.get_available_models()
                
                if available_models:
                    st.info(f"📦 Available models: {', '.join(available_models)}")
                    
                    # Model selection
                    selected_model = st.selectbox(
                        "Choose Ollama Model:",
                        available_models,
                        index=0,
                        help="Select which model to use for AI responses"
                    )
                    
                    # Update model if different
                    if selected_model != ollama_provider.model_name:
                        if st.button("Switch Model", key="switch_model"):
                            ollama_provider.model_name = selected_model
                            st.success(f"✅ Switched to model: {selected_model}")
                            st.rerun()
                else:
                    st.warning("⚠️ No models available. Run: ollama pull llama2:7b")
            
            if st.button("Switch Provider", key="switch_provider"):
                if ai_manager.set_provider(selected_provider):
                    st.success(f"✅ Switched to {selected_provider}")
                    st.rerun()
            
            # Show current provider status
            current_provider = ai_manager.get_current_provider()
            if current_provider:
                st.info(f"🔄 Current: {ai_manager.current_provider}")
                
                # Test provider
                if st.button("Test Provider", key="test_provider"):
                    with st.spinner("Testing provider..."):
                        test_result = ai_manager.test_provider(selected_provider)
                        if test_result.get("status") == "success":
                            st.success("✅ Provider working!")
                            st.write(f"Test answer: {test_result.get('test_answer', '')[:100]}...")
                        else:
                            st.error(f"❌ Provider test failed: {test_result.get('error', 'Unknown error')}")
        else:
            st.warning("⚠️ No AI providers available")
        
        # OpenAI API Key (for fallback)
        st.markdown("#### 🔑 OpenAI API Key (Optional)")
        openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key for fallback")
        
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            st.success("✅ OpenAI API Key configured!")
        
        # 📚 Document Management
        st.markdown("---")
        st.markdown("### 📚 Document Management")
        
        doc_list = vector_store.list_documents()
        if doc_list:
            # Document selection dropdown
            selected_doc_for_management = st.selectbox(
                "Select document to manage:",
                options=["Choose a document..."] + doc_list,
                key="management_dropdown"
            )
            
            if selected_doc_for_management != "Choose a document...":
                # Show document info
                doc_chunks = vector_store.get_document_chunks(selected_doc_for_management)
                if doc_chunks:
                    st.info(f"📄 **Document:** {selected_doc_for_management}")
                    st.info(f"📝 **Chunks:** {len(doc_chunks)} text segments")
                
                # Delete button with popup confirmation
                if st.button("🗑️ Delete Document", key="sidebar_delete"):
                    st.session_state.show_delete_popup = True
                    st.session_state.doc_to_delete = selected_doc_for_management
                    st.rerun()
        else:
            st.info("No documents uploaded yet.")
        
        # 📊 System Status
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        # Document count
        doc_count = len(vector_store.list_documents())
        st.metric("📚 Documents", doc_count)
        
        # Total chunks
        total_chunks = 0
        for doc in vector_store.list_documents():
            chunks = vector_store.get_document_chunks(doc)
            total_chunks += len(chunks) if chunks else 0
        
        st.metric("📝 Total Chunks", total_chunks)
        
        # Vector store status
        try:
            collection_stats = vector_store.collection.count()
            st.metric("🔍 Vector Store", f"{collection_stats} entries")
        except:
            st.metric("🔍 Vector Store", "Ready")

# Render the delete confirmation popup
def render_delete_popup(vector_store):
    """Render the delete confirmation popup."""
    if st.session_state.get('show_delete_popup'):
        # Create a popup-like container
        with st.container():
            st.markdown("---")
            
            # Popup header
            st.markdown("""
            <div style="
                background-color: #ff6b6b; 
                color: white; 
                padding: 1rem; 
                border-radius: 10px; 
                margin: 1rem 0;
                text-align: center;
            ">
                <h3>⚠️ Confirm Document Deletion</h3>
            </div>
            """, unsafe_allow_html=True)
            
            doc_to_delete = st.session_state.doc_to_delete
            
            st.warning(f"**Document to delete:** {doc_to_delete}")
            st.error("⚠️ **WARNING:** This action cannot be undone. The document and all its data will be permanently removed from the database.")
            
            # Confirmation buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                pass  # Empty column for spacing
            
            with col2:
                if st.button("✅ Yes, Delete", use_container_width=True, key="confirm_delete"):
                    with st.spinner("Deleting document..."):
                        success = vector_store.delete_document(doc_to_delete)
                        if success:
                            st.success(f"✅ **{doc_to_delete}** has been deleted successfully!")
                            # Clear the popup state
                            del st.session_state.show_delete_popup
                            del st.session_state.doc_to_delete
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to delete **{doc_to_delete}**")
            
            with col3:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_delete"):
                    del st.session_state.show_delete_popup
                    del st.session_state.doc_to_delete
                    st.rerun()

# Render navigation buttons after document processing
def render_navigation_buttons():
    """Render navigation buttons after document processing."""
    if st.session_state.document_processed:
        st.markdown("---")
        st.markdown("### 🎯 What would you like to do next?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❓ Ask Q&A", use_container_width=True, key="nav_qa"):
                st.session_state.current_page = "qa"
                st.rerun()
        
        with col2:
            if st.button("📝 Generate Quiz", use_container_width=True, key="nav_quiz"):
                st.session_state.current_page = "quiz"
                st.rerun()
        
        with col3:
            if st.button("💬 Conversation History", use_container_width=True, key="nav_history"):
                st.session_state.current_page = "history"
                st.rerun()

def render_back_button():
    """Render back to upload button."""
    if st.button("← Back to Upload", key="back_to_upload"):
        st.session_state.current_page = "upload"
        st.rerun()

def process_uploaded_file(uploaded_file, document_processor, vector_store):
    """Process an uploaded PDF file."""
    if uploaded_file is not None:
        st.success(f"✅ File selected: **{uploaded_file.name}**")
        st.info(f"📊 File size: {uploaded_file.size / 1024:.1f} KB")
        
        if st.button("🚀 Process Document", use_container_width=True, key="process_main"):
            with st.spinner("Processing PDF..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Process the uploaded PDF
                processed = document_processor.process_pdfs([tmp_path])
                
                success_count = 0
                for filename, chunks in processed.items():
                    if not chunks or (isinstance(chunks[0], str) and chunks[0].startswith("ERROR:")):
                        st.error(f"Failed to process {filename}: {chunks[0] if chunks else 'No chunks extracted.'}")
                        continue
                    
                    st.success(f"✅ Extracted {len(chunks)} chunks from '{filename}'")
                    
                    # Add to vector store
                    success = vector_store.add_document(filename, chunks, batch_size=32)
                    if success:
                        success_count += 1
                        st.session_state.processed_filename = filename
                        st.session_state.document_processed = True
                
                if success_count > 0:
                    st.success("✅ Document processed successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to process document")
                
                # Clean up temporary file
                import os
                os.unlink(tmp_path) 