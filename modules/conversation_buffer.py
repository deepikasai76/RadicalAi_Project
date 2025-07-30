"""
conversation_buffer.py

Provides conversation memory and context management for the Document Q&A and quiz generation.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import uuid

## Conversation Buffer Class for managing conversation history and context
class ConversationBuffer:
    """
    Manages conversation history and context for better AI interactions.
    """
    
    def __init__(self, max_history: int = 10, max_tokens: int = 2000):
        """
        Initialize the ConversationBuffer.
        
        Args:
            max_history (int): Maximum number of conversation turns to remember
            max_tokens (int): Maximum tokens to include in context
        """
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.conversations = {}  # Store multiple conversations by session_id
    
    # Add a new interaction to the conversation buffer
    def add_interaction(self, 
                       session_id: str, 
                       user_message: str, 
                       ai_response: str, 
                       context_chunks: List[str] = None,
                       metadata: Dict[str, Any] = None) -> None:
        """
        Add a new interaction to the conversation buffer.
        
        Args:
            session_id (str): Unique identifier for the conversation session
            user_message (str): User's question or input
            ai_response (str): AI's response
            context_chunks (List[str]): Document chunks used for context
            metadata (Dict[str, Any]): Additional metadata (document name, timestamp, etc.)
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        # Create a new interaction dictionary
        interaction = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response,
            "context_chunks": context_chunks or [],
            "metadata": metadata or {}
        }
        
        # Add to conversation history
        self.conversations[session_id].append(interaction)
        
        # Maintain max history limit
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
    
    # Get conversation context for AI processing
    def get_conversation_context(self, 
                                session_id: str, 
                                include_context: bool = True,
                                max_interactions: int = 5) -> str:
        """
        Get conversation context for AI processing.
        
        Args:
            session_id (str): Conversation session ID
            include_context (bool): Whether to include document context
            max_interactions (int): Maximum interactions to include
            
        Returns:
            str: Formatted conversation context
        """
        if session_id not in self.conversations:
            return ""
        # Get the last max_interactions interactions
        conversation = self.conversations[session_id][-max_interactions:]
        context_parts = []
        
        for interaction in conversation:
            # Add user message and AI response
            context_parts.append(f"User: {interaction['user_message']}")
            context_parts.append(f"Assistant: {interaction['ai_response']}")
            
            # Add document context if requested
            if include_context and interaction['context_chunks']:
                context_text = " ".join(interaction['context_chunks'][:2])  # Limit context chunks
                context_parts.append(f"Context: {context_text[:200]}...")
        
        return "\n\n".join(context_parts)
    
    # Get recent conversation interactions for context
    def get_recent_context(self, 
                          session_id: str, 
                          num_interactions: int = 3) -> List[Dict[str, Any]]:
        """
        Get recent conversation interactions for context.
        
        Args:
            session_id (str): Conversation session ID
            num_interactions (int): Number of recent interactions to return
            
        Returns:
            List[Dict[str, Any]]: Recent interactions
        """
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id][-num_interactions:]
    
    # Get a summary of the conversation
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the conversation.
        
        Args:
            session_id (str): Conversation session ID
            
        Returns:
            Dict[str, Any]: Conversation summary
        """
        if session_id not in self.conversations:
            return {
                "session_id": session_id,
                "total_interactions": 0,
                "start_time": None,
                "end_time": None,
                "topics_discussed": [],
                "documents_referenced": set()
            }
        
        conversation = self.conversations[session_id]
        
        if not conversation:
            return {
                "session_id": session_id,
                "total_interactions": 0,
                "start_time": None,
                "end_time": None,
                "topics_discussed": [],
                "documents_referenced": set()
            }
        
        # Extract metadata from the conversation interactions 
        documents_referenced = set()
        for interaction in conversation:
            if 'metadata' in interaction and 'document_name' in interaction['metadata']: #metadata is a dictionary that contains the document name
                documents_referenced.add(interaction['metadata']['document_name'])
        
        return {
            "session_id": session_id,
            "total_interactions": len(conversation),
            "start_time": conversation[0]['timestamp'],
            "end_time": conversation[-1]['timestamp'],
            "topics_discussed": [interaction['user_message'][:50] + "..." for interaction in conversation],
            "documents_referenced": list(documents_referenced)
        }
    
    # Clear a specific conversation
    def clear_conversation(self, session_id: str) -> None:
        """
        Clear a specific conversation.
        
        Args:
            session_id (str): Conversation session ID to clear
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    # Clear all conversations
    def clear_all_conversations(self) -> None:
        """Clear all conversations."""
        self.conversations.clear()
    
    def get_all_sessions(self) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List[str]: List of session IDs
        """
        return list(self.conversations.keys())
    
    # Export a conversation to a specific format
    def export_conversation(self, session_id: str, format: str = "json") -> str:
        """
        Export a conversation to a specific format.
        
        Args:
            session_id (str): Conversation session ID
            format (str): Export format ("json" or "text")
            
        Returns:
            str: Exported conversation
        """
        if session_id not in self.conversations:
            return ""
        
        conversation = self.conversations[session_id]
        
        if format == "json":
            return json.dumps(conversation, indent=2)
        elif format == "text":
            text_parts = []
            for interaction in conversation:
                text_parts.append(f"Timestamp: {interaction['timestamp']}")
                text_parts.append(f"User: {interaction['user_message']}")
                text_parts.append(f"Assistant: {interaction['ai_response']}")
                text_parts.append("-" * 50)
            return "\n".join(text_parts)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def search_conversation(self, 
                           session_id: str, 
                           query: str, 
                           case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search within a conversation for specific terms.
        
        Args:
            session_id (str): Conversation session ID
            query (str): Search query
            case_sensitive (bool): Whether search should be case sensitive
            
        Returns:
            List[Dict[str, Any]]: Matching interactions
        """
        if session_id not in self.conversations:
            return []
        
        conversation = self.conversations[session_id]
        matches = []
        
        search_query = query if case_sensitive else query.lower()
        
        for interaction in conversation:
            user_msg = interaction['user_message']
            ai_response = interaction['ai_response']
            
            if not case_sensitive:
                user_msg = user_msg.lower()
                ai_response = ai_response.lower()
            
            if search_query in user_msg or search_query in ai_response:
                matches.append(interaction)
        
        return matches

# Global instance for easy access
# this is a global instance of the ConversationBuffer class
conversation_buffer = ConversationBuffer() 

# Helper functions for backward compatibility
## Backward compatible means your changes don’t break or negatively affect the existing functionality
def add_interaction(session_id: str, user_message: str, ai_response: str, 
                   context_chunks: List[str] = None, metadata: Dict[str, Any] = None) -> None:
    """Backward compatibility function."""
    conversation_buffer.add_interaction(session_id, user_message, ai_response, context_chunks, metadata)


def get_conversation_context(session_id: str, include_context: bool = True, 
                           max_interactions: int = 5) -> str:
    """Backward compatibility function."""
    return conversation_buffer.get_conversation_context(session_id, include_context, max_interactions)


def get_conversation_summary(session_id: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    return conversation_buffer.get_conversation_summary(session_id) 