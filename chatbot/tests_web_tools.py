import unittest
from django.test import TestCase
from unittest.mock import patch, MagicMock
from .web_search_tools import WebSearchTools

class WebSearchToolsTestCase(TestCase):
    """Test cases for the WebSearchTools class"""
    
    @patch('chatbot.web_search_tools.chatgpt_helper')
    def test_web_search(self, mock_chatgpt_helper):
        # Mock the chatgpt_helper.ask_gpt method
        mock_chatgpt_helper.ask_gpt.return_value = "Mocked web search response"
        
        # Call the web_search method
        result = WebSearchTools.web_search("trending web technologies")
        
        # Check the result
        self.assertTrue(result['success'])
        self.assertEqual(result['query'], "trending web technologies")
        self.assertEqual(result['results'], "Mocked web search response")
        self.assertTrue(result['is_markdown'])
        
        # Verify the chatgpt_helper.ask_gpt was called with the right prompt
        mock_chatgpt_helper.ask_gpt.assert_called_once()
        call_args = mock_chatgpt_helper.ask_gpt.call_args[0][0]
        self.assertIn("trending web technologies", call_args)
    
    @patch('chatbot.web_search_tools.chatgpt_helper')
    def test_web_search_error(self, mock_chatgpt_helper):
        # Mock the chatgpt_helper.ask_gpt method to raise an exception
        mock_chatgpt_helper.ask_gpt.side_effect = Exception("API error")
        
        # Call the web_search method
        result = WebSearchTools.web_search("trending web technologies")
        
        # Check the result
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], "API error")
        self.assertEqual(result['query'], "trending web technologies")
    
    @patch('chatbot.web_search_tools.Job')
    @patch('chatbot.web_search_tools.chatgpt_helper')
    def test_job_search(self, mock_chatgpt_helper, mock_job_model):
        # Mock the job search type determination
        mock_chatgpt_helper.ask_gpt.return_value = "title"
        
        # Mock the job model and query
        mock_job = MagicMock()
        mock_job.id = 1
        mock_job.title = "Test Job"
        mock_job.employer.company_name = "Test Company"
        mock_job.get_location_display.return_value = "Test Location"
        mock_job.get_job_type_display.return_value = "Full-time"
        mock_job.min_salary = 10000000
        mock_job.max_salary = 15000000
        mock_job.application_deadline.strftime.return_value = "01/01/2023"
        mock_job.description = "Test Description"
        mock_job.created_at.strftime.return_value = "01/01/2023"
        mock_job.skills.all.return_value = []
        
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_job]
        mock_job_model.objects.filter.return_value = mock_queryset
        
        # Call the job_search method
        result = WebSearchTools.job_search("python developer")
        
        # Check the result
        self.assertTrue(result['success'])
        self.assertEqual(result['search_type'], "title")
        self.assertEqual(result['query'], "python developer")
        self.assertEqual(result['result_count'], 1)
        self.assertIn("formatted_results", result)
        
        # Verify that chatgpt_helper.ask_gpt was called
        mock_chatgpt_helper.ask_gpt.assert_called_once()
        
    @patch('chatbot.web_search_tools.Job')
    @patch('chatbot.web_search_tools.chatgpt_helper')
    def test_job_search_with_type(self, mock_chatgpt_helper, mock_job_model):
        # Mock the job model and query
        mock_job = MagicMock()
        mock_job.id = 1
        mock_job.title = "Test Job"
        mock_job.employer.company_name = "Test Company"
        mock_job.get_location_display.return_value = "Test Location"
        mock_job.get_job_type_display.return_value = "Full-time"
        mock_job.min_salary = 10000000
        mock_job.max_salary = 15000000
        mock_job.application_deadline.strftime.return_value = "01/01/2023"
        mock_job.description = "Test Description"
        mock_job.created_at.strftime.return_value = "01/01/2023"
        mock_job.skills.all.return_value = []
        
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_job]
        mock_job_model.objects.filter.return_value = mock_queryset
        
        # Call the job_search method with explicit search_type
        result = WebSearchTools.job_search("python", search_type="skills")
        
        # Check the result
        self.assertTrue(result['success'])
        self.assertEqual(result['search_type'], "skills")
        self.assertEqual(result['query'], "python")
        self.assertEqual(result['result_count'], 1)
        self.assertIn("formatted_results", result)
        
        # Verify that chatgpt_helper.ask_gpt was not called (since search_type was provided)
        mock_chatgpt_helper.ask_gpt.assert_not_called()

if __name__ == '__main__':
    unittest.main() 