from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import logging
import re
import time
import tempfile
from django.db import models
import openai
from datetime import datetime

from .models import Conversation, Message
# Import chatgpt helper module
from .chatgpt_helper import chatgpt_helper
# Import the database agent
from .db_agent import JobDatabaseAgent, CVAnalysisAgent
# Import Resume model
from accounts.models import Resume
# Import CV analyzer module
from app.services.cv_analyzer import analyze_cv_file, extract_skills, analyze_text
# Import web search tools
from .web_search_tools import WebSearchTools

# Cấu hình logger
logger = logging.getLogger(__name__)

# Dict to store analysis status keyed by resume_id
resume_analysis_status = {}

@login_required
def chatbot_view(request):
    """Render trang chatbot."""
    return render(request, 'chatbot.html')

def extract_json_from_response(response:str) -> dict:
    """
    Attempts to extract a JSON object from a string response using regex.
    
    Args:
        response: The string potentially containing a JSON object.
        
    Returns:
        A dictionary if a valid JSON object is found, otherwise None or raises an error.
    """
    # Regex to find JSON object (handles nested structures)
    # It looks for patterns starting with { and ending with }
    # Note: This regex might be too simple for complex nested JSON within other text.
    # A more robust approach might involve finding the first '{' and matching braces.
    match = re.search(r'\{[\s\S]*\}', response)
    
    if match:
        json_str = match.group(0)
        try:
            # Attempt to parse the extracted string as JSON
            parsed_json = json.loads(json_str)
            return parsed_json
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode JSON extracted from response: {e}")
            logger.warning(f"Extracted string: {json_str}")
            # Optionally, you could return None or raise a custom exception here
            return None # Or raise ValueError("Invalid JSON found in response")
    else:
        logger.warning("No JSON object found in the response string.")
        return None # No JSON found

@csrf_exempt
@login_required
def chatbot_api(request):
    """API để xử lý tin nhắn chatbot"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        resume_id = data.get('resume_id')  # Thêm tham số resume_id
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            # If no conversation_id is provided, get the most recent conversation or create a new one
            user_conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
            if user_conversations.exists():
                conversation = user_conversations.first()
            else:
                conversation = Conversation.objects.create(user=request.user)
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Update conversation timestamp
        conversation.save()  # This will update the updated_at field
        
        # Check if API key is configured
        if not os.environ.get("OPENAI_API_KEY"):
            error_message = "Chưa cấu hình API key cho chatbot. Vui lòng liên hệ quản trị viên."
            logger.error(error_message)
            
            # Save error response
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=error_message
            )
            
            return JsonResponse({
                'message': error_message,
                'conversation_id': conversation.id,
                'is_html': False
            })
        
        # Step 1: Kiểm tra nếu có resume_id, đây là request phân tích CV đã chọn
        if resume_id:
            try:
                # Sử dụng CVAnalysisAgent để phân tích CV
                analysis_result = CVAnalysisAgent.analyze_resume(request.user, resume_id)
                
                if not analysis_result.get('success', False):
                    assistant_message = analysis_result.get('error', 'Lỗi không xác định khi phân tích CV')
                    is_html = False
                    is_markdown = False
                else:
                    assistant_message = analysis_result.get('analysis')
                    is_html = True
                    is_markdown = True
                
                # Save response
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_message
                )
                
                return JsonResponse({
                    'message': assistant_message,
                    'conversation_id': conversation.id,
                    'is_html': is_html,
                    'is_markdown': is_markdown,
                    'is_resume_analysis': True
                })
            except Exception as e:
                logger.error(f"Error in CV analysis: {str(e)}")
                assistant_message = f"Lỗi khi phân tích CV: {str(e)}"
                is_html = False
                is_markdown = False
                
                # Save error response
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_message
                )
                
                return JsonResponse({
                    'message': assistant_message,
                    'conversation_id': conversation.id,
                    'is_html': is_html,
                    'is_markdown': is_markdown
                })
        
        # Step 2: Kiểm tra xem người dùng có đang yêu cầu phân tích CV không
        is_cv_analysis_request = CVAnalysisAgent.detect_resume_analysis_intent(user_message)
        
        # Nếu người dùng yêu cầu phân tích CV, trả về danh sách CV để chọn
        if is_cv_analysis_request:
            try:
                # Lấy danh sách CV của người dùng
                resumes_result = CVAnalysisAgent.get_resume_list(request.user)
                
                if not resumes_result.get('success', False):
                    # Không có CV hoặc có lỗi
                    assistant_message = resumes_result.get('error', 'Bạn chưa tải lên CV nào. Vui lòng tải CV trước khi phân tích.')
                    is_html = False
                    is_markdown = False
                else:
                    # Có danh sách CV, hiển thị để người dùng chọn
                    resumes = resumes_result.get('resumes', [])
                    message = resumes_result.get('message', 'Vui lòng chọn CV bạn muốn phân tích:')
                    
                    # Tạo HTML cho danh sách CV
                    resume_list_html = f"""
                    <div class="resume-selection">
                        <p>{message}</p>
                        <div class="resume-list">
                    """
                    
                    for resume in resumes:
                        resume_list_html += f"""
                            <div class="resume-item" data-id="{resume['id']}">
                                <div class="resume-info">
                                    <div class="resume-title">{resume['title']} {' (Primary)' if resume.get('is_primary') else ''}</div>
                                    <div class="resume-date">Uploaded: {resume['uploaded_at']}</div>
                                </div>
                                <button class="resume-select-btn">Phân tích</button>
                            </div>
                        """
                    
                    resume_list_html += """
                        </div>
                    </div>
                    """
                    
                    assistant_message = resume_list_html
                    is_html = True
                    is_markdown = False
                
                # Save response
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_message
                )
                
                return JsonResponse({
                    'message': assistant_message,
                    'conversation_id': conversation.id,
                    'is_html': is_html,
                    'is_markdown': is_markdown,
                    'is_resume_selection': True
                })
            except Exception as e:
                logger.error(f"Error in CV list retrieval: {str(e)}")
                assistant_message = f"Lỗi khi lấy danh sách CV: {str(e)}"
                is_html = False
                is_markdown = False
                
                # Save error response
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_message
                )
                
                return JsonResponse({
                    'message': assistant_message,
                    'conversation_id': conversation.id,
                    'is_html': is_html,
                    'is_markdown': is_markdown
                })
        
        # Step 3: Use AI to determine the intent of the user's message
        intent_prompt = f"""
        Phân tích tin nhắn sau của người dùng và xác định đây là loại yêu cầu nào:
        
        "{user_message}"
        
        Chọn một trong các loại sau và trả về chỉ một từ khóa:
        1. "job_search" - nếu người dùng đang tìm kiếm công việc cụ thể
        2. "web_search" - nếu người dùng đang hỏi về công nghệ web, xu hướng, thông tin kỹ thuật
        3. "general" - các câu hỏi chung khác về nghề nghiệp, phát triển kỹ năng
        
        Chỉ trả về đúng một từ: "job_search", "web_search" hoặc "general"
        """
        
        intent_response = chatgpt_helper.ask_gpt(intent_prompt).strip().lower()
        
        # Step 4: Process based on the detected intent
        if intent_response == "job_search":
            try:
                # Use the job_search tool
                job_search_result = WebSearchTools.job_search(user_message)
                
                if job_search_result.get('success', False):
                    assistant_message = job_search_result.get('formatted_results', '')
                    is_html = True
                    is_markdown = False
                else:
                    # Fallback to standard response if job search fails
                    error = job_search_result.get('error', 'Unknown error')
                    logger.error(f"Job search failed: {error}")
                    assistant_message = chatgpt_helper.ask_gpt(user_message)
                    is_html = False
                    is_markdown = True
            except Exception as e:
                logger.error(f"Error in job search processing: {str(e)}")
                # Fallback to standard ChatGPT response
                assistant_message = chatgpt_helper.ask_gpt(user_message)
                is_html = False
                is_markdown = True
        
        elif intent_response == "web_search":
            try:
                # Use the web_search tool for technology queries
                web_search_result = WebSearchTools.web_search(user_message)
                
                if web_search_result.get('success', False):
                    assistant_message = web_search_result.get('results', '')
                    is_html = False
                    is_markdown = web_search_result.get('is_markdown', False)
                else:
                    # Fallback to standard response if web search fails
                    error = web_search_result.get('error', 'Unknown error')
                    logger.error(f"Web search failed: {error}")
                    assistant_message = chatgpt_helper.ask_gpt(user_message)
                    is_html = False
                    is_markdown = False
            except Exception as e:
                logger.error(f"Error in web search processing: {str(e)}")
                assistant_message = chatgpt_helper.ask_gpt(user_message)
                is_html = False
                is_markdown = False
        
        else:  # "general" or any other response
            try:
                # For educational/career development/general queries
                enhanced_prompt = f"""
                Bạn là một trợ lý phát triển nghề nghiệp và kỹ năng chuyên môn, chuyên cung cấp hướng dẫn cá nhân hóa về học tập và phát triển kỹ năng trong lĩnh vực công nghệ thông tin và các ngành nghề khác. Người dùng đang hỏi:
                
                "{user_message}"
                
                Hãy phân tích câu hỏi để xác định:
                1. Lĩnh vực chuyên môn cụ thể mà người dùng quan tâm (Web, AI, lập trình, thiết kế, v.v.)
                2. Mục tiêu phát triển nghề nghiệp của họ (cải thiện kỹ năng hiện tại, học kỹ năng mới, v.v.)
                3. Mức độ hiểu biết hiện tại (người mới, trung cấp, nâng cao)
                
                Dựa trên phân tích, hãy cung cấp một phản hồi cá nhân hóa bao gồm:
                
                • Tổng quan ngắn gọn về lĩnh vực/kỹ năng và tầm quan trọng của nó trên thị trường lao động
                • Lộ trình học tập cụ thể và phù hợp với mục tiêu nghề nghiệp
                • Tài nguyên học tập chất lượng (khóa học, sách, website, v.v.)
                • Phương pháp thực hành hiệu quả và dự án thực tế để xây dựng portfolio
                • Các kỹ năng bổ sung cần thiết để nâng cao cơ hội việc làm
                
                Trả lời bằng tiếng Việt, sử dụng định dạng markdown để dễ đọc. Cung cấp thông tin thực tế, cập nhật và hữu ích với lộ trình rõ ràng.
                """
                assistant_message = chatgpt_helper.ask_gpt(enhanced_prompt)
                is_html = False
                is_markdown = True
            except Exception as e:
                logger.error(f"Error in general query processing: {str(e)}")
                assistant_message = f"Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau."
                is_html = False
                is_markdown = False
        
        # Save response
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_message
        )
        
        response_data = {
            'message': assistant_message,
            'conversation_id': conversation.id,
            'is_html': is_html,
            'is_markdown': is_markdown if 'is_markdown' in locals() else False
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        # Add more detailed logging for errors
        import traceback
        logger.error(f"Error in chatbot_api: {str(e)}")
        logger.error(traceback.format_exc())  # Log the full stack trace
        
        # Provide more helpful error message
        error_message = "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        return JsonResponse({'error': error_message, 'details': str(e)}, status=500)

@csrf_exempt
@login_required
def analyze_resume_api(request):
    """API to analyze resumes/CVs and provide detailed feedback"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST method is supported'}, status=405)
        
        # Parse JSON data from request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # Get parameters
        resume_id = data.get('resume_id')
        job_category = data.get('job_category', '')
        conversation_id = data.get('conversation_id')
        
        if not resume_id:
            return JsonResponse({'error': 'Thiếu thông tin CV cần phân tích'}, status=400)
        
        try:
            # Get the resume from database
            try:
                resume = get_object_or_404(Resume, id=resume_id)
                resume_path = resume.file.path
            except Exception as e:
                logger.error(f"Error accessing resume file: {str(e)}")
                return JsonResponse({'error': f'Không thể truy cập file CV: {str(e)}'}, status=404)
            
            # Check if user has permission to access this resume
            if resume.user != request.user and not request.user.is_staff:
                return JsonResponse({'error': 'Bạn không có quyền phân tích CV này'}, status=403)
            
            # Check if file exists
            if not os.path.exists(resume_path):
                logger.error(f"Resume file does not exist: {resume_path}")
                return JsonResponse({'error': 'File CV không tồn tại hoặc đã bị xóa'}, status=404)
            
            # Simple direct process:
            # 1. Extract text from PDF
            from app.services.cv_analyzer import extract_text_from_pdf
            cv_text = extract_text_from_pdf(resume_path)
            
            if not cv_text or cv_text.startswith("Error") or cv_text.startswith("Không thể"):
                return JsonResponse({
                    'status': 'failed',
                    'error': cv_text or 'Không thể trích xuất văn bản từ PDF'
                }, status=500)
                
            # 2. Send directly to ChatGPT for analysis
            from chatbot.chatgpt_helper import analyze_cv_with_gpt
            analysis_result = analyze_cv_with_gpt(cv_text, job_category)
            
            # Check if analysis was successful
            if not analysis_result.get('success', False):
                error_message = analysis_result.get('error', 'Lỗi không xác định khi phân tích CV')
                logger.error(f"Error in CV analysis: {error_message}")
                return JsonResponse({
                    'status': 'failed',
                    'error': error_message
                }, status=500)
            
            # Get the markdown analysis
            markdown_analysis = analysis_result.get('analysis_markdown', '')
            
            # 3. If there's a conversation_id, add the analysis to the conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=markdown_analysis
                    )
                except Conversation.DoesNotExist:
                    logger.warning(f"Conversation {conversation_id} not found for resume analysis")
            
            # 4. Return analysis result directly
            is_from_profile = request.headers.get('X-Profile-Analysis') == 'true'
            
            return JsonResponse({
                'status': 'completed',
                'message': markdown_analysis,
                'analysis_markdown': markdown_analysis,
                'is_markdown': True,
                'success': True
            })
            
        except Resume.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy CV'}, status=404)
        except Exception as e:
            logger.error(f"Error processing resume analysis: {str(e)}")
            return JsonResponse({'error': f'Lỗi phân tích CV: {str(e)}'}, status=500)
    
    except Exception as e:
        logger.error(f"Unexpected error in analyze_resume_api: {str(e)}")
        return JsonResponse({'error': f'Lỗi không xác định: {str(e)}'}, status=500)

@login_required
def get_conversation_history(request, conversation_id=None):
    """Lấy lịch sử tin nhắn của một cuộc hội thoại"""
    if conversation_id:
        # If conversation_id is provided, get that specific conversation
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        # If no conversation_id is provided, get the most recent conversation or create a new one
        user_conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
        if user_conversations.exists():
            conversation = user_conversations.first()
        else:
            conversation = Conversation.objects.create(user=request.user)
    
    messages = conversation.messages.all().order_by('timestamp')
    messages_data = [{
        'id': msg.id,
        'role': msg.role,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for msg in messages]
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'messages': messages_data
    })

@login_required
def clear_conversation(request):
    """Xóa toàn bộ tin nhắn trong cuộc hội thoại hiện tại"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Get the most recent conversation
    user_conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    if user_conversations.exists():
        conversation = user_conversations.first()
        conversation.messages.all().delete()
    
    return JsonResponse({'status': 'success'})
