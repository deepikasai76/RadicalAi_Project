"""
Upload Page Implementation
Class-based approach for the document upload page.
"""

import streamlit as st
import tempfile
import os
from ui_components import render_delete_popup

class UploadPage:
    """Handles the document upload page functionality."""
    
    def __init__(self, vector_store, document_processor):
        self.vector_store = vector_store
        self.document_processor = document_processor
    
    def render(self):
        """Render the upload page."""
        st.title("Advanced Document Intelligence Platform")
        st.header("Document Upload & Processing")
        
        # Render file upload section
        self._render_file_upload()
        
        # Render existing documents section
        self._render_existing_documents()
        
        # Render delete popup if needed
        render_delete_popup(self.vector_store)
        
        # Show success message after processing
        if st.session_state.document_processed:
            st.markdown("---")
            st.success("✅ Document processed successfully! You can now explore the document.")
            
            # Navigation buttons
            st.markdown("### 🎯 What would you like to do next?")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("❓ Ask Q&A", use_container_width=True, key="upload_go_to_qa"):
                    st.session_state.current_page = "qa"
                    st.rerun()
            
            with col2:
                if st.button("📝 Generate Quiz", use_container_width=True, key="upload_generate_quiz"):
                    st.session_state.current_page = "quiz"
                    st.rerun()
            
            with col3:
                if st.button("💬 View History", use_container_width=True, key="upload_view_history"):
                    st.session_state.current_page = "history"
                    st.rerun()
    
    def _render_file_upload(self):
        """Render the file upload section."""
        uploaded_file = st.file_uploader(
            "Choose a PDF file or drag and drop here",
            type=['pdf'],
            key="main_uploader",
            help="Upload a PDF file by browsing or dragging and dropping"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File selected: **{uploaded_file.name}**")
            st.info(f"📊 File size: {uploaded_file.size / 1024:.1f} KB")
            
            if st.button("🚀 Process Document", use_container_width=True, key="process_main"):
                self._process_uploaded_file(uploaded_file)
    
    def _process_uploaded_file(self, uploaded_file):
        """Process the uploaded PDF file."""
        with st.spinner("Processing PDF..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Process the uploaded PDF
            processed = self.document_processor.process_pdfs([tmp_path])
            
            success_count = 0
            for filename, chunks in processed.items():
                if not chunks or (isinstance(chunks[0], str) and chunks[0].startswith("ERROR:")):
                    st.error(f"Failed to process {filename}: {chunks[0] if chunks else 'No chunks extracted.'}")
                    continue
                
                st.success(f"✅ Extracted {len(chunks)} chunks from '{filename}'")
                
                # Add to vector store
                success = self.vector_store.add_document(filename, chunks, batch_size=32)
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
            os.unlink(tmp_path)
    
    def _render_existing_documents(self):
        """Render the existing documents section."""
        doc_list = self.vector_store.list_documents()
        
        if doc_list:
            st.markdown("#### 📚 Or use existing document:")
            
            # Create dropdown with existing documents
            dropdown_options = ["Select a document..."] + doc_list
            
            selected_option = st.selectbox(
                "Choose from previously uploaded documents:",
                options=dropdown_options,
                index=0
            )
            
            if selected_option in doc_list:
                # User selected an existing document
                st.success(f"✅ Selected: **{selected_option}**")
                st.session_state.processed_filename = selected_option
                st.session_state.document_processed = True 