from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('api/', views.chatbot_api, name='chatbot_api'),
    path('api/send/', views.chatbot_api, name='chatbot_api'),
    path('api/history/', views.get_conversation_history, name='conversation_history'),
    path('api/history/<int:conversation_id>/', views.get_conversation_history, name='conversation_history_detail'),
    path('api/clear/', views.clear_conversation, name='clear_conversation'),
    path('api/analyze-resume/', views.analyze_resume_api, name='analyze_resume_api'),
]