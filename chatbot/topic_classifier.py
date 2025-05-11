import logging
import os
from django.conf import settings

# Configure logger
logger = logging.getLogger(__name__)

class TopicClassifier:
    """
    Classifier to determine if a user question is related to work topics or skill improvement.
    Uses OpenAI's model for classification.
    """
    
    def __init__(self):
        """Initialize the classifier"""
        # Try to get API key from settings or environment variables
        try:
            self.api_key = settings.OPENAI_API_KEY
        except AttributeError:
            self.api_key = os.environ.get('OPENAI_API_KEY')
            
        if not self.api_key:
            logger.warning("OpenAI API key not found. Classification functionality will not work.")
        
        # Configure OpenAI client - support both old and new API formats
        if self.api_key:
            try:
                # Try new client-based API (v1.0.0+)
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Topic classifier using OpenAI API with new client-based approach")
            except ImportError:
                # Fall back to older module-level API
                import openai
                openai.api_key = self.api_key
                logger.info("Topic classifier using OpenAI API with legacy approach")
    
    def classify_message(self, user_query):
        """
        Classify a user query to determine if it's:
        1. Work-related
        2. A greeting
        
        Args:
            user_query: The user's question or message
            
        Returns:
            tuple: (is_work_related, is_greeting, explanation, greeting_response)
                is_work_related: Boolean indicating if the query is work-related
                is_greeting: Boolean indicating if the query is a simple greeting
                explanation: Brief explanation of the classification decision
                greeting_response: Standard greeting response if is_greeting is True, otherwise None
        """
        if not self.api_key:
            logger.error("API key not configured - cannot classify message")
            return True, False, "Could not classify message due to API configuration issues. Proceeding as if relevant.", None
        
        # Construct the classification prompt
        prompt = [
            {"role": "system", "content": 
             """You are a classifier that determines:
             1. If a question is related to work, career, professional skills, or professional development topics.
             2. If the message is a simple greeting or conversation starter.
             
             Respond with a JSON object containing three fields:
             1. "is_work_related": a boolean (true/false)
             2. "is_greeting": a boolean (true/false) - true if this is just a greeting or conversation starter
             3. "explanation": a brief explanation of your decision
             
             Work-related topics include but are not limited to:
             - Job search and applications
             - Career advice and advancement
             - Workplace issues and relationships
             - Professional skill development
             - Resume and interview preparation
             - Technical skills for various professions
             - Professional certifications
             - Work-life balance
             - Remote work / hybrid work
             - Workplace tools and technologies
             - Professional networking
             
             Examples of greetings or conversation starters:
             - Hello
             - Hi there
             - Good morning
             - How are you?
             - Nice to meet you
             - Chào (hello in Vietnamese)
             - Xin chào (hello in Vietnamese)
             
             Non-work-related topics include:
             - Personal entertainment
             - Video games unrelated to professional development
             - Dating and personal relationships
             - General news unrelated to career impact
             - Personal hobbies unrelated to professional development
             - Controversial political topics
             - Illegal activities
             """
            },
            {"role": "user", "content": user_query}
        ]
        
        greeting_response = "Chào bạn, tôi là trợ lý AI của Job Portal bạn muốn giúp đỡ về vấn đề tìm kiếm công việc, chỉnh sửa tối ưu CV, cập nhật các xu hướng công nghệ mới nhất, các câu hỏi chung về nghề nghiệp, phát triển kỹ năng...  "
        
        try:
            # Use the client-based approach or fallback to older approach
            try:
                # Try with new OpenAI client approach first
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Using a smaller model for faster, cost-effective classification
                    messages=prompt,
                    temperature=0.1,  # Low temperature for more consistent responses
                    max_tokens=150  # Classification doesn't need many tokens
                )
                response_text = response.choices[0].message.content.strip()
            except AttributeError:
                # Fallback to older approach if needed
                import openai
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=prompt,
                    temperature=0.1,
                    max_tokens=150
                )
                response_text = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            try:
                # Extract JSON from response if it's embedded in text
                import re
                import json
                
                # Try to find JSON in the response
                match = re.search(r'\{[\s\S]*\}', response_text)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                else:
                    # If no JSON found, default to treating as work-related
                    logger.warning(f"Couldn't extract JSON from classification response: {response_text}")
                    return True, False, "Classification response format error. Proceeding as if relevant.", None
                
                is_work_related = result.get("is_work_related", True)
                is_greeting = result.get("is_greeting", False)
                explanation = result.get("explanation", "No explanation provided")
                
                logger.info(f"Classification result: work-related={is_work_related}, greeting={is_greeting}, explanation={explanation}")
                
                # Return the greeting response if it's a greeting
                final_greeting = greeting_response if is_greeting else None
                
                return is_work_related, is_greeting, explanation, final_greeting
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse classification response JSON: {e}")
                logger.error(f"Response text: {response_text}")
                # Default to treating as work-related in case of parsing errors
                return True, False, "Classification response parsing error. Proceeding as if relevant.", None
                
        except Exception as e:
            logger.error(f"Error during classification: {str(e)}")
            # Default to treating as work-related in case of API errors
            return True, False, f"Classification error: {str(e)}. Proceeding as if relevant.", None

    def is_work_related(self, user_query):
        """
        Determine if a user query is related to work topics or professional skills.
        
        Args:
            user_query: The user's question or message
            
        Returns:
            tuple: (is_relevant, explanation)
                is_relevant: Boolean indicating if the query is work-related
                explanation: Brief explanation of the classification decision
        """
        is_work_related,is_greeting, explanation, _ = self.classify_message(user_query)
        return is_work_related, is_greeting, explanation

# Create a singleton instance
topic_classifier = TopicClassifier() 