"""
quiz_generator.py

Provides advanced Q&A and LLM-powered quiz generation functionality using a class-based approach.
"""
from typing import List, Dict, Optional
from .vector_store import query_similar_chunks
import random
import re
import openai
from openai import OpenAI
import json
import os


class QuizGenerator:
    """
    Handles Q&A operations and quiz generation using LLM integration.
    """
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        """
        Initialize the QuizGenerator.
        
        Args:
            llm_model (str): OpenAI model to use for generation
        """
        self.llm_model = llm_model
        
        # Initialize OpenAI client with error handling
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                print("⚠️ OpenAI API key not found - LLM features will use fallbacks")
        except Exception as e:
            self.client = None
            print(f"⚠️ Failed to initialize OpenAI client: {e}")
        
        # Question type templates
        self.question_types = {
            "multiple_choice": {
                "prompt": "Create a multiple choice question with 4 options (A, B, C, D) where only one is correct. Format: Question: [question] A) [option] B) [option] C) [option] D) [option] Answer: [letter]",
                "difficulty": "medium"
            },
            "true_false": {
                "prompt": "Create a true/false question based on the content. Format: Question: [statement] Answer: [True/False]",
                "difficulty": "easy"
            },
            "short_answer": {
                "prompt": "Create a short answer question that requires understanding of the concept. Format: Question: [question] Answer: [brief answer]",
                "difficulty": "medium"
            },
            "definition": {
                "prompt": "Create a definition question asking about a key term or concept. Format: Question: Define [term/concept] Answer: [definition]",
                "difficulty": "easy"
            },
            "application": {
                "prompt": "Create an application question that asks how to apply a concept in practice. Format: Question: [scenario-based question] Answer: [explanation]",
                "difficulty": "hard"
            }
        }
    
    def answer_question(self, 
                       question: str, 
                       filename: Optional[str] = None, 
                       n_context: int = 3, 
                       use_hybrid: bool = True) -> str:
        """
        Answer a user question using hybrid search and LLM generation.
        
        Args:
            question (str): The user's question
            filename (Optional[str]): Restrict search to this document
            n_context (int): Number of top chunks to use as context
            use_hybrid (bool): Whether to use hybrid search (default: True)
            
        Returns:
            str: Clean, concise answer generated from context
        """
        print(f"[DEBUG] Question: {question}")
        print(f"[DEBUG] Using hybrid search: {use_hybrid}")
        print(f"[DEBUG] OpenAI API key configured: {bool(self.client and self.client.api_key)}")
        
        if use_hybrid:
            # Use hybrid search for better results
            try:
                from .hybrid_search import hybrid_search
                print("[DEBUG] Performing hybrid search...")
                results = hybrid_search(question, top_k=n_context, filename=filename)
                print(f"[DEBUG] Hybrid search returned {len(results)} results")
                if not results:
                    print("[DEBUG] No hybrid search results found")
                    return "Sorry, I couldn't find an answer in the documents."
                
                # Convert hybrid results to expected format
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "document": result["document"],
                        "metadata": {"filename": result["document_id"]},
                        "distance": 1.0 - result["combined_score"]  # Convert back to distance format
                    })
                print(f"[DEBUG] Converted {len(formatted_results)} results")
            except Exception as e:
                print(f"[DEBUG] Hybrid search failed: {e}")
                # Fallback to vector search
                results = query_similar_chunks(question, n_results=n_context, filename=filename)
                if not results:
                    return "Sorry, I couldn't find an answer in the documents."
                formatted_results = results
        else:
            # Fallback to original vector search
            print("[DEBUG] Using vector search...")
        results = query_similar_chunks(question, n_results=n_context, filename=filename)
        if not results:
            return "Sorry, I couldn't find an answer in the documents."
            formatted_results = results
        
        print(f"[DEBUG] About to generate LLM answer with {len(formatted_results)} context chunks")
        # Use LLM to generate a clean answer from the context
        return self.generate_llm_answer(question, formatted_results)
    
    def generate_llm_answer(self, question: str, context_results: List[Dict]) -> str:
        """
        Generate a clean, concise answer using LLM from retrieved context.
        
        Args:
            question (str): The user's question
            context_results (List[Dict]): Retrieved context chunks
            
        Returns:
            str: Generated answer
        """
        print(f"[DEBUG] generate_llm_answer called with {len(context_results)} context chunks")
        print(f"[DEBUG] OpenAI API key available: {bool(self.client and self.client.api_key)}")
        
        if not self.client or not self.client.api_key:
            print("[DEBUG] No OpenAI API key found - using fallback")
            # Fallback to simple answer if no API key
            return context_results[0]["document"][:500] + "..."
        
        # Prepare context from top results
        context_text = "\n\n".join([result["document"] for result in context_results])
        print(f"[DEBUG] Context text length: {len(context_text)} characters")
        print(f"[DEBUG] First 200 chars of context: {context_text[:200]}...")
        
        prompt = f"""
        Based on the following context, provide a clear and concise answer to the question.
        
        Question: {question}
        
        Context:
        {context_text}
        
        Instructions:
        - Provide a direct, accurate answer
        - Keep it concise (2-3 sentences maximum)
        - Use clear, simple language
        - If the context doesn't contain enough information, say so
        """
        
        print(f"[DEBUG] About to call OpenAI API...")
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides clear, concise answers based on given context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"[DEBUG] LLM response received: {answer[:100]}...")
            return answer

        except Exception as e:
            print(f"[DEBUG] LLM call failed with error: {e}")
            # Fallback to simple answer if LLM fails
            fallback_answer = context_results[0]["document"][:300] + "..."
            print(f"[DEBUG] Using fallback answer: {fallback_answer[:100]}...")
            return fallback_answer
    
    def generate_llm_question(self, context: str, question_type: str) -> Dict:
        """
        Generate a single question using LLM based on the given context and type.
        
        Args:
            context (str): Text context for question generation
            question_type (str): Type of question to generate
            
        Returns:
            Dict: Generated question with metadata
        """
        if not self.client or not self.client.api_key:
            return {"error": "OpenAI API key not configured"}
        
        template = self.question_types.get(question_type, self.question_types["multiple_choice"])
        
        prompt = f"""
        Based on the following text context, {template['prompt']}
        
        Context:
        {context}
        
        Generate a high-quality question that tests understanding of the key concepts in the context.
        
        IMPORTANT: Also provide:
        1. A clear, concise explanation of the correct answer (2-3 sentences)
        2. The page number or section where this topic is discussed (if mentioned in context)
        3. Key points that should be included in a good answer
        
        Format your response with clear sections for Question, Options (if multiple choice), Answer, Explanation, and Page Reference.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating quiz questions. Generate clear, accurate, and engaging questions with detailed explanations and page references."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            question_text = response.choices[0].message.content
            
            # Parse the response based on question type
            if question_type == "multiple_choice":
                return self.parse_multiple_choice(question_text, context)
            elif question_type == "true_false":
                return self.parse_true_false(question_text, context)
            else:
                return self.parse_short_answer(question_text, context, question_type)
                
        except Exception as e:
            return self.generate_fallback_question(context, question_type)
    
    def parse_multiple_choice(self, text: str, context: str) -> Dict:
        """Parse multiple choice question from LLM response."""
        try:
            # Extract question
            question_match = re.search(r'Question:\s*(.+?)(?=\s*A\)|$)', text, re.DOTALL)
            question = question_match.group(1).strip() if question_match else "Question not found"
            
            # Extract options
            options = {}
            for letter in ['A', 'B', 'C', 'D']:
                option_match = re.search(rf'{letter}\)\s*(.+?)(?=\s*[A-D]\)|Answer:|$)', text, re.DOTALL)
                if option_match:
                    options[letter] = option_match.group(1).strip()
            
            # Extract answer
            answer_match = re.search(r'Answer:\s*([A-D])', text)
            answer = answer_match.group(1) if answer_match else "A"
            
            # Extract explanation
            explanation_match = re.search(r'Explanation:\s*(.+?)(?=\s*Page|$)', text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
            
            # Extract page reference
            page_match = re.search(r'Page.*?Reference:\s*(.+?)(?=\s*$)', text, re.DOTALL | re.IGNORECASE)
            page_ref = page_match.group(1).strip() if page_match else "Page reference not available."
            
            return {
                "type": "multiple_choice",
                "question": question,
                "options": options,
                "answer": answer,
                "explanation": explanation,
                "page_reference": page_ref,
                "context": context[:200] + "..."
            }
        except Exception as e:
            return self.generate_fallback_question(context, "multiple_choice")
    
    def parse_true_false(self, text: str, context: str) -> Dict:
        """Parse true/false question from LLM response."""
        try:
            question_match = re.search(r'Question:\s*(.+?)(?=\s*Answer:|$)', text, re.DOTALL)
            question = question_match.group(1).strip() if question_match else "Question not found"
            
            answer_match = re.search(r'Answer:\s*(True|False)', text, re.IGNORECASE)
            answer = answer_match.group(1).title() if answer_match else "True"
            
            # Extract explanation
            explanation_match = re.search(r'Explanation:\s*(.+?)(?=\s*Page|$)', text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
            
            # Extract page reference
            page_match = re.search(r'Page.*?Reference:\s*(.+?)(?=\s*$)', text, re.DOTALL | re.IGNORECASE)
            page_ref = page_match.group(1).strip() if page_match else "Page reference not available."
            
            return {
                "type": "true_false",
                "question": question,
                "answer": answer,
                "explanation": explanation,
                "page_reference": page_ref,
                "context": context[:200] + "..."
            }
        except Exception as e:
            return self.generate_fallback_question(context, "true_false")
    
    def parse_short_answer(self, text: str, context: str, question_type: str) -> Dict:
        """Parse short answer question from LLM response."""
        try:
            question_match = re.search(r'Question:\s*(.+?)(?=\s*Answer:|$)', text, re.DOTALL)
            question = question_match.group(1).strip() if question_match else "Question not found"
            
            answer_match = re.search(r'Answer:\s*(.+?)(?=\s*Explanation:|$)', text, re.DOTALL)
            answer = answer_match.group(1).strip() if answer_match else "Answer not found"
            
            # Extract explanation
            explanation_match = re.search(r'Explanation:\s*(.+?)(?=\s*Page|$)', text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
            
            # Extract page reference
            page_match = re.search(r'Page.*?Reference:\s*(.+?)(?=\s*$)', text, re.DOTALL | re.IGNORECASE)
            page_ref = page_match.group(1).strip() if page_match else "Page reference not available."
            
            return {
                "type": question_type,
                "question": question,
                "answer": answer,
                "explanation": explanation,
                "page_reference": page_ref,
                "context": context[:200] + "..."
            }
        except Exception as e:
            return self.generate_fallback_question(context, question_type)
    
    def generate_advanced_quiz(self, 
                              filename: str, 
                              num_questions: int = 5, 
                              difficulty: str = "mixed") -> List[Dict]:
        """
        Generate an advanced quiz using LLM with multiple question types.
        
    Args:
            filename (str): Document filename to generate quiz for
            num_questions (int): Number of questions to generate
            difficulty (str): Difficulty level (easy, medium, hard, mixed)
            
    Returns:
            List[Dict]: List of generated questions
        """
        # Get document chunks for context
        results = query_similar_chunks("", n_results=10, filename=filename)
        if not results:
            return []
        
        # Select question types based on difficulty
        if difficulty == "easy":
            question_types = ["true_false", "definition"]
        elif difficulty == "medium":
            question_types = ["multiple_choice", "short_answer"]
        elif difficulty == "hard":
            question_types = ["application", "short_answer"]
        else:  # mixed
            question_types = list(self.question_types.keys())
        
        quiz_questions = []
        
        for i in range(num_questions):
            # Select random context chunk
            context_chunk = random.choice(results)["document"]
            
            # Select random question type
            question_type = random.choice(question_types)
            
            # Generate question
            question = self.generate_llm_question(context_chunk, question_type)
            
            if "error" not in question:
                quiz_questions.append(question)
        
        return quiz_questions
    
    def generate_fallback_question(self, context: str, question_type: str) -> Dict:
        """Generate a simple fallback question when LLM fails."""
        if question_type == "multiple_choice":
            return {
                "type": "multiple_choice",
                "question": "What is the main topic discussed in this text?",
                "options": {
                    "A": "Technology",
                    "B": "Science", 
                    "C": "History",
                    "D": "Literature"
                },
                "answer": "A",
                "explanation": "The text discusses technological concepts and applications.",
                "page_reference": "Page reference not available.",
                "context": context[:200] + "..."
            }
        elif question_type == "true_false":
            return {
                "type": "true_false",
                "question": "This text contains important information.",
                "answer": "True",
                "explanation": "The text provides valuable insights and information on the topic.",
                "page_reference": "Page reference not available.",
                "context": context[:200] + "..."
            }
        else:
            return {
                "type": question_type,
                "question": "What is the main concept discussed in this text?",
                "answer": "The text discusses various concepts and ideas.",
                "explanation": "The main concept involves understanding the key principles presented in the text.",
                "page_reference": "Page reference not available.",
                "context": context[:200] + "..."
            }
    
    def generate_quiz(self, filename: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate a quiz (wrapper for advanced quiz generation).
        
        Args:
            filename (str): Document filename
            num_questions (int): Number of questions
            
        Returns:
            List[Dict]: List of quiz questions
        """
        return self.generate_advanced_quiz(filename, num_questions, "mixed")


# Global instance for backward compatibility
quiz_generator = QuizGenerator()


# Backward compatibility functions
def answer_question(question: str, filename: Optional[str] = None, n_context: int = 3, use_hybrid: bool = True) -> str:
    """Backward compatibility function."""
    return quiz_generator.answer_question(question, filename, n_context, use_hybrid)


def generate_llm_answer(question: str, context_results: List[Dict]) -> str:
    """Backward compatibility function."""
    return quiz_generator.generate_llm_answer(question, context_results)


def generate_llm_question(context: str, question_type: str) -> Dict:
    """Backward compatibility function."""
    return quiz_generator.generate_llm_question(context, question_type)


def parse_multiple_choice(text: str, context: str) -> Dict:
    """Backward compatibility function."""
    return quiz_generator.parse_multiple_choice(text, context)


def parse_true_false(text: str, context: str) -> Dict:
    """Backward compatibility function."""
    return quiz_generator.parse_true_false(text, context)


def parse_short_answer(text: str, context: str, question_type: str) -> Dict:
    """Backward compatibility function."""
    return quiz_generator.parse_short_answer(text, context, question_type)


def generate_advanced_quiz(filename: str, num_questions: int = 5, difficulty: str = "mixed") -> List[Dict]:
    """Backward compatibility function."""
    return quiz_generator.generate_advanced_quiz(filename, num_questions, difficulty)


def generate_fallback_question(context: str, question_type: str) -> Dict:
    """Backward compatibility function."""
    return quiz_generator.generate_fallback_question(context, question_type)


def generate_quiz(filename: str, num_questions: int = 5) -> List[Dict]:
    """Backward compatibility function."""
    return quiz_generator.generate_quiz(filename, num_questions) 