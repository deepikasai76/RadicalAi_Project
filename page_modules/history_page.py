"""
History Page Implementation
Function-based approach for the conversation history page.
"""

import streamlit as st
from ui_components import render_back_button

def render_history_page(conversation_buffer):
    """Render the conversation history page."""
    st.title("💬 Conversation History")
    
    # Back to upload button
    render_back_button()
    
    # Get current session ID (use a default if not set)
    session_id = st.session_state.get('session_id', 'default_session')
    
    # Show conversation history
    if session_id in conversation_buffer.conversations and conversation_buffer.conversations[session_id]:
        _render_conversation_history(conversation_buffer, session_id)
    else:
        _render_no_history(conversation_buffer)

def _render_conversation_history(conversation_buffer, session_id):
    """Render the conversation history for a session."""
    st.markdown("### 📝 Recent Conversations")
    
    for i, interaction in enumerate(conversation_buffer.conversations[session_id], 1):
        with st.expander(f"Conversation {i} - {interaction['timestamp'][:19]}"):
            st.markdown(f"**👤 You:** {interaction['user_message']}")
            st.markdown(f"**🤖 AI:** {interaction['ai_response']}")
            
            # Show metadata if available
            if interaction.get('metadata'):
                metadata = interaction['metadata']
                if 'document_name' in metadata:
                    st.info(f"📄 Document: {metadata['document_name']}")
    
    # Show conversation summary
    _render_conversation_summary(conversation_buffer, session_id)
    
    # Clear history button
    _render_clear_history_button(conversation_buffer, session_id)
    
    # Add navigation buttons
    st.markdown("---")
    st.markdown("### 🎯 What would you like to do next?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❓ Ask Questions", use_container_width=True, key="history_ask_questions"):
            st.session_state.current_page = "qa"
            st.rerun()
    
    with col2:
        if st.button("📝 Generate Quiz", use_container_width=True, key="history_generate_quiz"):
            st.session_state.current_page = "quiz"
            st.rerun()

def _render_conversation_summary(conversation_buffer, session_id):
    """Render the conversation summary."""
    summary = conversation_buffer.get_conversation_summary(session_id)
    if summary['total_interactions'] > 0:
        st.markdown("---")
        st.markdown("### 📊 Conversation Summary")
        st.info(f"**Total Interactions:** {summary['total_interactions']}")
        if summary['documents_referenced']:
            st.info(f"**Documents Referenced:** {', '.join(summary['documents_referenced'])}")

def _render_clear_history_button(conversation_buffer, session_id):
    """Render the clear history button."""
    if st.button("🗑️ Clear Conversation History", key="history_clear"):
        conversation_buffer.clear_conversation(session_id)
        st.success("✅ Conversation history cleared!")
        st.rerun()

def _render_no_history(conversation_buffer):
    """Render message when no conversation history exists."""
    st.info("💬 No conversation history yet. Start asking questions in the Q&A section!")
    
    # Show available sessions if any
    all_sessions = conversation_buffer.get_all_sessions()
    if all_sessions:
        st.markdown("### 📚 Available Sessions")
        for session in all_sessions:
            st.info(f"Session: {session}") 