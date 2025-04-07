"""
CV Analyzer module for extracting text from PDF files and detecting language
"""

import io
import logging
import tempfile
import os
from langdetect import detect
import PyPDF2

# Try importing pdfplumber as a fallback option
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# Configure logging
logger = logging.getLogger(__name__)

class CVAnalyzer:
    """
    Class for analyzing CVs/Resumes
    - Extracts text from PDF files
    - Detects language
    """
    
    def extract_text_from_pdf_pypdf(self, file_stream):
        """Extract text from PDF using PyPDF2"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF with PyPDF2: {str(e)}")
            return None
    
    def extract_text_from_pdf_pdfplumber(self, file_path):
        """Extract text from PDF using pdfplumber"""
        if not HAS_PDFPLUMBER:
            return None
        
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n"
                
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF with pdfplumber: {str(e)}")
            return None
    
    def detect_language(self, text):
        """Detect language of the text"""
        try:
            if not text or len(text.strip()) < 20:
                # Default to English if text is too short
                return 'en'
            
            # Detect language
            detected = detect(text)
            return detected
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'en'  # Default to English
    
    def analyze_cv(self, file_path=None, django_file=None):
        """
        Extract text from a CV/Resume file and detect language
        
        Args:
            file_path: Path to the CV file (optional)
            django_file: Django FieldFile object (optional)
            
        Returns:
            dict with:
                success: Boolean indicating success
                text_content: Extracted text (if successful)
                language: Detected language code (if successful)
                error: Error message (if failed)
        """
        text_content = None
        
        try:
            # Case 1: Django file object passed
            if django_file:
                # First attempt: PyPDF2
                django_file.seek(0)
                text_content = self.extract_text_from_pdf_pypdf(django_file)
                
                # If PyPDF2 fails, try pdfplumber
                if not text_content and HAS_PDFPLUMBER:
                    django_file.seek(0)
                    
                    # pdfplumber requires a file path, so save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_path = temp_file.name
                        for chunk in django_file.chunks():
                            temp_file.write(chunk)
                    
                    # Extract with pdfplumber
                    text_content = self.extract_text_from_pdf_pdfplumber(temp_path)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
            
            # Case 2: File path provided
            elif file_path:
                # First attempt: PyPDF2
                with open(file_path, 'rb') as file:
                    text_content = self.extract_text_from_pdf_pypdf(file)
                
                # If PyPDF2 fails, try pdfplumber
                if not text_content and HAS_PDFPLUMBER:
                    text_content = self.extract_text_from_pdf_pdfplumber(file_path)
            
            # If we still don't have text, return an error
            if not text_content:
                return {
                    'success': False,
                    'error': 'Failed to extract text from PDF'
                }
            
            # Detect language
            language = self.detect_language(text_content)
            
            return {
                'success': True,
                'text_content': text_content,
                'language': language
            }
            
        except Exception as e:
            error_message = f"Error analyzing CV: {str(e)}"
            logger.error(error_message)
            
            return {
                'success': False,
                'error': error_message
            }

# Create a singleton instance for use throughout the application
cv_analyzer = CVAnalyzer()