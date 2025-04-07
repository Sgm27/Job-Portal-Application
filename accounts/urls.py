from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('upload-resume/', views.upload_resume_view, name='upload_resume'),
    path('delete-resume/<int:resume_id>/', views.delete_resume_view, name='delete_resume'),
    path('set-primary-resume/<int:resume_id>/', views.set_primary_resume_view, name='set_primary_resume'),
    path('analyze-resume/<int:resume_id>/', views.analyze_resume, name='analyze_resume'),
]
