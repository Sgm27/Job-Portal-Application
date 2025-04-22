from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    application_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Hạn nộp đơn ứng tuyển'
    )
    
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'location', 'min_salary', 'max_salary', 
                  'job_type', 'application_deadline', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['min_salary'].widget.attrs.update({
            'placeholder': 'Ví dụ: 18000000'
        })
        self.fields['max_salary'].widget.attrs.update({
            'placeholder': 'Ví dụ: 30000000'
        })
        
        # Đơn giản hóa help_text
        self.fields['min_salary'].help_text = 'Nhập mức lương tối thiểu (VNĐ/tháng)'
        self.fields['max_salary'].help_text = 'Nhập mức lương tối đa (VNĐ/tháng)'
        
        # Change labels to Vietnamese
        self.fields['title'].label = 'Vị trí tuyển dụng'
        self.fields['description'].label = 'Mô tả công việc'
        self.fields['requirements'].label = 'Yêu cầu'
        self.fields['location'].label = 'Địa điểm'
        self.fields['min_salary'].label = 'Mức lương tối thiểu (VNĐ/tháng)'
        self.fields['max_salary'].label = 'Mức lương tối đa (VNĐ/tháng)'
        self.fields['job_type'].label = 'Loại công việc'
        self.fields['application_deadline'].label = 'Hạn nộp đơn'
        self.fields['status'].label = 'Trạng thái'

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_letter'].label = 'Thư giới thiệu'

class JobSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tìm kiếm công việc...'}))
    location = forms.ChoiceField(
        required=False,
        choices=[('', 'Tất cả địa điểm')] + list(Job.VIETNAM_LOCATIONS),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Tất cả loại công việc')] + list(Job.JOB_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
