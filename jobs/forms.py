from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    SALARY_SUGGESTIONS = {
        'Fresher/Intern': '7,000,000 - 12,000,000 VNĐ/tháng',
        'Junior (1-2 năm KN)': '12,000,000 - 18,000,000 VNĐ/tháng',
        'Middle (2-4 năm KN)': '18,000,000 - 30,000,000 VNĐ/tháng',
        'Senior (4-8 năm KN)': '30,000,000 - 60,000,000 VNĐ/tháng',
        'Lead/Manager': '50,000,000 - 90,000,000 VNĐ/tháng',
        'CTO/Director': 'Từ 90,000,000 VNĐ/tháng',
    }
    
    application_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Hạn nộp đơn ứng tuyển'
    )
    
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'location', 'salary', 
                  'job_type', 'application_deadline', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Cập nhật placeholder và hướng dẫn cho trường salary
        salary_suggestions = "\n".join([f"• {level}: {salary}" for level, salary in self.SALARY_SUGGESTIONS.items()])
        self.fields['salary'].widget.attrs.update({
            'placeholder': 'Ví dụ: 18,000,000 - 30,000,000 VNĐ/tháng'
        })
        self.fields['salary'].help_text = f'''
            Vui lòng nhập mức lương phù hợp với vị trí và thị trường hiện tại. Gợi ý mức lương theo kinh nghiệm:
            {salary_suggestions}
        '''
        
        # Change labels to Vietnamese
        self.fields['title'].label = 'Chức danh'
        self.fields['description'].label = 'Mô tả công việc'
        self.fields['requirements'].label = 'Yêu cầu'
        self.fields['location'].label = 'Địa điểm'
        self.fields['salary'].label = 'Mức lương (VNĐ/tháng)'
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
