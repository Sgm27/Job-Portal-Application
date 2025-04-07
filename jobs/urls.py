from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list_view, name='job_list'),
    path('<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('<int:job_id>/apply/', views.job_apply_view, name='job_apply'),
    path('post-job/', views.post_job_view, name='post_job'),
    path('<int:job_id>/edit/', views.edit_job_view, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job_view, name='delete_job'),
    path('dashboard/', views.employer_dashboard_view, name='employer_dashboard'),
    path('<int:job_id>/applications/', views.applicant_tracking_view, name='applicant_tracking'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('applications/<int:application_id>/save-note/', views.save_application_note, name='save_application_note'),
    path('my-applications/', views.job_seeker_applications, name='my_applications'),
    
    # Đường dẫn cho tính năng thông báo
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('employer/<int:employer_id>/jobs/', views.employer_jobs_view, name='employer_jobs'),
    
    # Đường dẫn cho chức năng xem CV đã ứng tuyển
    path('applications/<int:application_id>/view-resume/', views.view_application_resume, name='view_application_resume'),
    path('my-applications/<int:application_id>/view-resume/', views.view_my_application_resume, name='view_my_application_resume'),
]
