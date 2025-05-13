import os
import json
import requests
import logging
import openai
from django.conf import settings
from django.core.cache import cache
from datetime import datetime
from .models import Conversation, Message
import re
import time
from accounts.models import Resume

logger = logging.getLogger(__name__)

class ChatGPTHelper:
    """Helper class for interacting with ChatGPT API"""
    
    def __init__(self):
        """Initialize ChatGPT API with credentials from settings"""
        # Try to get API key from settings or environment variables
        try:
            self.api_key = settings.OPENAI_API_KEY
        except AttributeError:
            self.api_key = os.environ.get('OPENAI_API_KEY')
            
        if not self.api_key:
            logger.warning("OpenAI API key not found. ChatGPT functionality will not work.")
            
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
        
        # Configure OpenAI client - support both old and new API formats
        if self.api_key:
            try:
                # Try new client-based API (v1.0.0+)
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Using OpenAI API with new client-based approach")
            except ImportError:
                # Fall back to older module-level API
                openai.api_key = self.api_key
                logger.info("Using OpenAI API with legacy approach")
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
    
    def create_conversation(self, user, title=None):
        """Create a new conversation for a user and return the conversation object."""
        if title is None:
            title = "New Conversation"
        
        conversation = Conversation.objects.create(
            user=user,
            title=title
        )
        
        return conversation
    
    def add_system_message(self, conversation, content):
        """Add a system message to the conversation."""
        message = Message.objects.create(
            conversation=conversation,
            role='system',
            content=content
        )
        return message
    
    def add_user_message(self, conversation, content):
        """Add a user message to the conversation."""
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
        return message
    
    def add_assistant_message(self, conversation, content):
        """Add an assistant message to the conversation."""
        message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=content
        )
        return message
    
    def get_messages(self, conversation):
        """Get all messages for a conversation in chronological order."""
        return conversation.messages.order_by('timestamp')
    
    def build_messages_payload(self, conversation):
        """Build the messages payload for the ChatGPT API from the conversation history."""
        messages = self.get_messages(conversation)
        
        # Format messages for the OpenAI API
        payload = []
        for message in messages:
            payload.append({
                'role': message.role,
                'content': message.content
            })
        
        return payload
    
    def send_message(self, conversation, message_content):
        """
        Send a message to ChatGPT and save the response.
        
        Args:
            conversation: Conversation object
            message_content: The user's message content
            
        Returns:
            dict: Response containing success flag and assistant message or error
        """
        # Add user message to conversation
        self.add_user_message(conversation, message_content)
        
        try:
            # Build messages payload from conversation history
            messages = self.build_messages_payload(conversation)
            
            # Make API call to ChatGPT
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            
            # Extract assistant's response
            assistant_message = response.choices[0].message.content
            
            # Add assistant's response to conversation
            self.add_assistant_message(conversation, assistant_message)
            
            return {
                "success": True,
                "message": assistant_message
            }
            
        except Exception as e:
            error_message = f"Error calling ChatGPT API: {str(e)}"
            self.logger.error(error_message)
            
            return {
                "success": False,
                "error": error_message
            }
    
    def generate_response(self, messages, model="chatgpt-4o", temperature=0.7, max_tokens=1000):
        """
        Generate a response from ChatGPT
        
        Args:
            messages: List of message objects (role, content)
            model: Model to use (default: chatgpt-4o)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (default: 1000)
            
        Returns:
            dict with:
                success: Boolean indicating success
                response: Generated response text (if successful)
                error: Error message (if failed)
        """
        if not self.api_key:
            logger.error("API key not configured - cannot generate response")
            return {
                'success': False,
                'error': 'OpenAI API key is not configured'
            }
            
        try:
            logger.info(f"Calling OpenAI API with model: {model}, temperature: {temperature}, max_tokens: {max_tokens}")
            
            # Use the client-based approach instead of the deprecated module-level functions
            try:
                # Try with new OpenAI client approach first
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response_text = response.choices[0].message.content.strip()
            except ImportError:
                # Fallback to older approach if needed
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response_text = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'response': response_text
            }
            
        except Exception as e:
            error_message = f"Error generating ChatGPT response: {str(e)}"
            logger.error(error_message)
            
            # Determine type of error from exception class name
            error_class = e.__class__.__name__
            
            if 'AuthenticationError' in error_class:
                return {
                    'success': False,
                    'error': 'API key is invalid or expired. Please contact the administrator.'
                }
            elif 'InvalidRequestError' in error_class:
                return {
                    'success': False,
                    'error': f'Invalid request: {str(e)}'
                }
            elif 'RateLimitError' in error_class:
                return {
                    'success': False,
                    'error': 'OpenAI API rate limit exceeded. Please try again later.'
                }
            else:
                return {
                    'success': False,
                    'error': error_message
                }
    
    def analyze_cv_with_markdown(self, cv_text, job_title=None, language='en'):
        """
        Analyze CV/Resume text and provide feedback in Markdown format
        
        Args:
            cv_text: Text extracted from the CV/Resume
            job_title: Optional job title to target the analysis for
            language: Language code of the CV ('en', 'vi', etc.)
            
        Returns:
            dict with:
                success: Boolean indicating success
                analysis_markdown: Analysis in Markdown format (if successful)
                language: Language code used for the analysis
                error: Error message (if failed)
        """
        try:
            # Generate a unique cache key for this CV text and job title
            import hashlib
            cache_key = f"cv_analysis_{hashlib.md5((cv_text + str(job_title or '') + language).encode()).hexdigest()}"
            
            # Try to get cached result
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached CV analysis for key: {cache_key[:10]}...")
                return cached_result
            
            # CV not in cache, perform new analysis
            logger.info(f"No cached analysis found. Performing new analysis for CV with {len(cv_text)} characters")
            
            # Determine system message based on language
            system_message = {
                'role': 'system',
                'content': ''
            }
            
            if language == 'vi':
                system_message['content'] = """
                Bạn là một chuyên gia tuyển dụng IT hàng đầu với hơn 20 năm kinh nghiệm đánh giá CV.
                Phân tích CV được cung cấp một cách NHANH CHÓNG, CHÍNH XÁC và CHUYÊN SÂU.
                
                Trả lời theo cấu trúc sau một cách ngắn gọn nhưng đầy đủ thông tin:
                
                ## 1. Tổng quan hồ sơ
                *Tóm tắt nhanh về ấn tượng tổng thể, kinh nghiệm và trình độ của ứng viên.*
                
                ## 2. Kỹ năng chuyên môn
                *Liệt kê chính xác 5-7 kỹ năng quan trọng nhất trong CV và đánh giá trình độ (Beginner/Intermediate/Advanced/Expert).*
                
                ## 3. Điểm mạnh nổi bật
                *Liệt kê súc tích 3-4 điểm mạnh quan trọng nhất với giải thích ngắn gọn tại sao đây là lợi thế.*
                
                ## 4. Điểm yếu cần cải thiện
                *Chỉ ra 2-3 điểm yếu chính với đề xuất cải thiện cụ thể.*
                
                ## 5. Kiến thức cần bổ sung
                *Đề xuất 3-4 lĩnh vực/công nghệ cụ thể ứng viên nên học thêm dựa trên xu hướng thị trường hiện tại.*
                
                ## 6. Đề xuất cải thiện CV
                *Đưa ra 3-5 gợi ý cụ thể để cải thiện CV.*
                
                ## 7. Phân tích mức độ phù hợp
                *Đánh giá nhanh về vị trí phù hợp nhất và cho điểm cạnh tranh (thang /10).*
                
                TRẢ LỜI NGẮn GỌN, SÚCÍCH, ĐÚNG TRỌNG TÂM, KHÔNG THỪA TỪ.
                Sử dụng định dạng Markdown để dễ đọc (headings, bold, bullet points).
                """
            else:  # Default to English
                system_message['content'] = """
                You are an elite IT recruitment expert with 20+ years of CV evaluation experience.
                Analyze the provided CV QUICKLY, ACCURATELY, and THOROUGHLY.
                
                Follow this precise structure with concise but complete information:
                
                ## 1. Profile Overview
                *Quick summary of the overall impression, experience, and qualifications.*
                
                ## 2. Technical Skills Analysis
                *List exactly 5-7 most important skills in the CV and assess proficiency (Beginner/Intermediate/Advanced/Expert).*
                
                ## 3. Notable Strengths
                *Concisely list 3-4 most important strengths with brief explanation of why these are advantages.*
                
                ## 4. Areas for Improvement
                *Identify 2-3 main weaknesses with specific improvement suggestions.*
                
                ## 5. Knowledge Gaps to Fill
                *Suggest 3-4 specific areas/technologies the candidate should learn based on current market trends.*
                
                ## 6. CV Improvement Suggestions
                *Provide 3-5 specific suggestions to improve the CV.*
                
                ## 7. Career Fit Analysis
                *Quick assessment of most suitable positions and competitive score (out of 10).*
                
                RESPOND CONCISELY, PRECISELY, ON POINT, NO WASTED WORDS.
                Use Markdown formatting for readability (headings, bold, bullet points).
                """
                
            # Create user message with CV text and optional job title
            user_message = {
                'role': 'user',
                'content': cv_text
            }
            
            # Add job title information if provided
            if job_title:
                if language == 'vi':
                    user_message['content'] += f"\n\nVị trí công việc đang ứng tuyển: {job_title}"
                else:
                    user_message['content'] += f"\n\nJob position being applied for: {job_title}"
            
            # Generate response from ChatGPT
            messages = [system_message, user_message]
            
            # Use GPT-4o directly for best quality and reasonable speed
            logger.info("Analyzing CV with GPT-4o model")
            response = self.generate_response(
                messages=messages,
                model="gpt-4o",  # Always use gpt-4o as requested
                temperature=0.5,  # Lower temperature for more deterministic results
                max_tokens=3000   # Sufficient tokens for comprehensive analysis
            )
            
            if response['success']:
                logger.info("Đã phân tích CV thành công với GPT-4o")
                result = {
                    'success': True,
                    'analysis_markdown': response['response'],
                    'language': language
                }
                # Cache the result for 24 hours (86400 seconds)
                cache.set(cache_key, result, 86400)
                return result
            else:
                error_msg = response.get('error', 'Unknown error')
                logger.error(f"GPT-4o analysis failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'language': language
                }
            
        except Exception as e:
            import traceback
            error_message = f"Error analyzing CV: {str(e)}"
            logger.error(error_message)
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': error_message,
                'language': language
            }
    
    def ask_gpt(self, prompt, model=None, temperature=None, max_tokens=1000):
        """
        Simple method to ask a single question to ChatGPT and get a text response
        
        Args:
            prompt: The question or prompt to send to ChatGPT
            model: Model to use (defaults to self.model)
            temperature: Sampling temperature (defaults to self.temperature)
            max_tokens: Maximum tokens in response (default: 1000)
            
        Returns:
            str: Response text from ChatGPT, or error message if failed
        """
        if not self.api_key:
            return "Error: OpenAI API key is not configured"
            
        try:
            model = model or self.model
            temperature = temperature or self.temperature
            
            logger.info(f"Calling ask_gpt with model={model}, temp={temperature}, max_tokens={max_tokens}")
            
            # System prompt updated to focus on information accuracy for technology and career development
            system_prompt = """Bạn là trợ lý AI chuyên nghiệp cung cấp thông tin chính xác về công nghệ và phát triển nghề nghiệp.

Quy tắc khi trả lời:
- Luôn trả lời ngắn gọn, đi thẳng vào trọng tâm câu hỏi
- Tránh dùng các câu mở đầu, kết luận không cần thiết
- Ưu tiên thông tin chính xác, cập nhật, khách quan
- Sử dụng cấu trúc gạch đầu dòng khi liệt kê
- Nếu câu hỏi đơn giản, trả lời trong 1-3 câu
- Chỉ trình bày nội dung thực sự quan trọng và liên quan
- Không nhắc lại câu hỏi trong câu trả lời"""
            
            # Tạo messages array với system prompt và câu hỏi hiện tại
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Use the client-based approach instead of the deprecated module-level functions
            try:
                # Try with new OpenAI client approach first
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content.strip()
            except ImportError:
                # Fallback to older approach if needed
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_message = f"Error calling ChatGPT API: {str(e)}"
            logger.error(error_message)
            return f"Error: {error_message}"

    def analyze_resume_for_chatbot(self, user, resume_id=None):
        """
        Phân tích CV cho chatbot, cho phép phân tích CV cụ thể của người dùng
        
        Args:
            user: User object của người đang chat
            resume_id: ID của CV cần phân tích (None nếu chưa chọn)
            
        Returns:
            dict với các thông tin:
                success: True/False
                resumes: Danh sách CV của người dùng (nếu resume_id=None)
                analysis: Kết quả phân tích (nếu có resume_id)
                error: Thông báo lỗi (nếu có)
        """
        try:
            # 1. Nếu không có resume_id, trả về danh sách CV để người dùng chọn
            if not resume_id:
                user_resumes = Resume.objects.filter(user=user).order_by('-uploaded_at')
                if not user_resumes.exists():
                    return {
                        'success': False,
                        'error': 'Bạn chưa tải lên CV nào. Vui lòng tải CV trước khi phân tích.',
                        'resumes': []
                    }
                
                # Trả về danh sách CV để hiển thị trong chatbot
                resumes_data = []
                for resume in user_resumes:
                    resumes_data.append({
                        'id': resume.id,
                        'title': resume.title,
                        'uploaded_at': resume.uploaded_at.strftime('%d/%m/%Y'),
                        'is_primary': resume.is_primary
                    })
                
                return {
                    'success': True,
                    'resumes': resumes_data,
                    'message': 'Vui lòng chọn CV bạn muốn phân tích:'
                }
            
            # 2. Nếu có resume_id, tiến hành phân tích CV đó
            try:
                resume = Resume.objects.get(id=resume_id, user=user)
            except Resume.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Không tìm thấy CV này hoặc bạn không có quyền truy cập.'
                }
            
            # Tiến hành phân tích CV
            from app.services.cv_analyzer import extract_text_from_pdf
            
            # Kiểm tra xem file có tồn tại không
            import os
            
            # Log thông tin file để debug
            logger.info(f"Resume file path: {resume.file.path}")
            logger.info(f"Resume file exists: {os.path.exists(resume.file.path)}")
            logger.info(f"Resume file size: {os.path.getsize(resume.file.path) if os.path.exists(resume.file.path) else 'N/A'}")
            
            if not os.path.exists(resume.file.path):
                # Thử lấy đường dẫn URL
                file_url = resume.file.url
                logger.info(f"Trying file URL: {file_url}")
                
                # Nhận đường dẫn tuyệt đối từ URL
                from django.conf import settings
                import os
                media_root = settings.MEDIA_ROOT
                media_url = settings.MEDIA_URL
                
                # Chuyển URL thành đường dẫn file tương đối
                relative_path = file_url.replace(media_url, '')
                absolute_path = os.path.join(media_root, relative_path)
                
                logger.info(f"Converted path: {absolute_path}")
                
                if os.path.exists(absolute_path):
                    # Sử dụng đường dẫn thay thế
                    file_path = absolute_path
                    logger.info(f"Using alternative path: {file_path}")
                else:
                    return {
                        'success': False,
                        'error': f'File CV không tồn tại hoặc đã bị xóa. Đường dẫn: {resume.file.path}'
                    }
            else:
                file_path = resume.file.path
            
            # Trích xuất văn bản từ CV
            cv_text = extract_text_from_pdf(file_path)
            if not cv_text or cv_text.startswith("Error") or cv_text.startswith("Không thể"):
                logger.error(f"Failed to extract text from PDF: {cv_text}")
                return {
                    'success': False,
                    'error': cv_text or 'Không thể trích xuất văn bản từ PDF. Vui lòng đảm bảo file PDF hợp lệ.'
                }
            
            # Log số lượng ký tự trích xuất được để debug
            logger.info(f"Extracted {len(cv_text)} characters from PDF")
            logger.info(f"First 100 chars: {cv_text[:100]}...")
            
            # Sử dụng hàm phân tích CV đã tối ưu
            analysis_result = analyze_cv_with_gpt(cv_text, language='vi')
            
            # Kiểm tra kết quả
            if not analysis_result.get('success', False):
                error_msg = analysis_result.get('error', 'Lỗi không xác định khi phân tích CV')
                logger.error(f"Analysis failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Trả về kết quả phân tích
            logger.info("Quá trình phân tích CV đã hoàn tất thành công")
            return {
                'success': True,
                'resume_info': {
                    'id': resume.id,
                    'title': resume.title
                },
                'analysis': analysis_result.get('analysis_markdown', '')
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Error analyzing resume in chatbot: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': f"Lỗi phân tích CV: {str(e)}"
            }

    def score_cv_for_job(self, cv_text, job_requirements, language='vi'):
        """
        Score a CV against job requirements using ChatGPT
        
        Args:
            cv_text: Text content of the candidate's CV
            job_requirements: The job requirements text to compare against
            language: Language for the response (default: Vietnamese)
            
        Returns:
            dict with:
                success: Boolean indicating success
                score: Numerical score (0-10)
                explanation: Brief explanation of the score
                error: Error message (if failed)
        """
        try:
            # Preprocess CV text to remove noise and normalize formatting
            processed_cv_text = preprocess_cv_text(cv_text)
            
            # Create prompt for GPT to evaluate the CV
            system_message = """Bạn là một chuyên gia tuyển dụng HR. Nhiệm vụ của bạn là đánh giá mức độ phù hợp của CV ứng viên với yêu cầu công việc.
            
            Quy tắc:
            1. Chấm điểm CV từ 0 đến 10, trong đó 0 là hoàn toàn không đáp ứng yêu cầu và 10 là phù hợp hoàn hảo.
            2. Đánh giá dựa trên mức độ phù hợp giữa kỹ năng/kinh nghiệm của ứng viên với yêu cầu công việc.
            3. Cung cấp giải thích ngắn gọn, khách quan (tối đa 150 từ) cho điểm số bằng tiếng Việt.
            4. Trả về kết quả ở định dạng JSON với các trường: 'score' (số) và 'explanation' (chuỗi).
            
            Hãy khách quan và công bằng trong đánh giá của bạn."""
            
            user_message = f"""
            YÊU CẦU CÔNG VIỆC:
            {job_requirements}
            
            CV ỨNG VIÊN:
            {processed_cv_text}
            
            Đánh giá CV này theo yêu cầu công việc. Chấm điểm từ 0-10 và giải thích đánh giá của bạn bằng tiếng Việt.
            Phản hồi của bạn phải ở định dạng JSON hợp lệ với các trường 'score' và 'explanation'.
            """
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            logger.info("Sending CV for scoring against job requirements")
            
            # Generate response from GPT
            response = self.generate_response(
                messages=messages,
                model=self.model,
                temperature=0.3,  # Lower temperature for more consistent scoring
                max_tokens=500
            )
            
            if not response.get('success'):
                return {
                    'success': False,
                    'error': response.get('error', 'Không thể tạo điểm số CV')
                }
            
            # Extract and parse JSON from response
            response_text = response.get('response', '')
            
            # Try to extract JSON from the response text
            try:
                # Look for JSON in the response
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                else:
                    # If no JSON pattern found, try parsing the whole response
                    result = json.loads(response_text)
                    
                # Validate the result has the expected fields
                if 'score' not in result or 'explanation' not in result:
                    raise ValueError("Phản hồi thiếu các trường bắt buộc")
                    
                # Ensure score is a number between 0-10
                score = float(result['score'])
                if score < 0:
                    score = 0
                elif score > 10:
                    score = 10
                    
                return {
                    'success': True,
                    'score': score,
                    'explanation': result['explanation']
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing CV scoring response: {str(e)}")
                return {
                    'success': False,
                    'error': f"Không thể phân tích phản hồi đánh giá: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Error scoring CV: {str(e)}")
            return {
                'success': False,
                'error': f"Lỗi khi chấm điểm CV: {str(e)}"
            }

# Create a singleton instance for use throughout the application
chatgpt_helper = ChatGPTHelper()

# Add a standalone function that uses the singleton instance
def analyze_cv_with_gpt(cv_text, job_title=None, language='vi', format=None):
    """
    Standalone function to analyze CV/Resume text using the chatgpt_helper singleton.
    This function serves as a wrapper around the ChatGPTHelper.analyze_cv_with_markdown method.
    
    Args:
        cv_text: Text extracted from the CV/Resume
        job_title: Optional job title to target the analysis for
        language: Language code of the CV ('en', 'vi', etc.)
        format: Output format (not used, kept for backward compatibility)
        
    Returns:
        The result from analyze_cv_with_markdown method which is a dict with:
            success: Boolean indicating success
            analysis_markdown: Analysis in Markdown format (if successful)
            language: Language code used for the analysis
            error: Error message (if failed)
    """
    start_time = time.time()  # Track processing time
    
    try:
        # Print debug information
        original_length = len(cv_text)
        logger.info(f"Analyzing CV with text length: {original_length} characters")
        
        if not cv_text or len(cv_text) < 10:
            logger.warning("CV text is too short or empty")
            return {
                'success': False,
                'error': "Không thể phân tích CV: nội dung CV quá ngắn hoặc trống.",
                'language': language
            }
        
        # Aggressively optimize for speed and quality
        # 1. Preprocess CV text to optimize for analysis
        logger.info("Preprocessing CV text...")
        cv_text = preprocess_cv_text(cv_text)
        preprocessed_length = len(cv_text)
        logger.info(f"Preprocessed CV text length: {preprocessed_length} characters (reduced by {original_length - preprocessed_length} characters)")
        
        # 2. Limit text length for very large CVs to improve performance
        max_length = 12000  # Optimized length for GPT-4o
        if len(cv_text) > max_length:
            logger.warning(f"CV text too long ({len(cv_text)} chars), truncating to {max_length} chars")
            cv_text = cv_text[:max_length] + "\n\n[Note: CV text was truncated due to length]"
        
        # 3. Set preferred language if not specified
        if not language or language not in ['vi', 'en']:
            # Try to detect language or default to Vietnamese
            if re.search(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', cv_text, re.IGNORECASE):
                language = 'vi'
            else:
                language = 'en'
            logger.info(f"Language auto-detected as: {language}")
            
        # 4. Call the analyze_cv_with_markdown method
        logger.info(f"Calling analyze_cv_with_markdown with language: {language}")
        result = chatgpt_helper.analyze_cv_with_markdown(cv_text, job_title, language)
        
        # 5. Log performance metrics
        elapsed_time = time.time() - start_time
        logger.info(f"CV analysis completed in {elapsed_time:.2f} seconds")
        logger.info(f"CV analysis result: success={result.get('success', False)}")
        
        return result
        
    except Exception as e:
        # Log the full exception
        import traceback
        elapsed_time = time.time() - start_time
        logger.error(f"Error in analyze_cv_with_gpt after {elapsed_time:.2f} seconds: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a properly formatted error response
        return {
            'success': False,
            'error': f"Lỗi phân tích CV: {str(e)}",
            'language': language
        }

def preprocess_cv_text(text):
    """
    Preprocess CV text to optimize for analysis with GPT-4o:
    - Remove redundant whitespace
    - Normalize line breaks
    - Remove irrelevant content
    - Structure key information for better analysis
    
    Args:
        text: The raw CV text
        
    Returns:
        Preprocessed CV text optimized for GPT-4o analysis
    """
    import re
    
    # Store original length for logging
    original_length = len(text)
    
    # 1. Basic cleaning
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks (max 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 2. Remove common irrelevant content
    patterns_to_remove = [
        r'Page \d+ of \d+',  # Page numbers
        r'Copyright © \d{4}.*', # Copyright notices
        r'All rights reserved.*', # Rights statements
        r'Curriculum Vitae|Resume|CV',  # Document type indicators (standalone)
        r'References available upon request',  # Common footer text
        r'Last updated:.*\d{4}',  # Last updated dates
        r'Document generated by.*', # Generation notices
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text)
    
    # 3. Handle contact information for privacy
    # Mask email addresses
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', '[EMAIL]', text)
    
    # Mask phone numbers with various formats
    text = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE]', text)
    
    # Mask URLs
    text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)
    
    # 4. Fix formatting issues
    # Remove excess punctuation
    text = re.sub(r'([.!?])\1+', r'\1', text)
    
    # Fix spacing after punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    # 5. Format key resume sections more clearly if they exist
    section_markers = [
        (r'(?i)WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY', '## WORK EXPERIENCE'),
        (r'(?i)EDUCATION|ACADEMIC BACKGROUND', '## EDUCATION'),
        (r'(?i)SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES', '## SKILLS'),
        (r'(?i)CERTIFICATIONS|CERTIFICATES', '## CERTIFICATIONS'),
        (r'(?i)PROJECTS|PROJECT EXPERIENCE', '## PROJECTS'),
    ]
    
    for pattern, replacement in section_markers:
        text = re.sub(pattern, replacement, text)
    
    # 6. Optimize bullets and lists
    # Convert various bullet styles to consistent format
    text = re.sub(r'(?m)^[\s•\-→*]+\s*', '- ', text)
    
    # Clean up multiple dashes
    text = re.sub(r'--+', '-', text)
    
    # 7. Final cleanup
    # Remove duplicate lines that are exactly the same
    lines = text.split('\n')
    unique_lines = []
    prev_line = None
    
    for line in lines:
        line = line.strip()
        if line and line != prev_line:
            unique_lines.append(line)
            prev_line = line
    
    text = '\n'.join(unique_lines)
    
    # Remove multiple consecutive spaces (again, after all processing)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\s+\n', '\n', text)
    
    # Final trim
    text = text.strip()
    
    # Log the size reduction
    new_length = len(text)
    reduction = original_length - new_length
    reduction_percent = (reduction / original_length * 100) if original_length > 0 else 0
    
    logger.debug(f"CV text reduced from {original_length} to {new_length} characters ({reduction_percent:.1f}% reduction)")
    
    return text
