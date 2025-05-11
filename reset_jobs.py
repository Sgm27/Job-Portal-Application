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
            'description': """
Chúng tôi đang tìm kiếm một Fresher Tester để tham gia vào đội ngũ đảm bảo chất lượng phần mềm của chúng tôi. Đây là cơ hội tuyệt vời để bắt đầu sự nghiệp trong lĩnh vực kiểm thử phần mềm, học hỏi các phương pháp kiểm thử thủ công và tự động dưới sự hướng dẫn của các chuyên gia QA giàu kinh nghiệm.

Trách nhiệm:
- Thực hiện kiểm thử thủ công các ứng dụng phần mềm theo kịch bản và tài liệu kiểm thử
- Xác định, ghi lại và báo cáo các lỗi một cách rõ ràng và chi tiết
- Theo dõi và xác minh quá trình sửa lỗi
- Tham gia vào quá trình tạo và cập nhật các tài liệu kiểm thử
- Kiểm tra tính tương thích của ứng dụng trên nhiều trình duyệt, thiết bị và môi trường
- Học hỏi về quy trình kiểm thử và các phương pháp đảm bảo chất lượng
- Tham gia các buổi họp đánh giá chất lượng và lập kế hoạch kiểm thử
- Hợp tác với các nhà phát triển để hiểu yêu cầu và chức năng của sản phẩm
- Học và dần áp dụng các kỹ thuật kiểm thử tự động cơ bản
- Tham gia vào quá trình kiểm thử hiệu suất và bảo mật cơ bản
            """,
            'requirements': """
- Tốt nghiệp Cao đẳng/Đại học chuyên ngành Công nghệ Thông tin hoặc các ngành liên quan
- Tư duy phân tích và logic tốt, chú ý đến chi tiết
- Khả năng phát hiện lỗi và báo cáo vấn đề một cách rõ ràng
- Hiểu biết cơ bản về quy trình phát triển phần mềm
- Kiến thức nền tảng về các loại kiểm thử (functional, regression, usability)
- Khả năng làm việc có tổ chức và theo dõi nhiều tác vụ cùng lúc
- Kỹ năng giao tiếp tốt và khả năng làm việc trong nhóm
- Kiên nhẫn và kiên trì trong việc tìm kiếm và xác định lỗi
- Hiểu biết cơ bản về HTML, CSS và JavaScript là một lợi thế
- Kiến thức về các công cụ quản lý lỗi (JIRA, TestRail) là một lợi thế
- Hiểu biết về SQL và cơ sở dữ liệu cơ bản là một lợi thế
- Sẵn sàng học hỏi và phát triển kỹ năng kiểm thử tự động trong tương lai
- Khả năng thích ứng với các thay đổi và làm việc trong môi trường năng động
            """,
            'location': 'ha_noi',
            'min_salary': 7000000,
            'max_salary': 10000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=18),
            'status': 'active'
        },
        {
            'title': 'Thực tập sinh Thiết kế UI/UX',
            'description': """
Chúng tôi đang tìm kiếm một Thực tập sinh Thiết kế UI/UX đầy sáng tạo để tham gia vào đội ngũ thiết kế của chúng tôi. Đây là cơ hội tuyệt vời để học hỏi và phát triển kỹ năng thiết kế trong môi trường thực tế, làm việc với các dự án đa dạng và được hướng dẫn bởi các nhà thiết kế chuyên nghiệp.

Trách nhiệm:
- Hỗ trợ đội ngũ thiết kế trong việc tạo wireframes, mockups và prototypes đơn giản
- Tham gia vào quá trình nghiên cứu người dùng và phân tích đối thủ cạnh tranh
- Học hỏi và áp dụng các nguyên tắc thiết kế UI/UX trong các dự án thực tế
- Tìm hiểu về quy trình thiết kế từ ý tưởng đến sản phẩm cuối cùng
- Thực hành sử dụng các công cụ thiết kế như Figma, Sketch hoặc Adobe XD
- Hỗ trợ tạo các tài sản đồ họa và icon cho các ứng dụng và trang web
- Tham gia vào các buổi brainstorming và đánh giá thiết kế
- Học cách tạo ra các giao diện nhất quán và thân thiện với người dùng
- Hiểu và áp dụng các nguyên tắc thiết kế responsive
- Ghi chép và tài liệu hóa các quyết định thiết kế
            """,
            'requirements': """
- Sinh viên ngành Thiết kế đồ họa, Mỹ thuật công nghiệp, Tương tác người-máy hoặc các lĩnh vực liên quan
- Có kiến thức cơ bản về các nguyên tắc thiết kế UI/UX
- Khả năng sáng tạo và tư duy thẩm mỹ tốt
- Biết sử dụng các công cụ thiết kế như Figma, Sketch, Adobe XD hoặc các công cụ tương tự
- Hiểu biết cơ bản về HTML/CSS là một lợi thế
- Có portfolio đơn giản thể hiện kỹ năng thiết kế và sáng tạo
- Khả năng làm việc trong nhóm và tiếp thu phản hồi
- Chú ý đến chi tiết và có khả năng tổ chức công việc tốt
- Hiểu biết về nguyên tắc thiết kế responsive và mobile-first
- Đam mê học hỏi về trải nghiệm người dùng và giao diện người dùng
- Khả năng thích nghi với các thay đổi và yêu cầu dự án
- Tư duy hướng giải pháp và khả năng giải quyết vấn đề
- Hiểu biết về accessibility trong thiết kế là một lợi thế
            """,
            'location': 'ho_chi_minh',
            'min_salary': 4000000,
            'max_salary': 6000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=10),
            'status': 'active'
        },
        {
            'title': 'Fresher Back-end Developer (Python/Django)',
            'description': """
Chúng tôi đang tìm kiếm một Fresher Back-end Developer có kiến thức về Python và Django để tham gia vào đội ngũ phát triển của chúng tôi. Đây là cơ hội tuyệt vời để phát triển kỹ năng trong môi trường thực tế, làm việc với các dự án web đa dạng và học hỏi từ các kỹ sư giàu kinh nghiệm.

Trách nhiệm:
- Phát triển các thành phần phía server cho ứng dụng web sử dụng Python và Django
- Xây dựng RESTful APIs và các điểm cuối cho giao tiếp với front-end
- Thiết kế và quản lý cơ sở dữ liệu, viết các truy vấn tối ưu
- Triển khai business logic và các tính năng theo yêu cầu dự án
- Tích hợp với các dịch vụ bên thứ ba và APIs
- Tham gia vào quy trình kiểm thử và đảm bảo chất lượng code
- Hợp tác với đội ngũ front-end để tích hợp các thành phần UI
- Học hỏi các phương pháp phát triển Agile và quy trình DevOps
- Tham gia vào các buổi code review và chia sẻ kiến thức
- Tài liệu hóa các API và thành phần back-end
            """,
            'requirements': """
- Tốt nghiệp ngành Công nghệ Thông tin, Khoa học Máy tính hoặc các lĩnh vực liên quan
- Có kiến thức cơ bản về Python và các nguyên tắc lập trình hướng đối tượng
- Hiểu biết về Django hoặc Flask framework
- Kiến thức về RESTful API và các nguyên tắc thiết kế API
- Hiểu biết cơ bản về cơ sở dữ liệu quan hệ (SQL) và phi quan hệ (NoSQL)
- Kiến thức về Git và các hệ thống quản lý phiên bản
- Hiểu biết về HTTP, web server và các nguyên tắc bảo mật web
- Khả năng học hỏi nhanh và thích nghi với công nghệ mới
- Kỹ năng giải quyết vấn đề và tư duy logic tốt
- Kỹ năng giao tiếp và làm việc nhóm hiệu quả
- Hiểu biết về testing frameworks (unittest, pytest) là một lợi thế
- Kiến thức về Docker và container là một lợi thế
            """,
            'location': 'da_nang',
            'min_salary': 9000000,
            'max_salary': 14000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=20),
            'status': 'active'
        },
         {
            'title': 'Thực tập sinh Nhân sự',
            'description': """
Chúng tôi đang tìm kiếm một Thực tập sinh Nhân sự năng động để hỗ trợ các hoạt động hành chính nhân sự và tuyển dụng của công ty. Đây là cơ hội tuyệt vời để học hỏi và phát triển kỹ năng trong lĩnh vực quản trị nhân sự, làm việc trong môi trường chuyên nghiệp và năng động.

Trách nhiệm:
- Hỗ trợ đăng tin tuyển dụng trên các nền tảng việc làm và mạng xã hội
- Sàng lọc hồ sơ ứng viên và hỗ trợ sắp xếp lịch phỏng vấn
- Hỗ trợ chuẩn bị tài liệu và hồ sơ nhân viên
- Tham gia vào quá trình onboarding nhân viên mới
- Hỗ trợ tổ chức các sự kiện nội bộ và hoạt động team building
- Cập nhật và duy trì cơ sở dữ liệu nhân sự
- Hỗ trợ các công việc hành chính văn phòng khi cần thiết
- Tham gia vào các dự án nhân sự khác như đánh giá hiệu suất, khảo sát nhân viên
- Học hỏi về các quy định pháp luật và chính sách liên quan đến nhân sự
- Hỗ trợ đội ngũ nhân sự trong các nhiệm vụ hàng ngày
            """,
            'requirements': """
- Sinh viên năm cuối hoặc mới tốt nghiệp ngành Quản trị Nhân lực, Quản trị Kinh doanh hoặc các ngành liên quan
- Kỹ năng giao tiếp tốt, thân thiện và nhiệt tình
- Khả năng tổ chức và quản lý thời gian hiệu quả
- Thành thạo Microsoft Office (đặc biệt là Excel, Word, PowerPoint)
- Cẩn thận, tỉ mỉ và chú ý đến chi tiết
- Có trách nhiệm và đáng tin cậy trong công việc
- Khả năng làm việc độc lập và theo nhóm
- Năng động, sáng tạo và có khả năng thích ứng với môi trường làm việc nhanh
- Hiểu biết cơ bản về luật lao động là một lợi thế
- Kinh nghiệm sử dụng các phần mềm quản lý nhân sự là một lợi thế
- Khả năng giữ bí mật và xử lý thông tin nhạy cảm
- Tinh thần học hỏi và cầu tiến trong công việc
            """,
            'location': 'ha_noi',
            'min_salary': 3000000,
            'max_salary': 5000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=14),
            'status': 'active'
        },
        {
            'title': 'Fresher Business Analyst',
            'description': """
Chúng tôi đang tìm kiếm một Fresher Business Analyst có tư duy phân tích tốt để tham gia vào đội ngũ phân tích nghiệp vụ. Bạn sẽ được học hỏi và phát triển kỹ năng trong việc thu thập, phân tích yêu cầu nghiệp vụ từ khách hàng và các bộ phận nội bộ, chuyển đổi chúng thành các yêu cầu kỹ thuật rõ ràng cho đội ngũ phát triển.

Trách nhiệm:
- Học hỏi và hỗ trợ thu thập, phân tích yêu cầu nghiệp vụ từ khách hàng và các bộ phận liên quan
- Phối hợp với đội ngũ phát triển để chuyển đổi yêu cầu nghiệp vụ thành yêu cầu kỹ thuật
- Viết tài liệu đặc tả yêu cầu và tài liệu hướng dẫn người dùng
- Hỗ trợ tạo và duy trì các mô hình quy trình nghiệp vụ
- Tham gia vào các buổi họp với khách hàng để làm rõ yêu cầu
- Hỗ trợ kiểm thử để đảm bảo sản phẩm đáp ứng yêu cầu nghiệp vụ
- Tìm hiểu về lĩnh vực kinh doanh cụ thể để hiểu rõ nhu cầu của khách hàng
- Phân tích dữ liệu để đưa ra các đề xuất cải thiện quy trình
- Học hỏi về các công cụ và phương pháp phân tích nghiệp vụ
- Tham gia vào các dự án từ giai đoạn khởi tạo đến triển khai
            """,
            'requirements': """
- Tốt nghiệp ngành Hệ thống thông tin quản lý, Công nghệ thông tin, Kinh tế hoặc các ngành liên quan
- Tư duy phân tích logic và khả năng giải quyết vấn đề tốt
- Kỹ năng giao tiếp và trình bày rõ ràng, mạch lạc
- Khả năng lắng nghe và hiểu yêu cầu của khách hàng
- Tiếng Anh đọc hiểu tài liệu kỹ thuật tốt
- Kỹ năng viết tài liệu kỹ thuật rõ ràng và cấu trúc
- Hiểu biết cơ bản về quy trình phát triển phần mềm
- Kiến thức về SQL và cơ sở dữ liệu cơ bản là một lợi thế
- Hiểu biết về các công cụ mô hình hóa quy trình (BPMN, UML) là một lợi thế
- Khả năng làm việc độc lập và trong nhóm đa chức năng
- Chủ động, ham học hỏi và sẵn sàng tiếp thu kiến thức mới
- Kỹ năng quản lý thời gian và tổ chức công việc tốt
- Có khả năng chịu áp lực công việc và thích nghi với thay đổi
            """,
            'location': 'ho_chi_minh',
            'min_salary': 8000000,
            'max_salary': 13000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=22),
            'status': 'active'
        },
        {
            'title': 'Thực tập sinh Content Marketing',
            'description': """
Chúng tôi đang tìm kiếm một Thực tập sinh Content Marketing sáng tạo để hỗ trợ đội ngũ marketing trong việc tạo ra nội dung hấp dẫn cho các kênh truyền thông của công ty. Đây là cơ hội tuyệt vời để phát triển kỹ năng viết lách, sáng tạo nội dung và học hỏi về digital marketing trong môi trường chuyên nghiệp.

Trách nhiệm:
- Hỗ trợ viết bài cho blog, website, mạng xã hội theo chủ đề được giao
- Tham gia lên ý tưởng nội dung và chiến dịch marketing sáng tạo
- Nghiên cứu và tìm hiểu về các chủ đề liên quan đến ngành
- Học cách tối ưu hóa nội dung cho SEO (Search Engine Optimization)
- Hỗ trợ quản lý và tương tác trên các kênh mạng xã hội của công ty
- Tìm hiểu cách sử dụng các công cụ phân tích và theo dõi hiệu quả nội dung
- Hỗ trợ biên tập và đảm bảo chất lượng nội dung trước khi xuất bản
- Tham gia vào việc tạo các tài liệu marketing như infographics, email newsletter
- Học hỏi về các chiến lược content marketing và inbound marketing
- Hỗ trợ các nhiệm vụ marketing khác khi cần thiết
            """,
            'requirements': """
- Sinh viên các ngành Báo chí, Truyền thông, Marketing, Ngữ văn hoặc các ngành liên quan
- Khả năng viết lách tốt, sáng tạo và sử dụng tiếng Việt chuẩn xác
- Đam mê và hiểu biết về marketing số, mạng xã hội và xu hướng nội dung
- Có khả năng nghiên cứu và tổng hợp thông tin từ nhiều nguồn
- Kỹ năng sáng tạo và tư duy hình ảnh tốt
- Thành thạo các công cụ Microsoft Office (Word, Excel, PowerPoint)
            """,
            'location': 'ho_chi_minh',
            'min_salary': 4000000,
            'max_salary': 6000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=10),
            'status': 'active'
        },
        {
            'title': 'Fresher IT Support/Helpdesk',
            'description': """
Chúng tôi đang tìm kiếm một Fresher IT Support/Helpdesk tận tâm để hỗ trợ người dùng nội bộ về các vấn đề công nghệ thông tin. Đây là vị trí tuyệt vời để bắt đầu sự nghiệp trong lĩnh vực CNTT, với cơ hội học hỏi đa dạng về phần cứng, phần mềm, mạng và hỗ trợ người dùng trong môi trường doanh nghiệp.

Trách nhiệm:
- Hỗ trợ người dùng trong công ty về các vấn đề kỹ thuật thông qua điện thoại, email, chat và trực tiếp
- Xử lý và giải quyết các sự cố liên quan đến máy tính, mạng, phần mềm và các thiết bị ngoại vi
- Cài đặt, cấu hình và bảo trì hệ điều hành, phần mềm và các ứng dụng văn phòng
- Thiết lập và quản lý tài khoản người dùng, phân quyền truy cập
- Hỗ trợ kỹ thuật cho các cuộc họp trực tuyến và hội nghị
- Ghi nhận, phân loại và theo dõi các yêu cầu hỗ trợ trong hệ thống ticket
- Bảo trì thiết bị phần cứng và thực hiện các công việc bảo dưỡng định kỳ
- Tài liệu hóa các giải pháp khắc phục sự cố để sử dụng trong tương lai
- Hỗ trợ quản lý và cập nhật hệ thống bảo mật cơ bản
- Báo cáo các vấn đề phức tạp cho cấp quản lý IT cao hơn khi cần thiết
            """,
            'requirements': """
- Tốt nghiệp Cao đẳng/Đại học chuyên ngành Mạng máy tính, Công nghệ thông tin hoặc các lĩnh vực liên quan
- Kiến thức cơ bản về hệ điều hành Windows, macOS và Linux
- Hiểu biết về cấu trúc phần cứng máy tính, mạng LAN/WAN và Wi-Fi
- Kiến thức về các ứng dụng văn phòng phổ biến (Microsoft Office, Google Workspace)
- Kỹ năng giao tiếp tốt và khả năng giải thích vấn đề kỹ thuật bằng ngôn ngữ đơn giản
- Kiên nhẫn, thân thiện và hướng đến dịch vụ khách hàng
- Khả năng làm việc độc lập và giải quyết vấn đề
- Kỹ năng quản lý thời gian và xử lý nhiều yêu cầu cùng lúc
- Kiến thức cơ bản về bảo mật thông tin và các phương pháp bảo vệ dữ liệu
- Hiểu biết về các hệ thống helpdesk và quản lý ticket là một lợi thế
- Có chứng chỉ CNTT cơ bản (A+, Network+, MCSA) là một lợi thế
- Khả năng làm việc theo ca (nếu cần) và sẵn sàng hỗ trợ ngoài giờ trong trường hợp khẩn cấp
- Tinh thần học hỏi liên tục để cập nhật kiến thức về công nghệ mới
            """,
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
            'description': """
Chúng tôi đang tìm kiếm một nhà khoa học nghiên cứu AI xuất sắc để thực hiện các nghiên cứu tiên tiến trong lĩnh vực học máy, học sâu và trí tuệ nhân tạo. Bạn sẽ là một phần quan trọng trong đội ngũ nghiên cứu, phát triển các mô hình AI tiên tiến và đột phá.

Trách nhiệm:
- Nghiên cứu và phát triển các thuật toán học máy và học sâu tiên tiến
- Thiết kế và thực hiện các thí nghiệm để kiểm chứng giả thuyết và cải thiện các mô hình hiện có
- Xuất bản các phát hiện tại các hội nghị và tạp chí AI hàng đầu
- Cộng tác với các nhà nghiên cứu khác và đội ngũ kỹ thuật để ứng dụng các phát hiện vào sản phẩm
- Theo dõi và đánh giá các xu hướng và tiến bộ mới nhất trong lĩnh vực AI
- Đề xuất và phát triển các giải pháp AI sáng tạo cho các vấn đề kinh doanh phức tạp
            """,
            'requirements': """
- Tiến sĩ hoặc Thạc sĩ trong lĩnh vực Khoa học Máy tính, Trí tuệ nhân tạo, hoặc lĩnh vực liên quan
- Có thành tích xuất bản tại các hội nghị/tạp chí AI uy tín (như NeurIPS, ICML, ICLR, CVPR, AAAI)
- Thành thạo Python và các framework học máy (TensorFlow, PyTorch)
- Kinh nghiệm sâu về xử lý dữ liệu lớn và tối ưu hóa các mô hình học máy
- Hiểu biết vững chắc về các kỹ thuật học máy cổ điển và hiện đại
- Khả năng nghiên cứu độc lập và làm việc trong môi trường đổi mới
- Kỹ năng giao tiếp và truyền đạt ý tưởng phức tạp một cách rõ ràng
- Khả năng đọc và viết tiếng Anh khoa học tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 50000000,
            'max_salary': 80000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=40),
            'status': 'active'
        },
        {
            'title': 'Full-stack Web Developer (Remote)',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Web Full-stack có kỹ năng toàn diện để xây dựng và duy trì các ứng dụng web hiện đại, làm việc từ xa. Bạn sẽ tham gia vào toàn bộ chu trình phát triển, từ concept đến triển khai sản phẩm hoàn chỉnh.

Trách nhiệm:
- Phát triển ứng dụng web đáp ứng, tương thích đa nền tảng sử dụng các công nghệ front-end và back-end hiện đại
- Thiết kế và triển khai các API RESTful và cơ sở dữ liệu hiệu quả
- Tối ưu hóa ứng dụng cho tốc độ và khả năng mở rộng
- Cộng tác với đội ngũ phát triển từ xa thông qua các công cụ quản lý dự án và mã nguồn
- Xác định và giải quyết các vấn đề kỹ thuật, hiệu suất và khả năng mở rộng
- Cập nhật và cải thiện mã nguồn hiện có, đảm bảo tuân thủ các tiêu chuẩn phát triển tốt nhất
- Tham gia vào quy trình đánh giá mã nguồn và cung cấp phản hồi xây dựng
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm với các framework front-end hiện đại (React, Angular hoặc Vue.js)
- Tối thiểu 3 năm kinh nghiệm với các framework back-end (Node.js, Django, Ruby on Rails...)
- Thành thạo JavaScript/TypeScript, HTML5 và CSS3
- Kinh nghiệm sâu về cơ sở dữ liệu SQL (MySQL, PostgreSQL) và NoSQL (MongoDB, Redis)
- Hiểu biết về các nền tảng điện toán đám mây (AWS, Azure, GCP) và các dịch vụ của chúng
- Kinh nghiệm với các công cụ quản lý mã nguồn (Git) và quy trình CI/CD
- Khả năng thiết kế cơ sở dữ liệu và tối ưu hóa truy vấn
- Kỹ năng giải quyết vấn đề và tư duy phân tích tốt
- Kỹ năng giao tiếp xuất sắc và khả năng làm việc hiệu quả trong môi trường từ xa
- Tiếng Anh giao tiếp tốt, đặc biệt là đọc hiểu tài liệu kỹ thuật
            """,
            'location': 'remote',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'remote',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'Software Engineer (Mobile - iOS)',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phần mềm iOS giàu kinh nghiệm để thiết kế và phát triển các ứng dụng tiên tiến cho nền tảng iOS. Bạn sẽ là một phần của đội ngũ phát triển di động tài năng, làm việc trên các ứng dụng iOS sáng tạo và có tác động lớn.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các ứng dụng iOS chất lượng cao, hiệu suất tốt
- Cộng tác với các nhóm liên chức năng (thiết kế, back-end, QA) để định nghĩa, thiết kế và triển khai các tính năng mới
- Tối ưu hóa hiệu suất ứng dụng, đảm bảo mượt mà và đáp ứng tốt trên nhiều thiết bị iOS
- Thực hiện kiểm thử đơn vị và sửa lỗi để đảm bảo chất lượng mã nguồn
- Nghiên cứu và ứng dụng các công nghệ và thư viện mới để cải thiện quá trình phát triển
- Đánh giá và cải thiện các ứng dụng hiện tại, áp dụng các phương pháp tốt nhất trong phát triển iOS
- Tham gia xây dựng kiến trúc ứng dụng và đưa ra các quyết định kỹ thuật
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển ứng dụng iOS sử dụng Swift hoặc Objective-C
- Hiểu biết sâu về nền tảng iOS và các nguyên tắc thiết kế giao diện người dùng của Apple
- Kinh nghiệm làm việc với các framework iOS như Core Data, Core Animation, Core Graphics, AutoLayout
- Thành thạo trong việc tích hợp RESTful API và các dịch vụ web vào ứng dụng iOS
- Kinh nghiệm với các công cụ quản lý phụ thuộc như CocoaPods, Carthage hoặc Swift Package Manager
- Kiến thức về các mẫu thiết kế phổ biến (MVC, MVVM, Viper) và lập trình hướng đối tượng
- Kinh nghiệm với Xcode, Interface Builder và các công cụ debug iOS
- Hiểu biết về quy trình phát hành ứng dụng lên App Store
- Tư duy phân tích và khả năng giải quyết vấn đề phức tạp
- Khả năng làm việc độc lập và trong môi trường nhóm
            """,
            'location': 'ha_noi',
            'min_salary': 28000000,
            'max_salary': 45000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=35),
            'status': 'active'
        },
        {
            'title': 'Machine Learning Engineer',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Học máy tài năng để thiết kế, xây dựng và triển khai các mô hình học máy nhằm giải quyết các vấn đề thực tế phức tạp. Bạn sẽ làm việc với dữ liệu lớn và hệ thống sản xuất để chuyển đổi thuật toán thành các giải pháp có giá trị.

Trách nhiệm:
- Thiết kế và phát triển các mô hình học máy và thuật toán advanced analytics
- Xử lý và phân tích dữ liệu lớn, thực hiện feature engineering và selection
- Triển khai các mô hình học máy vào môi trường sản xuất, đảm bảo khả năng mở rộng và hiệu suất
- Phối hợp với các kỹ sư dữ liệu và nhà phát triển phần mềm để tích hợp các giải pháp ML
- Tối ưu hóa các mô hình hiện có để cải thiện độ chính xác và hiệu suất
- Theo dõi, đánh giá và cải thiện các mô hình đã triển khai
- Nghiên cứu và áp dụng các kỹ thuật học máy mới nhất
            """,
            'requirements': """
- Thạc sĩ hoặc Cử nhân về Khoa học Máy tính, Thống kê, Toán học hoặc lĩnh vực liên quan
- Tối thiểu 2 năm kinh nghiệm phát triển và triển khai các mô hình học máy
- Thành thạo Python và các thư viện ML/DL như scikit-learn, TensorFlow, PyTorch, Keras
- Kinh nghiệm với xử lý dữ liệu lớn và các công cụ như Spark, Hadoop
- Hiểu biết vững chắc về các thuật toán học máy, thống kê và toán học
- Kinh nghiệm với các phương pháp phân loại, hồi quy, clustering và các kỹ thuật giảm chiều dữ liệu
- Kỹ năng gỡ lỗi, tối ưu hóa hiệu suất, và đánh giá mô hình ML
- Khả năng giao tiếp hiệu quả và làm việc trong môi trường nhóm đa lĩnh vực
- Kinh nghiệm với triển khai MLOps và CI/CD cho hệ thống ML là một lợi thế
- Hiểu biết về domain cụ thể (tài chính, y tế, bán lẻ...) là một lợi thế
            """,
            'location': 'da_nang',
            'min_salary': 35000000,
            'max_salary': 60000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'React Native Developer',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển React Native có kinh nghiệm để xây dựng ứng dụng di động đa nền tảng chất lượng cao. Bạn sẽ tập trung vào việc tạo ra trải nghiệm di động thân thiện với người dùng, hiệu suất cao và hoạt động trên cả iOS và Android.

Trách nhiệm:
- Phát triển ứng dụng di động đa nền tảng sử dụng React Native và JavaScript/TypeScript
- Tạo giao diện người dùng hấp dẫn, mượt mà và đáp ứng theo thiết kế
- Kết nối ứng dụng với các API và dịch vụ back-end
- Tối ưu hóa hiệu suất ứng dụng trên nhiều loại thiết bị
- Xử lý và cải thiện trải nghiệm offline cho người dùng
- Thực hiện kiểm thử đơn vị và phát hiện lỗi
- Cộng tác với nhóm thiết kế và back-end để cung cấp giải pháp di động toàn diện
- Duy trì, cập nhật và nâng cấp ứng dụng khi cần thiết
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển với React Native
- Hiểu biết sâu về JavaScript, ES6+ và TypeScript
- Kinh nghiệm với các công cụ build native như XCode, Android Studio
- Thành thạo việc sử dụng Redux/Context API để quản lý state
- Kinh nghiệm tích hợp với RESTful API và GraphQL
- Hiểu biết về các nguyên tắc thiết kế UI/UX trên di động
- Kinh nghiệm triển khai ứng dụng lên App Store và Google Play
- Kinh nghiệm với các thư viện React Native phổ biến (React Navigation, Async Storage...)
- Hiểu biết về các API native của thiết bị (camera, GPS, thông báo đẩy...)
- Kỹ năng gỡ lỗi và khắc phục sự cố trên nhiều thiết bị
- Khả năng tối ưu hóa hiệu suất ứng dụng di động
- Tinh thần đồng đội và kỹ năng giao tiếp tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 25000000,
            'max_salary': 40000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=28),
            'status': 'active'
        },
        {
            'title': 'Back-end Developer (Java/Spring)',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Back-end giàu kinh nghiệm chuyên về Java và Spring Framework để xây dựng các ứng dụng server-side mạnh mẽ và có khả năng mở rộng. Bạn sẽ thiết kế và triển khai các API và microservices, đồng thời làm việc với cơ sở dữ liệu và hạ tầng cloud.

Trách nhiệm:
- Thiết kế và phát triển các ứng dụng back-end sử dụng Java và Spring Framework
- Xây dựng RESTful APIs và microservices có khả năng mở rộng cao
- Quản lý dữ liệu và tối ưu hóa cơ sở dữ liệu
- Tích hợp với các dịch vụ của bên thứ ba và APIs
- Đảm bảo hiệu suất, bảo mật và chất lượng mã nguồn
- Phối hợp với nhóm front-end để tích hợp các thành phần UI/UX
- Triển khai và duy trì các pipeline CI/CD
- Thực hiện code review và mentoring cho các thành viên junior
- Phân tích và giải quyết các vấn đề kỹ thuật phức tạp
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển với Java và Spring Boot/Spring Framework
- Kinh nghiệm sâu rộng với RESTful APIs và kiến trúc microservices
- Thành thạo với JPA/Hibernate, Spring Data, Spring Security
- Kinh nghiệm làm việc với các hệ cơ sở dữ liệu SQL (MySQL, PostgreSQL) và NoSQL (MongoDB)
- Hiểu biết về các công cụ build (Maven, Gradle) và quản lý mã nguồn (Git)
- Kinh nghiệm với Docker, Kubernetes và các nền tảng cloud (AWS, Azure, GCP)
- Kiến thức về các mẫu thiết kế và nguyên tắc SOLID
- Kinh nghiệm với testing frameworks (JUnit, Mockito)
- Hiểu biết về các công cụ monitoring và logging (ELK Stack, Prometheus)
- Kỹ năng giải quyết vấn đề và tư duy phân tích tốt
- Khả năng giao tiếp hiệu quả và làm việc trong môi trường nhóm Agile
- Tiếng Anh đọc hiểu tài liệu kỹ thuật tốt
            """,
            'location': 'ha_noi',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=32),
            'status': 'active'
        },
        {
            'title': 'Data Scientist - NLP Specialist',
            'description': """
Chúng tôi đang tìm kiếm một Chuyên gia Xử lý Ngôn ngữ Tự nhiên (NLP) tài năng để ứng dụng các kỹ thuật NLP tiên tiến vào việc phân tích và khai thác thông tin từ dữ liệu văn bản. Bạn sẽ phát triển các mô hình cho phân loại văn bản, phân tích cảm xúc, trích xuất thực thể và nhiều ứng dụng NLP khác.

Trách nhiệm:
- Phát triển và triển khai các mô hình NLP để giải quyết các vấn đề kinh doanh phức tạp
- Xử lý và chuẩn bị dữ liệu văn bản lớn cho mục đích huấn luyện mô hình
- Nghiên cứu và ứng dụng các phương pháp NLP tiên tiến (word embeddings, transformer models, attention mechanisms)
- Xây dựng các hệ thống phân loại văn bản, phân tích cảm xúc, trích xuất thông tin và chatbot thông minh
- Tối ưu hóa mô hình NLP để đạt hiệu suất và độ chính xác cao
- Phối hợp với đội ngũ kỹ thuật để tích hợp các giải pháp NLP vào sản phẩm
- Đánh giá và so sánh hiệu suất của các mô hình khác nhau
- Cập nhật kiến thức về các tiến bộ mới nhất trong lĩnh vực NLP
            """,
            'requirements': """
- Thạc sĩ hoặc Tiến sĩ trong lĩnh vực Khoa học Máy tính, Xử lý Ngôn ngữ Tự nhiên, hoặc lĩnh vực định lượng liên quan
- Tối thiểu 3 năm kinh nghiệm với các dự án NLP thực tế
- Kinh nghiệm sâu với các thư viện NLP như NLTK, SpaCy, Hugging Face Transformers
- Thành thạo Python và các framework học máy phổ biến (TensorFlow, PyTorch)
- Kinh nghiệm làm việc với các mô hình ngôn ngữ lớn (BERT, GPT, T5)
- Hiểu biết vững chắc về các kỹ thuật xử lý văn bản (tokenization, stemming, lemmatization)
- Kinh nghiệm với các kỹ thuật word embedding (Word2Vec, GloVe, FastText)
- Kiến thức về ngôn ngữ học tính toán và thống kê
- Kỹ năng xử lý dữ liệu lớn và tối ưu hóa hiệu suất mô hình
- Khả năng nghiên cứu và triển khai các bài báo khoa học về NLP
- Kỹ năng giao tiếp tốt để trình bày các kết quả phức tạp một cách rõ ràng
- Tiếng Anh đọc hiểu tài liệu kỹ thuật tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 40000000,
            'max_salary': 70000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=38),
            'status': 'active'
        },
        {
            'title': 'Frontend Developer - Vue.js',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Frontend chuyên về Vue.js để xây dựng giao diện người dùng tương tác và đáp ứng cho các ứng dụng web của chúng tôi. Bạn sẽ hợp tác chặt chẽ với các nhà thiết kế UI/UX và các nhà phát triển backend để tạo ra trải nghiệm người dùng tuyệt vời.

Trách nhiệm:
- Phát triển các giao diện người dùng hiện đại, tương tác và đáp ứng sử dụng Vue.js
- Chuyển đổi các mẫu thiết kế UI/UX thành mã frontend chất lượng cao
- Triển khai quản lý state hiệu quả với Vuex
- Tạo các component Vue có thể tái sử dụng và dễ bảo trì
- Tối ưu hóa ứng dụng cho hiệu suất và tốc độ tải trang tốt nhất
- Phối hợp với backend developers để tích hợp APIs và dịch vụ
- Thực hiện kiểm thử và đảm bảo tương thích trên nhiều trình duyệt
- Tham gia vào quá trình đánh giá mã nguồn và cải thiện code base
- Theo dõi và cập nhật các xu hướng mới trong phát triển frontend
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển với Vue.js và hệ sinh thái của nó (Vuex, Vue Router)
- Thành thạo HTML5, CSS3 (SCSS/LESS) và JavaScript/TypeScript
- Kinh nghiệm với các thư viện UI của Vue (Vuetify, Element UI, Quasar)
- Hiểu biết sâu về quản lý state và lifecycle của Vue components
- Kinh nghiệm với RESTful APIs và tương tác dữ liệu bất đồng bộ
- Kiến thức tốt về Webpack, npm/yarn và các công cụ build frontend hiện đại
- Hiểu biết về responsive design và cross-browser compatibility
- Kinh nghiệm với công cụ kiểm thử frontend (Jest, Vue Test Utils)
- Khả năng tối ưu hóa hiệu suất ứng dụng web
- Kỹ năng giải quyết vấn đề và tư duy phân tích tốt
- Kinh nghiệm với version control systems (Git)
- Khả năng làm việc trong môi trường Agile/Scrum
- Đam mê học hỏi công nghệ mới và chia sẻ kiến thức
            """,
            'location': 'da_nang',
            'min_salary': 22000000,
            'max_salary': 38000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=25),
            'status': 'active'
        },
        {
            'title': 'Software Development Engineer in Test (SDET)',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phát triển Phần mềm trong lĩnh vực Kiểm thử (SDET) tài năng để thiết kế và triển khai các framework kiểm thử tự động và các bộ kiểm thử. Bạn sẽ đóng vai trò quan trọng trong việc đảm bảo chất lượng phần mềm thông qua tích hợp liên tục và quy trình giao hàng.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các framework kiểm thử tự động mạnh mẽ
- Tạo và thực thi các kịch bản kiểm thử tự động cho front-end, back-end và API
- Triển khai các kiểm thử tích hợp, hệ thống và hiệu suất
- Phối hợp với các nhà phát triển để cải thiện khả năng kiểm thử của mã nguồn
- Thiết lập và quản lý môi trường CI/CD cho việc chạy kiểm thử tự động
- Xác định và báo cáo các lỗi, theo dõi quá trình sửa lỗi
- Tham gia vào quy trình đánh giá mã nguồn và cung cấp góc nhìn về khả năng kiểm thử
- Phân tích kết quả kiểm thử và đề xuất cải tiến
- Làm việc trong môi trường Agile, hỗ trợ các sprint và các hoạt động release
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm trong lĩnh vực phát triển phần mềm và kiểm thử tự động
- Kỹ năng lập trình vững chắc với một hoặc nhiều ngôn ngữ (Python, Java, C#)
- Kinh nghiệm với các công cụ kiểm thử tự động: Selenium, Appium, Cypress, JUnit, TestNG
- Hiểu biết về các framework kiểm thử API (Postman, RestAssured, Karate)
- Kinh nghiệm với các công cụ CI/CD như Jenkins, GitLab CI, CircleCI
- Kiến thức về các phương pháp kiểm thử và các design pattern
- Hiểu biết về các công cụ quản lý kiểm thử (TestRail, JIRA)
- Kinh nghiệm với kiểm thử hiệu suất (JMeter, Gatling, Locust)
- Khả năng phân tích mã nguồn để xác định tiềm ẩn lỗi và cải thiện khả năng kiểm thử
- Kinh nghiệm với Docker và Kubernetes là một lợi thế
- Kỹ năng giao tiếp tốt và khả năng làm việc trong môi trường nhóm đa chức năng
- Tư duy phân tích và khả năng giải quyết vấn đề tốt
- Hiểu biết về phương pháp Agile/Scrum
            """,
            'location': 'ha_noi',
            'min_salary': 28000000,
            'max_salary': 48000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=29),
            'status': 'active'
        },
        {
            'title': 'AI Ethics Researcher',
            'description': """
Chúng tôi đang tìm kiếm một Nhà nghiên cứu Đạo đức AI để điều tra các ảnh hưởng đạo đức của công nghệ AI. Bạn sẽ phát triển các hướng dẫn và khung làm việc cho việc phát triển và triển khai AI có trách nhiệm, đảm bảo các giải pháp AI của chúng tôi tuân thủ các tiêu chuẩn đạo đức cao nhất.

Trách nhiệm:
- Nghiên cứu và phân tích các tác động đạo đức và xã hội của công nghệ AI
- Phát triển các hướng dẫn, chính sách và khung làm việc cho AI có trách nhiệm
- Đánh giá các sản phẩm và giải pháp AI hiện có về các vấn đề đạo đức
- Hợp tác với đội ngũ kỹ thuật để triển khai các biện pháp giảm thiểu định kiến và tăng tính công bằng
- Tư vấn cho đội ngũ phát triển sản phẩm về các vấn đề đạo đức AI
- Theo dõi và cập nhật xu hướng mới nhất trong lĩnh vực đạo đức AI và quản trị
- Tham gia vào các hội nghị và diễn đàn về đạo đức AI
- Phát triển và tổ chức đào tạo về đạo đức AI cho các nhóm nội bộ
- Đại diện cho công ty trong các diễn đàn công nghiệp và học thuật về đạo đức AI
            """,
            'requirements': """
- Bằng cao học hoặc tiến sĩ trong lĩnh vực Đạo đức, Luật, Triết học, Khoa học Máy tính hoặc lĩnh vực liên quan với trọng tâm về đạo đức AI
- Kinh nghiệm nghiên cứu về các khía cạnh đạo đức, xã hội và pháp lý của AI
- Hiểu biết sâu sắc về các vấn đề đạo đức AI như công bằng, trách nhiệm giải trình, minh bạch và quyền riêng tư
- Kiến thức vững chắc về các kỹ thuật AI/ML và những thách thức đạo đức cụ thể của chúng
- Khả năng phân tích và đánh giá tác động đạo đức của các hệ thống AI
- Kỹ năng giao tiếp xuất sắc, có khả năng trình bày các vấn đề phức tạp cho nhiều đối tượng khác nhau
- Khả năng làm việc hiệu quả với các nhóm kỹ thuật và phi kỹ thuật
- Cập nhật về các quy định và tiêu chuẩn mới nổi liên quan đến AI
- Kinh nghiệm xuất bản hoặc trình bày về các chủ đề đạo đức AI là một lợi thế
- Tư duy phản biện và khả năng đánh giá nhiều khía cạnh của các vấn đề phức tạp
- Tiếng Anh thành thạo để đọc nghiên cứu và tham gia vào các diễn đàn quốc tế
            """,
            'location': 'remote',
            'min_salary': 35000000,
            'max_salary': 60000000,
            'job_type': 'remote',
            'application_deadline': timezone.now() + timedelta(days=45),
            'status': 'active'
        },
        {
            'title': 'Junior Web Developer (Internship)',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Web junior đầy nhiệt huyết để tham gia chương trình thực tập. Bạn sẽ hỗ trợ các nhà phát triển senior trong việc xây dựng và kiểm thử các ứng dụng web, đồng thời học hỏi và áp dụng các nguyên tắc phát triển web trong môi trường thực tế.

Trách nhiệm:
- Hỗ trợ phát triển các tính năng front-end và back-end dưới sự hướng dẫn của các nhà phát triển senior
- Tham gia vào việc cải thiện và duy trì các ứng dụng web hiện có
- Học hỏi và áp dụng các công nghệ web hiện đại (HTML5, CSS3, JavaScript, các framework)
- Tham gia vào quy trình kiểm thử và đảm bảo chất lượng
- Tối ưu hóa các trang web để tăng tốc độ và khả năng mở rộng
- Hợp tác với đội ngũ thiết kế để triển khai các giao diện người dùng
- Nghiên cứu và đề xuất các giải pháp kỹ thuật
- Tham gia các cuộc họp nhóm và học hỏi từ các nhà phát triển có kinh nghiệm
- Thực hiện các nhiệm vụ khác khi được giao
            """,
            'requirements': """
- Đang theo học hoặc mới tốt nghiệp ngành Khoa học Máy tính, Công nghệ Thông tin hoặc lĩnh vực liên quan
- Kiến thức cơ bản về HTML, CSS và JavaScript
- Hiểu biết cơ bản về các nguyên tắc thiết kế web và trải nghiệm người dùng
- Khả năng học hỏi nhanh và tiếp thu các công nghệ mới
- Kỹ năng giải quyết vấn đề và tư duy logic tốt
- Hiểu biết cơ bản về các framework front-end (React, Angular, Vue) là một lợi thế
- Kiến thức cơ bản về các ngôn ngữ back-end (PHP, Python, Node.js) là một lợi thế
- Kiến thức về hệ quản trị cơ sở dữ liệu là một lợi thế
- Tinh thần làm việc nhóm tốt và khả năng giao tiếp hiệu quả
- Có portfolio hoặc dự án cá nhân để thể hiện kỹ năng là một lợi thế
- Đam mê học hỏi và sẵn sàng tiếp nhận phản hồi để cải thiện
            """,
            'location': 'ho_chi_minh',
            'min_salary': 5000000,
            'max_salary': 8000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=15),
            'status': 'active'
        },
        {
            'title': 'Software Engineer (Android)',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phần mềm Android tài năng để phát triển các ứng dụng di động Android chất lượng cao. Bạn sẽ làm việc với các SDK và công cụ Android mới nhất để tạo ra những trải nghiệm di động hấp dẫn và tiên tiến.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các ứng dụng Android chất lượng cao
- Cộng tác với đội thiết kế để xây dựng giao diện người dùng hấp dẫn và trực quan
- Đảm bảo hiệu suất tốt, khả năng đáp ứng cao và tối ưu hóa việc sử dụng pin
- Xác định và khắc phục các lỗi và vấn đề hiệu suất trong ứng dụng
- Làm việc với API và dịch vụ web để tích hợp với back-end
- Viết mã nguồn có thể kiểm thử, bảo trì và tái sử dụng
- Tìm hiểu và đưa vào ứng dụng các tính năng mới của nền tảng Android
- Tối ưu hóa ứng dụng cho các thiết bị và phiên bản Android khác nhau
- Hợp tác với các phòng ban khác để phát triển các tính năng mới
- Tham gia vào quá trình review code và chia sẻ kiến thức
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển ứng dụng Android
- Thành thạo lập trình Java và/hoặc Kotlin
- Hiểu biết sâu về kiến trúc Android, các thành phần, lifecycle
- Kinh nghiệm với các thư viện và framework phổ biến (Retrofit, Glide, Dagger, RxJava)
- Kiến thức về các mẫu thiết kế phổ biến (MVVM, MVP, Clean Architecture)
- Kinh nghiệm làm việc với Room, LiveData, ViewModel và các thành phần Jetpack khác
- Hiểu biết về Material Design và các nguyên tắc thiết kế trải nghiệm người dùng trên Android
- Kinh nghiệm với các công cụ kiểm thử (JUnit, Espresso, Mockito)
- Quen thuộc với các công cụ quản lý phụ thuộc (Gradle)
- Kinh nghiệm với các công cụ phát hiện lỗi và phân tích hiệu suất
- Kiến thức về quy trình phát hành ứng dụng lên Google Play
- Khả năng tối ưu hóa mã cho hiệu suất và khả năng mở rộng
- Kỹ năng giao tiếp tốt và khả năng làm việc trong môi trường nhóm
            """,
            'location': 'da_nang',
            'min_salary': 26000000,
            'max_salary': 42000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=33),
            'status': 'active'
        },
        # --- Intern/Fresher Jobs End ---
        # +++ AI, Web, Software Jobs Start +++
        {
            'title': 'AI Research Scientist',
            'description': """
Chúng tôi đang tìm kiếm một nhà khoa học nghiên cứu AI xuất sắc để thực hiện các nghiên cứu tiên tiến trong lĩnh vực học máy, học sâu và trí tuệ nhân tạo. Bạn sẽ là một phần quan trọng trong đội ngũ nghiên cứu, phát triển các mô hình AI tiên tiến và đột phá.

Trách nhiệm:
- Nghiên cứu và phát triển các thuật toán học máy và học sâu tiên tiến
- Thiết kế và thực hiện các thí nghiệm để kiểm chứng giả thuyết và cải thiện các mô hình hiện có
- Xuất bản các phát hiện tại các hội nghị và tạp chí AI hàng đầu
- Cộng tác với các nhà nghiên cứu khác và đội ngũ kỹ thuật để ứng dụng các phát hiện vào sản phẩm
- Theo dõi và đánh giá các xu hướng và tiến bộ mới nhất trong lĩnh vực AI
- Đề xuất và phát triển các giải pháp AI sáng tạo cho các vấn đề kinh doanh phức tạp
            """,
            'requirements': """
- Tiến sĩ hoặc Thạc sĩ trong lĩnh vực Khoa học Máy tính, Trí tuệ nhân tạo, hoặc lĩnh vực liên quan
- Có thành tích xuất bản tại các hội nghị/tạp chí AI uy tín (như NeurIPS, ICML, ICLR, CVPR, AAAI)
- Thành thạo Python và các framework học máy (TensorFlow, PyTorch)
- Kinh nghiệm sâu về xử lý dữ liệu lớn và tối ưu hóa các mô hình học máy
- Hiểu biết vững chắc về các kỹ thuật học máy cổ điển và hiện đại
- Khả năng nghiên cứu độc lập và làm việc trong môi trường đổi mới
- Kỹ năng giao tiếp và truyền đạt ý tưởng phức tạp một cách rõ ràng
- Khả năng đọc và viết tiếng Anh khoa học tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 50000000,
            'max_salary': 80000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=40),
            'status': 'active'
        },
        {
            'title': 'Full-stack Web Developer (Remote)',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Web Full-stack có kỹ năng toàn diện để xây dựng và duy trì các ứng dụng web hiện đại, làm việc từ xa. Bạn sẽ tham gia vào toàn bộ chu trình phát triển, từ concept đến triển khai sản phẩm hoàn chỉnh.

Trách nhiệm:
- Phát triển ứng dụng web đáp ứng, tương thích đa nền tảng sử dụng các công nghệ front-end và back-end hiện đại
- Thiết kế và triển khai các API RESTful và cơ sở dữ liệu hiệu quả
- Tối ưu hóa ứng dụng cho tốc độ và khả năng mở rộng
- Cộng tác với đội ngũ phát triển từ xa thông qua các công cụ quản lý dự án và mã nguồn
- Xác định và giải quyết các vấn đề kỹ thuật, hiệu suất và khả năng mở rộng
- Cập nhật và cải thiện mã nguồn hiện có, đảm bảo tuân thủ các tiêu chuẩn phát triển tốt nhất
- Tham gia vào quy trình đánh giá mã nguồn và cung cấp phản hồi xây dựng
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm với các framework front-end hiện đại (React, Angular hoặc Vue.js)
- Tối thiểu 3 năm kinh nghiệm với các framework back-end (Node.js, Django, Ruby on Rails...)
- Thành thạo JavaScript/TypeScript, HTML5 và CSS3
- Kinh nghiệm sâu về cơ sở dữ liệu SQL (MySQL, PostgreSQL) và NoSQL (MongoDB, Redis)
- Hiểu biết về các nền tảng điện toán đám mây (AWS, Azure, GCP) và các dịch vụ của chúng
- Kinh nghiệm với các công cụ quản lý mã nguồn (Git) và quy trình CI/CD
- Khả năng thiết kế cơ sở dữ liệu và tối ưu hóa truy vấn
- Kỹ năng giải quyết vấn đề và tư duy phân tích tốt
- Kỹ năng giao tiếp xuất sắc và khả năng làm việc hiệu quả trong môi trường từ xa
- Tiếng Anh giao tiếp tốt, đặc biệt là đọc hiểu tài liệu kỹ thuật
            """,
            'location': 'remote',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'remote',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'Software Engineer (Mobile - iOS)',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phần mềm iOS giàu kinh nghiệm để thiết kế và phát triển các ứng dụng tiên tiến cho nền tảng iOS. Bạn sẽ là một phần của đội ngũ phát triển di động tài năng, làm việc trên các ứng dụng iOS sáng tạo và có tác động lớn.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các ứng dụng iOS chất lượng cao, hiệu suất tốt
- Cộng tác với các nhóm liên chức năng (thiết kế, back-end, QA) để định nghĩa, thiết kế và triển khai các tính năng mới
- Tối ưu hóa hiệu suất ứng dụng, đảm bảo mượt mà và đáp ứng tốt trên nhiều thiết bị iOS
- Thực hiện kiểm thử đơn vị và sửa lỗi để đảm bảo chất lượng mã nguồn
- Nghiên cứu và ứng dụng các công nghệ và thư viện mới để cải thiện quá trình phát triển
- Đánh giá và cải thiện các ứng dụng hiện tại, áp dụng các phương pháp tốt nhất trong phát triển iOS
- Tham gia xây dựng kiến trúc ứng dụng và đưa ra các quyết định kỹ thuật
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển ứng dụng iOS sử dụng Swift hoặc Objective-C
- Hiểu biết sâu về nền tảng iOS và các nguyên tắc thiết kế giao diện người dùng của Apple
- Kinh nghiệm làm việc với các framework iOS như Core Data, Core Animation, Core Graphics, AutoLayout
- Thành thạo trong việc tích hợp RESTful API và các dịch vụ web vào ứng dụng iOS
- Kinh nghiệm với các công cụ quản lý phụ thuộc như CocoaPods, Carthage hoặc Swift Package Manager
- Kiến thức về các mẫu thiết kế phổ biến (MVC, MVVM, Viper) và lập trình hướng đối tượng
- Kinh nghiệm với Xcode, Interface Builder và các công cụ debug iOS
- Hiểu biết về quy trình phát hành ứng dụng lên App Store
- Tư duy phân tích và khả năng giải quyết vấn đề phức tạp
- Khả năng làm việc độc lập và trong môi trường nhóm
            """,
            'location': 'ha_noi',
            'min_salary': 28000000,
            'max_salary': 45000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=35),
            'status': 'active'
        },
        {
            'title': 'Machine Learning Engineer',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Học máy tài năng để thiết kế, xây dựng và triển khai các mô hình học máy nhằm giải quyết các vấn đề thực tế phức tạp. Bạn sẽ làm việc với dữ liệu lớn và hệ thống sản xuất để chuyển đổi thuật toán thành các giải pháp có giá trị.

Trách nhiệm:
- Thiết kế và phát triển các mô hình học máy và thuật toán advanced analytics
- Xử lý và phân tích dữ liệu lớn, thực hiện feature engineering và selection
- Triển khai các mô hình học máy vào môi trường sản xuất, đảm bảo khả năng mở rộng và hiệu suất
- Phối hợp với các kỹ sư dữ liệu và nhà phát triển phần mềm để tích hợp các giải pháp ML
- Tối ưu hóa các mô hình hiện có để cải thiện độ chính xác và hiệu suất
- Theo dõi, đánh giá và cải thiện các mô hình đã triển khai
- Nghiên cứu và áp dụng các kỹ thuật học máy mới nhất
            """,
            'requirements': """
- Thạc sĩ hoặc Cử nhân về Khoa học Máy tính, Thống kê, Toán học hoặc lĩnh vực liên quan
- Tối thiểu 2 năm kinh nghiệm phát triển và triển khai các mô hình học máy
- Thành thạo Python và các thư viện ML/DL như scikit-learn, TensorFlow, PyTorch, Keras
- Kinh nghiệm với xử lý dữ liệu lớn và các công cụ như Spark, Hadoop
- Hiểu biết vững chắc về các thuật toán học máy, thống kê và toán học
- Kinh nghiệm với các phương pháp phân loại, hồi quy, clustering và các kỹ thuật giảm chiều dữ liệu
- Kỹ năng gỡ lỗi, tối ưu hóa hiệu suất, và đánh giá mô hình ML
- Khả năng giao tiếp hiệu quả và làm việc trong môi trường nhóm đa lĩnh vực
- Kinh nghiệm với triển khai MLOps và CI/CD cho hệ thống ML là một lợi thế
- Hiểu biết về domain cụ thể (tài chính, y tế, bán lẻ...) là một lợi thế
            """,
            'location': 'da_nang',
            'min_salary': 35000000,
            'max_salary': 60000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'React Native Developer',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển React Native có kinh nghiệm để xây dựng ứng dụng di động đa nền tảng chất lượng cao. Bạn sẽ tập trung vào việc tạo ra trải nghiệm di động thân thiện với người dùng, hiệu suất cao và hoạt động trên cả iOS và Android.

Trách nhiệm:
- Phát triển ứng dụng di động đa nền tảng sử dụng React Native và JavaScript/TypeScript
- Tạo giao diện người dùng hấp dẫn, mượt mà và đáp ứng theo thiết kế
- Kết nối ứng dụng với các API và dịch vụ back-end
- Tối ưu hóa hiệu suất ứng dụng trên nhiều loại thiết bị
- Xử lý và cải thiện trải nghiệm offline cho người dùng
- Thực hiện kiểm thử đơn vị và phát hiện lỗi
- Cộng tác với nhóm thiết kế và back-end để cung cấp giải pháp di động toàn diện
- Duy trì, cập nhật và nâng cấp ứng dụng khi cần thiết
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển với React Native
- Hiểu biết sâu về JavaScript, ES6+ và TypeScript
- Kinh nghiệm với các công cụ build native như XCode, Android Studio
- Thành thạo việc sử dụng Redux/Context API để quản lý state
- Kinh nghiệm tích hợp với RESTful API và GraphQL
- Hiểu biết về các nguyên tắc thiết kế UI/UX trên di động
- Kinh nghiệm triển khai ứng dụng lên App Store và Google Play
- Kinh nghiệm với các thư viện React Native phổ biến (React Navigation, Async Storage...)
- Hiểu biết về các API native của thiết bị (camera, GPS, thông báo đẩy...)
- Kỹ năng gỡ lỗi và khắc phục sự cố trên nhiều thiết bị
- Khả năng tối ưu hóa hiệu suất ứng dụng di động
- Tinh thần đồng đội và kỹ năng giao tiếp tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 25000000,
            'max_salary': 40000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=28),
            'status': 'active'
        },
        {
            'title': 'Back-end Developer (Java/Spring)',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Back-end giàu kinh nghiệm chuyên về Java và Spring Framework để xây dựng các ứng dụng server-side mạnh mẽ và có khả năng mở rộng. Bạn sẽ thiết kế và triển khai các API và microservices, đồng thời làm việc với cơ sở dữ liệu và hạ tầng cloud.

Trách nhiệm:
- Thiết kế và phát triển các ứng dụng back-end sử dụng Java và Spring Framework
- Xây dựng RESTful APIs và microservices có khả năng mở rộng cao
- Quản lý dữ liệu và tối ưu hóa cơ sở dữ liệu
- Tích hợp với các dịch vụ của bên thứ ba và APIs
- Đảm bảo hiệu suất, bảo mật và chất lượng mã nguồn
- Phối hợp với nhóm front-end để tích hợp các thành phần UI/UX
- Triển khai và duy trì các pipeline CI/CD
- Thực hiện code review và mentoring cho các thành viên junior
- Phân tích và giải quyết các vấn đề kỹ thuật phức tạp
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển với Java và Spring Boot/Spring Framework
- Kinh nghiệm sâu rộng với RESTful APIs và kiến trúc microservices
- Thành thạo với JPA/Hibernate, Spring Data, Spring Security
- Kinh nghiệm làm việc với các hệ cơ sở dữ liệu SQL (MySQL, PostgreSQL) và NoSQL (MongoDB)
- Hiểu biết về các công cụ build (Maven, Gradle) và quản lý mã nguồn (Git)
- Kinh nghiệm với Docker, Kubernetes và các nền tảng cloud (AWS, Azure, GCP)
- Kiến thức về các mẫu thiết kế và nguyên tắc SOLID
- Kinh nghiệm với testing frameworks (JUnit, Mockito)
- Hiểu biết về các công cụ monitoring và logging (ELK Stack, Prometheus)
- Kỹ năng giải quyết vấn đề và tư duy phân tích tốt
- Khả năng giao tiếp hiệu quả và làm việc trong môi trường nhóm Agile
- Tiếng Anh đọc hiểu tài liệu kỹ thuật tốt
            """,
            'location': 'ha_noi',
            'min_salary': 30000000,
            'max_salary': 50000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=32),
            'status': 'active'
        },
        {
            'title': 'Data Scientist - NLP Specialist',
            'description': """
Chúng tôi đang tìm kiếm một Chuyên gia Xử lý Ngôn ngữ Tự nhiên (NLP) tài năng để ứng dụng các kỹ thuật NLP tiên tiến vào việc phân tích và khai thác thông tin từ dữ liệu văn bản. Bạn sẽ phát triển các mô hình cho phân loại văn bản, phân tích cảm xúc, trích xuất thực thể và nhiều ứng dụng NLP khác.

Trách nhiệm:
- Phát triển và triển khai các mô hình NLP để giải quyết các vấn đề kinh doanh phức tạp
- Xử lý và chuẩn bị dữ liệu văn bản lớn cho mục đích huấn luyện mô hình
- Nghiên cứu và ứng dụng các phương pháp NLP tiên tiến (word embeddings, transformer models, attention mechanisms)
- Xây dựng các hệ thống phân loại văn bản, phân tích cảm xúc, trích xuất thông tin và chatbot thông minh
- Tối ưu hóa mô hình NLP để đạt hiệu suất và độ chính xác cao
- Phối hợp với đội ngũ kỹ thuật để tích hợp các giải pháp NLP vào sản phẩm
- Đánh giá và so sánh hiệu suất của các mô hình khác nhau
- Cập nhật kiến thức về các tiến bộ mới nhất trong lĩnh vực NLP
            """,
            'requirements': """
- Thạc sĩ hoặc Tiến sĩ trong lĩnh vực Khoa học Máy tính, Xử lý Ngôn ngữ Tự nhiên, hoặc lĩnh vực định lượng liên quan
- Tối thiểu 3 năm kinh nghiệm với các dự án NLP thực tế
- Kinh nghiệm sâu với các thư viện NLP như NLTK, SpaCy, Hugging Face Transformers
- Thành thạo Python và các framework học máy phổ biến (TensorFlow, PyTorch)
- Kinh nghiệm làm việc với các mô hình ngôn ngữ lớn (BERT, GPT, T5)
- Hiểu biết vững chắc về các kỹ thuật xử lý văn bản (tokenization, stemming, lemmatization)
- Kinh nghiệm với các kỹ thuật word embedding (Word2Vec, GloVe, FastText)
- Kiến thức về ngôn ngữ học tính toán và thống kê
- Kỹ năng xử lý dữ liệu lớn và tối ưu hóa hiệu suất mô hình
- Khả năng nghiên cứu và triển khai các bài báo khoa học về NLP
- Kỹ năng giao tiếp tốt để trình bày các kết quả phức tạp một cách rõ ràng
- Tiếng Anh đọc hiểu tài liệu kỹ thuật tốt
            """,
            'location': 'ho_chi_minh',
            'min_salary': 40000000,
            'max_salary': 70000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=38),
            'status': 'active'
        },
        {
            'title': 'Frontend Developer - Vue.js',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Frontend chuyên về Vue.js để xây dựng giao diện người dùng tương tác và đáp ứng cho các ứng dụng web của chúng tôi. Bạn sẽ hợp tác chặt chẽ với các nhà thiết kế UI/UX và các nhà phát triển backend để tạo ra trải nghiệm người dùng tuyệt vời.

Trách nhiệm:
- Phát triển các giao diện người dùng hiện đại, tương tác và đáp ứng sử dụng Vue.js
- Chuyển đổi các mẫu thiết kế UI/UX thành mã frontend chất lượng cao
- Triển khai quản lý state hiệu quả với Vuex
- Tạo các component Vue có thể tái sử dụng và dễ bảo trì
- Tối ưu hóa ứng dụng cho hiệu suất và tốc độ tải trang tốt nhất
- Phối hợp với backend developers để tích hợp APIs và dịch vụ
- Thực hiện kiểm thử và đảm bảo tương thích trên nhiều trình duyệt
- Tham gia vào quá trình đánh giá mã nguồn và cải thiện code base
- Theo dõi và cập nhật các xu hướng mới trong phát triển frontend
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển với Vue.js và hệ sinh thái của nó (Vuex, Vue Router)
- Thành thạo HTML5, CSS3 (SCSS/LESS) và JavaScript/TypeScript
- Kinh nghiệm với các thư viện UI của Vue (Vuetify, Element UI, Quasar)
- Hiểu biết sâu về quản lý state và lifecycle của Vue components
- Kinh nghiệm với RESTful APIs và tương tác dữ liệu bất đồng bộ
- Kiến thức tốt về Webpack, npm/yarn và các công cụ build frontend hiện đại
- Hiểu biết về responsive design và cross-browser compatibility
- Kinh nghiệm với công cụ kiểm thử frontend (Jest, Vue Test Utils)
- Khả năng tối ưu hóa hiệu suất ứng dụng web
- Kỹ năng giải quyết vấn đề và tư duy phân tích tốt
- Kinh nghiệm với version control systems (Git)
- Khả năng làm việc trong môi trường Agile/Scrum
- Đam mê học hỏi công nghệ mới và chia sẻ kiến thức
            """,
            'location': 'da_nang',
            'min_salary': 22000000,
            'max_salary': 38000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=25),
            'status': 'active'
        },
        {
            'title': 'Software Development Engineer in Test (SDET)',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phát triển Phần mềm trong lĩnh vực Kiểm thử (SDET) tài năng để thiết kế và triển khai các framework kiểm thử tự động và các bộ kiểm thử. Bạn sẽ đóng vai trò quan trọng trong việc đảm bảo chất lượng phần mềm thông qua tích hợp liên tục và quy trình giao hàng.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các framework kiểm thử tự động mạnh mẽ
- Tạo và thực thi các kịch bản kiểm thử tự động cho front-end, back-end và API
- Triển khai các kiểm thử tích hợp, hệ thống và hiệu suất
- Phối hợp với các nhà phát triển để cải thiện khả năng kiểm thử của mã nguồn
- Thiết lập và quản lý môi trường CI/CD cho việc chạy kiểm thử tự động
- Xác định và báo cáo các lỗi, theo dõi quá trình sửa lỗi
- Tham gia vào quy trình đánh giá mã nguồn và cung cấp góc nhìn về khả năng kiểm thử
- Phân tích kết quả kiểm thử và đề xuất cải tiến
- Làm việc trong môi trường Agile, hỗ trợ các sprint và các hoạt động release
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm trong lĩnh vực phát triển phần mềm và kiểm thử tự động
- Kỹ năng lập trình vững chắc với một hoặc nhiều ngôn ngữ (Python, Java, C#)
- Kinh nghiệm với các công cụ kiểm thử tự động: Selenium, Appium, Cypress, JUnit, TestNG
- Hiểu biết về các framework kiểm thử API (Postman, RestAssured, Karate)
- Kinh nghiệm với các công cụ CI/CD như Jenkins, GitLab CI, CircleCI
- Kiến thức về các phương pháp kiểm thử và các design pattern
- Hiểu biết về các công cụ quản lý kiểm thử (TestRail, JIRA)
- Kinh nghiệm với kiểm thử hiệu suất (JMeter, Gatling, Locust)
- Khả năng phân tích mã nguồn để xác định tiềm ẩn lỗi và cải thiện khả năng kiểm thử
- Kinh nghiệm với Docker và Kubernetes là một lợi thế
- Kỹ năng giao tiếp tốt và khả năng làm việc trong môi trường nhóm đa chức năng
- Tư duy phân tích và khả năng giải quyết vấn đề tốt
- Hiểu biết về phương pháp Agile/Scrum
            """,
            'location': 'ha_noi',
            'min_salary': 28000000,
            'max_salary': 48000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=29),
            'status': 'active'
        },
        {
            'title': 'AI Ethics Researcher',
            'description': """
Chúng tôi đang tìm kiếm một Nhà nghiên cứu Đạo đức AI để điều tra các ảnh hưởng đạo đức của công nghệ AI. Bạn sẽ phát triển các hướng dẫn và khung làm việc cho việc phát triển và triển khai AI có trách nhiệm, đảm bảo các giải pháp AI của chúng tôi tuân thủ các tiêu chuẩn đạo đức cao nhất.

Trách nhiệm:
- Nghiên cứu và phân tích các tác động đạo đức và xã hội của công nghệ AI
- Phát triển các hướng dẫn, chính sách và khung làm việc cho AI có trách nhiệm
- Đánh giá các sản phẩm và giải pháp AI hiện có về các vấn đề đạo đức
- Hợp tác với đội ngũ kỹ thuật để triển khai các biện pháp giảm thiểu định kiến và tăng tính công bằng
- Tư vấn cho đội ngũ phát triển sản phẩm về các vấn đề đạo đức AI
- Theo dõi và cập nhật xu hướng mới nhất trong lĩnh vực đạo đức AI và quản trị
- Tham gia vào các hội nghị và diễn đàn về đạo đức AI
- Phát triển và tổ chức đào tạo về đạo đức AI cho các nhóm nội bộ
- Đại diện cho công ty trong các diễn đàn công nghiệp và học thuật về đạo đức AI
            """,
            'requirements': """
- Đang theo học hoặc mới tốt nghiệp ngành Khoa học Máy tính, Công nghệ Thông tin hoặc lĩnh vực liên quan
- Kiến thức cơ bản về HTML, CSS và JavaScript
- Hiểu biết cơ bản về các nguyên tắc thiết kế web và trải nghiệm người dùng
- Khả năng học hỏi nhanh và tiếp thu các công nghệ mới
- Kỹ năng giải quyết vấn đề và tư duy logic tốt
- Hiểu biết cơ bản về các framework front-end (React, Angular, Vue) là một lợi thế
- Kiến thức cơ bản về các ngôn ngữ back-end (PHP, Python, Node.js) là một lợi thế
- Kiến thức về hệ quản trị cơ sở dữ liệu là một lợi thế
- Tinh thần làm việc nhóm tốt và khả năng giao tiếp hiệu quả
- Có portfolio hoặc dự án cá nhân để thể hiện kỹ năng là một lợi thế
- Đam mê học hỏi và sẵn sàng tiếp nhận phản hồi để cải thiện
            """,
            'location': 'ho_chi_minh',
            'min_salary': 5000000,
            'max_salary': 8000000,
            'job_type': 'internship',
            'application_deadline': timezone.now() + timedelta(days=15),
            'status': 'active'
        },
        {
            'title': 'Software Engineer (Android)',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phần mềm Android tài năng để phát triển các ứng dụng di động Android chất lượng cao. Bạn sẽ làm việc với các SDK và công cụ Android mới nhất để tạo ra những trải nghiệm di động hấp dẫn và tiên tiến.

Trách nhiệm:
- Thiết kế, phát triển và duy trì các ứng dụng Android chất lượng cao
- Cộng tác với đội thiết kế để xây dựng giao diện người dùng hấp dẫn và trực quan
- Đảm bảo hiệu suất tốt, khả năng đáp ứng cao và tối ưu hóa việc sử dụng pin
- Xác định và khắc phục các lỗi và vấn đề hiệu suất trong ứng dụng
- Làm việc với API và dịch vụ web để tích hợp với back-end
- Viết mã nguồn có thể kiểm thử, bảo trì và tái sử dụng
- Tìm hiểu và đưa vào ứng dụng các tính năng mới của nền tảng Android
- Tối ưu hóa ứng dụng cho các thiết bị và phiên bản Android khác nhau
- Hợp tác với các phòng ban khác để phát triển các tính năng mới
- Tham gia vào quá trình review code và chia sẻ kiến thức
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển ứng dụng Android
- Thành thạo lập trình Java và/hoặc Kotlin
- Hiểu biết sâu về kiến trúc Android, các thành phần, lifecycle
- Kinh nghiệm với các thư viện và framework phổ biến (Retrofit, Glide, Dagger, RxJava)
- Kiến thức về các mẫu thiết kế phổ biến (MVVM, MVP, Clean Architecture)
- Kinh nghiệm làm việc với Room, LiveData, ViewModel và các thành phần Jetpack khác
- Hiểu biết về Material Design và các nguyên tắc thiết kế trải nghiệm người dùng trên Android
- Kinh nghiệm với các công cụ kiểm thử (JUnit, Espresso, Mockito)
- Quen thuộc với các công cụ quản lý phụ thuộc (Gradle)
- Kinh nghiệm với các công cụ phát hiện lỗi và phân tích hiệu suất
- Kiến thức về quy trình phát hành ứng dụng lên Google Play
- Khả năng tối ưu hóa mã cho hiệu suất và khả năng mở rộng
- Kỹ năng giao tiếp tốt và khả năng làm việc trong môi trường nhóm
            """,
            'location': 'da_nang',
            'min_salary': 26000000,
            'max_salary': 42000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=33),
            'status': 'active'
        },
        {
            'title': 'Computer Vision Engineer',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Thị giác Máy tính (Computer Vision) có kỹ năng cao để phát triển và triển khai các thuật toán thị giác máy tính tiên tiến cho các ứng dụng phân tích hình ảnh và video. Bạn sẽ làm việc với các dự án đa dạng liên quan đến nhận dạng đối tượng, phân tích hình ảnh và xử lý video.

Trách nhiệm:
- Nghiên cứu, thiết kế và triển khai các thuật toán thị giác máy tính tiên tiến
- Phát triển các giải pháp cho các vấn đề như nhận dạng đối tượng, theo dõi chuyển động, phân đoạn hình ảnh
- Chuyển đổi các bài báo nghiên cứu thành mã nguồn có thể triển khai trong môi trường sản xuất
- Tối ưu hóa hiệu suất các thuật toán trên nhiều nền tảng, bao gồm cả thiết bị di động và embedded
- Xây dựng các pipeline xử lý hình ảnh và video cho các ứng dụng thời gian thực
- Phối hợp với các kỹ sư phần mềm để tích hợp các mô hình thị giác máy tính vào sản phẩm
- Đánh giá và cải thiện hiệu suất của các mô hình thị giác máy tính
- Nghiên cứu và áp dụng các phương pháp mới từ các bài báo nghiên cứu và hội nghị
- Tư vấn cho các nhóm phát triển sản phẩm về khả năng và giới hạn của công nghệ thị giác máy tính
            """,
            'requirements': """
- Thạc sĩ hoặc Tiến sĩ trong lĩnh vực Khoa học Máy tính, Thị giác Máy tính hoặc các lĩnh vực liên quan
- Tối thiểu 3 năm kinh nghiệm làm việc với các dự án thị giác máy tính thực tế
- Thành thạo các thuật toán và kỹ thuật thị giác máy tính
- Kinh nghiệm sâu rộng với OpenCV và các framework học sâu như TensorFlow, PyTorch
- Kỹ năng lập trình mạnh mẽ với C++ và Python
- Kinh nghiệm với các mô hình học sâu cho thị giác máy tính (CNN, R-CNN, YOLO, SSD)
- Kiến thức về xử lý hình ảnh, trích xuất đặc trưng, và các phương pháp phân loại
- Hiểu biết về tối ưu hóa hiệu suất cho các ứng dụng thị giác máy tính
- Kinh nghiệm với các nền tảng xử lý hình ảnh và video (GPU, FPGA, các thiết bị edge)
- Khả năng hiểu và triển khai các bài báo nghiên cứu về thị giác máy tính
- Kỹ năng phân tích vấn đề và giải quyết vấn đề mạnh mẽ
- Kinh nghiệm làm việc trong môi trường phát triển nhóm Agile
- Có đóng góp vào các dự án mã nguồn mở hoặc các ấn phẩm trong lĩnh vực thị giác máy tính là một lợi thế
            """,
            'location': 'ha_noi',
            'min_salary': 40000000,
            'max_salary': 75000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=36),
            'status': 'active'
        },
        {
            'title': 'Angular Developer',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Angular giàu kinh nghiệm để xây dựng các ứng dụng web động và đáp ứng cao. Bạn sẽ phát triển các giao diện người dùng hiệu suất cao và đảm bảo khả năng mở rộng của các giải pháp front-end.

Trách nhiệm:
- Phát triển ứng dụng web phía client sử dụng Angular và TypeScript
- Xây dựng các thành phần (components) tùy chỉnh, có khả năng tái sử dụng cao
- Triển khai các giải pháp quản lý trạng thái (state management) hiệu quả
- Tối ưu hóa hiệu suất ứng dụng và thời gian tải trang
- Tích hợp với các RESTful API và dịch vụ web
- Đảm bảo khả năng tương thích trên nhiều trình duyệt và thiết bị
- Thực hiện testing (unit tests, e2e tests) để đảm bảo chất lượng mã
- Tham gia vào quá trình đánh giá mã nguồn và hướng dẫn các thành viên junior
- Cải tiến liên tục kiến trúc và quy trình phát triển của nhóm
- Phối hợp với đội ngũ UI/UX để triển khai các thiết kế thành các thành phần thực tế
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển với Angular (từ phiên bản 2+) và TypeScript
- Hiểu biết sâu sắc về HTML5, CSS3, JavaScript (ES6+)
- Kinh nghiệm với RxJS và quản lý state (NgRx, Akita, hoặc tương tự)
- Hiểu biết về Angular CLI, Angular Material và các thư viện Angular phổ biến khác
- Kinh nghiệm với các công cụ kiểm thử cho Angular (Jasmine, Karma, Protractor, Cypress)
- Kiến thức về responsive design và cross-browser compatibility
- Hiểu biết về các design patterns trong phát triển front-end
- Kinh nghiệm làm việc với hệ thống quản lý phiên bản (Git)
- Kiến thức về hiệu suất web và tối ưu hóa tải trang
- Tư duy tổ chức mã nguồn rõ ràng và có khả năng mở rộng
- Khả năng giải quyết vấn đề phức tạp và tư duy phân tích
- Kỹ năng giao tiếp tốt và khả năng làm việc trong môi trường nhóm
- Kiến thức về các công cụ build và deployment là một lợi thế
- Hiểu biết về security best practices trong phát triển front-end
            """,
            'location': 'ho_chi_minh',
            'min_salary': 27000000,
            'max_salary': 43000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=26),
            'status': 'active'
        },
        {
            'title': 'Cloud Solutions Architect (Software Focus)',
            'description': """
Chúng tôi đang tìm kiếm một Kiến trúc sư Giải pháp Đám mây chuyên về phần mềm để thiết kế và triển khai các giải pháp dựa trên nền tảng đám mây. Bạn sẽ tư vấn về chiến lược đám mây, kiến trúc và các phương pháp tốt nhất cho phát triển ứng dụng, đồng thời dẫn dắt việc triển khai các hệ thống phức tạp.

Trách nhiệm:
- Thiết kế và triển khai các giải pháp phần mềm dựa trên nền tảng đám mây cho khách hàng và các dự án nội bộ
- Phát triển kiến trúc cloud có khả năng mở rộng cao, linh hoạt và hiệu quả về chi phí
- Cung cấp tư vấn kỹ thuật về việc lựa chọn dịch vụ đám mây, microservices và containerization
- Tối ưu hóa hiệu suất, bảo mật và độ tin cậy của các hệ thống đám mây
- Tạo tài liệu chi tiết về kiến trúc, thiết kế và các quy trình triển khai
- Hướng dẫn và hỗ trợ đội ngũ phát triển trong việc áp dụng các phương pháp tốt nhất về đám mây
- Phối hợp với các bên liên quan để đảm bảo giải pháp đáp ứng các yêu cầu nghiệp vụ
- Thực hiện đánh giá và tối ưu hóa chi phí đám mây
- Điều tra và giải quyết các vấn đề về hiệu suất và khả năng mở rộng
- Theo dõi xu hướng công nghệ đám mây và đề xuất cải tiến
            """,
            'requirements': """
- Tối thiểu 5 năm kinh nghiệm với một hoặc nhiều nền tảng đám mây lớn (AWS, Azure, GCP)
- Chứng chỉ chuyên môn về đám mây (AWS Solutions Architect, Azure Solutions Architect, GCP Professional Cloud Architect)
- Hiểu biết sâu rộng về các nguyên tắc kiến trúc phần mềm và thiết kế hệ thống
- Kinh nghiệm với containerization (Docker) và orchestration (Kubernetes)
- Kiến thức vững chắc về kiến trúc microservices và các mẫu thiết kế phân tán
- Kinh nghiệm với Infrastructure as Code (Terraform, CloudFormation, ARM Templates)
- Hiểu biết về CI/CD pipelines và DevOps practices
- Kinh nghiệm với monitoring, logging và quản lý hiệu suất ứng dụng trên đám mây
- Kiến thức về bảo mật đám mây và các phương pháp tốt nhất về tuân thủ
- Kỹ năng lập trình tốt với một hoặc nhiều ngôn ngữ (Python, Java, C#, JavaScript)
- Kinh nghiệm với databases (SQL và NoSQL) trên đám mây
- Kinh nghiệm với serverless computing và event-driven architecture
- Khả năng giao tiếp hiệu quả với cả các đối tượng kỹ thuật và phi kỹ thuật
- Kỹ năng giải quyết vấn đề phức tạp và tư duy kiến trúc mạnh mẽ
            """,
            'location': 'remote',
            'min_salary': 50000000,
            'max_salary': 90000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=40),
            'status': 'active'
        },
        {
            'title': 'Robotics Software Engineer',
            'description': """
Chúng tôi đang tìm kiếm một Kỹ sư Phần mềm Robotics tài năng để phát triển phần mềm cho các hệ thống robot, bao gồm các thành phần nhận thức, điều hướng và điều khiển. Bạn sẽ làm việc trong một đội ngũ đa ngành để tích hợp các thành phần phần cứng và phần mềm, tạo ra các giải pháp robotics tiên tiến.

Trách nhiệm:
- Phát triển phần mềm cho các hệ thống robotics sử dụng ROS (Robot Operating System)
- Thiết kế và triển khai các thuật toán cho nhận thức, điều hướng và điều khiển robot
- Tích hợp các cảm biến (camera, lidar, radar, IMU) và xử lý dữ liệu cảm biến
- Xây dựng và duy trì các hệ thống định vị và lập bản đồ (SLAM)
- Tối ưu hóa hiệu suất các thuật toán robotics cho các ứng dụng thời gian thực
- Phối hợp với các kỹ sư phần cứng để tích hợp hệ thống và giải quyết các vấn đề giao tiếp
- Thiết kế và thực hiện các thử nghiệm để xác thực tính năng và hiệu suất hệ thống
- Tìm hiểu và áp dụng các kỹ thuật học máy cho các ứng dụng robotics
- Viết tài liệu kỹ thuật chi tiết về các thuật toán và hệ thống phần mềm
- Hỗ trợ quá trình triển khai và bảo trì các hệ thống robotics
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm phát triển phần mềm cho hệ thống robotics
- Kinh nghiệm sâu rộng với ROS (Robot Operating System) và các công cụ liên quan
- Kỹ năng lập trình mạnh mẽ với C++ và Python
- Hiểu biết vững chắc về các thuật toán điều khiển, động học học và quy hoạch chuyển động
- Kinh nghiệm với các thuật toán SLAM (Simultaneous Localization and Mapping)
- Kiến thức về xử lý hình ảnh và thị giác máy tính cho ứng dụng robotics
- Kinh nghiệm với việc tích hợp cảm biến (cameras, lidar, radar, IMU)
- Hiểu biết về các hệ thống thời gian thực và lập trình nhúng
- Kinh nghiệm với các công cụ mô phỏng robotics (Gazebo, Webots)
- Kiến thức về học máy và ứng dụng trong robotics là một lợi thế
- Bằng cấp trong Khoa học Máy tính, Kỹ thuật Điện, Robotics hoặc lĩnh vực liên quan
- Kỹ năng giải quyết vấn đề và tư duy phân tích mạnh mẽ
- Khả năng làm việc trong môi trường đa ngành, phối hợp với các chuyên gia phần cứng
- Kỹ năng giao tiếp tốt và khả năng giải thích các khái niệm kỹ thuật phức tạp
            """,
            'location': 'da_nang',
            'min_salary': 38000000,
            'max_salary': 65000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=34),
            'status': 'active'
        },
        {
            'title': 'Technical Writer (Software)',
            'description': """
Chúng tôi đang tìm kiếm một Biên tập viên Kỹ thuật chuyên về phần mềm để tạo ra tài liệu rõ ràng và súc tích cho các sản phẩm phần mềm của chúng tôi. Bạn sẽ chịu trách nhiệm viết hướng dẫn API, hướng dẫn sử dụng và hướng dẫn thực hành, giúp người dùng và nhà phát triển hiểu và sử dụng hiệu quả sản phẩm của chúng tôi.

Trách nhiệm:
- Tạo và duy trì tài liệu kỹ thuật chất lượng cao cho các sản phẩm phần mềm
- Viết hướng dẫn API, tài liệu tham khảo, hướng dẫn sử dụng và hướng dẫn thực hành
- Phối hợp với các kỹ sư phần mềm, nhà thiết kế sản phẩm và đội ngũ hỗ trợ khách hàng để thu thập thông tin chính xác
- Đơn giản hóa các khái niệm kỹ thuật phức tạp thành ngôn ngữ dễ hiểu
- Tổ chức, cấu trúc và định dạng tài liệu một cách nhất quán và thân thiện với người dùng
- Biên tập và cải thiện nội dung do người khác viết
- Làm việc với đội ngũ bản địa hóa để đảm bảo tài liệu có thể được dịch một cách hiệu quả
- Tạo nội dung đa phương tiện (hình ảnh, video, infographics) để bổ sung cho tài liệu văn bản
- Theo dõi phản hồi của người dùng và cải thiện tài liệu dựa trên phản hồi
- Duy trì hệ thống quản lý tài liệu và thực hiện quy trình xuất bản
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm viết tài liệu kỹ thuật cho phần mềm
- Kỹ năng viết và giao tiếp xuất sắc bằng tiếng Việt và tiếng Anh
- Khả năng hiểu các khái niệm kỹ thuật phức tạp và giải thích chúng một cách rõ ràng, đơn giản
- Kiến thức về các công cụ biên soạn tài liệu (Markdown, AsciiDoc, Docusaurus, MkDocs)
- Kinh nghiệm với các hệ thống quản lý nội dung (CMS) và hệ thống quản lý tài liệu
- Hiểu biết cơ bản về phát triển phần mềm, API và các công nghệ web
- Kinh nghiệm với các công cụ thiết kế đồ họa (Illustrator, Photoshop) là một lợi thế
- Kiến thức về tìm kiếm thông tin (SEO) cho tài liệu kỹ thuật
- Khả năng tổ chức và ưu tiên nhiều dự án cùng một lúc
- Kỹ năng chỉnh sửa và cải thiện nội dung do người khác viết
- Sự chú ý đến chi tiết và cam kết về chất lượng
- Kinh nghiệm với Git và quy trình Docs-as-Code là một lợi thế
- Tư duy phản biện và khả năng thu thập thông tin từ các nguồn khác nhau
- Bằng cấp trong Truyền thông Kỹ thuật, Khoa học Máy tính, Ngôn ngữ học hoặc lĩnh vực liên quan
            """,
            'location': 'ho_chi_minh',
            'min_salary': 20000000,
            'max_salary': 35000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=24),
            'status': 'active'
        },
        {
            'title': 'Game Developer (Unity/Unreal Engine)',
            'description': """
Chúng tôi đang tìm kiếm một Nhà phát triển Game đầy đam mê để phát triển các trò chơi hấp dẫn cho nhiều nền tảng sử dụng Unity hoặc Unreal Engine. Bạn sẽ tham gia vào toàn bộ quá trình phát triển game, từ thiết kế đến triển khai, làm việc với cơ chế game, đồ họa và tối ưu hóa hiệu suất.

Trách nhiệm:
- Phát triển game cho nhiều nền tảng (PC, mobile, console) sử dụng Unity (C#) hoặc Unreal Engine (C++)
- Thiết kế và triển khai các cơ chế game, hệ thống nhân vật và tương tác người dùng
- Tạo và tối ưu hóa mã game, đảm bảo hiệu suất và trải nghiệm mượt mà trên nhiều thiết bị
- Phối hợp với team đồ họa để tích hợp các tài sản hình ảnh vào game
- Làm việc với nhà thiết kế âm thanh để triển khai âm thanh và nhạc nền
- Phát hiện và khắc phục lỗi, đảm bảo trải nghiệm người dùng ổn định
- Triển khai các tính năng mạng và multiplayer nếu cần
- Tích hợp các dịch vụ của bên thứ ba (analytics, in-app purchases, ads)
- Tham gia vào quá trình kiểm thử và cân bằng game
- Tối ưu hóa game cho các thiết bị khác nhau và giảm thiểu dung lượng
            """,
            'requirements': """
- Tối thiểu 2 năm kinh nghiệm phát triển game với Unity (C#) hoặc Unreal Engine (C++)
- Portfolio thể hiện các dự án game đã hoàn thành hoặc đóng góp đáng kể
- Hiểu biết sâu sắc về nguyên tắc phát triển game và thiết kế game
- Kỹ năng lập trình mạnh mẽ với C# (cho Unity) hoặc C++ (cho Unreal)
- Kinh nghiệm với physics engines, AI, và các hệ thống animation
- Kiến thức về tối ưu hóa hiệu suất và quản lý bộ nhớ
- Hiểu biết cơ bản về đồ họa hai chiều và ba chiều, shaders và hiệu ứng hình ảnh
- Kinh nghiệm với version control (Git, Perforce)
- Khả năng làm việc với các công cụ tích hợp và pipeline của game engine
- Hiểu biết về UI/UX trong game và thiết kế responsive
- Kỹ năng giải quyết vấn đề tốt và tư duy sáng tạo
- Kinh nghiệm với các hệ thống multiplayer là một lợi thế
- Kiến thức về monetization và analytics trong game là một lợi thế
- Đam mê về game và hiểu biết về các thể loại game khác nhau
- Khả năng làm việc trong môi trường nhóm sáng tạo
            """,
            'location': 'ha_noi',
            'min_salary': 25000000,
            'max_salary': 45000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=30),
            'status': 'active'
        },
        {
            'title': 'AI Product Manager',
            'description': """
Chúng tôi đang tìm kiếm một Quản lý Sản phẩm AI có tầm nhìn để định hướng và thúc đẩy chiến lược sản phẩm cho các tính năng và sản phẩm ứng dụng AI. Bạn sẽ làm việc chặt chẽ với các đội ngũ kỹ thuật, thiết kế và nghiên cứu để phát triển các giải pháp AI đột phá, đáp ứng nhu cầu của thị trường và người dùng.

Trách nhiệm:
- Xác định tầm nhìn và lộ trình sản phẩm cho các tính năng và sản phẩm dựa trên AI
- Thực hiện nghiên cứu thị trường và người dùng để xác định các cơ hội sản phẩm AI
- Phối hợp với đội ngũ kỹ thuật, thiết kế và nghiên cứu AI để phát triển giải pháp
- Chuyển đổi các ý tưởng thành các yêu cầu sản phẩm rõ ràng và chi tiết kỹ thuật
- Xác định và theo dõi các chỉ số thành công cho các tính năng AI
- Làm việc với đội ngũ kinh doanh để phát triển chiến lược go-to-market
- Theo dõi xu hướng công nghệ và cạnh tranh trong lĩnh vực AI
- Ưu tiên tính năng và tạo backlog sản phẩm dựa trên giá trị kinh doanh và khả thi kỹ thuật
- Quản lý các bên liên quan và giao tiếp về tiến độ, rủi ro và cơ hội sản phẩm
- Hợp tác với đội ngũ pháp lý và đạo đức AI để đảm bảo tuân thủ các quy định
            """,
            'requirements': """
- Tối thiểu 3 năm kinh nghiệm trong quản lý sản phẩm, ưu tiên kinh nghiệm với sản phẩm AI/ML
- Kiến thức vững chắc về các công nghệ và xu hướng AI, hiểu biết về khả năng và giới hạn của chúng
- Kinh nghiệm chuyển đổi các khái niệm AI phức tạp thành tính năng sản phẩm hữu ích
- Kiến thức về các phương pháp nghiên cứu người dùng và phân tích dữ liệu
- Kỹ năng giao tiếp và trình bày xuất sắc, có khả năng truyền đạt tầm nhìn sản phẩm
- Kinh nghiệm làm việc với các đội ngũ kỹ thuật trong môi trường Agile
- Hiểu biết về quy trình phát triển phần mềm và vòng đời phát triển sản phẩm
- Khả năng đưa ra quyết định dựa trên dữ liệu và phân tích định lượng
- Tư duy chiến lược và khả năng xác định cơ hội thị trường
- Kinh nghiệm với các công cụ quản lý sản phẩm (Jira, Asana, Trello)
- Bằng cấp trong Khoa học Máy tính, Kỹ thuật, Kinh doanh hoặc lĩnh vực liên quan
- Kỹ năng lãnh đạo mạnh mẽ và khả năng tạo ảnh hưởng mà không cần quyền lực trực tiếp
- Đam mê về AI và tác động của nó đến người dùng và xã hội
- Tiếng Anh thành thạo, đặc biệt trong giao tiếp kỹ thuật
            """,
            'location': 'ho_chi_minh',
            'min_salary': 45000000,
            'max_salary': 75000000,
            'job_type': 'full_time',
            'application_deadline': timezone.now() + timedelta(days=37),
            'status': 'active'
        },
        {
            'title': 'Part-time Web Content Uploader',
            'description': """
Chúng tôi đang tìm kiếm một Chuyên viên Đăng tải Nội dung Web bán thời gian để hỗ trợ việc đăng tải và định dạng nội dung trên các trang web của công ty. Bạn sẽ chịu trách nhiệm đảm bảo tính chính xác và nhất quán của nội dung web, làm việc linh hoạt theo lịch trình bán thời gian.

Trách nhiệm:
- Đăng tải và định dạng các loại nội dung (văn bản, hình ảnh, video) lên các trang web của công ty
- Chỉnh sửa và cập nhật nội dung hiện có trên các trang web
- Đảm bảo tính nhất quán và chính xác của nội dung web
- Tối ưu hóa hình ảnh và đa phương tiện cho web
- Kiểm tra các liên kết và khắc phục các lỗi nội dung
- Cấu trúc nội dung theo các yêu cầu SEO cơ bản
- Phối hợp với đội ngũ nội dung và tiếp thị để đăng tải chiến dịch và bài viết mới
- Theo dõi các chỉ số hiệu suất nội dung cơ bản
- Hỗ trợ việc xuất báo cáo và phân tích dữ liệu website khi cần
- Báo cáo và giải quyết các vấn đề kỹ thuật liên quan đến nội dung
            """,
            'requirements': """
- Kiến thức cơ bản về HTML và các công cụ quản lý nội dung web (CMS) như WordPress, Drupal, Joomla
- Kỹ năng sử dụng thành thạo MS Office hoặc Google Docs
- Có khả năng xử lý và chỉnh sửa hình ảnh cơ bản
- Chú ý đến chi tiết và có kỹ năng tổ chức tốt
- Khả năng làm việc độc lập và quản lý thời gian hiệu quả
- Kỹ năng giao tiếp rõ ràng và khả năng làm việc với các bộ phận khác
- Hiểu biết cơ bản về SEO và các nguyên tắc thân thiện với công cụ tìm kiếm
- Kinh nghiệm trước đây với quản lý nội dung web là một lợi thế
- Kiến thức về các công cụ phân tích web (Google Analytics) là một lợi thế
- Khả năng làm việc với các thời hạn ngắn và xử lý nhiều yêu cầu
- Có khả năng làm việc linh hoạt về thời gian (buổi tối/cuối tuần nếu cần)
- Tinh thần trách nhiệm cao và đáng tin cậy
- Đam mê học hỏi và theo kịp các xu hướng web mới
            """,
            'location': 'remote',
            'min_salary': 10000000, # Giả định là mức lương theo giờ hoặc theo dự án
            'max_salary': 15000000, # Giả định là mức lương theo giờ hoặc theo dự án
            'job_type': 'part_time',
            'application_deadline': timezone.now() + timedelta(days=20),
            'status': 'active'
        }  # Thêm dấu phẩy ở đây
    ]  # Đảm bảo dấu ngoặc vuông đóng ở đây
    
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