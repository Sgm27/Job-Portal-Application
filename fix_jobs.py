#!/usr/bin/env python
"""
Script đơn giản để kiểm tra cú pháp
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

# Import các model sau khi thiết lập Django
from jobs.models import Job
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def add_sample_job():
    """Thêm một công việc mẫu vào cơ sở dữ liệu"""
    # Lấy danh sách người dùng loại 'employer'
    employers = User.objects.filter(user_type='employer')
    
    if not employers.exists():
        print("Không có nhà tuyển dụng nào trong hệ thống. Vui lòng tạo tài khoản nhà tuyển dụng trước.")
        return
    
    # Lấy employer đầu tiên làm ví dụ
    employer = employers.first()
    
    # Tạo công việc mẫu
    sample_job = {
        'title': 'Nhà phát triển Game',
        'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Game. Bạn sẽ làm việc với các công cụ hiện đại.

Trách nhiệm:
- Phát triển game cho nhiều nền tảng
- Thiết kế và triển khai các cơ chế game
- Phối hợp với team đồ họa để tích hợp hình ảnh
        """,
        'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển game
- Hiểu biết về đồ họa hai chiều và ba chiều
- Kinh nghiệm với version control
        """,
        'location': 'ha_noi',
        'min_salary': 25000000,
        'max_salary': 45000000,
        'job_type': 'full_time',
        'application_deadline': timezone.now() + timedelta(days=30),
        'status': 'active'
    }
    
    # Thêm công việc mẫu vào cơ sở dữ liệu
    Job.objects.create(
        employer=employer,
        **sample_job
    )
    
    print("Đã thêm công việc mẫu vào cơ sở dữ liệu.")

if __name__ == "__main__":
    add_sample_job() 