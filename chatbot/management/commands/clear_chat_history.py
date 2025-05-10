from django.core.management.base import BaseCommand
from chatbot.models import Conversation, Message
from django.db.models import Count
from django.utils import timezone

class Command(BaseCommand):
    help = 'Xóa toàn bộ lịch sử chat trong hệ thống'

    def handle(self, *args, **options):
        # Count conversations and messages before deletion
        conversation_count = Conversation.objects.count()
        message_count = Message.objects.count()
        
        # Delete all messages
        Message.objects.all().delete()
        
        # Delete all conversations
        Conversation.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Đã xóa thành công {conversation_count} cuộc hội thoại và {message_count} tin nhắn tại {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
            )
        ) 