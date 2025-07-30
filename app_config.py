"""
App Configuration and Initialization
Handles app setup, caching, and session state management.
"""

import os
import streamlit as st
import uuid
from datetime import datetime
from dotenv import load_dotenv
import openai
from openai import OpenAI

# Import our modules
from modules.quiz_generator import QuizGenerator
from modules.vector_store import VectorStore
from modules.document_processor import DocumentProcessor
from modules.conversation_buffer import ConversationBuffer

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_resource
def get_instances():
    """Cache class instances to prevent reloading."""
    return {
        'quiz_generator': QuizGenerator(),
        'vector_store': VectorStore(),
        'document_processor': DocumentProcessor(),
        'conversation_buffer': ConversationBuffer()
    }

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "upload"
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    if 'processed_filename' not in st.session_state:
        st.session_state.processed_filename = ""

def get_app_instances():
    """Get cached app instances."""
    instances = get_instances()
    return {
        'quiz_generator': instances['quiz_generator'],
        'vector_store': instances['vector_store'],
        'document_processor': instances['document_processor'],
        'conversation_buffer': instances['conversation_buffer'],
        'openai_client': client
    }

def check_api_key():
    """Check if OpenAI API key is configured."""
    if client.api_key:
        return True
    else:
        return False 