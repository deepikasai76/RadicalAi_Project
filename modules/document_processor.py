"""
document_processor.py

Provides PDF text extraction and chunking functionality using a class-based approach.
"""
from typing import List, Dict, Optional
import pypdf
import re
import os


class DocumentProcessor:
    """
    Handles PDF document processing, text extraction, and chunking operations.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the DocumentProcessor.
        
        Args:
            chunk_size (int): Size of each text chunk in characters
            chunk_overlap (int): Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                        continue
                
                return text.strip()
                
        except Exception as e:
            raise Exception(f"Failed to process PDF {pdf_path}: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text (str): Text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_single_pdf(self, pdf_path: str) -> List[str]:
        """
        Process a single PDF file: extract, clean, and chunk text.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[str]: List of text chunks
            
        Raises:
            Exception: If processing fails
        """
        try:
            # Extract text
            raw_text = self.extract_text_from_pdf(pdf_path)
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            
            # Chunk text
            chunks = self.chunk_text(cleaned_text)
            
            if not chunks:
                raise Exception(f"No text content extracted from {pdf_path}")
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Failed to process {pdf_path}: {str(e)}")
    
    def process_pdfs(self, pdf_paths: List[str]) -> Dict[str, List[str]]:
        """
        Process multiple PDF files.
        
        Args:
            pdf_paths (List[str]): List of PDF file paths
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping filename to chunks
        """
        results = {}
        
        for pdf_path in pdf_paths:
            try:
                filename = os.path.basename(pdf_path)
                chunks = self.process_single_pdf(pdf_path)
                results[filename] = chunks
                print(f"✅ Successfully processed {filename}: {len(chunks)} chunks")
                
            except Exception as e:
                error_msg = f"ERROR: {str(e)}"
                results[filename] = [error_msg]
                print(f"❌ Failed to process {filename}: {str(e)}")
        
        return results
    
    def get_processing_stats(self, results: Dict[str, List[str]]) -> Dict[str, any]:
        """
        Get statistics about the processing results.
        
        Args:
            results (Dict[str, List[str]]): Processing results
            
        Returns:
            Dict[str, any]: Statistics about processing
        """
        stats = {
            "total_files": len(results),
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "average_chunks_per_file": 0
        }
        
        for filename, chunks in results.items():
            if chunks and not (isinstance(chunks[0], str) and chunks[0].startswith("ERROR:")):
                stats["successful_files"] += 1
                stats["total_chunks"] += len(chunks)
            else:
                stats["failed_files"] += 1
        
        if stats["successful_files"] > 0:
            stats["average_chunks_per_file"] = stats["total_chunks"] / stats["successful_files"]
        
        return stats


# Global instance for backward compatibility
document_processor = DocumentProcessor()


# Backward compatibility functions
def extract_text_from_pdf(pdf_path: str) -> str:
    """Backward compatibility function."""
    return document_processor.extract_text_from_pdf(pdf_path)


def chunk_text(text: str) -> List[str]:
    """Backward compatibility function."""
    return document_processor.chunk_text(text)


def process_pdfs(pdf_paths: List[str]) -> Dict[str, List[str]]:
    """Backward compatibility function."""
    return document_processor.process_pdfs(pdf_paths) 