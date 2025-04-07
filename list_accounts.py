import os
import django
import sys

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from accounts.models import User

def list_all_accounts():
    users = User.objects.all()
    print(f"Tổng số tài khoản: {users.count()}")
    print("-" * 80)
    print(f"{'Username':<20} {'Email':<30} {'Loại người dùng':<20} {'Công ty/Kỹ năng'}")
    print("-" * 80)
    
    for user in users:
        user_type = user.get_user_type_display()
        additional_info = user.company_name if user.user_type == 'employer' else user.skills
        additional_info = additional_info or ''
        if additional_info and len(additional_info) > 30:
            additional_info = additional_info[:27] + '...'
        
        print(f"{user.username:<20} {user.email:<30} {user_type:<20} {additional_info}")

def list_employers():
    employers = User.objects.filter(user_type='employer')
    print(f"Tổng số nhà tuyển dụng: {employers.count()}")
    print("-" * 80)
    print(f"{'Username':<20} {'Email':<30} {'Công ty':<30} {'Website'}")
    print("-" * 80)
    
    for employer in employers:
        company = employer.company_name or ''
        website = employer.company_website or ''
        print(f"{employer.username:<20} {employer.email:<30} {company:<30} {website}")

def list_job_seekers():
    job_seekers = User.objects.filter(user_type='job_seeker')
    print(f"Tổng số người tìm việc: {job_seekers.count()}")
    print("-" * 80)
    print(f"{'Username':<20} {'Email':<30} {'Kỹ năng'}")
    print("-" * 80)
    
    for seeker in job_seekers:
        skills = seeker.skills or ''
        if skills and len(skills) > 40:
            skills = skills[:37] + '...'
        print(f"{seeker.username:<20} {seeker.email:<30} {skills}")

if __name__ == "__main__":
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'employers':
            list_employers()
        elif command == 'job_seekers':
            list_job_seekers()
        else:
            print("Lệnh không hợp lệ. Sử dụng: employers, job_seekers hoặc không tham số để liệt kê tất cả.")
    else:
        list_all_accounts()