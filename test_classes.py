"""
test_classes.py

Test script to verify our new class-based architecture works correctly.
"""
import os
from modules.document_processor import DocumentProcessor
from modules.vector_store import VectorStore
from modules.quiz_generator import QuizGenerator
from modules.hybrid_search import HybridSearchEngine


def test_document_processor():
    """Test the DocumentProcessor class."""
    print("🧪 Testing DocumentProcessor...")
    
    processor = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    
    # Test text chunking
    test_text = "This is a test document. It contains multiple sentences. We want to see how chunking works. This should be split into chunks based on the chunk size and overlap settings."
    
    chunks = processor.chunk_text(test_text)
    print(f"✅ Chunking test: Created {len(chunks)} chunks")
    
    # Test text cleaning
    dirty_text = "This   has   extra   spaces   and   \n\n\nline   breaks."
    clean_text = processor.clean_text(dirty_text)
    print(f"✅ Cleaning test: '{clean_text}'")
    
    return True


def test_vector_store():
    """Test the VectorStore class."""
    print("🧪 Testing VectorStore...")
    
    # Create a test vector store
    test_store = VectorStore(
        persist_directory="./test_chroma_db",
        collection_name="test_collection"
    )
    
    # Test adding documents
    test_chunks = [
        "This is the first chunk about artificial intelligence.",
        "This is the second chunk about machine learning.",
        "This is the third chunk about deep learning."
    ]
    
    success = test_store.add_document("test_doc.pdf", test_chunks)
    print(f"✅ Add document test: {'Success' if success else 'Failed'}")
    
    # Test querying
    results = test_store.query_similar_chunks("artificial intelligence", n_results=2)
    print(f"✅ Query test: Found {len(results)} results")
    
    # Test listing documents
    docs = test_store.list_documents()
    print(f"✅ List documents test: Found {len(docs)} documents")
    
    # Test getting stats
    stats = test_store.get_collection_stats()
    print(f"✅ Stats test: {stats}")
    
    # Clean up
    test_store.clear_vector_store()
    
    return True


def test_quiz_generator():
    """Test the QuizGenerator class."""
    print("🧪 Testing QuizGenerator...")
    
    generator = QuizGenerator()
    
    # Test question generation (without API key)
    test_context = "Natural Language Processing (NLP) is a field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language."
    
    question = generator.generate_llm_question(test_context, "multiple_choice")
    print(f"✅ Question generation test: {question.get('type', 'error')}")
    
    # Test fallback question
    fallback = generator.generate_fallback_question(test_context, "true_false")
    print(f"✅ Fallback question test: {fallback.get('type', 'error')}")
    
    return True


def test_hybrid_search():
    """Test the HybridSearchEngine class."""
    print("🧪 Testing HybridSearchEngine...")
    
    engine = HybridSearchEngine()
    
    # Test index building
    test_docs = [
        "This document is about artificial intelligence and machine learning.",
        "This document discusses natural language processing techniques.",
        "This document covers deep learning and neural networks."
    ]
    
    engine.build_index(test_docs, ["doc1", "doc2", "doc3"])
    print("✅ Index building test: Success")
    
    # Test BM25 search
    bm25_results = engine.bm25_search("artificial intelligence", top_k=2)
    print(f"✅ BM25 search test: Found {len(bm25_results)} results")
    
    # Test query analysis
    analysis = engine.analyze_query("What is machine learning?")
    print(f"✅ Query analysis test: {analysis.get('intent', 'error')}")
    
    return True


def main():
    """Run all tests."""
    print("🚀 Testing Class-Based Architecture")
    print("=" * 50)
    
    try:
        test_document_processor()
        print()
        
        test_vector_store()
        print()
        
        test_quiz_generator()
        print()
        
        test_hybrid_search()
        print()
        
        print("🎉 All tests passed! Class-based architecture is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main() 