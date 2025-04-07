from django.contrib import admin
from .models import Job, Application, Notification

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'job_type', 'status', 'created_at', 'application_deadline')
    list_filter = ('job_type', 'status', 'created_at')
    search_fields = ('title', 'description', 'requirements', 'location')
    date_hierarchy = 'created_at'

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'applicant__username', 'cover_letter')
    date_hierarchy = 'created_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'application', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'application__job__title', 'message')
    date_hierarchy = 'created_at'
