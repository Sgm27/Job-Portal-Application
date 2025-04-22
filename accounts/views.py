from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.core.exceptions import PermissionDenied
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, ResumeUploadForm
from .models import User, Resume
import io  # For BytesIO
import logging  # For logging
import PyPDF2  # For PDF reading
import json
from cv_analyzer import cv_analyzer
from chatbot.chatgpt_helper import chatgpt_helper

# Try importing pdfplumber for fallback
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Get an instance of a logger
logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify the authentication backend explicitly
            from django.contrib.auth import get_backends
            backend = get_backends()[0]  # Use the first backend (ModelBackend)
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            messages.success(request, f'Tài khoản đã được tạo cho {user.username}!')
            return redirect('profile')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Chào mừng trở lại, {user.username}!')
                return redirect('profile')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Process additional fields based on user type
            if user.user_type == 'job_seeker':
                if 'resume' in request.FILES:
                    user.resume = request.FILES['resume']
                if 'skills' in form.cleaned_data:
                    user.skills = form.cleaned_data['skills']
            elif user.user_type == 'employer':
                if 'company_name' in form.cleaned_data:
                    user.company_name = form.cleaned_data['company_name']
                if 'company_description' in form.cleaned_data:
                    user.company_description = form.cleaned_data['company_description']
                if 'company_website' in form.cleaned_data:
                    user.company_website = form.cleaned_data['company_website']
            
            user.save()
            messages.success(request, 'Hồ sơ của bạn đã được cập nhật!')
            return redirect('profile')
        else:
            messages.error(request, 'Đã xảy ra lỗi khi cập nhật hồ sơ của bạn. Vui lòng kiểm tra biểu mẫu.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Lấy danh sách CV của người dùng
    resumes = []
    resume_form = None
    
    if request.user.user_type == 'job_seeker':
        resumes = Resume.objects.filter(user=request.user)
        resume_form = ResumeUploadForm(user=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'resumes': resumes,
        'resume_form': resume_form
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def upload_resume_view(request):
    if request.user.user_type != 'job_seeker':
        return HttpResponseForbidden('Chỉ người tìm việc mới có thể tải lên CV')
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            
            messages.success(request, 'CV của bạn đã được tải lên thành công!')
            
            # Cập nhật trường resume trong User nếu đây là CV chính
            if resume.is_primary:
                request.user.resume = resume.file
                request.user.save()
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    
    return redirect('profile')

@login_required
def delete_resume_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        # Nếu xóa CV chính, cập nhật lại user.resume
        if resume.is_primary and request.user.resume:
            request.user.resume = None
            request.user.save()
            
            # Tìm CV khác để đặt làm CV chính
            other_resume = Resume.objects.filter(user=request.user).exclude(id=resume_id).first()
            if other_resume:
                other_resume.is_primary = True
                other_resume.save()
                request.user.resume = other_resume.file
                request.user.save()
        
        resume.delete()
        messages.success(request, 'CV đã được xóa thành công')
    
    return redirect('profile')

@login_required
def set_primary_resume_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        # Đặt tất cả CV khác không phải là primary
        Resume.objects.filter(user=request.user).update(is_primary=False)
        
        # Đặt CV này là primary
        resume.is_primary = True
        resume.save()
        
        # Cập nhật trường resume trong User
        request.user.resume = resume.file
        request.user.save()
        
        messages.success(request, 'CV chính đã được cập nhật')
    
    return redirect('profile')

@login_required
@require_http_methods(["POST"])
def analyze_resume(request, resume_id):
    """
    API endpoint to analyze a resume and return the analysis in Markdown format
    """
    # Validate the resume exists and belongs to the user
    resume = get_object_or_404(Resume, id=resume_id)
    
    if resume.user != request.user:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to analyze this resume.'
        }, status=403)
    
    # Extract text from the PDF resume
    extraction_result = cv_analyzer.analyze_cv(django_file=resume.file)
    
    if not extraction_result['success']:
        return JsonResponse({
            'success': False,
            'message': 'Failed to extract text from the resume.',
            'details': extraction_result.get('error', 'Unknown error')
        }, status=400)
    
    # Get the extracted text content
    cv_text = extraction_result['text_content']
    language = extraction_result['language']
    
    # Get optional job title from request if provided
    data = {}
    try:
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        pass
    
    job_title = data.get('job_title', None)
    
    # Analyze the CV text with ChatGPT
    analysis_result = chatgpt_helper.analyze_cv_with_markdown(
        cv_text=cv_text,
        job_title=job_title,
        language=language
    )
    
    if not analysis_result['success']:
        return JsonResponse({
            'success': False,
            'message': 'Failed to analyze the resume.',
            'details': analysis_result.get('error', 'Unknown error')
        }, status=500)
    
    # Return the Markdown analysis
    return JsonResponse({
        'success': True,
        'markdown': analysis_result['analysis_markdown'],
        'language': analysis_result['language']
    })
