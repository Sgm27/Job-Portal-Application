from django.core.management.base import BaseCommand
from chatbot.web_search_tools import WebSearchTools
import json
import os

class Command(BaseCommand):
    help = 'Test the web search functionality with a query'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The search query to test')

    def handle(self, *args, **options):
        query = options['query']
        self.stdout.write(self.style.SUCCESS(f'Testing web search with query: "{query}"'))
        
        try:
            # Run the web search
            result = WebSearchTools.web_search(query)
            
            # Pretty print the result
            self.stdout.write(self.style.SUCCESS('Web search result:'))
            self.stdout.write('-' * 80)
            self.stdout.write(result['results'])
            self.stdout.write('-' * 80)
            
            # Show metadata
            self.stdout.write(self.style.SUCCESS('Metadata:'))
            metadata = {
                'success': result['success'],
                'query': result['query'],
                'is_markdown': result.get('is_markdown', False)
            }
            self.stdout.write(json.dumps(metadata, indent=2))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running web search: {str(e)}')) 