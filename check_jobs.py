#!/usr/bin/env python
"""
Script để kiểm tra chi tiết các công việc hiện có trong cơ sở dữ liệu
"""
import os
import sys
import django
import textwrap

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

# Import các model sau khi thiết lập Django
from jobs.models import Job

def check_job_details(job_id=None):
    """Kiểm tra chi tiết của một công việc theo ID hoặc tất cả các công việc"""
    jobs = []
    
    if job_id:
        try:
            jobs = [Job.objects.get(id=job_id)]
        except Job.DoesNotExist:
            print(f"Không tìm thấy công việc với ID = {job_id}")
            return
    else:
        jobs = Job.objects.all().order_by('-id')
    
    for job in jobs:
        print("="*80)
        print(f"ID: {job.id}")
        print(f"Tiêu đề: {job.title}")
        print(f"Nhà tuyển dụng: {job.employer.username}")
        print(f"Địa điểm: {dict(Job.VIETNAM_LOCATIONS).get(job.location, job.location)}")
        print(f"Loại công việc: {dict(Job.JOB_TYPE_CHOICES).get(job.job_type, job.job_type)}")
        print(f"Mức lương: {job.min_salary:,} - {job.max_salary:,} VNĐ/tháng")
        print(f"Trạng thái: {dict(Job.STATUS_CHOICES).get(job.status, job.status)}")
        print(f"Thời hạn: {job.application_deadline.strftime('%d/%m/%Y %H:%M')}")
        print(f"Đã đăng: {job.created_at.strftime('%d/%m/%Y %H:%M')}")
        
        print("\nMô tả:")
        description = job.description.strip() if job.description else "Không có mô tả"
        print(textwrap.fill(description, width=80)[:300])
        if len(description) > 300:
            print("... (còn nữa)")
            
        print("\nYêu cầu:")
        requirements = job.requirements.strip() if job.requirements else "Không có yêu cầu"
        print(textwrap.fill(requirements, width=80)[:300])
        if len(requirements) > 300:
            print("... (còn nữa)")
        
        print("="*80)
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            job_id = int(sys.argv[1])
            check_job_details(job_id)
        except ValueError:
            print("ID công việc phải là một số nguyên.")
    else:
        check_job_details()
        print(f"Tổng số: {Job.objects.count()} công việc.") 