from django.core.management.base import BaseCommand
from chatbot.web_search_tools import WebSearchTools
import json
import os

class Command(BaseCommand):
    help = 'Test the job search functionality with a query'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The job search query to test')
        parser.add_argument('--type', type=str, help='The search type (title, location, skills)', default=None)

    def handle(self, *args, **options):
        query = options['query']
        search_type = options['type']
        
        self.stdout.write(self.style.SUCCESS(f'Testing job search with query: "{query}" (type: {search_type or "auto"})'))
        
        try:
            # Run the job search
            result = WebSearchTools.job_search(query, search_type)
            
            # Show metadata first
            self.stdout.write(self.style.SUCCESS('Metadata:'))
            metadata = {
                'success': result['success'],
                'query': result['query'],
                'search_type': result['search_type'],
                'result_count': result['result_count']
            }
            self.stdout.write(json.dumps(metadata, indent=2))
            
            # Show job results
            if result['result_count'] > 0:
                self.stdout.write(self.style.SUCCESS('Found jobs:'))
                for i, job in enumerate(result['jobs'], 1):
                    self.stdout.write(f"{i}. {job['title']} at {job['company']} ({job['location']})")
            else:
                self.stdout.write(self.style.WARNING('No jobs found'))
            
            # Save formatted HTML to a file for inspection
            html_file = "job_search_results.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(result['formatted_results'])
            
            self.stdout.write(self.style.SUCCESS(f'Formatted HTML results saved to {html_file}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running job search: {str(e)}')) 