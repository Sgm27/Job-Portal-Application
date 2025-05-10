#!/usr/bin/env python
"""
Script để xóa tất cả các công việc có trong cơ sở dữ liệu và thêm lại các công việc mẫu mới
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

def delete_all_jobs():
    """Xóa tất cả các công việc trong cơ sở dữ liệu"""
    count, _ = Job.objects.all().delete()
    print(f"Đã xóa {count} công việc khỏi cơ sở dữ liệu.")

def add_sample_jobs():
    """Thêm các công việc mẫu vào cơ sở dữ liệu"""
    # Lấy danh sách người dùng loại 'employer'
    employers = User.objects.filter(user_type='employer')
    
    if not employers.exists():
        print("Không có nhà tuyển dụng nào trong hệ thống. Vui lòng tạo tài khoản nhà tuyển dụng trước.")
        return
    
    # Lấy employer đầu tiên làm ví dụ
    employer = employers.first()
    
    # Định nghĩa các công việc mẫu
    sample_jobs = [
        {
            'title': 'Kỹ sư Phần mềm Senior',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phần mềm Senior để tham gia vào đội ngũ phát triển sản phẩm của chúng tôi. Bạn sẽ chịu trách nhiệm thiết kế, phát triển và duy trì các ứng dụng phần mềm của chúng tôi.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các ứng dụng phần mềm
- Cộng tác với các thành viên trong nhóm để phát triển các tính năng mới
- Tối ưu hóa hiệu suất ứng dụng
- Đảm bảo chất lượng và khả năng mở rộng của mã
- Tham gia vào quá trình phát triển từ lúc hình thành ý tưởng đến khi triển khai
            """,
            'requirements': """
- Tối thiểu 5 năm kinh nghiệm phát triển phần mềm
- Thành thạo một hoặc nhiều ngôn ngữ lập trình: Python, Java, C++
- Kinh nghiệm với các framework web hiện đại
- Hiểu biết sâu về cấu trúc dữ liệu và thuật toán
- Khả năng làm việc độc lập và theo nhóm
- Kỹ năng giao tiếp và giải quyết vấn đề tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'Nhà phát triển Front-end',
            'description': """
Công ty chúng tôi đang tìm kiếm một Nhà phát triển Front-end tài năng để tạo ra giao diện người dùng hấp dẫn và trực quan cho các ứng dụng web của chúng tôi.

Trách nhiệm:
- Phát triển giao diện người dùng hấp dẫn và đáp ứng
- Làm việc với HTML, CSS, JavaScript và các framework hiện đại
- Cộng tác với nhà thiết kế và nhà phát triển back-end
- Tối ưu hóa ứng dụng cho hiệu suất và khả năng mở rộng
- Đảm bảo tính tương thích trên nhiều trình duyệt và thiết bị
            """,
            'requirements': """
- Ít nhất 3 năm kinh nghiệm phát triển front-end
- Thành thạo HTML, CSS, JavaScript
- Kinh nghiệm với React, Angular hoặc Vue.js
- Hiểu biết về thiết kế đáp ứng và trải nghiệm người dùng
- Khả năng làm việc trong môi trường phát triển nhanh
- Tinh thần làm việc nhóm tốt
            """,
            'location': 'ha_noi',
            'min_salary': 20000000,
            'max_salary': 35000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=20),
            'status': 'active'
        },
        {
            'title': 'Chuyên viên Phân tích Dữ liệu',
            'description': """
Chúng tôi đang tìm kiếm một Chuyên viên Phân tích Dữ liệu có năng lực để phân tích và diễn giải dữ liệu phức tạp, giúp công ty đưa ra quyết định dựa trên dữ liệu.

Trách nhiệm:
- Thu thập, xử lý và phân tích dữ liệu từ nhiều nguồn
- Phát triển và triển khai các mô hình phân tích
- Tạo báo cáo và trực quan hóa dữ liệu
- Xác định xu hướng và mẫu trong dữ liệu
- Đưa ra đề xuất dựa trên phân tích dữ liệu
            """,
            'requirements': """
- Bằng cử nhân hoặc cao hơn trong Khoa học Dữ liệu, Thống kê hoặc lĩnh vực liên quan
- Kinh nghiệm với SQL, Python, R và các công cụ phân tích dữ liệu
- Kỹ năng trực quan hóa dữ liệu (Tableau, Power BI)
- Hiểu biết về thống kê và khai thác dữ liệu
- Kỹ năng giao tiếp và trình bày tốt
- Khả năng giải quyết vấn đề và tư duy phản biện
            """,
            'location': 'da_nang',
            'min_salary': 25000000,
            'max_salary': 40000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=25),
            'status': 'active'
        },
        {
            'title': 'Thực tập sinh Marketing số',
            'description': """
Chúng tôi đang tìm kiếm các thực tập sinh đam mê Marketing Số để tham gia vào đội ngũ marketing của chúng tôi. Đây là cơ hội tuyệt vời để học hỏi và phát triển kỹ năng trong lĩnh vực marketing số.

Trách nhiệm:
- Hỗ trợ các chiến dịch marketing số
- Quản lý và tạo nội dung cho mạng xã hội
- Phân tích dữ liệu từ các chiến dịch marketing
- Hỗ trợ tổ chức sự kiện và quảng cáo
- Nghiên cứu thị trường và đối thủ cạnh tranh
            """,
            'requirements': """
- Đang theo học hoặc vừa tốt nghiệp ngành Marketing, Truyền thông hoặc lĩnh vực liên quan
- Hiểu biết cơ bản về marketing số
- Kỹ năng viết và giao tiếp tốt
- Sáng tạo và ham học hỏi
- Làm việc nhóm hiệu quả
- Có kiến thức về các nền tảng mạng xã hội là một lợi thế
            """,
            'location': 'ho_chi_minh',
            'min_salary': 5000000,
            'max_salary': 8000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=15),
            'status': 'active'
        },
        {
            'title': 'Nhà thiết kế UI/UX',
            'description': """
Chúng tôi đang tìm kiếm một Nhà thiết kế UI/UX tài năng để tạo ra trải nghiệm người dùng tuyệt vời cho các sản phẩm số của chúng tôi.

Trách nhiệm:
- Thiết kế giao diện người dùng hấp dẫn và trực quan
- Tạo wireframes, mockups và prototypes
- Tiến hành nghiên cứu người dùng và phân tích đối thủ cạnh tranh
- Cộng tác với nhà phát triển để triển khai thiết kế
- Đảm bảo tính nhất quán trong thiết kế của sản phẩm
            """,
            'requirements': """
- Ít nhất 2 năm kinh nghiệm thiết kế UI/UX
- Thành thạo các công cụ thiết kế như Figma, Sketch, Adobe XD
- Hiểu biết về nguyên tắc thiết kế và tương tác người dùng
- Portfolio thể hiện kỹ năng thiết kế UI/UX
- Kỹ năng giao tiếp và làm việc nhóm tốt
- Khả năng quản lý nhiều dự án cùng một lúc
            """,
            'location': 'ha_noi',
            'min_salary': 18000000,
            'max_salary': 30000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=22),
            'status': 'active'
        },
        {
            'title': 'Kỹ sư DevOps',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư DevOps tài năng để tự động hóa và tối ưu hóa quy trình phát triển và triển khai của chúng tôi.

Trách nhiệm:
- Thiết kế và triển khai cơ sở hạ tầng CI/CD
- Tự động hóa quy trình triển khai và kiểm thử
- Quản lý và tối ưu hóa hệ thống đám mây
- Giám sát hiệu suất hệ thống và đảm bảo tính sẵn sàng cao
- Cộng tác với đội ngũ phát triển để cải thiện quy trình
            """,
            'requirements': """
- Ít nhất 3 năm kinh nghiệm trong vị trí DevOps
- Kinh nghiệm với các công cụ CI/CD như Jenkins, GitLab CI
- Kiến thức về containerization (Docker, Kubernetes)
- Kinh nghiệm với các dịch vụ đám mây (AWS, Azure, GCP)
- Kỹ năng tự động hóa với scripting (Python, Bash)
- Hiểu biết về bảo mật và quản lý cấu hình
            """,
            'location': 'ho_chi_minh',
            'min_salary': 25000000,
            'max_salary': 45000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=28),
            'status': 'active'
        },
        {
            'title': 'Giáo viên tiếng Anh bán thời gian',
            'description': """
Trung tâm Anh ngữ của chúng tôi đang tìm kiếm Giáo viên tiếng Anh bán thời gian để giảng dạy cho học sinh các lứa tuổi.

Trách nhiệm:
- Giảng dạy tiếng Anh cho học sinh từ 5-15 tuổi
- Chuẩn bị giáo án và tài liệu giảng dạy
- Đánh giá tiến bộ của học sinh
- Tham gia các cuộc họp và đào tạo giáo viên
- Tạo môi trường học tập thú vị và hiệu quả
            """,
            'requirements': """
- Chứng chỉ giảng dạy tiếng Anh (TESOL, TEFL, CELTA)
- Phát âm chuẩn và kỹ năng giao tiếp tốt
- Kinh nghiệm giảng dạy là một lợi thế
- Yêu thích làm việc với trẻ em
- Kiên nhẫn và sáng tạo
- Có thể làm việc vào buổi tối và cuối tuần
            """,
            'location': 'ho_chi_minh',
            'min_salary': 150000,
            'max_salary': 250000,
            'job_type': 'part_time',
            'application_deadline': timezone.now() + timedelta(days=18),
            'status': 'active'
        },
        {
            'title': 'Chuyên viên Quản lý Dự án',
            'description': """
Chúng tôi đang tìm kiếm một Chuyên viên Quản lý Dự án có kinh nghiệm để lập kế hoạch, thực hiện và hoàn thành các dự án phức tạp đúng thời hạn và trong ngân sách.

Trách nhiệm:
- Lập kế hoạch và phối hợp các dự án từ đầu đến cuối
- Xác định và quản lý nguồn lực dự án
- Lập lịch trình, ngân sách và phạm vi dự án
- Giao tiếp với các bên liên quan và báo cáo tiến độ
- Quản lý rủi ro và giải quyết vấn đề
            """,
            'requirements': """
- Ít nhất 3 năm kinh nghiệm quản lý dự án
- Chứng chỉ PMP hoặc tương đương là một lợi thế
- Hiểu biết về các phương pháp quản lý dự án (Agile, Scrum, Waterfall)
- Kỹ năng giao tiếp và lãnh đạo xuất sắc
- Khả năng làm việc dưới áp lực và xử lý nhiều nhiệm vụ
- Thành thạo MS Project hoặc các công cụ quản lý dự án tương tự
            """,
            'location': 'ha_noi',
            'min_salary': 25000000,
            'max_salary': 40000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=25),
            'status': 'active'
        },
        {
            'title': 'Chuyên viên Hỗ trợ Kỹ thuật từ xa',
            'description': """
Chúng tôi đang tìm kiếm một Chuyên viên Hỗ trợ Kỹ thuật để hỗ trợ khách hàng từ xa, giải quyết các vấn đề kỹ thuật và đảm bảo sự hài lòng của khách hàng.

Trách nhiệm:
- Cung cấp hỗ trợ kỹ thuật qua điện thoại, email và chat
- Chẩn đoán và giải quyết các vấn đề phần mềm và phần cứng
- Tạo và duy trì tài liệu hỗ trợ kỹ thuật
- Theo dõi và cập nhật các yêu cầu hỗ trợ trong hệ thống
- Đề xuất cải tiến sản phẩm và dịch vụ
            """,
            'requirements': """
- Kiến thức về hệ điều hành Windows, macOS và các ứng dụng phổ biến
- Kỹ năng giao tiếp và giải quyết vấn đề tốt
- Kinh nghiệm với các công cụ hỗ trợ khách hàng
- Khả năng làm việc độc lập và trong nhóm
- Kiên nhẫn và hướng đến dịch vụ khách hàng
- Có thể làm việc theo ca nếu cần thiết
            """,
            'location': 'da_nang',
            'min_salary': 15000000,
            'max_salary': 25000000,
            'job_type': 'remote',
            'application_deadline': timezone.now() + timedelta(days=20),
            'status': 'active'
        },
        {
            'title': 'Nhà phát triển Blockchain',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Blockchain tài năng để tham gia vào đội ngũ xây dựng các giải pháp phân tán tiên tiến.

Trách nhiệm:
- Thiết kế và phát triển các ứng dụng blockchain
- Triển khai smart contracts và các giao thức blockchain
- Tối ưu hóa hiệu suất và bảo mật của các giải pháp blockchain
- Nghiên cứu và đề xuất các công nghệ blockchain mới
- Cộng tác với đội ngũ để tích hợp blockchain vào các sản phẩm hiện có
            """,
            'requirements': """
- Ít nhất 2 năm kinh nghiệm phát triển blockchain
- Kinh nghiệm với Ethereum, Solidity, Web3.js
- Hiểu biết về các giao thức đồng thuận và cấu trúc dữ liệu phân tán
- Kiến thức về mật mã học và bảo mật blockchain
- Kỹ năng giải quyết vấn đề và tư duy phản biện
- Đam mê học hỏi và theo kịp các xu hướng blockchain mới
            """,
            'location': 'ho_chi_minh',
            'min_salary': 30000000,
            'max_salary': 60000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        # --- Intern/Fresher Jobs Start ---
        {
            'title': 'Thực tập sinh Kỹ sư Phần mềm',
            'description': 'Tham gia hỗ trợ đội ngũ phát triển phần mềm trong các dự án thực tế. Cơ hội học hỏi về quy trình phát triển và công nghệ mới.',
            'requirements': '- Sinh viên năm cuối hoặc mới tốt nghiệp ngành CNTT hoặc liên quan.\n- Có kiến thức cơ bản về lập trình (Python, Java, C#...). \n- Tư duy logic tốt, ham học hỏi.',
            'location': 'ha_noi',
            'min_salary': 4000000,
            'max_salary': 7000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=10),
            'status': 'active'
        },
        {
            'title': 'Fresher Front-end Developer',
            'description': 'Phát triển giao diện người dùng cho các ứng dụng web dưới sự hướng dẫn của các senior. Học hỏi và áp dụng các công nghệ front-end mới nhất.',
            'requirements': '- Tốt nghiệp ngành CNTT hoặc có kinh nghiệm tương đương.\n- Nắm vững HTML, CSS, JavaScript cơ bản.\n- Có hiểu biết về React, Angular hoặc Vue.js là lợi thế.\n- Có sản phẩm demo là một điểm cộng.',
            'location': 'ho_chi_minh',
            'min_salary': 8000000,
            'max_salary': 12000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=15),
            'status': 'active'
        },
        {
            'title': 'Thực tập sinh Phân tích Dữ liệu',
            'description': 'Hỗ trợ thu thập, làm sạch và phân tích dữ liệu cơ bản. Học cách sử dụng các công cụ phân tích và trực quan hóa dữ liệu.',
            'requirements': '- Sinh viên các ngành Toán tin, Thống kê, Kinh tế lượng hoặc liên quan.\n- Có kiến thức cơ bản về SQL, Excel.\n- Biết Python hoặc R là lợi thế.\n- Cẩn thận, tỉ mỉ.',
            'location': 'da_nang',
            'min_salary': 4000000,
            'max_salary': 6000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=12),
            'status': 'active'
        },
        {
            'title': 'Fresher Tester (Manual)',
            'description': 'Thực hiện kiểm thử thủ công các tính năng phần mềm theo kịch bản. Báo cáo lỗi và theo dõi quá trình sửa lỗi.',
            'requirements': '- Tốt nghiệp Cao đẳng/Đại học.\n- Không yêu cầu kinh nghiệm, sẽ được đào tạo.\n- Cẩn thận, chi tiết, có khả năng phát hiện lỗi.\n- Có kiến thức cơ bản về quy trình test là lợi thế.',
            'location': 'ha_noi',
            'min_salary': 7000000,
            'max_salary': 10000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=18),
            'status': 'active'
        },
        {
            'title': 'Thực tập sinh Thiết kế UI/UX',
            'description': 'Hỗ trợ team thiết kế trong việc tạo wireframes, mockups đơn giản. Tìm hiểu về quy trình thiết kế và các công cụ thiết kế.',
            'requirements': '- Sinh viên ngành Thiết kế đồ họa, Mỹ thuật công nghiệp hoặc liên quan.\n- Có kiến thức cơ bản về các nguyên tắc thiết kế.\n- Biết sử dụng Figma, Sketch hoặc Adobe XD là lợi thế.\n- Có portfolio đơn giản.',
            'location': 'ho_chi_minh',
            'min_salary': 4000000,
            'max_salary': 6000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=10),
            'status': 'active'
        },
        {
            'title': 'Fresher Back-end Developer (Python/Django)',
            'description': 'Tham gia phát triển phía server cho các ứng dụng web sử dụng Python và Django. Xây dựng API và làm việc với cơ sở dữ liệu.',
            'requirements': '- Tốt nghiệp ngành CNTT hoặc tương đương.\n- Có kiến thức cơ bản về Python và lập trình hướng đối tượng.\n- Hiểu biết về Django hoặc Flask là lợi thế.\n- Có kiến thức về RESTful API, cơ sở dữ liệu (SQL/NoSQL).',
            'location': 'da_nang',
            'min_salary': 9000000,
            'max_salary': 14000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=20),
            'status': 'active'
        },
         {
            'title': 'Thực tập sinh Nhân sự',
            'description': 'Hỗ trợ các công việc hành chính nhân sự, tuyển dụng (đăng tin, sàng lọc hồ sơ), tổ chức sự kiện nội bộ.',
            'requirements': '- Sinh viên các ngành Quản trị Nhân lực, Quản trị Kinh doanh hoặc liên quan.\n- Kỹ năng giao tiếp tốt, năng động.\n- Cẩn thận, có trách nhiệm.\n- Thành thạo tin học văn phòng.',
            'location': 'ha_noi',
            'min_salary': 3000000,
            'max_salary': 5000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=14),
            'status': 'active'
        },
        {
            'title': 'Fresher Business Analyst',
            'description': 'Học hỏi và hỗ trợ thu thập, phân tích yêu cầu nghiệp vụ từ khách hàng/các bộ phận. Viết tài liệu mô tả yêu cầu.',
            'requirements': '- Tốt nghiệp các ngành Hệ thống thông tin quản lý, CNTT, Kinh tế.\n- Tư duy logic, khả năng phân tích tốt.\n- Kỹ năng giao tiếp, trình bày tốt.\n- Tiếng Anh đọc hiểu tài liệu kỹ thuật.',
            'location': 'ho_chi_minh',
            'min_salary': 8000000,
            'max_salary': 13000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=22),
            'status': 'active'
        },
        {
            'title': 'Thực tập sinh Content Marketing',
            'description': 'Hỗ trợ viết bài cho blog, website, mạng xã hội theo chủ đề được giao. Tìm hiểu về SEO cơ bản và các công cụ marketing.',
            'requirements': '- Sinh viên các ngành Báo chí, Truyền thông, Marketing, Ngữ văn.\n- Khả năng viết lách tốt, sáng tạo.\n- Yêu thích lĩnh vực marketing, mạng xã hội.\n- Ham học hỏi, có trách nhiệm.',
            'location': 'da_nang',
            'min_salary': 3000000,
            'max_salary': 5000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=16),
            'status': 'active'
        },
        {
            'title': 'Fresher IT Support/Helpdesk',
            'description': 'Hỗ trợ người dùng trong công ty về các vấn đề kỹ thuật máy tính, mạng, phần mềm cơ bản. Cài đặt, cấu hình thiết bị.',
            'requirements': '- Tốt nghiệp Cao đẳng/Đại học chuyên ngành Mạng máy tính, CNTT.\n- Có kiến thức cơ bản về phần cứng, phần mềm, mạng.\n- Kỹ năng giao tiếp tốt, kiên nhẫn.\n- Có thể làm việc theo ca (nếu có).',
            'location': 'ha_noi',
            'min_salary': 7000000,
            'max_salary': 11000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=19),
            'status': 'active'
        },
        # --- Intern/Fresher Jobs End ---
        # +++ AI, Web, Software Jobs Start +++
        {
            'title': 'AI Research Scientist',
            'description': 'Conduct cutting-edge research in machine learning, deep learning, and artificial intelligence. Publish findings and contribute to the development of innovative AI solutions.',
            'requirements': '- PhD or Master\'s in Computer Science, AI, or related field.\n- Strong publication record in top AI conferences/journals.\n- Expertise in Python, TensorFlow, PyTorch.',
            'location': 'ho_chi_minh',
            'min_salary': 50000000,
            'max_salary': 80000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=40),
            'status': 'active'
        },
        {
            'title': 'Full-stack Web Developer (Remote)',
            'description': 'Develop and maintain web applications using modern front-end and back-end technologies. Work collaboratively in a remote team environment.',
            'requirements': '- 3+ years of experience with React/Angular/Vue and Node.js/Python/Ruby.\n- Proficient in database technologies (SQL/NoSQL).\n- Experience with cloud platforms (AWS, Azure, GCP).',
            'location': 'remote',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'remote',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'Software Engineer (Mobile - iOS)',
            'description': 'Design and build advanced applications for the iOS platform. Collaborate with cross-functional teams to define, design, and ship new features.',
            'requirements': '- Proven working experience in iOS app development (Swift/Objective-C).\n- Experience with iOS frameworks such as Core Data, Core Animation, etc.\n- Familiarity with RESTful APIs to connect iOS applications to back-end services.',
            'location': 'ha_noi',
            'min_salary': 28000000,
            'max_salary': 45000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=35),
            'status': 'active'
        },
        {
            'title': 'Machine Learning Engineer',
            'description': 'Design, build, and deploy machine learning models to solve real-world problems. Work with large datasets and production systems.',
            'requirements': '- Master\'s or Bachelor\'s in CS, Statistics, or related field.\n- Experience with ML frameworks (scikit-learn, Keras, etc.).\n- Strong programming skills in Python.',
            'location': 'da_nang',
            'min_salary': 35000000,
            'max_salary': 60000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'React Native Developer',
            'description': 'Develop cross-platform mobile applications using React Native. Focus on building user-friendly and performant mobile experiences.',
            'requirements': '- 2+ years of experience with React Native.\n- Strong understanding of JavaScript, ES6+.\n- Experience with native build tools, like XCode, Android Studio.',
            'location': 'ho_chi_minh',
            'min_salary': 25000000,
            'max_salary': 40000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=28),
            'status': 'active'
        },
        {
            'title': 'Back-end Developer (Java/Spring)',
            'description': 'Develop robust and scalable server-side applications using Java and Spring Framework. Design and implement APIs and microservices.',
            'requirements': '- 3+ years of experience with Java and Spring Boot.\n- Experience with RESTful APIs, microservices architecture.\n- Knowledge of databases (SQL/NoSQL) and CI/CD pipelines.',
            'location': 'ha_noi',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=32),
            'status': 'active'
        },
        {
            'title': 'Data Scientist - NLP Specialist',
            'description': 'Apply natural language processing techniques to extract insights from textual data. Develop models for text classification, sentiment analysis, etc.',
            'requirements': '- Master\'s or PhD in a quantitative field.\n- Strong experience with NLP libraries (NLTK, SpaCy, Transformers).\n- Proficiency in Python and machine learning.',
            'location': 'ho_chi_minh',
            'min_salary': 40000000,
            'max_salary': 70000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=38),
            'status': 'active'
        },
        {
            'title': 'Frontend Developer - Vue.js',
            'description': 'Build interactive and responsive user interfaces using Vue.js. Collaborate with UI/UX designers and backend developers.',
            'requirements': '- 2+ years of experience with Vue.js and its ecosystem (Vuex, Vue Router).\n- Proficient in HTML, CSS, JavaScript.\n- Experience with modern front-end build pipelines and tools.',
            'location': 'da_nang',
            'min_salary': 22000000,
            'max_salary': 38000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=25),
            'status': 'active'
        },
        {
            'title': 'Software Development Engineer in Test (SDET)',
            'description': 'Design and implement automated testing frameworks and test cases. Ensure software quality through continuous integration and delivery.',
            'requirements': '- Experience in software development and test automation (Selenium, Appium, etc.).\n- Strong programming skills (Python, Java, C#).\n- Knowledge of CI/CD tools and agile methodologies.',
            'location': 'ha_noi',
            'min_salary': 28000000,
            'max_salary': 48000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=29),
            'status': 'active'
        },
        {
            'title': 'AI Ethics Researcher',
            'description': 'Investigate the ethical implications of AI technologies. Develop guidelines and frameworks for responsible AI development and deployment.',
            'requirements': '- Advanced degree in Ethics, Law, Philosophy, CS, or related field with a focus on AI ethics.\n- Strong analytical and communication skills.\n- Understanding of current AI trends and societal impacts.',
            'location': 'remote',
            'min_salary': 35000000,
            'max_salary': 60000000,
            'job_type': 'remote',
            'application_deadline': timezone.now() + timedelta(days=45),
            'status': 'active'
        },
        {
            'title': 'Junior Web Developer (Internship)',
            'description': 'Assist senior developers in building and testing web applications. Learn and apply web development fundamentals in a practical setting.',
            'requirements': '- Currently enrolled in or recent graduate of a CS or related program.\n- Basic knowledge of HTML, CSS, JavaScript.\n- Eagerness to learn and strong problem-solving skills.',
            'location': 'ho_chi_minh',
            'min_salary': 5000000,
            'max_salary': 8000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=15),
            'status': 'active'
        },
        {
            'title': 'Software Engineer (Android)',
            'description': 'Develop native Android applications. Work with the latest Android SDKs and tools to create engaging mobile experiences.',
            'requirements': '- Proven experience in Android app development (Java/Kotlin).\n- Familiarity with Android design principles and interface guidelines.\n- Experience with third-party libraries and APIs.',
            'location': 'da_nang',
            'min_salary': 26000000,
            'max_salary': 42000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=33),
            'status': 'active'
        },
        {
            'title': 'Computer Vision Engineer',
            'description': 'Develop and implement computer vision algorithms for image and video analysis. Work on projects related to object detection, image recognition, etc.',
            'requirements': '- Master\'s or PhD in CS or related field with a focus on Computer Vision.\n- Experience with OpenCV, TensorFlow, PyTorch.\n- Strong C++ and Python programming skills.',
            'location': 'ha_noi',
            'min_salary': 40000000,
            'max_salary': 75000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=36),
            'status': 'active'
        },
        {
            'title': 'Angular Developer',
            'description': 'Build dynamic and responsive web applications using the Angular framework. Ensure high performance and scalability of front-end solutions.',
            'requirements': '- 2+ years of experience with Angular and TypeScript.\n- Proficient in HTML, CSS, and JavaScript.\n- Experience with RxJS and state management (NgRx).',
            'location': 'ho_chi_minh',
            'min_salary': 27000000,
            'max_salary': 43000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=26),
            'status': 'active'
        },
        {
            'title': 'Cloud Solutions Architect (Software Focus)',
            'description': 'Design and implement cloud-based software solutions. Advise on cloud strategy, architecture, and best practices for application development.',
            'requirements': '- Extensive experience with AWS, Azure, or GCP.\n- Strong understanding of software architecture principles.\n- Experience with containerization and microservices.',
            'location': 'remote',
            'min_salary': 50000000,
            'max_salary': 90000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=40),
            'status': 'active'
        },
        {
            'title': 'Robotics Software Engineer',
            'description': 'Develop software for robotic systems, including perception, navigation, and control. Integrate hardware and software components.',
            'requirements': '- Experience with ROS (Robot Operating System).\n- Strong C++ and Python programming skills.\n- Knowledge of robotics algorithms and kinematics.',
            'location': 'da_nang',
            'min_salary': 38000000,
            'max_salary': 65000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=34),
            'status': 'active'
        },
        {
            'title': 'Technical Writer (Software)',
            'description': 'Create clear and concise documentation for software products, including API guides, user manuals, and tutorials.',
            'requirements': '- Proven experience in technical writing for software.\n- Excellent written and verbal communication skills in English and Vietnamese.\n- Ability to understand complex technical concepts and explain them simply.',
            'location': 'ho_chi_minh',
            'min_salary': 20000000,
            'max_salary': 35000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=24),
            'status': 'active'
        },
        {
            'title': 'Game Developer (Unity/Unreal Engine)',
            'description': 'Develop games for various platforms using Unity or Unreal Engine. Work on game mechanics, graphics, and performance optimization.',
            'requirements': '- Experience with Unity (C#) or Unreal Engine (C++).\n- Strong understanding of game development principles.\n- Portfolio of game projects.',
            'location': 'ha_noi',
            'min_salary': 25000000,
            'max_salary': 45000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'AI Product Manager',
            'description': 'Define and drive the product strategy for AI-powered features and products. Work closely with engineering, design, and research teams.',
            'requirements': '- Experience in product management, preferably with AI/ML products.\n- Strong understanding of AI technologies and market trends.\n- Excellent communication and leadership skills.',
            'location': 'ho_chi_minh',
            'min_salary': 45000000,
            'max_salary': 75000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=37),
            'status': 'active'
        },
        {
            'title': 'Part-time Web Content Uploader',
            'description': 'Responsible for uploading and formatting content on company websites. Ensure accuracy and consistency of web content.',
            'requirements': '- Basic HTML knowledge.\n- Attention to detail and good organizational skills.\n- Ability to work independently and meet deadlines.',
            'location': 'remote',
            'min_salary': 100000, # Assuming per hour or project-based
            'max_salary': 150000, # Assuming per hour or project-based
            'job_type': 'part_time',
            'application_deadline': timezone.now() + timedelta(days=20),
            'status': 'active'
        }
        # +++ AI, Web, Software Jobs End +++
    ]
    
    # Thêm các công việc mẫu vào cơ sở dữ liệu
    count = 0
    for job_data in sample_jobs:
        Job.objects.create(
            employer=employer,
            **job_data
        )
        count += 1
    
    print(f"Đã thêm {count} công việc mẫu vào cơ sở dữ liệu.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--no-reset':
        # Chỉ thêm mới jobs mà không xóa cái cũ
        add_sample_jobs()
    else:
        # Xác nhận từ người dùng trước khi xóa
        confirm = input("Bạn có chắc chắn muốn xóa TẤT CẢ các công việc hiện có? (y/n): ")
        if confirm.lower() == 'y':
            delete_all_jobs()
            add_sample_jobs()
        else:
            print("Đã hủy thao tác.") 