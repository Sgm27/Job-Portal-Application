from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from accounts.models import User
from jobs.models import Job, Application
from .serializers import (
    UserSerializer, JobSeekerSerializer, EmployerSerializer,
    JobSerializer, ApplicationSerializer, UserRegistrationSerializer
)
from .permissions import IsEmployer, IsJobSeeker, IsJobOwner, IsApplicationOwner
from django_filters.rest_framework import DjangoFilterBackend

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.user.user_type == 'job_seeker':
            return JobSeekerSerializer
        elif self.request.user.user_type == 'employer':
            return EmployerSerializer
        return UserSerializer
    
    def get_object(self):
        """
        Users can only access their own profile
        """
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'job_type', 'status']
    search_fields = ['title', 'description', 'requirements']
    ordering_fields = ['created_at', 'application_deadline', 'salary']
    
    def get_permissions(self):
        """
        - List and retrieve are available for all authenticated users
        - Create, update, partial_update, destroy are for employers only
        - Object-level permission makes sure only the job owner can modify it
        """
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsEmployer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsJobOwner()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsJobSeeker])
    def apply(self, request, pk=None):
        job = self.get_object()
        
        # Check if user already applied for this job
        if Application.objects.filter(job=job, applicant=request.user).exists():
            return Response(
                {"detail": "You have already applied for this job"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(job=job, applicant=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def applications(self, request, pk=None):
        job = self.get_object()
        
        # Only the employer who posted the job can view applications
        if job.employer != request.user:
            return Response(
                {"detail": "You do not have permission to view these applications"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        applications = Application.objects.filter(job=job)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicationOwner]
    
    def get_queryset(self):
        """
        - Job seekers can see their own applications
        - Employers can see applications for their jobs
        """
        user = self.request.user
        
        if user.user_type == 'job_seeker':
            return Application.objects.filter(applicant=user)
        elif user.user_type == 'employer':
            return Application.objects.filter(job__employer=user)
        
        return Application.objects.none()
    
    def perform_create(self, serializer):
        job_id = self.request.data.get('job')
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is a job seeker
        if self.request.user.user_type != 'job_seeker':
            return Response(
                {"detail": "Only job seekers can apply for jobs"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save(job=job, applicant=self.request.user)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsEmployer])
    def update_status(self, request, pk=None):
        application = self.get_object()
        
        # Only the employer who posted the job can update application status
        if application.job.employer != request.user:
            return Response(
                {"detail": "You do not have permission to update this application"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {"detail": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = status_value
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
