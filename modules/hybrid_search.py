"""
hybrid_search.py

Advanced hybrid search combining BM25 keyword search with vector search.
"""
from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import openai
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from .vector_store import query_similar_chunks


class HybridSearchEngine:
    """
    Advanced hybrid search engine combining BM25 and vector search.
    """
    
    def __init__(self):
        self.bm25_index = None
        self.documents = []
        self.document_ids = []
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=10000
        )
    
    def build_index(self, documents: List[str], document_ids: List[str] = None):
        """
        Build BM25 index from documents.
        Args:
            documents: List of document texts
            document_ids: Optional list of document IDs
        """
        self.documents = documents
        self.document_ids = document_ids or [f"doc_{i}" for i in range(len(documents))]
        
        # Tokenize documents for BM25
        tokenized_docs = [self._tokenize(doc) for doc in documents]
        self.bm25_index = BM25Okapi(tokenized_docs)
        
        # Build TF-IDF for additional features
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25 indexing."""
        # Simple tokenization - can be enhanced with NLTK/spaCy
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [token for token in tokens if len(token) > 2]
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query intent using LLM.
        Args:
            query: User query
        Returns:
            Dict with query analysis
        """
        if not client.api_key:
            # Fallback analysis
            return self._simple_query_analysis(query)
        
        try:
            prompt = f"""
            Analyze this query and provide search strategy:
            Query: "{query}"
            
            Return JSON with:
            - intent: "definition", "comparison", "how_to", "factual", "conceptual"
            - keywords: list of important terms
            - search_weights: {{"semantic": 0.7, "keyword": 0.3}}
            - query_type: "specific" or "general"
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a search query analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            return self._simple_query_analysis(query)
    
    def _simple_query_analysis(self, query: str) -> Dict:
        """Simple fallback query analysis."""
        keywords = self._tokenize(query)
        
        # Simple heuristics
        if any(word in query.lower() for word in ['what', 'define', 'definition']):
            intent = "definition"
            weights = {"semantic": 0.6, "keyword": 0.4}
        elif any(word in query.lower() for word in ['how', 'process', 'steps']):
            intent = "how_to"
            weights = {"semantic": 0.8, "keyword": 0.2}
        else:
            intent = "factual"
            weights = {"semantic": 0.7, "keyword": 0.3}
        
        return {
            "intent": intent,
            "keywords": keywords,
            "search_weights": weights,
            "query_type": "specific" if len(keywords) <= 3 else "general"
        }
    
    def bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Perform BM25 keyword search.
        Args:
            query: Search query
            top_k: Number of results to return
        Returns:
            List of search results with scores
        """
        if not self.bm25_index:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top-k results
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include relevant results
                results.append({
                    "document": self.documents[idx],
                    "document_id": self.document_ids[idx],
                    "score": float(scores[idx]),
                    "search_type": "keyword"
                })
        
        return results
    
    def vector_search(self, query: str, top_k: int = 10, filename: Optional[str] = None) -> List[Dict]:
        """
        Perform vector search using existing vector store.
        Args:
            query: Search query
            top_k: Number of results to return
            filename: Optional document filter
        Returns:
            List of search results with scores
        """
        results = query_similar_chunks(query, n_results=top_k, filename=filename)
        
        # Convert to standard format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document": result["document"],
                "document_id": result["metadata"]["filename"],
                "score": 1.0 - result["distance"],  # Convert distance to similarity score
                "search_type": "semantic"
            })
        
        return formatted_results
    
    def hybrid_search(self, query: str, top_k: int = 10, filename: Optional[str] = None) -> List[Dict]:
        """
        Perform hybrid search combining BM25 and vector search.
        Args:
            query: Search query
            top_k: Number of results to return
            filename: Optional document filter
        Returns:
            List of hybrid search results
        """
        # Analyze query
        analysis = self.analyze_query(query)
        weights = analysis["search_weights"]
        
        # Perform both searches
        bm25_results = self.bm25_search(query, top_k=top_k*2)
        vector_results = self.vector_search(query, top_k=top_k*2, filename=filename)
        
        # Combine and rerank results
        combined_results = self._combine_results(
            bm25_results, vector_results, weights, top_k
        )
        
        return combined_results
    
    def _combine_results(self, bm25_results: List[Dict], vector_results: List[Dict], 
                        weights: Dict, top_k: int) -> List[Dict]:
        """
        Combine and rerank results from both search methods.
        """
        # Create document lookup
        doc_scores = {}
        
        # Process BM25 results
        for result in bm25_results:
            doc_id = result["document_id"]
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    "document": result["document"],
                    "bm25_score": result["score"],
                    "vector_score": 0.0,
                    "combined_score": 0.0
                }
        
        # Process vector results
        for result in vector_results:
            doc_id = result["document_id"]
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    "document": result["document"],
                    "bm25_score": 0.0,
                    "vector_score": result["score"],
                    "combined_score": 0.0
                }
            else:
                doc_scores[doc_id]["vector_score"] = result["score"]
        
        # Calculate combined scores
        for doc_id, scores in doc_scores.items():
            combined = (scores["bm25_score"] * weights["keyword"] + 
                       scores["vector_score"] * weights["semantic"])
            scores["combined_score"] = combined
        
        # Sort by combined score and return top-k
        sorted_results = sorted(
            doc_scores.items(), 
            key=lambda x: x[1]["combined_score"], 
            reverse=True
        )[:top_k]
        
        # Format final results
        final_results = []
        for doc_id, scores in sorted_results:
            final_results.append({
                "document": scores["document"],
                "document_id": doc_id,
                "combined_score": scores["combined_score"],
                "bm25_score": scores["bm25_score"],
                "vector_score": scores["vector_score"],
                "search_type": "hybrid"
            })
        
        return final_results


# Global hybrid search engine instance
hybrid_engine = HybridSearchEngine()


def initialize_hybrid_search(documents: List[str], document_ids: List[str] = None):
    """
    Initialize the hybrid search engine with documents.
    Args:
        documents: List of document texts
        document_ids: Optional list of document IDs
    """
    hybrid_engine.build_index(documents, document_ids)


def hybrid_search(query: str, top_k: int = 10, filename: Optional[str] = None) -> List[Dict]:
    """
    Perform hybrid search.
    Args:
        query: Search query
        top_k: Number of results to return
        filename: Optional document filter
    Returns:
        List of search results
    """
    return hybrid_engine.hybrid_search(query, top_k, filename) 