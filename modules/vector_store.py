"""
vector_store.py

Provides ChromaDB integration and vector storage functionality using a class-based approach.
"""
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
import os


class VectorStore:
    """
    Manages ChromaDB operations, embeddings, and document storage.
    """
    
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 collection_name: str = "documents"):
        """
        Initialize the VectorStore.
        
        Args:
            persist_directory (str): Directory to persist ChromaDB data
            embedding_model (str): SentenceTransformer model name
            collection_name (str): Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model
        try:
            self.embedder = SentenceTransformer(embedding_model)
            print(f"✅ Loaded embedding model: {embedding_model}")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
    
    def add_document(self, filename: str, chunks: List[str], batch_size: int = 256) -> bool:
        """
        Add a document's text chunks and their embeddings to the vector store.
        
        Args:
            filename (str): Name of the document
            chunks (List[str]): List of text chunks
            batch_size (int): Number of chunks to embed at a time
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Filter valid chunks
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, str) and chunk.strip() and not chunk.strip().startswith("ERROR:"):
                valid_chunks.append(chunk.strip())

        if not valid_chunks:
            print(f"Warning: No valid text chunks to embed for {filename}.")
            return False

        all_embeddings = []
        successful_chunks = []

        # Process chunks in batches
        for i in range(0, len(valid_chunks), batch_size):
            batch = valid_chunks[i:i+batch_size]
            
            # Filter batch again for safety
            batch = [b for b in batch if isinstance(b, str) and b.strip()]
            if not batch:
                continue

            try:
                batch_embeddings = self.embedder.encode(batch, show_progress_bar=False)
                all_embeddings.extend(batch_embeddings.tolist())
                successful_chunks.extend(batch)

            except Exception as e:
                print(f"Warning: Failed to embed batch {i}-{i+batch_size}: {e}")
                continue

        if not successful_chunks:
            print(f"Warning: No chunks were successfully embedded for {filename}")
            return False

        # Prepare metadata and IDs
        ids = [f"{filename}_{i}" for i in range(len(successful_chunks))]
        metadatas = [{"filename": filename, "chunk_id": i} for i in range(len(successful_chunks))]

        # Add to collection
        try:
            self.collection.add(
                documents=successful_chunks,
                metadatas=metadatas,
                ids=ids,
                embeddings=all_embeddings
            )
            
            print(f"✅ Added {len(successful_chunks)} chunks from '{filename}' to vector store")
            
            # Initialize hybrid search with new documents
            try:
                from .hybrid_search import initialize_hybrid_search
                initialize_hybrid_search(successful_chunks, ids)
            except Exception as e:
                # Silently fail if hybrid search initialization fails
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add document to vector store: {e}")
            return False
    
    def query_similar_chunks(self, 
                           query: str, 
                           n_results: int = 5, 
                           filename: Optional[str] = None) -> List[Dict]:
        """
        Query the vector store for similar chunks.
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
            filename (Optional[str]): Filter by specific document
            
        Returns:
            List[Dict]: List of similar chunks with metadata
        """
        try:
            # Create query filter if filename is specified
            where_filter = {"filename": filename} if filename else None
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "document": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
    
    def list_documents(self) -> List[str]:
        """
        Get list of all documents in the vector store.
        
        Returns:
            List[str]: List of document filenames
        """
        try:
            # Get all documents from collection
            results = self.collection.get()
            
            if not results['metadatas']:
                return []
            
            # Extract unique filenames
            filenames = set()
            for metadata in results['metadatas']:
                if metadata and 'filename' in metadata:
                    filenames.add(metadata['filename'])
            
            return sorted(list(filenames))
            
        except Exception as e:
            print(f"❌ Failed to list documents: {e}")
            return []
    
    def delete_document(self, filename: str) -> bool:
        """
        Delete a document and all its chunks from the vector store.
        
        Args:
            filename (str): Name of the document to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all IDs for this document
            results = self.collection.get(where={"filename": filename})
            
            if not results['ids']:
                print(f"Document '{filename}' not found in vector store")
                return False
            
            # Delete all chunks for this document
            self.collection.delete(ids=results['ids'])
            
            print(f"✅ Deleted document '{filename}' from vector store")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete document: {e}")
            return False
    
    def get_document_stats(self, filename: str) -> Dict[str, Any]:
        """
        Get statistics about a specific document.
        
        Args:
            filename (str): Name of the document
            
        Returns:
            Dict[str, Any]: Document statistics
        """
        try:
            results = self.collection.get(where={"filename": filename})
            
            stats = {
                "filename": filename,
                "chunk_count": len(results['ids']) if results['ids'] else 0,
                "total_characters": 0,
                "average_chunk_length": 0
            }
            
            if results['documents']:
                total_chars = sum(len(doc) for doc in results['documents'])
                stats["total_characters"] = total_chars
                stats["average_chunk_length"] = total_chars / len(results['documents'])
            
            return stats
            
        except Exception as e:
            print(f"❌ Failed to get document stats: {e}")
            return {"filename": filename, "error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics about the vector store.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            results = self.collection.get()
            
            stats = {
                "total_chunks": len(results['ids']) if results['ids'] else 0,
                "total_documents": len(set(m.get('filename', '') for m in results['metadatas'] if m)),
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def refresh_vector_store(self) -> bool:
        """
        Refresh the vector store (reload collection).
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print("✅ Vector store refreshed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to refresh vector store: {e}")
            return False
    
    def clear_vector_store(self) -> bool:
        """
        Clear all data from the vector store.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
            print("✅ Vector store cleared successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to clear vector store: {e}")
            return False
    
    def get_document_chunks(self, filename: str) -> List[str]:
        """
        Get all chunks for a specific document.
        
        Args:
            filename (str): Name of the document
            
        Returns:
            List[str]: List of document chunks
        """
        try:
            results = self.collection.get(where={"filename": filename})
            return results['documents'] if results['documents'] else []
        except Exception as e:
            print(f"❌ Failed to get document chunks: {e}")
            return []


# Global instance for backward compatibility
vector_store = VectorStore()


# Backward compatibility functions
def add_document(filename: str, chunks: List[str], batch_size: int = 256) -> None:
    vector_store.add_document(filename, chunks, batch_size)

def query_similar_chunks(query: str, n_results: int = 5, filename: Optional[str] = None) -> List[Dict]:
    return vector_store.query_similar_chunks(query, n_results, filename)

def list_documents() -> List[str]:
    return vector_store.list_documents()

def delete_document(filename: str) -> None:
    vector_store.delete_document(filename)

def refresh_vector_store() -> None:
    vector_store.refresh_vector_store() 