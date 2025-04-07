#!/usr/bin/env python
"""
Script để liệt kê tất cả các công việc có trong cơ sở dữ liệu
"""
import os
import sys
import django

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

# Import các model sau khi thiết lập Django
from jobs.models import Job
from django.contrib.auth import get_user_model

def list_all_jobs():
    """Liệt kê tất cả các công việc trong cơ sở dữ liệu"""
    print("DANH SÁCH TẤT CẢ CÔNG VIỆC HIỆN CÓ TRONG HỆ THỐNG")
    print("="*80)
    print(f"{'ID':<5} {'TIÊU ĐỀ':<30} {'ĐỊA ĐIỂM':<15} {'LOẠI CÔNG VIỆC':<15} {'TRẠNG THÁI':<12} {'THỜI HẠN':<20}")
    print("-"*80)
    
    jobs = Job.objects.all().order_by('-created_at')
    
    if not jobs:
        print("Không có công việc nào trong cơ sở dữ liệu.")
        return
    
    for job in jobs:
        job_type_display = dict(Job.JOB_TYPE_CHOICES).get(job.job_type, job.job_type)
        status_display = dict(Job.STATUS_CHOICES).get(job.status, job.status)
        location_display = dict(Job.VIETNAM_LOCATIONS).get(job.location, job.location)
        
        print(f"{job.id:<5} {job.title[:28]:<30} {location_display[:13]:<15} "
              f"{job_type_display[:13]:<15} {status_display[:10]:<12} "
              f"{job.application_deadline.strftime('%d/%m/%Y %H:%M'):<20}")
    
    print("="*80)
    print(f"Tổng số: {jobs.count()} công việc")

def list_jobs_by_status(status):
    """Liệt kê công việc theo trạng thái"""
    status_choices = dict(Job.STATUS_CHOICES)
    
    if status not in status_choices:
        print(f"Trạng thái không hợp lệ. Các trạng thái hợp lệ: {', '.join(status_choices.keys())}")
        return
    
    print(f"DANH SÁCH CÔNG VIỆC CÓ TRẠNG THÁI: {status_choices[status]}")
    print("="*80)
    print(f"{'ID':<5} {'TIÊU ĐỀ':<30} {'ĐỊA ĐIỂM':<15} {'LOẠI CÔNG VIỆC':<15} {'THỜI HẠN':<20}")
    print("-"*80)
    
    jobs = Job.objects.filter(status=status).order_by('-created_at')
    
    if not jobs:
        print(f"Không có công việc nào có trạng thái '{status_choices[status]}'.")
        return
    
    for job in jobs:
        job_type_display = dict(Job.JOB_TYPE_CHOICES).get(job.job_type, job.job_type)
        location_display = dict(Job.VIETNAM_LOCATIONS).get(job.location, job.location)
        
        print(f"{job.id:<5} {job.title[:28]:<30} {location_display[:13]:<15} "
              f"{job_type_display[:13]:<15} {job.application_deadline.strftime('%d/%m/%Y %H:%M'):<20}")
    
    print("="*80)
    print(f"Tổng số: {jobs.count()} công việc")

def list_jobs_by_employer(employer_id=None, employer_username=None):
    """Liệt kê các công việc theo người tuyển dụng"""
    User = get_user_model()
    
    try:
        if employer_id:
            employer = User.objects.get(id=employer_id)
        elif employer_username:
            employer = User.objects.get(username=employer_username)
        else:
            print("Vui lòng cung cấp ID hoặc tên người dùng của nhà tuyển dụng")
            return
    except User.DoesNotExist:
        print("Không tìm thấy người dùng với thông tin đã cung cấp")
        return
        
    print(f"DANH SÁCH CÔNG VIỆC CỦA NHÀ TUYỂN DỤNG: {employer.username}")
    print("="*80)
    print(f"{'ID':<5} {'TIÊU ĐỀ':<30} {'ĐỊA ĐIỂM':<15} {'LOẠI CÔNG VIỆC':<15} {'TRẠNG THÁI':<12} {'THỜI HẠN':<20}")
    print("-"*80)
    
    jobs = Job.objects.filter(employer=employer).order_by('-created_at')
    
    if not jobs:
        print(f"Không có công việc nào được đăng bởi '{employer.username}'.")
        return
    
    for job in jobs:
        job_type_display = dict(Job.JOB_TYPE_CHOICES).get(job.job_type, job.job_type)
        status_display = dict(Job.STATUS_CHOICES).get(job.status, job.status)
        location_display = dict(Job.VIETNAM_LOCATIONS).get(job.location, job.location)
        
        print(f"{job.id:<5} {job.title[:28]:<30} {location_display[:13]:<15} "
              f"{job_type_display[:13]:<15} {status_display[:10]:<12} "
              f"{job.application_deadline.strftime('%d/%m/%Y %H:%M'):<20}")
    
    print("="*80)
    print(f"Tổng số: {jobs.count()} công việc")

if __name__ == "__main__":
    # Xử lý tham số dòng lệnh
    if len(sys.argv) == 1:
        list_all_jobs()
    elif len(sys.argv) >= 2:
        option = sys.argv[1]
        
        if option == '--status' and len(sys.argv) == 3:
            list_jobs_by_status(sys.argv[2])
        elif option == '--employer-id' and len(sys.argv) == 3:
            list_jobs_by_employer(employer_id=sys.argv[2])
        elif option == '--employer-username' and len(sys.argv) == 3:
            list_jobs_by_employer(employer_username=sys.argv[2])
        else:
            print("Sử dụng:")
            print("  python list_jobs.py                       # Liệt kê tất cả công việc")
            print("  python list_jobs.py --status STATUS       # Lọc theo trạng thái (active/filled/expired/draft)")
            print("  python list_jobs.py --employer-id ID      # Lọc theo ID nhà tuyển dụng")
            print("  python list_jobs.py --employer-username USERNAME  # Lọc theo tên người dùng nhà tuyển dụng")