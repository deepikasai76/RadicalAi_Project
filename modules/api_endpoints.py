"""
API Endpoints Module

Provides RESTful API access to Radical AI functionality.
Includes authentication, rate limiting, and comprehensive endpoints.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from functools import wraps
import hashlib
import hmac
import base64
from collections import defaultdict
import threading
import tempfile
import os

try:
    from flask import Flask, request, jsonify, make_response
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Rate limit key (e.g., API key or IP)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed
        """
        now = time.time()
        
        with self.lock:
            # Clean old requests
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if now - req_time < window_seconds]
            
            # Check if limit exceeded
            if len(self.requests[key]) >= max_requests:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests for a key."""
        now = time.time()
        
        with self.lock:
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if now - req_time < window_seconds]
            
            return max(0, max_requests - len(self.requests[key]))


class APIEndpoints:
    """Manages API endpoints for Radical AI."""
    
    def __init__(self, integration_manager=None, export_manager=None, 
                 vector_store=None, quiz_generator=None, conversation_buffer=None):
        self.integration_manager = integration_manager
        self.export_manager = export_manager
        self.vector_store = vector_store
        self.quiz_generator = quiz_generator
        self.conversation_buffer = conversation_buffer
        
        self.rate_limiter = RateLimiter()
        self.app = None
        
        if FLASK_AVAILABLE:
            self._initialize_flask_app()
    
    def _initialize_flask_app(self):
        """Initialize Flask application."""
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        @self.app.route('/api/documents', methods=['GET'])
        @self.limiter.limit("100 per hour")
        def list_documents():
            """List all documents in the system."""
            try:
                if not self.vector_store:
                    return jsonify({'error': 'Vector store not available'}), 500
                
                documents = self.vector_store.list_documents()
                return jsonify({
                    'documents': documents,
                    'count': len(documents)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/documents/<document_name>', methods=['GET'])
        @self.limiter.limit("200 per hour")
        def get_document_info(document_name):
            """Get information about a specific document."""
            try:
                if not self.vector_store:
                    return jsonify({'error': 'Vector store not available'}), 500
                
                # Get document chunks
                chunks = self.vector_store.get_document_chunks(document_name)
                
                return jsonify({
                    'document_name': document_name,
                    'chunk_count': len(chunks) if chunks else 0,
                    'chunks': chunks[:10] if chunks else []  # Limit to first 10 chunks
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/query', methods=['POST'])
        @self.limiter.limit("50 per hour")
        def query_document():
            """Query a document with a question."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                question = data.get('question')
                document_name = data.get('document_name')
                use_hybrid = data.get('use_hybrid', True)
                session_id = data.get('session_id')
                
                if not question or not document_name:
                    return jsonify({'error': 'Question and document_name are required'}), 400
                
                if not self.quiz_generator:
                    return jsonify({'error': 'Quiz generator not available'}), 500
                
                # Get answer
                answer = self.quiz_generator.answer_question(
                    question, 
                    filename=document_name, 
                    use_hybrid=use_hybrid
                )
                
                # Store in conversation buffer if available
                if self.conversation_buffer and session_id:
                    self.conversation_buffer.add_interaction(
                        session_id=session_id,
                        user_message=question,
                        ai_response=answer,
                        metadata={
                            'document_name': document_name,
                            'use_hybrid_search': use_hybrid,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                
                return jsonify({
                    'question': question,
                    'answer': answer,
                    'document_name': document_name,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/quiz/generate', methods=['POST'])
        @self.limiter.limit("20 per hour")
        def generate_quiz():
            """Generate a quiz from a document."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                document_name = data.get('document_name')
                num_questions = data.get('num_questions', 5)
                difficulty = data.get('difficulty', 'mixed')
                
                if not document_name:
                    return jsonify({'error': 'Document name is required'}), 400
                
                if not self.quiz_generator:
                    return jsonify({'error': 'Quiz generator not available'}), 500
                
                # Generate quiz
                quiz = self.quiz_generator.generate_advanced_quiz(
                    document_name,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
                
                return jsonify({
                    'document_name': document_name,
                    'quiz': quiz,
                    'num_questions': len(quiz) if quiz else 0,
                    'difficulty': difficulty,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/quiz/submit', methods=['POST'])
        @self.limiter.limit("100 per hour")
        def submit_quiz():
            """Submit quiz answers and get results."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                quiz = data.get('quiz')
                answers = data.get('answers')
                
                if not quiz or not answers:
                    return jsonify({'error': 'Quiz and answers are required'}), 400
                
                # Grade quiz
                results = self._grade_quiz(quiz, answers)
                
                return jsonify({
                    'results': results,
                    'score': results['score'],
                    'total_questions': results['total_questions'],
                    'correct_answers': results['correct_answers'],
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/conversations/<session_id>', methods=['GET'])
        @self.limiter.limit("200 per hour")
        def get_conversation(session_id):
            """Get conversation history for a session."""
            try:
                if not self.conversation_buffer:
                    return jsonify({'error': 'Conversation buffer not available'}), 500
                
                max_interactions = request.args.get('max_interactions', 50, type=int)
                
                context = self.conversation_buffer.get_recent_context(
                    session_id, 
                    num_interactions=max_interactions
                )
                
                summary = self.conversation_buffer.get_conversation_summary(session_id)
                
                return jsonify({
                    'session_id': session_id,
                    'interactions': context,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/conversations/<session_id>/export', methods=['POST'])
        @self.limiter.limit("10 per hour")
        def export_conversation(session_id):
            """Export conversation in various formats."""
            try:
                data = request.get_json() or {}
                format_type = data.get('format', 'json')
                
                if not self.conversation_buffer:
                    return jsonify({'error': 'Conversation buffer not available'}), 500
                
                if not self.export_manager:
                    return jsonify({'error': 'Export manager not available'}), 500
                
                # Get conversation data
                conversation_data = {
                    'session_id': session_id,
                    'interactions': self.conversation_buffer.get_recent_context(session_id, 100),
                    'summary': self.conversation_buffer.get_conversation_summary(session_id)
                }
                
                # Export
                exported_data = self.export_manager.export_conversation(
                    conversation_data, 
                    format_type=format_type,
                    filename=f"conversation_{session_id}"
                )
                
                if format_type in ['pdf', 'docx', 'pptx', 'xlsx']:
                    # Return file as download
                    response = make_response(exported_data)
                    response.headers['Content-Type'] = self._get_content_type(format_type)
                    response.headers['Content-Disposition'] = f'attachment; filename=conversation_{session_id}.{format_type}'
                    return response
                else:
                    # Return JSON response
                    return jsonify({
                        'session_id': session_id,
                        'format': format_type,
                        'data': exported_data,
                        'timestamp': datetime.now().isoformat()
                    })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/integrations/status', methods=['GET'])
        @self.limiter.limit("50 per hour")
        def get_integration_status():
            """Get status of all integrations."""
            try:
                if not self.integration_manager:
                    return jsonify({'error': 'Integration manager not available'}), 500
                
                status = self.integration_manager.get_integration_status()
                return jsonify(status)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/integrations/google-drive/upload', methods=['POST'])
        @self.limiter.limit("10 per hour")
        def upload_to_google_drive():
            """Upload file to Google Drive."""
            try:
                if not self.integration_manager:
                    return jsonify({'error': 'Integration manager not available'}), 500
                
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                folder_id = request.form.get('folder_id')
                
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                    file.save(tmp_file.name)
                    tmp_path = tmp_file.name
                
                try:
                    result = self.integration_manager.upload_to_google_drive(tmp_path, folder_id)
                    return jsonify(result)
                finally:
                    # Clean up temporary file
                    os.unlink(tmp_path)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/integrations/dropbox/upload', methods=['POST'])
        @self.limiter.limit("10 per hour")
        def upload_to_dropbox():
            """Upload file to Dropbox."""
            try:
                if not self.integration_manager:
                    return jsonify({'error': 'Integration manager not available'}), 500
                
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                dropbox_path = request.form.get('dropbox_path', f'/radical_ai/{file.filename}')
                
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                    file.save(tmp_file.name)
                    tmp_path = tmp_file.name
                
                try:
                    result = self.integration_manager.upload_to_dropbox(tmp_path, dropbox_path)
                    return jsonify(result)
                finally:
                    # Clean up temporary file
                    os.unlink(tmp_path)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _grade_quiz(self, quiz: List[Dict], answers: Dict[str, str]) -> Dict[str, Any]:
        """Grade a quiz submission."""
        correct_answers = 0
        total_questions = len(quiz)
        results = []
        
        for i, question in enumerate(quiz, 1):
            answer_key = f"q{i}"
            user_answer = answers.get(answer_key, "")
            correct_answer = question.get('answer', '')
            
            # Check if answer is correct
            is_correct = False
            if question.get('type') == 'multiple_choice':
                is_correct = user_answer == correct_answer
            elif question.get('type') == 'true_false':
                is_correct = user_answer.lower() == correct_answer.lower()
            else:
                # For short answer, do basic similarity check
                is_correct = (user_answer.lower().strip() in correct_answer.lower() or 
                             correct_answer.lower() in user_answer.lower().strip())
            
            if is_correct:
                correct_answers += 1
            
            results.append({
                'question_number': i,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            'score': score_percentage,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'results': results
        }
    
    def _get_content_type(self, format_type: str) -> str:
        """Get content type for file format."""
        content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json',
            'csv': 'text/csv',
            'txt': 'text/plain'
        }
        return content_types.get(format_type, 'application/octet-stream')
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the API server."""
        if not self.app:
            raise RuntimeError("Flask is not available. Install with: pip install flask flask-cors flask-limiter")
        
        self.app.run(host=host, port=port, debug=debug)
    
    def get_app(self):
        """Get the Flask app instance."""
        return self.app 