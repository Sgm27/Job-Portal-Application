import os
import PyPDF2
import re
import logging
from chatbot.chatgpt_helper import analyze_cv_with_gpt
from datetime import datetime
from chatbot.chatgpt_helper import chatgpt_helper

# Cấu hình logger
logger = logging.getLogger(__name__)

def analyze_cv_file(file_path):
    """
    Analyze a CV file and extract relevant information.
    Supports only PDF documents.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"CV file does not exist: {file_path}")
            return "File không tồn tại. Vui lòng tải lên lại CV."
            
        if file_ext == '.pdf':
            return extract_text_from_pdf(file_path)
        else:
            logger.warning(f"Unsupported file format: {file_ext}")
            return "Không hỗ trợ định dạng file này. Vui lòng tải lên file PDF."
    except Exception as e:
        logger.error(f"Error analyzing CV file: {str(e)}")
        return f"Có lỗi khi phân tích CV: {str(e)}"

def analyze_text(text, job_category=None):
    """
    Analyze the text content of a CV.
    Extracts key information and provides analysis.
    
    Args:
        text: The text content to analyze
        job_category: Optional job category to contextualize the analysis
        
    Returns:
        Dict containing analysis results
    """
    try:
        logger.info("Analyzing CV text content")
        
        # Extract basic information
        skills = extract_skills(text)
        education = extract_education(text)
        experience = extract_experience(text)
        
        # Create basic analysis result
        analysis = {
            "skills": skills,
            "education": education,
            "experience": experience,
            "text": text[:1000] + ("..." if len(text) > 1000 else "")  # Include truncated text
        }
        
        logger.info(f"Basic analysis complete. Found {len(skills)} skills.")
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing text content: {str(e)}")
        return {"error": str(e)}

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text, or error message if extraction fails
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        error_message = f"Không thể tìm thấy file PDF tại đường dẫn: {pdf_path}"
        logger.error(error_message)
        return error_message
    
    # Check if file is readable and not empty
    try:
        file_size = os.path.getsize(pdf_path)
        logger.info(f"PDF file size: {file_size} bytes")
        if file_size == 0:
            error_message = "File PDF trống (0 bytes)"
            logger.error(error_message)
            return error_message
    except OSError as e:
        error_message = f"Lỗi khi đọc thông tin file PDF: {str(e)}"
        logger.error(error_message)
        return error_message
    
    try:
        # Try with PyPDF2 first
        logger.info("Trying extraction with PyPDF2")
        
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            logger.info(f"PDF has {num_pages} pages")
            
            if num_pages == 0:
                error_message = "PDF không có trang nào hoặc bị hỏng"
                logger.error(error_message)
                return error_message
                
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        # If PyPDF2 extraction worked and returned good text
        if text and len(text.strip()) > 100:  # At least 100 chars of content
            logger.info(f"PyPDF2 extracted {len(text)} characters")
            return text
            
        # If PyPDF2 did not produce good results, try pdfplumber
        import pdfplumber
        logger.info("Trying extraction with pdfplumber")
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                    
        logger.info(f"pdfplumber extracted {len(text)} characters")
        return text
        
    except Exception as e:
        import traceback
        error_message = f"Không thể trích xuất text từ PDF: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        return error_message

# The following functions can still be used for basic analysis if needed,
# but are no longer part of the main CV analysis flow

def extract_skills(text):
    # Basic skill extraction - replace with more sophisticated logic
    common_skills = [
        "Python", "Java", "JavaScript", "C++", "SQL", "HTML", "CSS", 
        "React", "Angular", "Vue", "Node.js", "Django", "Flask",
        "Machine Learning", "Data Analysis", "AI"
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills

def extract_education(text):
    # Simple education extraction
    education_patterns = [
        r'(?:University|College|Institute|Trường|Đại học).*?(?:of|-).*?[\w\s]+',
        r'(?:Bachelor|Master|PhD|Cử nhân|Thạc sĩ|Tiến sĩ).*?(?:of|-).*?[\w\s]+'
    ]
    
    for pattern in education_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def extract_experience(text):
    # Simple experience extraction
    experience_patterns = [
        r'(?:Experience|Work Experience|Employment|Kinh nghiệm).*?(?:\d+).*?(?:years|năm)',
        r'(?:Company|Công ty).*?:.*?[\w\s]+'
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None
