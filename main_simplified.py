"""
Radical AI: Simplified Main Application

This version demonstrates both class-based and function-based approaches
for organizing the Streamlit application code.
"""

import streamlit as st

# Load custom CSS
def load_css():
    with open('static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Import configuration and initialization
from app_config import initialize_session_state, get_app_instances, check_api_key

# Import UI components
from ui_components import render_sidebar

# Import pages (both class-based and function-based)
from page_modules.upload_page import UploadPage
from page_modules.qa_page import render_qa_page
from page_modules.quiz_page import QuizPage
from page_modules.history_page import render_history_page

# Main application function
def main():
    """Main application function."""
    # Load custom CSS
    load_css()
    
    # Initialize app
    initialize_session_state()
    instances = get_app_instances()
    
    # Check API key
    check_api_key()
    
    # Render sidebar
    render_sidebar(instances['vector_store'], instances['conversation_buffer'])
    
    # Page routing
    current_page = st.session_state.current_page
    
    # Upload Page
    if current_page == "upload":
        # Class-based approach
        upload_page = UploadPage(instances['vector_store'], instances['document_processor'])
        upload_page.render()
        
    elif current_page == "qa":
        # Function-based approach
        render_qa_page(
            instances['vector_store'], 
            instances['quiz_generator'], 
            instances['conversation_buffer']
        )
        
    elif current_page == "quiz":
        # Class-based approach
        quiz_page = QuizPage(instances['vector_store'], instances['quiz_generator'])
        quiz_page.render()
        
    elif current_page == "history":
        # Function-based approach
        render_history_page(instances['conversation_buffer'])

# Run the main application
if __name__ == "__main__":
    main() 