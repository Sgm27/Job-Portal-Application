from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging
from .models import Job, Application, Notification
from .forms import JobForm, ApplicationForm, JobSearchForm
from accounts.models import User, Resume
from chatbot.chatgpt_helper import chatgpt_helper
from cv_analyzer import cv_analyzer
from .decorators import employer_required, job_owner_required, application_owner_required, job_seeker_required, user_required

def home_view(request):
    # Display recent jobs on the home page
    recent_jobs = Job.objects.filter(status='active', application_deadline__gt=timezone.now()).order_by('-created_at')[:5]
    
    # Get employer count
    employer_count = User.objects.filter(user_type='employer').count()
    
    # Get job seeker count
    job_seeker_count = User.objects.filter(user_type='job_seeker').count()
    
    # Get active jobs count
    active_jobs_count = Job.objects.filter(status='active').count()
    
    context = {
        'recent_jobs': recent_jobs,
        'employer_count': employer_count,
        'job_seeker_count': job_seeker_count,
        'active_jobs_count': active_jobs_count
    }
    return render(request, 'index.html', context)

def job_list_view(request):
    # Get all active jobs
    jobs = Job.objects.filter(status='active', application_deadline__gt=timezone.now())
    
    # Tạo từ điển ánh xạ mã địa điểm với tên hiển thị
    location_display_names = dict(Job.VIETNAM_LOCATIONS)
    
    # Handle search form
    form = JobSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')
        
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(requirements__icontains=search)
            )
        if location:
            jobs = jobs.filter(location=location)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
    
    # Paginate results
    paginator = Paginator(jobs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Thêm tên hiển thị của địa điểm vào context
    context = {
        'jobs': page_obj,
        'form': form,
        'location_display_names': location_display_names  # Truyền từ điển ánh xạ vào context
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    user_applied = False
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        user_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    
    # Get similar jobs
    similar_jobs = Job.objects.filter(
        status='active',
        application_deadline__gt=timezone.now(),
        job_type=job.job_type
    ).exclude(id=job.id).order_by('-created_at')[:3]
    
    context = {
        'job': job,
        'user_applied': user_applied,
        'similar_jobs': similar_jobs
    }
    return render(request, 'jobs/job_detail.html', context)

def employer_jobs_view(request, employer_id):
    # Get the employer
    employer = get_object_or_404(User, id=employer_id, user_type='employer')
    
    # Get all jobs from the employer (including expired and inactive jobs)
    jobs = Job.objects.filter(employer=employer).order_by('-created_at')
    
    # Paginate results
    paginator = Paginator(jobs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'jobs': page_obj,
        'employer': employer,
        'now': timezone.now()  # Thêm thời gian hiện tại vào context
    }
    return render(request, 'jobs/employer_jobs.html', context)

@job_seeker_required
def job_apply_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if deadline has passed
    if job.application_deadline < timezone.now():
        messages.error(request, 'The application deadline has passed.')
        return redirect('job_detail', job_id=job.id)
    
    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job.id)
    
    # Lấy danh sách CV của người dùng
    resumes = Resume.objects.filter(user=request.user)
    
    # Kiểm tra xem người dùng có CV nào không
    has_resume = resumes.exists() or request.user.resume
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            
            # Lấy CV đã chọn từ form nếu có
            selected_resume_id = request.POST.get('selected_resume')
            
            # Nếu người dùng chọn CV cụ thể, cập nhật trường resume của user
            if selected_resume_id:
                try:
                    selected_resume = Resume.objects.get(id=selected_resume_id, user=request.user)
                    # Đặt CV này là CV chính
                    Resume.objects.filter(user=request.user).update(is_primary=False)
                    selected_resume.is_primary = True
                    selected_resume.save()
                    
                    # Lưu resume được chọn vào application
                    application.resume = selected_resume
                    
                    # Cập nhật CV chính trong hồ sơ người dùng
                    request.user.resume = selected_resume.file
                    request.user.save()
                except Resume.DoesNotExist:
                    pass
            else:
                # Nếu không chọn CV cụ thể nhưng user có CV chính, sử dụng CV chính
                primary_resume = Resume.objects.filter(user=request.user, is_primary=True).first()
                if primary_resume:
                    application.resume = primary_resume
            
            application.save()
            
            # Tạo thông báo cho nhà tuyển dụng về đơn ứng tuyển mới
            notification_message = f"{request.user.get_full_name() or request.user.username} đã nộp đơn ứng tuyển vào vị trí {job.title}"
            Notification.objects.create(
                user=job.employer,  # Gửi thông báo cho nhà tuyển dụng
                application=application,
                notification_type='application_submitted',
                message=notification_message
            )
            
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'job': job,
        'resumes': resumes,
        'has_resume': has_resume
    }
    return render(request, 'jobs/job_apply.html', context)

@employer_required
def employer_dashboard_view(request):
    # Get all jobs posted by the employer
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    
    context = {
        'jobs': jobs
    }
    return render(request, 'dashboard/employer_dashboard.html', context)

@employer_required
def post_job_view(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    
    context = {
        'form': form
    }
    return render(request, 'jobs/job_post.html', context)

@job_owner_required
def edit_job_view(request, job_id, job=None):
    # job được truyền từ decorator
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job
    }
    return render(request, 'jobs/job_edit.html', context)

@job_owner_required
def delete_job_view(request, job_id, job=None):
    # job được truyền từ decorator
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('employer_dashboard')
    
    context = {
        'job': job
    }
    return render(request, 'jobs/job_delete.html', context)

@job_owner_required
def applicant_tracking_view(request, job_id, job=None):
    # job được truyền từ decorator
    applications = Application.objects.filter(job=job)
    
    # Check if auto-reject feature should be enabled
    if request.method == 'POST' and 'auto_reject' in request.POST:
        auto_reject_applications(job, applications.filter(status='pending'))
        messages.success(request, 'Auto-reject process completed. Applications with low scores have been rejected.')
        return redirect('applicant_tracking', job_id=job.id)
    
    # Tính toán số lượng ứng viên theo từng trạng thái
    pending_count = applications.filter(status='pending').count()
    reviewed_count = applications.filter(status='reviewed').count()
    shortlisted_count = applications.filter(status='shortlisted').count()
    rejected_count = applications.filter(status='rejected').count()
    hired_count = applications.filter(status='hired').count()
    
    # Thêm các số liệu thống kê vào queryset như các thuộc tính
    applications.pending_count = pending_count
    applications.reviewed_count = reviewed_count
    applications.shortlisted_count = shortlisted_count
    applications.rejected_count = rejected_count
    applications.hired_count = hired_count
    
    # Tạo thông báo khi nhà tuyển dụng xem các đơn ứng tuyển (CV)
    for application in applications:
        # Kiểm tra nếu chưa có thông báo "đã xem" cho đơn ứng tuyển này
        if not Notification.objects.filter(
            application=application,
            notification_type='cv_viewed'
        ).exists():
            # Tạo thông báo cho ứng viên
            notification_message = f"Nhà tuyển dụng đã xem đơn ứng tuyển của bạn cho vị trí {job.title}"
            Notification.objects.create(
                user=application.applicant,
                application=application,
                notification_type='cv_viewed',
                message=notification_message
            )
    
    context = {
        'job': job,
        'applications': applications
    }
    return render(request, 'dashboard/applicant_tracking.html', context)

def auto_reject_applications(job, applications):
    """
    Automatically evaluate and reject applications with scores below 5
    
    Args:
        job: The job object
        applications: QuerySet of applications to evaluate
    """
    job_requirements = job.requirements
    rejected_count = 0
    processed_count = 0
    
    for application in applications:
        processed_count += 1
        try:
            # Skip applications with no resume
            if not application.resume:
                continue
            
            # Extract text from CV
            resume_file = application.resume.file
            cv_text = ""
            
            # Extract text from resume file
            try:
                cv_analysis = cv_analyzer.analyze_cv(file_path=None, django_file=resume_file)
                if cv_analysis['success']:
                    cv_text = cv_analysis['text_content']
                else:
                    continue  # Skip if text extraction failed
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error extracting CV text: {str(e)}")
                continue  # Skip if any error occurs during extraction
            
            # Score the CV against job requirements
            score_result = chatgpt_helper.score_cv_for_job(
                cv_text=cv_text,
                job_requirements=job_requirements
            )
            
            # If scoring was successful and score is below 5, auto-reject
            if score_result['success'] and score_result['score'] < 5:
                # Update application status to rejected
                application.status = 'rejected'
                
                # Add explanation to the employer notes
                explanation = score_result['explanation']
                note = f"Hệ thống tự động từ chối. Điểm: {score_result['score']}/10\n\nLý do: {explanation}"
                
                if application.employer_notes:
                    application.employer_notes = f"{note}\n\n--- Ghi chú trước đó ---\n{application.employer_notes}"
                else:
                    application.employer_notes = note
                
                application.save(update_fields=['status', 'employer_notes'])
                rejected_count += 1
                
                # Create notification for the applicant
                notification_message = f"Đơn ứng tuyển của bạn cho vị trí {job.title} đã được xem xét và không phù hợp với yêu cầu công việc."
                Notification.objects.create(
                    user=application.applicant,
                    application=application,
                    notification_type='status_updated',
                    message=notification_message
                )
        except Exception as e:
            # Log error but continue with other applications
            logger = logging.getLogger(__name__)
            logger.error(f"Error in auto-reject for application {application.id}: {str(e)}")
            continue
    
    return {
        'processed': processed_count,
        'rejected': rejected_count
    }

@application_owner_required
@require_POST
def update_application_status(request, application_id, application=None):
    # application được truyền từ decorator
    new_status = request.POST.get('status')
    current_status = application.status
    
    # Define valid status transitions
    valid_transitions = {
        'pending': ['reviewed', 'shortlisted', 'rejected'],
        'reviewed': ['shortlisted', 'rejected'],
        'shortlisted': ['hired', 'rejected'],
        'rejected': [],
        'hired': []
    }
    
    # Check if the transition is valid
    if new_status in dict(Application.STATUS_CHOICES):
        if new_status in valid_transitions[current_status] or new_status == current_status:
            # Valid transition or same status
            application.status = new_status
            application.save()
            
            # Create notification for the applicant only if status has changed
            if current_status != new_status:
                status_display = dict(Application.STATUS_CHOICES).get(new_status)
                notification_message = f"Đơn ứng tuyển của bạn cho vị trí {application.job.title} đã được cập nhật trạng thái thành: {status_display}"
                
                Notification.objects.create(
                    user=application.applicant,
                    application=application,
                    notification_type='status_updated',
                    message=notification_message
                )
            
            messages.success(request, 'Application status updated successfully!')
        else:
            # Invalid transition
            messages.error(request, f'Không thể chuyển trạng thái từ "{dict(Application.STATUS_CHOICES).get(current_status)}" sang "{dict(Application.STATUS_CHOICES).get(new_status)}".')
    
    return redirect('applicant_tracking', job_id=application.job.id)

@job_seeker_required
def job_seeker_applications(request):
    # Get all applications submitted by the job seeker
    applications = Application.objects.filter(applicant=request.user).order_by('-created_at')
    
    # Lấy thông báo chưa đọc cho widget thông báo
    unread_notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-created_at')
    
    # Đếm số lượng thông báo chưa đọc
    unread_notification_count = unread_notifications.count()
    
    # Prefetch related notifications cho mỗi đơn ứng tuyển để tối ưu hiệu suất
    applications = applications.prefetch_related('notifications')
    
    context = {
        'applications': applications,
        'unread_notifications': unread_notifications,
        'unread_notification_count': unread_notification_count,
    }
    return render(request, 'jobs/job_applications.html', context)

@user_required
def notifications_view(request):
    # Lấy tất cả thông báo của người dùng hiện tại
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Đánh dấu tất cả thông báo là đã đọc khi người dùng xem danh sách
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        notifications.update(is_read=True)
        messages.success(request, 'Tất cả thông báo đã được đánh dấu là đã đọc.')
        return redirect('notifications')
    
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notification_list.html', context)

@user_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Chuyển hướng trở lại trang trước đó
    next_url = request.GET.get('next', 'notifications')
    return redirect(next_url)

def get_unread_notification_count(request):
    """Helper function để lấy số lượng thông báo chưa đọc của người dùng"""
    if request.user.is_authenticated:
        return Notification.objects.filter(user=request.user, is_read=False).count()
    return 0

@application_owner_required
def view_application_resume(request, application_id, application=None):
    """
    View for employers to view the resume submitted with an application
    """
    if not application.resume:
        messages.error(request, 'Không tìm thấy CV cho đơn ứng tuyển này.')
        return redirect('applicant_tracking', job_id=application.job.id)
    
    # Return the resume file for viewing/download
    response = redirect(application.resume.file.url)
    return response

@job_seeker_required
def view_my_application_resume(request, application_id):
    """
    View for job seekers to view the resume they submitted with their application
    """
    # Ensure the job seeker has access to this application
    application = get_object_or_404(Application, id=application_id, applicant=request.user)
    
    if not application.resume:
        messages.error(request, 'Không tìm thấy CV cho đơn ứng tuyển này.')
        return redirect('my_applications')
    
    # Return the resume file for viewing/download
    response = redirect(application.resume.file.url)
    return response

@application_owner_required
@require_POST
def save_application_note(request, application_id, application=None):
    """
    Save employer's notes for an application
    """
    try:
        data = json.loads(request.body)
        note = data.get('note', '').strip()
        
        # Update the note
        application.employer_notes = note
        application.save(update_fields=['employer_notes'])
        
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
