"""
test_conversation_buffer.py

Test script to demonstrate the conversation buffer functionality.
"""
from modules.conversation_buffer import ConversationBuffer


def test_conversation_buffer():
    """Test the ConversationBuffer functionality."""
    print("🧪 Testing Conversation Buffer...")
    
    # Create a conversation buffer
    buffer = ConversationBuffer(max_history=5)
    
    # Simulate a conversation about NLP
    session_id = "test_session_123"
    
    # Add interactions
    buffer.add_interaction(
        session_id=session_id,
        user_message="What is Natural Language Processing?",
        ai_response="Natural Language Processing (NLP) is a field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language.",
        metadata={"document_name": "NLP_Guide.pdf", "topic": "definition"}
    )
    
    buffer.add_interaction(
        session_id=session_id,
        user_message="What are its main applications?",
        ai_response="NLP has many applications including machine translation, sentiment analysis, chatbots, text summarization, and question answering systems.",
        metadata={"document_name": "NLP_Guide.pdf", "topic": "applications"}
    )
    
    buffer.add_interaction(
        session_id=session_id,
        user_message="How does it work with transformers?",
        ai_response="Transformers use attention mechanisms to process text sequences, allowing them to understand context and relationships between words better than previous models.",
        metadata={"document_name": "NLP_Guide.pdf", "topic": "transformers"}
    )
    
    # Test conversation context
    print("📝 Testing conversation context...")
    context = buffer.get_conversation_context(session_id, include_context=True, max_interactions=3)
    print(f"Context length: {len(context)} characters")
    print(f"Context preview: {context[:200]}...")
    
    # Test conversation summary
    print("\n📊 Testing conversation summary...")
    summary = buffer.get_conversation_summary(session_id)
    print(f"Total interactions: {summary['total_interactions']}")
    print(f"Documents referenced: {summary['documents_referenced']}")
    print(f"Topics discussed: {summary['topics_discussed']}")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    search_results = buffer.search_conversation(session_id, "transformers")
    print(f"Found {len(search_results)} interactions containing 'transformers'")
    
    # Test export functionality
    print("\n📤 Testing export functionality...")
    export_text = buffer.export_conversation(session_id, format="text")
    print(f"Export length: {len(export_text)} characters")
    
    print("\n✅ Conversation buffer test completed successfully!")
    
    return True


def test_multiple_sessions():
    """Test multiple conversation sessions."""
    print("\n🧪 Testing Multiple Sessions...")
    
    buffer = ConversationBuffer(max_history=3)
    
    # Session 1: NLP conversation
    session1 = "nlp_session"
    buffer.add_interaction(session1, "What is NLP?", "NLP is natural language processing.")
    buffer.add_interaction(session1, "Give examples", "Examples include translation and chatbots.")
    
    # Session 2: ML conversation
    session2 = "ml_session"
    buffer.add_interaction(session2, "What is ML?", "ML is machine learning.")
    buffer.add_interaction(session2, "Types of ML?", "Supervised, unsupervised, and reinforcement learning.")
    
    # Check all sessions
    all_sessions = buffer.get_all_sessions()
    print(f"Active sessions: {all_sessions}")
    
    # Test session isolation
    context1 = buffer.get_conversation_context(session1)
    context2 = buffer.get_conversation_context(session2)
    
    print(f"Session 1 context length: {len(context1)}")
    print(f"Session 2 context length: {len(context2)}")
    
    print("✅ Multiple sessions test completed!")
    
    return True


def main():
    """Run all conversation buffer tests."""
    print("🚀 Testing Conversation Buffer System")
    print("=" * 50)
    
    try:
        test_conversation_buffer()
        test_multiple_sessions()
        
        print("\n🎉 All conversation buffer tests passed!")
        print("\n💡 Key Features Demonstrated:")
        print("✅ Conversation memory and context")
        print("✅ Multi-session support")
        print("✅ Search functionality")
        print("✅ Export capabilities")
        print("✅ Conversation summaries")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main() 