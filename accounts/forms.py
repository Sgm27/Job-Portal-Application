from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Resume

class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('employer', 'Employer'),
        ('job_seeker', 'Job Seeker'),
    )
    
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'user_type':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'phone_number']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add appropriate classes to form fields
        for field_name in self.fields:
            if field_name != 'profile_picture':
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        
        # Add conditional fields based on user type
        if self.instance.user_type == 'job_seeker':
            self.fields['resume'] = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
            self.fields['skills'] = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
        elif self.instance.user_type == 'employer':
            self.fields['company_name'] = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
            self.fields['company_description'] = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=False)
            self.fields['company_website'] = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file', 'title', 'is_primary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề CV'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.instance.pk:  # Nếu là CV mới
            if Resume.objects.filter(user=self.user).count() >= 5:
                raise forms.ValidationError("Bạn chỉ có thể tải lên tối đa 5 CV")
        return cleaned_data
