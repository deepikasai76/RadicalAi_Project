"""
AI Provider Module
Supports multiple AI providers with a unified interface.
"""

import os
import json
import requests
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import time

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate_answer(self, question: str, context: str) -> str:
        """Generate an answer based on question and context."""
        pass
    
    @abstractmethod
    def generate_quiz_question(self, context: str, question_type: str) -> Dict:
        """Generate a quiz question based on context and type."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass

class OllamaProvider(AIProvider):
    """Ollama local AI provider."""
    
    def __init__(self, model_name: str = "gemma3:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available."""
        try:
            # First check if server is running
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if the specific model is available
            models_response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if models_response.status_code == 200:
                models = models_response.json().get("models", [])
                available_models = [model.get("name", "") for model in models]
                return self.model_name in available_models
            
            return False
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model.get("name", "") for model in models]
            return []
        except:
            return []
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate an answer using Ollama."""
        if not self.is_available():
            available_models = self.get_available_models()
            if not available_models:
                return "Ollama server is not available. Please start Ollama with 'ollama serve'"
            else:
                return f"Model '{self.model_name}' not found. Available models: {', '.join(available_models)}. Please run 'ollama pull {self.model_name}' or choose a different model."
        
        # Truncate context if too long to prevent timeouts
        max_context_length = 2000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        prompt = f"""Context: {context}

Question: {question}

Answer briefly (2-3 sentences):"""
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated").strip()
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. The model is taking longer than expected to respond. Please try again or use a shorter question."
        except requests.exceptions.ConnectionError:
            return "Connection error. Please check if Ollama server is running with 'ollama serve'"
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def generate_quiz_question(self, context: str, question_type: str) -> Dict:
        """Generate a quiz question using Ollama."""
        if not self.is_available():
            return {"error": "Ollama server is not available"}
        
        # Truncate context if too long to prevent timeouts
        max_context_length = 1500
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        # Define question type templates
        templates = {
            "multiple_choice": """Context: {context}

Create a multiple choice question. Respond with JSON:
{{
    "question": "Question text?",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "answer": "A",
    "explanation": "Brief explanation",
    "type": "multiple_choice"
}}""",
            
            "true_false": """Context: {context}

Create a true/false question. Respond with JSON:
{{
    "question": "True/false statement",
    "answer": "True",
    "explanation": "Brief explanation",
    "type": "true_false"
}}""",
            
            "short_answer": """Context: {context}

Create a short answer question. Respond with JSON:
{{
    "question": "Question text?",
    "answer": "Brief answer",
    "explanation": "Brief explanation",
    "type": "short_answer"
}}"""
        }
        
        template = templates.get(question_type, templates["multiple_choice"])
        prompt = template.format(context=context)
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 800
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                # Try to parse JSON response
                try:
                    # Extract JSON from response (sometimes Ollama adds extra text)
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = response_text[json_start:json_end]
                        return json.loads(json_str)
                    else:
                        return {"error": "Invalid response format", "raw_response": response_text}
                except json.JSONDecodeError:
                    return {"error": "Failed to parse response", "raw_response": response_text}
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. The model is taking longer than expected to respond. Please try again or use a shorter question."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Please check if Ollama server is running with 'ollama serve'"}
        except Exception as e:
            return {"error": f"Error generating question: {str(e)}"}

class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI library not installed")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None and self.api_key is not None
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate an answer using OpenAI."""
        if not self.is_available():
            return "OpenAI API key not configured"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides clear, concise answers based on the given context."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this context:\n\n{context}\n\nAnswer this question: {question}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def generate_quiz_question(self, context: str, question_type: str) -> Dict:
        """Generate a quiz question using OpenAI."""
        if not self.is_available():
            return {"error": "OpenAI API key not configured"}
        
        templates = {
            "multiple_choice": """Create a multiple choice question with 4 options (A, B, C, D) where only one is correct.

Context:
{context}

Return a JSON object with this structure:
{{
    "question": "Your question here?",
    "options": {{
        "A": "Option A",
        "B": "Option B", 
        "C": "Option C",
        "D": "Option D"
    }},
    "answer": "A",
    "explanation": "Brief explanation of why this is correct",
    "type": "multiple_choice"
}}""",
            
            "true_false": """Create a true/false question based on the content.

Context:
{context}

Return a JSON object with this structure:
{{
    "question": "Your true/false statement here",
    "answer": "True",
    "explanation": "Brief explanation",
    "type": "true_false"
}}""",
            
            "short_answer": """Create a short answer question that requires understanding of the concept.

Context:
{context}

Return a JSON object with this structure:
{{
    "question": "Your question here?",
    "answer": "Brief answer",
    "explanation": "Detailed explanation",
    "type": "short_answer"
}}"""
        }
        
        template = templates.get(question_type, templates["multiple_choice"])
        prompt = template.format(context=context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quiz generator. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            response_text = response.choices[0].message.content.strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {"error": "Failed to parse response", "raw_response": response_text}
                
        except Exception as e:
            return {"error": f"Error generating question: {str(e)}"}

class AIProviderManager:
    """Manages multiple AI providers with fallback support."""
    
    def __init__(self):
        self.providers = {}
        self.current_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers."""
        # Try Ollama first (local, privacy-focused)
        ollama = OllamaProvider()
        if ollama.is_available():
            self.providers["ollama"] = ollama
            self.current_provider = "ollama"
            print(f"✅ Ollama (local) provider initialized with model: {ollama.model_name}")
        else:
            # Check if Ollama server is running but model is missing
            try:
                response = ollama.session.get(f"{ollama.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    available_models = [model.get("name", "") for model in models]
                    if available_models:
                        print(f"⚠️ Ollama server running but model '{ollama.model_name}' not found")
                        print(f"   Available models: {', '.join(available_models)}")
                        print(f"   Run: ollama pull {ollama.model_name}")
                    else:
                        print("⚠️ Ollama server running but no models installed")
                        print("   Run: ollama pull llama2:7b")
                else:
                    print("⚠️ Ollama server not running")
                    print("   Run: ollama serve")
            except:
                print("⚠️ Ollama server not available")
        
        # Try OpenAI as fallback
        openai_provider = OpenAIProvider()
        if openai_provider.is_available():
            self.providers["openai"] = openai_provider
            if not self.current_provider:
                self.current_provider = "openai"
            print("✅ OpenAI provider initialized")
        
        if not self.current_provider:
            print("⚠️ No AI providers available")
    
    def set_provider(self, provider_name: str) -> bool:
        """Set the current provider."""
        if provider_name in self.providers:
            self.current_provider = provider_name
            return True
        return False
    
    def get_current_provider(self) -> Optional[AIProvider]:
        """Get the current provider."""
        if self.current_provider:
            return self.providers[self.current_provider]
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using current provider."""
        provider = self.get_current_provider()
        if provider:
            return provider.generate_answer(question, context)
        return "No AI provider available"
    
    def generate_quiz_question(self, context: str, question_type: str) -> Dict:
        """Generate quiz question using current provider."""
        provider = self.get_current_provider()
        if provider:
            return provider.generate_quiz_question(context, question_type)
        return {"error": "No AI provider available"}
    
    def test_provider(self, provider_name: str) -> Dict:
        """Test a specific provider."""
        if provider_name not in self.providers:
            return {"error": f"Provider {provider_name} not available"}
        
        provider = self.providers[provider_name]
        test_context = "The Earth is the third planet from the Sun."
        test_question = "What is the Earth's position from the Sun?"
        
        try:
            answer = provider.generate_answer(test_question, test_context)
            return {
                "status": "success",
                "provider": provider_name,
                "test_answer": answer
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": provider_name,
                "error": str(e)
            } 