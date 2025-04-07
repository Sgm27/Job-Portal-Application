from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import os

def validate_pdf_file(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('File phải có định dạng PDF')
    if value.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('Kích thước file không được vượt quá 5MB')

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('employer', 'Employer'),
        ('job_seeker', 'Job Seeker'),
    )
    
    user_type = models.CharField(_('User Type'), max_length=10, choices=USER_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    # Additional fields for job seekers
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    
    # Additional fields for employers
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    company_website = models.URLField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.username

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/', validators=[validate_pdf_file])
    title = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Nếu là primary resume đầu tiên
        if self.is_primary:
            # Đặt tất cả resume khác của user này không phải là primary
            Resume.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        
        # Nếu đây là resume đầu tiên của user, đặt là primary
        if not Resume.objects.filter(user=self.user).exists():
            self.is_primary = True
        
        # Kiểm tra số lượng resume của user
        if not self.pk and Resume.objects.filter(user=self.user).count() >= 5:
            raise ValidationError('Bạn chỉ có thể tải lên tối đa 5 CV')
            
        super().save(*args, **kwargs)
