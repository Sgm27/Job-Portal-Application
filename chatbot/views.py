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

# Cấu hình logger
logger = logging.getLogger(__name__)

# Dict to store analysis status keyed by resume_id
resume_analysis_status = {}

@login_required
def chatbot_view(request):
    """Render trang chatbot."""
    return render(request, 'chatbot.html')

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
                else:
                    assistant_message = analysis_result.get('analysis')
                    is_html = True
                
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
                    'is_markdown': True,
                    'is_resume_analysis': True
                })
            except Exception as e:
                logger.error(f"Error in CV analysis: {str(e)}")
                assistant_message = f"Lỗi khi phân tích CV: {str(e)}"
                is_html = False
                
                # Save error response
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_message
                )
                
                return JsonResponse({
                    'message': assistant_message,
                    'conversation_id': conversation.id,
                    'is_html': is_html
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
                                <button class="resume-select-btn" onclick="selectResumeForAnalysis('{resume['id']}', '{conversation.id}')">Phân tích</button>
                            </div>
                        """
                    
                    resume_list_html += """
                        </div>
                    </div>
                    """
                    
                    assistant_message = resume_list_html
                    is_html = True
                
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
                    'is_resume_selection': True
                })
            except Exception as e:
                logger.error(f"Error in CV list retrieval: {str(e)}")
                assistant_message = f"Lỗi khi lấy danh sách CV: {str(e)}"
                is_html = False
                
                # Save error response
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_message
                )
                
                return JsonResponse({
                    'message': assistant_message,
                    'conversation_id': conversation.id,
                    'is_html': is_html
                })
        
        # Step 3: First check if this is an educational query that should NOT trigger job search
        is_educational_query = JobDatabaseAgent.is_educational_query(user_message)
        
        # Step 4: If not an educational query, then check for job search intent
        if not is_educational_query:
            try:
                is_job_query, query_type, query_value = JobDatabaseAgent.detect_job_query_intent(user_message)
            except Exception as e:
                logger.error(f"Error in job intent detection: {str(e)}")
                is_job_query = False
        else:
            # Educational query shouldn't trigger job search
            logger.info(f"Educational query detected: {user_message[:50]}...")
            is_job_query = False
        
        # Step 5: If direct detection fails and it's not an educational query, try using ChatGPT to analyze
        if not is_job_query and not is_educational_query:
            try:
                # Create a prompt to extract job search intent
                analysis_prompt = f"""
                Bạn là một trợ lý AI chuyên phân tích ngữ cảnh và ý định của người dùng. Hãy phân tích tin nhắn sau và xác định xem người dùng có đang tìm kiếm thông tin liên quan đến công việc và nghề nghiệp không:

                "{user_message}"

                Phân tích kỹ lưỡng ngữ cảnh và ý định của người dùng:
                
                1. Nếu người dùng đang TÌM KIẾM VIỆC LÀM, họ thường sẽ:
                   - Hỏi trực tiếp về các vị trí công việc cụ thể
                   - Muốn danh sách công việc ở một địa điểm
                   - Tìm kiếm công việc với một kỹ năng cụ thể
                   - Sử dụng từ ngữ như "tìm việc", "công việc ở đâu", "việc làm nào"
                
                2. Nếu người dùng đang HỎI VỀ PHÁT TRIỂN KỸ NĂNG NGHỀ NGHIỆP, họ thường sẽ:
                   - Hỏi về cách học một kỹ năng liên quan đến công việc (lập trình, thiết kế, marketing, v.v.)
                   - Muốn cải thiện kiến thức trong một lĩnh vực chuyên môn
                   - Tìm kiếm lộ trình học tập cho nghề nghiệp cụ thể
                   - Hỏi về kỹ năng cần thiết cho một công việc
                   
                   => Đây VẪN LÀ câu hỏi LIÊN QUAN ĐẾN CÔNG VIỆC và NGHỀ NGHIỆP, nên cần được trả lời.
                
                3. Nếu người dùng đang HỎI CÂU HỎI KHÔNG LIÊN QUAN ĐẾN CÔNG VIỆC, họ thường sẽ:
                   - Hỏi về chủ đề cá nhân (sức khỏe, mối quan hệ, v.v.)
                   - Hỏi về giải trí (phim, âm nhạc, trò chơi, v.v.)
                   - Hỏi về các chủ đề chung không liên quan đến công việc
                
                Ví dụ LIÊN QUAN ĐẾN CÔNG VIỆC:
                - "Tôi muốn cải thiện kỹ năng AI của mình" → LIÊN QUAN đến công việc
                - "Làm thế nào để học tốt Python?" → LIÊN QUAN đến công việc
                - "Tôi muốn học thiết kế web" → LIÊN QUAN đến công việc
                - "Cần lộ trình học web development" → LIÊN QUAN đến công việc
                - "Tìm việc AI ở Hà Nội" → LIÊN QUAN đến công việc
                
                Phân tích ngữ nghĩa sâu hơn, không chỉ dựa vào từ khóa đơn lẻ. Xem xét liệu câu hỏi có liên quan đến:
                - Kỹ năng nghề nghiệp
                - Phát triển chuyên môn
                - Lộ trình học tập cho công việc
                - Nhu cầu thị trường lao động
                
                Nếu có, hãy coi đó là câu hỏi liên quan đến công việc.

                Trả về dạng JSON:
                
                Nếu là câu hỏi liên quan đến công việc (bao gồm cả tìm việc và phát triển kỹ năng nghề nghiệp):
                {{
                    "is_job_related": true,
                    "is_job_search": true/false,
                    "search_type": "title/location/skill", // chỉ điền nếu is_job_search=true
                    "search_term": "term_extracted", // chỉ điền nếu is_job_search=true
                    "confidence": 0.XX
                }}
                
                Nếu KHÔNG liên quan đến công việc:
                {{
                    "is_job_related": false,
                    "confidence": 0.XX
                }}
                
                Chỉ trả về JSON, không có giải thích thêm.
                """
                
                # Call ChatGPT to analyze the intent
                analysis_response = chatgpt_helper.ask_gpt(analysis_prompt)
                logger.debug(f"Analysis response: {analysis_response}")
                
                try:
                    # Try to parse the JSON response
                    analysis_result = json.loads(analysis_response)
                    if analysis_result.get('is_job_related', False):
                        # Determine if this is a job search or career development question
                        is_job_related = True
                        confidence = analysis_result.get('confidence', 0)
                        
                        # Check if this is specifically a job search query
                        if analysis_result.get('is_job_search', False) and confidence >= 0.6:
                            is_job_query = True
                            query_type = analysis_result.get('search_type', 'title')
                            query_value = analysis_result.get('search_term', '')
                            
                            # Log the extracted intent for debugging
                            logger.debug(f"ChatGPT extracted job search intent: {query_type}='{query_value}' with confidence {confidence}")
                        else:
                            # Job-related but not a job search - handle as career/skill development
                            is_job_query = False
                            logger.debug(f"ChatGPT detected career development question (confidence: {confidence})")
                            
                            # Treat this as a special type of educational query that is job-related
                            is_educational_query = True
                    else:
                        # Not job-related at all
                        is_job_related = False
                        is_job_query = False
                        confidence = analysis_result.get('confidence', 0)
                        logger.debug(f"ChatGPT determined this is NOT job-related (confidence: {confidence})")
                        
                        # If not job-related with high confidence, give a polite refusal
                        if confidence >= 0.7:
                            assistant_message = "Xin lỗi, tôi chỉ có thể trả lời các câu hỏi liên quan đến công việc và nghề nghiệp. Bạn có thể hỏi tôi về việc cải thiện CV, chuẩn bị phỏng vấn, phát triển kỹ năng chuyên môn, hoặc tìm kiếm cơ hội việc làm."
                            
                            # Save response
                            Message.objects.create(
                                conversation=conversation,
                                role='assistant',
                                content=assistant_message
                            )
                            
                            return JsonResponse({
                                'message': assistant_message,
                                'conversation_id': conversation.id,
                                'is_html': False
                            })
                except json.JSONDecodeError as e:
                    # If parsing fails, continue with normal processing
                    logger.warning(f"Failed to parse ChatGPT analysis: {str(e)}")
                    logger.warning(f"Raw response: {analysis_response}")
                    pass
            except Exception as e:
                logger.error(f"Error in ChatGPT analysis: {str(e)}")
                is_job_query = False
        
        if is_job_query:
            try:
                # Use the database agent to query jobs
                if query_type == 'title':
                    jobs = JobDatabaseAgent.query_jobs_by_title(query_value)
                elif query_type == 'location':
                    jobs = JobDatabaseAgent.query_jobs_by_location(query_value)
                elif query_type == 'skills':
                    jobs = JobDatabaseAgent.query_jobs_by_skills(query_value)
                else:
                    jobs = []
                
                # If no jobs found with the first query, try alternative search terms
                if not jobs and query_value:
                    try:
                        # Ask ChatGPT for alternative search terms
                        alternatives_prompt = f"""
                        Đề xuất 3 từ khóa tìm kiếm thay thế cho "{query_value}" để tìm công việc IT.
                        Chỉ liệt kê các từ khóa, cách nhau bằng dấu phẩy, không có giải thích.
                        """
                        alternatives_response = chatgpt_helper.ask_gpt(alternatives_prompt)
                        
                        # Try each alternative
                        for alt_term in alternatives_response.split(','):
                            alt_term = alt_term.strip()
                            if alt_term and alt_term != query_value:
                                try:
                                    alt_jobs = JobDatabaseAgent.query_jobs_by_title(alt_term)
                                    if alt_jobs:
                                        # Add an explanation about the alternative search
                                        alternative_explanation = f"""
                                        <div class="search-alternative-notice">
                                            <p>Tôi không tìm thấy công việc nào cho từ khóa '{query_value}', 
                                            nhưng đây là kết quả cho '{alt_term}':</p>
                                        </div>
                                        """
                                        formatted_jobs = JobDatabaseAgent.format_job_results(alt_jobs, query_type, alt_term)
                                        assistant_message = alternative_explanation + formatted_jobs
                                        is_html = True
                                        break
                                except Exception as e:
                                    logger.error(f"Error in alternative search for '{alt_term}': {str(e)}")
                        else:
                            # If no results with alternatives either, format the original empty result
                            assistant_message = JobDatabaseAgent.format_job_results(jobs, query_type, query_value)
                            is_html = True
                    except Exception as e:
                        logger.error(f"Error in alternatives search: {str(e)}")
                        # Fallback to normal formatting
                        assistant_message = JobDatabaseAgent.format_job_results(jobs, query_type, query_value)
                        is_html = True
                else:
                    # Format the response with HTML
                    assistant_message = JobDatabaseAgent.format_job_results(jobs, query_type, query_value)
                    is_html = True
            except Exception as e:
                logger.error(f"Error in job query processing: {str(e)}")
                # Fallback to standard ChatGPT response
                assistant_message = chatgpt_helper.ask_gpt(user_message)
                is_html = False
        else:
            try:
                # For educational queries, add a special prompt to get better responses
                if is_educational_query:
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
                    
                    Nếu câu hỏi liên quan đến phát triển web, hãy cung cấp:
                    • Các công nghệ và framework hiện đại và được ưa chuộng nhất
                    • Lộ trình phát triển từ cơ bản đến nâng cao
                    • Các dự án thực tế để xây dựng portfolio
                    • Kỹ năng cần thiết để làm việc trong các công ty công nghệ
                    
                    Trả lời bằng tiếng Việt, sử dụng định dạng bullet points để dễ đọc. Cung cấp thông tin thực tế, cập nhật và hữu ích với lộ trình rõ ràng.
                    """
                    assistant_message = chatgpt_helper.ask_gpt(enhanced_prompt)
                else:
                    # Standard GPT processing for normal queries
                    assistant_message = chatgpt_helper.ask_gpt(user_message)
                    
                is_html = False
            except Exception as e:
                logger.error(f"Error in standard GPT processing: {str(e)}")
                assistant_message = f"Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau."
                is_html = False
        
        # Save response
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_message
        )
        
        return JsonResponse({
            'message': assistant_message,
            'conversation_id': conversation.id,
            'is_html': is_html
        })
        
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
