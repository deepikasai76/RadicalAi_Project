"""
Quiz Page Implementation
Class-based approach for the quiz generation and scoring page.
"""

import streamlit as st
from ui_components import render_back_button

class QuizPage:
    """Handles the quiz generation and scoring functionality."""
    
    def __init__(self, vector_store, quiz_generator):
        self.vector_store = vector_store
        self.quiz_generator = quiz_generator
    
    def render(self):
        """Render the quiz page."""
        st.title("📝 Quiz Generation")
        
        # Back to upload button
        render_back_button()
        
        # Check if documents are available
        doc_list = self.vector_store.list_documents()
        if not doc_list:
            self._render_no_documents()
            return
        
        # Select a document
        selected_doc = st.selectbox("Select a document for quiz:", doc_list)
        
        # Check if we have a quiz to display
        if 'quiz' in st.session_state and st.session_state.quiz:
            self._render_quiz_display(selected_doc)
        else:
            self._render_quiz_generation(selected_doc)
    
    def _render_no_documents(self):
        """Render message when no documents are available."""
        st.info("No documents indexed yet. Please upload and process a PDF first.")
        if st.button("Go to Upload", key="quiz_go_to_upload"):
            st.session_state.current_page = "upload"
            st.rerun()
    
    def _render_quiz_generation(self, selected_doc):
        """Render the quiz generation section."""
        st.subheader("Generate Quiz")
        
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.slider("Number of questions", 1, 10, 5)
        with col2:
            difficulty = st.selectbox("Difficulty", ["mixed", "easy", "medium", "hard"])
        
        if st.button("🎲 Generate Quiz", use_container_width=True, key="quiz_generate"):
            self._generate_quiz(selected_doc, num_questions, difficulty)
    
    def _generate_quiz(self, selected_doc, num_questions, difficulty):
        """Generate a new quiz."""
        with st.spinner("Generating quiz..."):
            quiz = self.quiz_generator.generate_advanced_quiz(
                selected_doc, 
                num_questions=num_questions, 
                difficulty=difficulty
            )
        
        if quiz:
            st.session_state.quiz = quiz
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False
            st.success(f"✅ Generated {len(quiz)} questions!")
            st.rerun()  # Refresh to show the quiz
        else:
            st.warning("Could not generate quiz questions from this document.")
    
    def _render_quiz_display(self, selected_doc):
        """Render the quiz display and answer collection."""
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
            self._render_question(i, q)
            st.markdown("---")
        
        # Submit and New Quiz buttons
        self._render_quiz_actions()
        
        # Show results after submission
        if st.session_state.get('quiz_submitted', False):
            self._render_quiz_results(quiz)
    
    def _render_question(self, question_num, question):
        """Render a single question with appropriate input method."""
        st.markdown(f"**Question {question_num}:**")
        st.write(question['question'])
        
        # Different input methods based on question type
        if question.get('type') == 'multiple_choice' and 'options' in question:
            self._render_multiple_choice(question_num, question)
        elif question.get('type') == 'true_false':
            self._render_true_false(question_num, question)
        else:
            self._render_short_answer(question_num, question)
    
    def _render_multiple_choice(self, question_num, question):
        """Render multiple choice question."""
        options = question['options']
        user_answer = st.radio(
            f"Select your answer for Question {question_num}:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}) {options[x]}",
            key=f"q{question_num}_answer"
        )
        st.session_state.user_answers[f"q{question_num}"] = user_answer
    
    def _render_true_false(self, question_num, question):
        """Render true/false question."""
        user_answer = st.radio(
            f"Select your answer for Question {question_num}:",
            options=["True", "False"],
            key=f"q{question_num}_answer"
        )
        st.session_state.user_answers[f"q{question_num}"] = user_answer
    
    def _render_short_answer(self, question_num, question):
        """Render short answer question."""
        user_answer = st.text_input(
            f"Your answer for Question {question_num}:",
            key=f"q{question_num}_answer",
            placeholder="Type your answer here..."
        )
        st.session_state.user_answers[f"q{question_num}"] = user_answer
    
    def _render_quiz_actions(self):
        """Render submit and new quiz buttons."""
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Submit Quiz", use_container_width=True, key="quiz_submit"):
                self._submit_quiz()
        
        with col2:
            if st.button("🔄 New Quiz", use_container_width=True, key="quiz_new"):
                self._clear_quiz()
    
    def _submit_quiz(self):
        """Submit the quiz and validate answers."""
        quiz = st.session_state.quiz
        
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
    
    def _clear_quiz(self):
        """Clear the current quiz and start over."""
        if 'quiz' in st.session_state:
            del st.session_state.quiz
        if 'user_answers' in st.session_state:
            del st.session_state.user_answers
        if 'quiz_submitted' in st.session_state:
            del st.session_state.quiz_submitted
        st.rerun()
    
    def _render_quiz_results(self, quiz):
        """Render the quiz results and scoring."""
        st.markdown("---")
        st.subheader("📊 Quiz Results")
        
        correct_answers = 0
        total_questions = len(quiz)
        
        for i, q in enumerate(quiz, 1):
            user_answer = st.session_state.user_answers.get(f"q{i}", "")
            correct_answer = q['answer']
            
            # Check if answer is correct
            is_correct = self._check_answer_correctness(q, user_answer, correct_answer)
            
            if is_correct:
                correct_answers += 1
            
            # Display result for each question
            self._render_question_result(i, q, user_answer, correct_answer, is_correct)
        
        # Calculate and display final score
        self._render_final_score(correct_answers, total_questions)
    
    def _check_answer_correctness(self, question, user_answer, correct_answer):
        """Check if a user answer is correct based on question type."""
        if question.get('type') == 'multiple_choice':
            return user_answer == correct_answer
        elif question.get('type') == 'true_false':
            return user_answer.lower() == correct_answer.lower()
        else:
            # For short answer, do basic similarity check
            return (user_answer.lower().strip() in correct_answer.lower() or 
                   correct_answer.lower() in user_answer.lower())
    
    def _render_question_result(self, question_num, question, user_answer, correct_answer, is_correct):
        """Render the result for a single question."""
        with st.expander(f"Question {question_num} - {'✅ Correct' if is_correct else '❌ Incorrect'}"):
            st.write(f"**Your Answer:** {user_answer}")
            st.write(f"**Correct Answer:** {correct_answer}")
            
            # Show explanation if available
            if 'explanation' in question:
                st.success("💡 **Explanation:** " + question['explanation'])
    
    def _render_final_score(self, correct_answers, total_questions):
        """Render the final score and performance feedback."""
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
        
        # Add navigation buttons after quiz completion
        st.markdown("---")
        st.markdown("### 🎯 What would you like to do next?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❓ Ask More Questions", use_container_width=True, key="quiz_ask_more"):
                st.session_state.current_page = "qa"
                st.rerun()
        
        with col2:
            if st.button("🔄 New Quiz", use_container_width=True, key="quiz_new_after_results"):
                self._clear_quiz()
        
        with col3:
            if st.button("💬 View History", use_container_width=True, key="quiz_view_history"):
                st.session_state.current_page = "history"
                st.rerun() 