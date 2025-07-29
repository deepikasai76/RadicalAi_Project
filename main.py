"""
Radical AI: Advanced Document Intelligence Platform

A comprehensive AI-powered platform for document processing, intelligent Q&A, 
and automated content generation with enterprise-grade capabilities.
"""

import os
import streamlit as st
from typing import List, Dict
import json
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Add OpenAI import and API setup
import openai
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Import our modules
from modules.quiz_generator import QuizGenerator
from modules.vector_store import VectorStore
from modules.document_processor import DocumentProcessor
from modules.hybrid_search import hybrid_search, initialize_hybrid_search
from modules.conversation_buffer import ConversationBuffer

# Cache the class instances to prevent reloading
@st.cache_resource
def get_instances():
    """Cache class instances to prevent reloading."""
    return {
        'quiz_generator': QuizGenerator(),
        'vector_store': VectorStore(),
        'document_processor': DocumentProcessor(),
        'conversation_buffer': ConversationBuffer()
    }

# Get cached instances
instances = get_instances()
quiz_generator = instances['quiz_generator']
vector_store = instances['vector_store']
document_processor = instances['document_processor']
conversation_buffer = instances['conversation_buffer']

# Initialize session state
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

# Check if API key is configured
if client.api_key:
    st.sidebar.success("✅ OpenAI API key configured")
else:
    st.sidebar.warning("⚠️ OpenAI API key not found - using fallback answers")

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # API Configuration
    st.markdown("### 🔑 API Configuration")
    openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
    
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        st.success("✅ API Key configured!")
    
    # Document Management in Sidebar
    doc_list = vector_store.list_documents()
    if doc_list:
        st.markdown("---")
        st.markdown("### 📚 Document Management")
        
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
    
    # System Status
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

# Check if there are existing documents
doc_list = vector_store.list_documents()

# Page Navigation Logic
if st.session_state.current_page == "upload":
    # Screen 1: Document Upload
    st.title("📚 Radical AI: Document Upload")
    st.header("📖 Document Upload & Processing")
    
    # Single file upload section
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
            with st.spinner("Processing PDF..."):
                # Save uploaded file temporarily
                import tempfile
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
    
    # Show existing documents section below upload interface (smaller text)
    if doc_list:
        st.markdown("---")
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
    
    # Delete Confirmation Popup (using st.container for popup effect)
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
    
    # Show navigation buttons after successful processing
    if st.session_state.document_processed:
        st.markdown("---")
        st.markdown("### 🎯 What would you like to do next?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❓ Ask Q&A", use_container_width=True):
                st.session_state.current_page = "qa"
                st.rerun()
        
        with col2:
            if st.button("📝 Generate Quiz", use_container_width=True):
                st.session_state.current_page = "quiz"
                st.rerun()
        
        with col3:
            if st.button("💬 Conversation History", use_container_width=True):
                st.session_state.current_page = "history"
                st.rerun()

elif st.session_state.current_page == "qa":
    # Q&A Screen
    st.title("❓ Q&A Interface")
    
    # Back to upload button
    if st.button("← Back to Upload"):
        st.session_state.current_page = "upload"
        st.rerun()
    
    # Select a document
    doc_list = vector_store.list_documents()
    if not doc_list:
        st.info("No documents indexed yet. Please upload and process a PDF first.")
        if st.button("Go to Upload"):
            st.session_state.current_page = "upload"
            st.rerun()
    else:
        selected_doc = st.selectbox("Select a document for Q&A:", doc_list)
        
        # Q&A Section
        st.subheader("Ask a Question")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            user_question = st.text_input("Type your question about the document:")
        with col2:
            use_hybrid = st.checkbox("Use Hybrid Search", value=True, help="Combines keyword and semantic search for better results")
        
        if st.button("Get Answer") and user_question:
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

elif st.session_state.current_page == "quiz":
    # Quiz Screen
    st.title("📝 Quiz Generation")
    
    # Back to upload button
    if st.button("← Back to Upload"):
        st.session_state.current_page = "upload"
        st.rerun()
    
    # Select a document
    doc_list = vector_store.list_documents()
    if not doc_list:
        st.info("No documents indexed yet. Please upload and process a PDF first.")
        if st.button("Go to Upload"):
            st.session_state.current_page = "upload"
            st.rerun()
    else:
        selected_doc = st.selectbox("Select a document for quiz:", doc_list)
        
        # Check if we have a quiz to display
        if 'quiz' in st.session_state and st.session_state.quiz:
            # Display the quiz
            quiz = st.session_state.quiz
            st.markdown("---")
            st.markdown(f"### 📝 Quiz: {len(quiz)} Questions")
            
            # Quiz instructions
            st.info("💡 Answer the questions below. You can review your answers before submitting.")
            
            # Initialize user answers if not exists
            if 'user_answers' not in st.session_state:
                st.session_state.user_answers = {}
            
            # Display questions and collect answers
            for i, q in enumerate(quiz, 1):
                st.markdown(f"**Question {i}:**")
                st.write(q['question'])
                
                # Different input methods based on question type
                if q.get('type') == 'multiple_choice' and 'options' in q:
                    # Multiple choice with radio buttons
                    options = q['options']
                    user_answer = st.radio(
                        f"Select your answer for Question {i}:",
                        options=list(options.keys()),
                        format_func=lambda x: f"{x}) {options[x]}",
                        key=f"q{i}_answer"
                    )
                    st.session_state.user_answers[f"q{i}"] = user_answer
                    
                elif q.get('type') == 'true_false':
                    # True/False with radio buttons
                    user_answer = st.radio(
                        f"Select your answer for Question {i}:",
                        options=["True", "False"],
                        key=f"q{i}_answer"
                    )
                    st.session_state.user_answers[f"q{i}"] = user_answer
                    
                else:
                    # Short answer with text input
                    user_answer = st.text_input(
                        f"Your answer for Question {i}:",
                        key=f"q{i}_answer",
                        placeholder="Type your answer here..."
                    )
                    st.session_state.user_answers[f"q{i}"] = user_answer
                
                st.markdown("---")
            
            # Submit and New Quiz buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Submit Quiz", use_container_width=True):
                    # Check if all questions are answered
                    all_answered = True
                    missing_questions = []
                    
                    for i in range(1, len(quiz) + 1):
                        answer = st.session_state.user_answers.get(f"q{i}", "")
                        if not answer or (isinstance(answer, str) and not answer.strip()):
                            all_answered = False
                            missing_questions.append(i)
                    
                    if all_answered:
                        st.session_state.quiz_submitted = True
                        st.rerun()
                    else:
                        st.error(f"⚠️ Please answer all questions. Missing: {', '.join(map(str, missing_questions))}")
            
            with col2:
                if st.button("🔄 New Quiz", use_container_width=True):
                    # Clear current quiz
                    if 'quiz' in st.session_state:
                        del st.session_state.quiz
                    if 'user_answers' in st.session_state:
                        del st.session_state.user_answers
                    if 'quiz_submitted' in st.session_state:
                        del st.session_state.quiz_submitted
                    st.rerun()
            
            # Show results after submission
            if st.session_state.get('quiz_submitted', False):
                st.markdown("---")
                st.subheader("📊 Quiz Results")
                
                correct_answers = 0
                total_questions = len(quiz)
                
                for i, q in enumerate(quiz, 1):
                    user_answer = st.session_state.user_answers.get(f"q{i}", "")
                    correct_answer = q['answer']
                    
                    # Check if answer is correct
                    is_correct = False
                    if q.get('type') == 'multiple_choice':
                        is_correct = user_answer == correct_answer
                    elif q.get('type') == 'true_false':
                        is_correct = user_answer.lower() == correct_answer.lower()
                    else:
                        # For short answer, do basic similarity check
                        is_correct = user_answer.lower().strip() in correct_answer.lower() or correct_answer.lower() in user_answer.lower()
                    
                    if is_correct:
                        correct_answers += 1
                    
                    # Display result for each question
                    with st.expander(f"Question {i} - {'✅ Correct' if is_correct else '❌ Incorrect'}"):
                        st.write(f"**Your Answer:** {user_answer}")
                        st.write(f"**Correct Answer:** {correct_answer}")
                        
                        # Show explanation if available
                        if 'explanation' in q:
                            st.success("💡 **Explanation:** " + q['explanation'])
                
                # Calculate and display score
                score_percentage = (correct_answers / total_questions) * 100
                
                st.markdown("---")
                st.markdown(f"### 🎯 Final Score: {correct_answers}/{total_questions} ({score_percentage:.1f}%)")
                
                # Performance feedback
                if score_percentage >= 90:
                    st.success("🌟 Excellent! You have a great understanding of the material!")
                elif score_percentage >= 80:
                    st.success("👍 Very Good! You understand most of the concepts well.")
                elif score_percentage >= 70:
                    st.info("📚 Good! You have a solid foundation, but there's room for improvement.")
                elif score_percentage >= 60:
                    st.warning("⚠️ Fair. Consider reviewing the material to strengthen your understanding.")
                else:
                    st.error("📖 Needs Improvement. We recommend reviewing the document content more thoroughly.")
        
        else:
            # Quiz Generation Section
            st.subheader("Generate Quiz")
            
            col1, col2 = st.columns(2)
            with col1:
                num_questions = st.slider("Number of questions", 1, 10, 5)
            with col2:
                difficulty = st.selectbox("Difficulty", ["mixed", "easy", "medium", "hard"])
            
            if st.button("🎲 Generate Quiz", use_container_width=True):
                with st.spinner("Generating quiz..."):
                    quiz = quiz_generator.generate_advanced_quiz(selected_doc, num_questions=num_questions, difficulty=difficulty)
                
                if quiz:
                    st.session_state.quiz = quiz
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success(f"✅ Generated {len(quiz)} questions!")
                    st.rerun()  # Refresh to show the quiz
                else:
                    st.warning("Could not generate quiz questions from this document.")

elif st.session_state.current_page == "history":
    # History Screen
    st.title("💬 Conversation History")
    
    # Back to upload button
    if st.button("← Back to Upload"):
        st.session_state.current_page = "upload"
        st.rerun()
    
    # Get current session ID (use a default if not set)
    session_id = st.session_state.get('session_id', 'default_session')
    
    # Show conversation history
    if session_id in conversation_buffer.conversations and conversation_buffer.conversations[session_id]:
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
        summary = conversation_buffer.get_conversation_summary(session_id)
        if summary['total_interactions'] > 0:
            st.markdown("---")
            st.markdown("### 📊 Conversation Summary")
            st.info(f"**Total Interactions:** {summary['total_interactions']}")
            if summary['documents_referenced']:
                st.info(f"**Documents Referenced:** {', '.join(summary['documents_referenced'])}")
        
        # Clear history button
        if st.button("🗑️ Clear Conversation History"):
            conversation_buffer.clear_conversation(session_id)
            st.success("✅ Conversation history cleared!")
            st.rerun()
    
    else:
        st.info("💬 No conversation history yet. Start asking questions in the Q&A section!")
        
        # Show available sessions if any
        all_sessions = conversation_buffer.get_all_sessions()
        if all_sessions:
            st.markdown("### 📚 Available Sessions")
            for session in all_sessions:
                st.info(f"Session: {session}")
