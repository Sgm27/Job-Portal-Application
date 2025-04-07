from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import Resume

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Toàn thời gian'),
        ('part_time', 'Bán thời gian'),
        ('contract', 'Hợp đồng'),
        ('internship', 'Thực tập'),
        ('remote', 'Từ xa'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Đang tuyển'),
        ('filled', 'Đã tuyển xong'),
        ('expired', 'Hết hạn'),
        ('draft', 'Bản nháp'),
    )
    
    VIETNAM_LOCATIONS = (
        ('ha_noi', 'Hà Nội'),
        ('ho_chi_minh', 'Hồ Chí Minh'),
        ('da_nang', 'Đà Nẵng'),
        ('hai_phong', 'Hải Phòng'),
        ('can_tho', 'Cần Thơ'),
        ('an_giang', 'An Giang'),
        ('ba_ria_vung_tau', 'Bà Rịa - Vũng Tàu'),
        ('bac_giang', 'Bắc Giang'),
        ('bac_kan', 'Bắc Kạn'),
        ('bac_lieu', 'Bạc Liêu'),
        ('bac_ninh', 'Bắc Ninh'),
        ('ben_tre', 'Bến Tre'),
        ('binh_dinh', 'Bình Định'),
        ('binh_duong', 'Bình Dương'),
        ('binh_phuoc', 'Bình Phước'),
        ('binh_thuan', 'Bình Thuận'),
        ('ca_mau', 'Cà Mau'),
        ('cao_bang', 'Cao Bằng'),
        ('dak_lak', 'Đắk Lắk'),
        ('dak_nong', 'Đắk Nông'),
        ('dien_bien', 'Điện Biên'),
        ('dong_nai', 'Đồng Nai'),
        ('dong_thap', 'Đồng Tháp'),
        ('gia_lai', 'Gia Lai'),
        ('ha_giang', 'Hà Giang'),
        ('ha_nam', 'Hà Nam'),
        ('ha_tinh', 'Hà Tĩnh'),
        ('hai_duong', 'Hải Dương'),
        ('hau_giang', 'Hậu Giang'),
        ('hoa_binh', 'Hòa Bình'),
        ('hung_yen', 'Hưng Yên'),
        ('khanh_hoa', 'Khánh Hòa'),
        ('kien_giang', 'Kiên Giang'),
        ('kon_tum', 'Kon Tum'),
        ('lai_chau', 'Lai Châu'),
        ('lam_dong', 'Lâm Đồng'),
        ('lang_son', 'Lạng Sơn'),
        ('lao_cai', 'Lào Cai'),
        ('long_an', 'Long An'),
        ('nam_dinh', 'Nam Định'),
        ('nghe_an', 'Nghệ An'),
        ('ninh_binh', 'Ninh Bình'),
        ('ninh_thuan', 'Ninh Thuận'),
        ('phu_tho', 'Phú Thọ'),
        ('phu_yen', 'Phú Yên'),
        ('quang_binh', 'Quảng Bình'),
        ('quang_nam', 'Quảng Nam'),
        ('quang_ngai', 'Quảng Ngãi'),
        ('quang_ninh', 'Quảng Ninh'),
        ('quang_tri', 'Quảng Trị'),
        ('soc_trang', 'Sóc Trăng'),
        ('son_la', 'Sơn La'),
        ('tay_ninh', 'Tây Ninh'),
        ('thai_binh', 'Thái Bình'),
        ('thai_nguyen', 'Thái Nguyên'),
        ('thanh_hoa', 'Thanh Hóa'),
        ('thua_thien_hue', 'Thừa Thiên Huế'),
        ('tien_giang', 'Tiền Giang'),
        ('tra_vinh', 'Trà Vinh'),
        ('tuyen_quang', 'Tuyên Quang'),
        ('vinh_long', 'Vĩnh Long'),
        ('vinh_phuc', 'Vĩnh Phúc'),
        ('yen_bai', 'Yên Bái'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100, choices=VIETNAM_LOCATIONS)
    salary = models.CharField(max_length=50, null=True, blank=True, help_text='Mức lương theo tháng (VNĐ)')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        return self.application_deadline < timezone.now()

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Đang chờ'),
        ('reviewed', 'Đã xem xét'),
        ('shortlisted', 'Trong danh sách rút gọn'),
        ('rejected', 'Đã từ chối'),
        ('hired', 'Đã tuyển dụng'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_applications')
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    employer_notes = models.TextField(null=True, blank=True, help_text='Private notes for the employer')
    
    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('cv_viewed', 'CV Đã Xem'),
        ('status_updated', 'Trạng Thái Cập Nhật'),
        ('application_submitted', 'Đơn Ứng Tuyển Mới'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
