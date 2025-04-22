from rest_framework import serializers
from accounts.models import User
from jobs.models import Job, Application

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                  'phone_number', 'profile_picture']
        read_only_fields = ['id']

class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 
                  'phone_number', 'skills', 'resume']
        read_only_fields = ['id', 'username', 'user_type']

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture',
                  'phone_number', 'company_name', 'company_description', 'company_website']
        read_only_fields = ['id', 'username', 'user_type']

class JobSerializer(serializers.ModelSerializer):
    employer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'min_salary', 'max_salary', 'job_type', 
                  'created_at', 'employer', 'employer_name', 'status', 'requirements', 
                  'application_deadline']
        read_only_fields = ['id', 'employer', 'created_at']
    
    def get_employer_name(self, obj):
        return f"{obj.employer.company_name}" if obj.employer.company_name else f"{obj.employer.username}"

class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'applicant', 'applicant_name', 'cover_letter', 
                  'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'applicant', 'created_at', 'updated_at']
    
    def get_applicant_name(self, obj):
        return f"{obj.applicant.first_name} {obj.applicant.last_name}" if obj.applicant.first_name else obj.applicant.username
    
    def get_job_title(self, obj):
        return obj.job.title

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
