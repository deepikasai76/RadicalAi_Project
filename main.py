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
    st.session_state.current_page = "Dashboard"

# Check if API key is configured
if client.api_key:
    st.sidebar.success("✅ OpenAI API key configured")
else:
    st.sidebar.warning("⚠️ OpenAI API key not found - using fallback answers")

# Streamlit UI
st.title("📚 Radical AI: PDF Quiz & Q&A")

st.header("📖 Document Upload & Processing")

# File upload section
uploaded_file = st.file_uploader("Upload a PDF document", type=['pdf'])

if uploaded_file is not None:
    # Save uploaded file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    if st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            # Process the uploaded PDF
            processed = document_processor.process_pdfs([tmp_path])
            
            for filename, chunks in processed.items():
                if not chunks or (isinstance(chunks[0], str) and chunks[0].startswith("ERROR:")):
                    st.error(f"Failed to process {filename}: {chunks[0] if chunks else 'No chunks extracted.'}")
                    continue
                
                st.success(f"✅ Extracted {len(chunks)} chunks from '{filename}'")
                
                # Add to vector store
                success = vector_store.add_document(filename, chunks, batch_size=32)
                if success:
                    st.success("✅ Added to vector store successfully!")
                else:
                    st.error("❌ Failed to add to vector store")
    
    # Clean up temporary file
    import os
    os.unlink(tmp_path)

st.header("📖 Document Q&A and Quiz")

# Select a document
doc_list = vector_store.list_documents()
if not doc_list:
    st.info("No documents indexed yet. Please upload and process a PDF first.")
else:
    selected_doc = st.selectbox("Select a document for Q&A or quiz:", doc_list)

    # Q&A Section
    st.subheader("Ask a Question")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_question = st.text_input("Type your question about the document:")
    with col2:
        use_hybrid = st.checkbox("Use Hybrid Search", value=True, help="Combines keyword and semantic search for better results")
    
    if st.button("Get Answer") and user_question:
        with st.spinner("Searching with hybrid search..." if use_hybrid else "Searching..."):
            # Temporarily disable debug prints for better UX
            import sys
            from io import StringIO
            
            # Capture debug output
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
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
                    context_chunks=[],  # Could extract from hybrid search results
                    metadata={
                        "document_name": selected_doc,
                        "use_hybrid_search": use_hybrid,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
            finally:
                # Restore stdout
                sys.stdout = old_stdout
            
            st.success("Answer:")
            st.write(answer)
            
            # Show conversation history
            if st.checkbox("Show Conversation History", value=False):
                st.subheader("💬 Conversation History")
                
                # Get conversation summary
                summary = conversation_buffer.get_conversation_summary(st.session_state.session_id)
                
                if summary['total_interactions'] > 0:
                    st.info(f"📊 **Session Summary:** {summary['total_interactions']} interactions, "
                           f"Documents: {', '.join(summary['documents_referenced']) if summary['documents_referenced'] else 'None'}")
                    
                    # Show recent interactions
                    recent_context = conversation_buffer.get_recent_context(st.session_state.session_id, num_interactions=5)
                    
                    for i, interaction in enumerate(recent_context, 1):
                        with st.expander(f"Interaction {i} - {interaction['timestamp'][:19]}"):
                            st.write(f"**You:** {interaction['user_message']}")
                            st.write(f"**Assistant:** {interaction['ai_response']}")
                            if interaction['metadata'].get('document_name'):
                                st.caption(f"📄 Document: {interaction['metadata']['document_name']}")
                else:
                    st.info("No conversation history yet. Start asking questions!")
                
                # Add conversation management options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Clear Conversation History"):
                        conversation_buffer.clear_conversation(st.session_state.session_id)
                        st.rerun()
                
                with col2:
                    if st.button("Export Conversation"):
                        export_data = conversation_buffer.export_conversation(st.session_state.session_id, format="text")
                        st.download_button(
                            label="Download Conversation",
                            data=export_data,
                            file_name=f"conversation_{st.session_state.session_id[:8]}.txt",
                            mime="text/plain"
                        )

    # Quiz Section
    st.subheader("Generate Advanced Quiz")
    
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of questions", 1, 10, 5)
    with col2:
        difficulty = st.selectbox("Difficulty", ["mixed", "easy", "medium", "hard"])
    
    if st.button("Generate Quiz"):
        with st.spinner("Generating advanced quiz with LLM..."):
            # Temporarily disable debug prints for better UX
            import sys
            from io import StringIO
            
            # Capture debug output
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                quiz = quiz_generator.generate_advanced_quiz(selected_doc, num_questions=num_questions, difficulty=difficulty)
            finally:
                # Restore stdout
                sys.stdout = old_stdout
        
        if quiz:
            # Store quiz in session state for user interaction
            st.session_state.quiz = quiz
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False
            st.success(f"✅ Generated {len(quiz)} questions!")
        else:
            st.warning("Could not generate quiz questions from this document.")
    
    # Display interactive quiz if available
    if 'quiz' in st.session_state and st.session_state.quiz:
        st.subheader("📝 Take the Quiz")
        
        quiz = st.session_state.quiz
        
        # Quiz instructions
        st.info("💡 Answer the questions below. You can review your answers before submitting.")
        
        # Initialize user answers if not exists
        if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
        
        # Use form to prevent re-runs on every input change
        with st.form("quiz_form"):
            # Display questions and collect answers
            for i, q in enumerate(quiz, 1):
                st.markdown(f"**Question {i} ({q.get('type', 'question').title()}):**")
                st.write(q['question'])
                
                # Different input methods based on question type
                if q.get('type') == 'multiple_choice' and 'options' in q:
                    # Multiple choice with radio buttons
                    options = q['options']
                    current_answer = st.session_state.user_answers.get(f"q{i}", None)
                    index = list(options.keys()).index(current_answer) if current_answer in options else None
                    
                    user_answer = st.radio(
                        f"Select your answer for Question {i}:",
                        options=list(options.keys()),
                        format_func=lambda x: f"{x}) {options[x]}",
                        key=f"q{i}_answer",
                        index=index
                    )
                    
                elif q.get('type') == 'true_false':
                    # True/False with radio buttons
                    current_answer = st.session_state.user_answers.get(f"q{i}", None)
                    index = 0 if current_answer == "True" else 1 if current_answer == "False" else None
                    
                    user_answer = st.radio(
                        f"Select your answer for Question {i}:",
                        options=["True", "False"],
                        key=f"q{i}_answer",
                        index=index
                    )
                    
                else:
                    # Short answer with text input
                    current_answer = st.session_state.user_answers.get(f"q{i}", "")
                    user_answer = st.text_input(
                        f"Your answer for Question {i}:",
                        value=current_answer,
                        key=f"q{i}_answer",
                        placeholder="Type your answer here..."
                    )
                
                st.divider()
            
            # Submit button inside form
            col1, col2 = st.columns([1, 3])
            with col1:
                # Always enable submit button in form - validation will happen on submission
                submit_button = st.form_submit_button("Submit Quiz", type="primary")
                
            with col2:
                new_quiz_button = st.form_submit_button("Generate New Quiz")
        
        # Handle form submission
        if submit_button:
            # Check if all questions are answered after form submission
            all_answered = True
            missing_questions = []
            
            for i in range(1, len(quiz) + 1):
                answer_key = f"q{i}_answer"
                if answer_key in st.session_state:
                    user_answer = st.session_state[answer_key]
                    if not user_answer or (isinstance(user_answer, str) and not user_answer.strip()):
                        all_answered = False
                        missing_questions.append(i)
                else:
                    all_answered = False
                    missing_questions.append(i)
            
            if all_answered:
                # Store answers in user_answers for results display
                for i in range(1, len(quiz) + 1):
                    answer_key = f"q{i}_answer"
                    if answer_key in st.session_state:
                        st.session_state.user_answers[f"q{i}"] = st.session_state[answer_key]
                
                st.session_state.quiz_submitted = True
                st.rerun()
            else:
                st.error(f"⚠️ Please answer all questions. Missing: {', '.join(map(str, missing_questions))}")
        
        if new_quiz_button:
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
                    
                    # Show explanation for all questions (both correct and incorrect)
                    if 'explanation' in q:
                        st.success("💡 **Explanation:** " + q['explanation'])
                    
                    # Show page reference if available
                    if 'page_reference' in q and q['page_reference'] != "Page reference not available.":
                        st.info("📖 **Reference:** " + q['page_reference'])
                    
                    # Show context only for incorrect answers as additional help
                    if not is_correct:
                        st.warning("📚 **Additional Context:** " + q.get('context', 'No context available.'))
            
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
            
            # Show context for missed questions
            missed_questions = []
            for i, q in enumerate(quiz, 1):
                user_answer = st.session_state.user_answers.get(f"q{i}", "")
                correct_answer = q['answer']
                
                if q.get('type') == 'multiple_choice':
                    is_correct = user_answer == correct_answer
                elif q.get('type') == 'true_false':
                    is_correct = user_answer.lower() == correct_answer.lower()
                else:
                    is_correct = user_answer.lower().strip() in correct_answer.lower() or correct_answer.lower() in user_answer.lower()
                
                if not is_correct:
                    missed_questions.append((i, q))
            
            if missed_questions:
                st.subheader("📖 Review Areas for Improvement")
                st.info("Here are the questions you missed, along with explanations and references:")
                
                for q_num, question in missed_questions:
                    st.markdown(f"**Question {q_num}:** {question['question']}")
                    st.write(f"**Correct Answer:** {question['answer']}")
                    
                    if 'explanation' in question:
                        st.success("💡 **Explanation:** " + question['explanation'])
                    
                    if 'page_reference' in question and question['page_reference'] != "Page reference not available.":
                        st.info("📖 **Reference:** " + question['page_reference'])
                    
                    st.divider()
