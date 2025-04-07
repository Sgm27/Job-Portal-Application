from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.views import redirect_to_login
from .models import Job

def employer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator để đảm bảo rằng chỉ nhà tuyển dụng mới có thể truy cập view.
    Thực hiện xác thực người dùng đầy đủ mà không phụ thuộc vào login_required của Django.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Tự kiểm tra xác thực thay vì dùng login_required
            if not request.user.is_authenticated:
                path = request.build_absolute_uri()
                login_url_resolved = login_url or settings.LOGIN_URL
                return redirect_to_login(path, login_url_resolved, redirect_field_name)
            
            # Kiểm tra loại người dùng
            if request.user.user_type != 'employer':
                messages.error(request, 'Chỉ nhà tuyển dụng mới có quyền truy cập trang này.')
                return redirect('home')
            
            # Thực thi view gốc
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator

def job_owner_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator để đảm bảo rằng người dùng là chủ sở hữu của công việc.
    Thực hiện xác thực người dùng đầy đủ mà không phụ thuộc vào login_required của Django.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, job_id, *args, **kwargs):
            # Tự kiểm tra xác thực thay vì dùng login_required
            if not request.user.is_authenticated:
                path = request.build_absolute_uri()
                login_url_resolved = login_url or settings.LOGIN_URL
                return redirect_to_login(path, login_url_resolved, redirect_field_name)
            
            # Kiểm tra loại người dùng - cần phải là nhà tuyển dụng
            if request.user.user_type != 'employer':
                messages.error(request, 'Chỉ nhà tuyển dụng mới có quyền truy cập trang này.')
                return redirect('home')
            
            # Lấy job và kiểm tra quyền sở hữu
            try:
                job = get_object_or_404(Job, id=job_id)
                # Kiểm tra employer thay vì user
                if job.employer.id != request.user.id:
                    messages.error(request, 'Bạn không có quyền truy cập công việc này.')
                    return redirect('employer_dashboard')
                
                # Tất cả kiểm tra đều thành công, thực thi view gốc với đối tượng job
                kwargs['job'] = job  # Truyền job vào view để tránh truy vấn lại
                return view_func(request, job_id, *args, **kwargs)
            except Exception as e:
                messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
                return redirect('employer_dashboard')
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator

def application_owner_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator để đảm bảo rằng người dùng là chủ sở hữu của application.
    Thực hiện xác thực người dùng đầy đủ mà không phụ thuộc vào login_required của Django.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, application_id, *args, **kwargs):
            # Tự kiểm tra xác thực thay vì dùng login_required
            if not request.user.is_authenticated:
                path = request.build_absolute_uri()
                login_url_resolved = login_url or settings.LOGIN_URL
                return redirect_to_login(path, login_url_resolved, redirect_field_name)
            
            # Kiểm tra loại người dùng - cần phải là nhà tuyển dụng
            if request.user.user_type != 'employer':
                messages.error(request, 'Chỉ nhà tuyển dụng mới có quyền truy cập trang này.')
                return redirect('home')
            
            # Lấy application và kiểm tra quyền sở hữu
            from .models import Application
            try:
                application = get_object_or_404(Application, id=application_id)
                # Kiểm tra employer thay vì user
                if application.job.employer.id != request.user.id:
                    messages.error(request, 'Bạn không có quyền truy cập đơn ứng tuyển này.')
                    return redirect('employer_dashboard')
                
                # Tất cả kiểm tra đều thành công, thực thi view gốc với đối tượng application
                kwargs['application'] = application  # Truyền application vào view để tránh truy vấn lại
                return view_func(request, application_id, *args, **kwargs)
            except Exception as e:
                messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
                return redirect('employer_dashboard')
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator

def job_seeker_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator để đảm bảo rằng chỉ người tìm việc mới có thể truy cập view
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Tự kiểm tra xác thực thay vì dùng login_required
            if not request.user.is_authenticated:
                path = request.build_absolute_uri()
                login_url_resolved = login_url or settings.LOGIN_URL
                return redirect_to_login(path, login_url_resolved, redirect_field_name)
            
            # Kiểm tra loại người dùng
            if request.user.user_type != 'job_seeker':
                messages.error(request, 'Chỉ người tìm việc mới có quyền truy cập trang này.')
                return redirect('home')
            
            # Thực thi view gốc
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator

def user_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator để đảm bảo người dùng đã đăng nhập, không quan tâm đến loại người dùng
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Tự kiểm tra xác thực thay vì dùng login_required
            if not request.user.is_authenticated:
                path = request.build_absolute_uri()
                login_url_resolved = login_url or settings.LOGIN_URL
                return redirect_to_login(path, login_url_resolved, redirect_field_name)
            
            # Thực thi view gốc
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator 