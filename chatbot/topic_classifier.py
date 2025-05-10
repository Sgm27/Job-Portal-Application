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
        if not self.api_key:
            logger.error("API key not configured - cannot classify message")
            return True, "Could not classify message due to API configuration issues. Proceeding as if relevant."
        
        # Construct the classification prompt
        prompt = [
            {"role": "system", "content": 
             """You are a classifier that determines if a question is related to work, career, professional skills, 
             or professional development topics. Respond with a JSON object containing two fields:
             1. "is_work_related": a boolean (true/false)
             2. "explanation": a brief explanation of your decision
             
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
        
        try:
            # Use the client-based approach or fallback to older approach
            try:
                # Try with new OpenAI client approach first
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using a smaller model for faster, cost-effective classification
                    messages=prompt,
                    temperature=0.1,  # Low temperature for more consistent responses
                    max_tokens=150  # Classification doesn't need many tokens
                )
                response_text = response.choices[0].message.content.strip()
            except AttributeError:
                # Fallback to older approach if needed
                import openai
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
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
                    return True, "Classification response format error. Proceeding as if relevant."
                
                is_work_related = result.get("is_work_related", True)
                explanation = result.get("explanation", "No explanation provided")
                
                logger.info(f"Classification result for query: {is_work_related} - {explanation}")
                return is_work_related, explanation
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse classification response JSON: {e}")
                logger.error(f"Response text: {response_text}")
                # Default to treating as work-related in case of parsing errors
                return True, "Classification response parsing error. Proceeding as if relevant."
                
        except Exception as e:
            logger.error(f"Error during classification: {str(e)}")
            # Default to treating as work-related in case of API errors
            return True, f"Classification error: {str(e)}. Proceeding as if relevant."

# Create a singleton instance
topic_classifier = TopicClassifier() 