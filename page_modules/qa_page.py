"""
Q&A Page Implementation
Function-based approach for the Q&A page.
"""

import streamlit as st
from datetime import datetime
from ui_components import render_back_button

# Render the Q&A page
def render_qa_page(vector_store, quiz_generator, conversation_buffer):
    """Render the Q&A page."""
    st.title("❓ Q&A Interface")
    
    # Navigation buttons row
    col1, col2, col3 = st.columns(3)
    
    # Back button
    with col1:
        render_back_button()
    # Generate Quiz button
    with col2:
        if st.button("📝 Generate Quiz", use_container_width=True, key="qa_generate_quiz"):
            st.session_state.current_page = "quiz"
            st.rerun()
    # View History button
    with col3:
        if st.button("💬 View History", use_container_width=True, key="qa_view_history"):
            st.session_state.current_page = "history"
            st.rerun()
    
    # Select a document
    doc_list = vector_store.list_documents()
    if not doc_list:
        st.info("No documents indexed yet. Please upload and process a PDF first.")
        if st.button("Go to Upload", key="qa_go_to_upload"):
            st.session_state.current_page = "upload"
            st.rerun()
    else:
        selected_doc = st.selectbox("Select a document for Q&A:", doc_list)
        
        # Q&A Section
        st.subheader("Ask a Question")
        # Q&A Section
        col1, col2 = st.columns([3, 1])
        with col1:
            user_question = st.text_input("Type your question about the document:")
        with col2:
            use_hybrid = st.checkbox("Use Hybrid Search", value=True, help="Combines keyword and semantic search for better results")
        
        if st.button("Get Answer", key="qa_get_answer") and user_question:
            _process_question(user_question, selected_doc, use_hybrid, quiz_generator, conversation_buffer)

# Process a user question and generate an answer
def _process_question(user_question, selected_doc, use_hybrid, quiz_generator, conversation_buffer):
    """Process a user question and generate an answer."""
    with st.spinner("Searching with hybrid search..." if use_hybrid else "Searching..."):
        # Get conversation context for better responses
        conversation_context = conversation_buffer.get_conversation_context(
            st.session_state.session_id, 
            include_context=True, 
            max_interactions=3
        )
        
        # Add conversation context to the question if available
        enhanced_question = user_question
        if conversation_context:
            enhanced_question = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_question}"
        
        # Generate an answer using the quiz generator
        answer = quiz_generator.answer_question(enhanced_question, filename=selected_doc, use_hybrid=use_hybrid)
        
        # Store the interaction in conversation buffer
        conversation_buffer.add_interaction(
            session_id=st.session_state.session_id,
            user_message=user_question,
            ai_response=answer,
            context_chunks=[],
            metadata={
                "document_name": selected_doc,
                "use_hybrid_search": use_hybrid,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        st.success("Answer:")
        st.write(answer) 