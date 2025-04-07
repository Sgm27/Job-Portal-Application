from rest_framework import permissions

class IsEmployer(permissions.BasePermission):
    """
    Permission to only allow employers to access the view
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'employer'

class IsJobSeeker(permissions.BasePermission):
    """
    Permission to only allow job seekers to access the view
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'job_seeker'

class IsJobOwner(permissions.BasePermission):
    """
    Permission to only allow owners of a job to edit it
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only the job owner can edit the job
        return obj.employer == request.user

class IsApplicationOwner(permissions.BasePermission):
    """
    Permission to only allow job applicants to view/edit their applications
    or employers to view applications for their jobs
    """
    def has_object_permission(self, request, view, obj):
        # Applicant can view/edit their own application
        if obj.applicant == request.user:
            return True
        
        # Employer can view applications for their jobs
        if request.user.user_type == 'employer' and obj.job.employer == request.user:
            return True
        
        return False
