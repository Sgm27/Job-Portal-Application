import logging
import json
from django.conf import settings
from django.urls import reverse
import requests
from typing import Dict, List, Any, Optional
from .chatgpt_helper import chatgpt_helper

from jobs.models import Job
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

class WebSearchTools:
    """A collection of tools for web search and information retrieval"""
    
    @staticmethod
    def job_search(query: str, search_type: Optional[str] = None, limit: int = 5, threshold: float = 0.7) -> Dict[str, Any]:
        """
        Search for jobs based on query and search type with confidence scoring
        
        Args:
            query (str): The search query
            search_type (str, optional): The type of search ("title", "location", "skills"). 
                                        If not provided, the function will automatically determine the best type.
            limit (int): Maximum number of jobs to return (only used as fallback)
            threshold (float): Confidence score threshold (0.0 to 1.0) for including jobs
            
        Returns:
            dict: A dictionary containing search results and metadata
        """
        try:
            # If search_type is not provided, determine it based on the query
            if not search_type:
                # Use LLM to determine the search type
                search_type_prompt = f"""
                Analyze this job search query: "{query}"
                
                Determine the most likely search type from these options:
                1. "title" - if searching for a specific job title or field
                2. "location" - if searching based on geographic location
                3. "skills" - if searching for jobs requiring specific skills
                
                Only return one of these values: "title", "location", or "skills"
                """
                search_type = chatgpt_helper.ask_gpt(search_type_prompt).strip().lower()
                
                # Validate the response
                if search_type not in ["title", "location", "skills"]:
                    search_type = "title"  # Default to title search if invalid response
            
            # Query jobs based on search type without initial limit since we'll filter by score
            if search_type == "location":
                candidate_jobs = WebSearchTools._query_jobs_by_location(query, limit=100)
            elif search_type == "skills":
                candidate_jobs = WebSearchTools._query_jobs_by_skills(query, limit=100)
            else:  # Default to title search
                candidate_jobs = WebSearchTools._query_jobs_by_title(query, limit=100)
            
            # If no jobs found, return empty results
            if not candidate_jobs:
                return {
                    "success": True,
                    "search_type": search_type,
                    "query": query,
                    "result_count": 0,
                    "jobs": [],
                    "formatted_results": WebSearchTools._format_job_results([], search_type, query)
                }
            
            # Use LLM to score each job's relevance to the query
            scored_jobs = WebSearchTools._score_jobs_with_llm(query, candidate_jobs, search_type)
            
            # Filter jobs by threshold and sort by confidence score
            filtered_jobs = [job for job in scored_jobs if job['confidence_score'] >= threshold]
            
            # Sort jobs by confidence score in descending order
            filtered_jobs.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            # Format and return the results
            return {
                "success": True,
                "search_type": search_type,
                "query": query,
                "result_count": len(filtered_jobs),
                "jobs": filtered_jobs,
                "formatted_results": WebSearchTools._format_job_results(filtered_jobs, search_type, query)
            }
            
        except Exception as e:
            logger.error(f"Error in job_search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "search_type": search_type if search_type else "unknown",
                "query": query
            }
    
    @staticmethod
    def _score_jobs_with_llm(query: str, jobs: List[Dict], search_type: str) -> List[Dict]:
        """
        Use LLM to score each job's relevance to the query
        
        Args:
            query (str): The search query
            jobs (List[Dict]): List of job dictionaries
            search_type (str): Type of search being performed
            
        Returns:
            List[Dict]: Jobs with added confidence scores
        """
        if not jobs:
            return []
            
        # Create a batch scoring prompt for efficiency
        scoring_prompt = f"""
        Task: Score the relevance of each job to the search query.
        
        Search query: "{query}"
        Search type: {search_type}
        
        For each job, analyze how well it matches the query and assign a confidence score (0.0 to 1.0).
        1.0 = Perfect match, extremely relevant
        0.7 = Good match, fairly relevant
        0.5 = Moderate match, somewhat relevant
        0.3 = Weak match, slightly relevant
        0.0 = No match, irrelevant
        
        Jobs to score:
        """
        
        # Add job details to the prompt
        for i, job in enumerate(jobs):
            job_summary = f"""
            Job {i+1}:
            - Title: {job['title']}
            - Company: {job['company']}
            - Location: {job['location']}
            - Job Type: {job['job_type']}
            - Skills: {job['skills']}
            - Description: {job['description']}
            """
            scoring_prompt += job_summary
        
        scoring_prompt += """
        For each job, provide a JSON response with job number and confidence score:
        [
          {"job_number": 1, "confidence_score": 0.X},
          {"job_number": 2, "confidence_score": 0.X},
          ...
        ]
        Only return the JSON array, nothing else.
        """
        
        try:
            # Get scores from LLM
            response = chatgpt_helper.ask_gpt(scoring_prompt)
            
            # Parse the JSON response
            # Ensure we're only parsing the JSON part in case there's extra text
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:].strip()
                    
            scores = json.loads(response)
            
            # Add confidence scores to the job dictionaries
            scored_jobs = []
            for i, job in enumerate(jobs):
                # Find the corresponding score from the LLM response
                score_entry = next((s for s in scores if s["job_number"] == i+1), None)
                
                if score_entry:
                    job_copy = job.copy()
                    job_copy['confidence_score'] = score_entry["confidence_score"]
                    scored_jobs.append(job_copy)
                else:
                    # If no score found, assign a default low score
                    job_copy = job.copy()
                    job_copy['confidence_score'] = 0.1
                    scored_jobs.append(job_copy)
            
            return scored_jobs
            
        except Exception as e:
            logger.error(f"Error scoring jobs with LLM: {str(e)}")
            # On error, return the original jobs with a default medium score
            for job in jobs:
                job['confidence_score'] = 0.5
            return jobs
    
    @staticmethod
    def _query_jobs_by_title(title_keywords, limit=5):
        """Query jobs by title keywords"""
        # Define job categories and related terms (including Vietnamese equivalents)
        job_categories = {
            'web': ['web', 'web dev', 'web developer', 'lập trình web', 'phát triển web', 'thiết kế web', 
                  'frontend', 'front-end', 'front end', 'front-end developer', 'lập trình front-end',
                  'backend', 'back-end', 'back end', 'back-end developer', 'lập trình back-end',
                  'fullstack', 'full-stack', 'full stack', 'full-stack developer', 'lập trình full-stack',
                  'developer', 'lập trình', 'lập trình viên', 'website', 'trang web',
                  'react', 'angular', 'vue', 'javascript', 'typescript', 'node', 'nodejs', 'node.js',
                  'php', 'html', 'css', 'django', 'flask', 'laravel', 'wordpress', 'asp.net'],
            
            'mobile': ['mobile', 'mobile dev', 'mobile developer', 'lập trình mobile', 'phát triển mobile',
                     'android', 'ios', 'flutter', 'react native', 'swift', 'kotlin', 'lập trình android', 'lập trình ios'],
            
            'data': ['data', 'analytics', 'analyst', 'science', 'scientist', 'machine learning', 'ml', 'ai', 
                   'big data', 'phân tích dữ liệu', 'khoa học dữ liệu', 'trí tuệ nhân tạo',
                   'tensorflow', 'pytorch', 'pandas', 'numpy', 'business intelligence', 'bi'],
            
            'design': ['design', 'ui', 'ux', 'ui/ux', 'graphic', 'designer', 'thiết kế', 'thiết kế đồ họa',
                     'photoshop', 'illustrator', 'figma', 'sketch', 'adobe xd', 'indesign'],
            
            'it_support': ['support', 'helpdesk', 'it support', 'it helpdesk', 'hỗ trợ', 'kỹ thuật',
                         'technical support', 'hỗ trợ kỹ thuật', 'hỗ trợ it', 'hỗ trợ người dùng'],
            
            'network': ['network', 'system', 'admin', 'administrator', 'mạng', 'hệ thống',
                      'quản trị mạng', 'quản trị hệ thống', 'devops', 'sysadmin', 'system admin'],
            
            'security': ['security', 'cyber', 'bảo mật', 'an ninh mạng', 'penetration testing',
                       'pen test', 'ethical hacking', 'bảo vệ dữ liệu'],
            
            'qa': ['qa', 'quality', 'testing', 'tester', 'test', 'kiểm thử', 'đảm bảo chất lượng',
                 'automation testing', 'kiểm thử tự động', 'manual testing', 'kiểm thử thủ công'],
            
            'management': ['manager', 'lead', 'quản lý', 'trưởng nhóm', 'trưởng phòng', 'giám đốc',
                         'project manager', 'quản lý dự án', 'product manager', 'quản lý sản phẩm'],
            
            'marketing': ['marketing', 'seo', 'sem', 'social media', 'content', 'digital marketing',
                        'tiếp thị', 'quảng cáo', 'truyền thông', 'content marketing'],
            
            'hr': ['hr', 'human resources', 'recruitment', 'nhân sự', 'tuyển dụng', 'đào tạo']
        }
        
        # Define category exclusions (categories that shouldn't appear when searching for specific categories)
        category_exclusions = {
            'web': ['it_support', 'hr', 'marketing'],
            'mobile': ['it_support', 'hr', 'marketing'],
            'data': ['it_support', 'hr', 'marketing'],
            'design': ['it_support', 'hr', 'marketing', 'network', 'security'],
            'it_support': ['web', 'mobile', 'data', 'design'],
            'marketing': ['web', 'mobile', 'data', 'it_support', 'network', 'security'],
            'hr': ['web', 'mobile', 'data', 'it_support', 'network', 'security']
        }
        
        # Normalize the input keywords
        query_terms = title_keywords.lower().strip()
        
        # Check if query matches any job category
        matching_categories = []
        excluded_categories = set()
        for category, terms in job_categories.items():
            for term in terms:
                if term in query_terms or any(term == keyword.lower() for keyword in query_terms.split()):
                    matching_categories.append(category)
                    # Add excluded categories based on this match
                    if category in category_exclusions:
                        excluded_categories.update(category_exclusions[category])
                    break
        
        # Remove duplicates while preserving order
        matching_categories = list(dict.fromkeys(matching_categories))
        
        # If web development is specifically mentioned, make sure it's prioritized
        if 'web' in matching_categories and ('web developer' in query_terms or 'lập trình web' in query_terms):
            matching_categories.remove('web')
            matching_categories.insert(0, 'web')
        
        # Check for exact phrase match first
        phrase_matches = Job.objects.filter(
            Q(title__icontains=query_terms),
            status='active',
            application_deadline__gt=timezone.now()
        )
        
        # Create weighted queries based on individual terms
        keywords = [keyword.strip() for keyword in query_terms.split() if keyword.strip()]
        
        # Create base query
        base_query = Q(status='active') & Q(application_deadline__gt=timezone.now())
        
        # Create specific query for matching categories
        category_query = Q()
        if matching_categories:
            for category in matching_categories:
                for term in job_categories[category]:
                    category_query |= Q(title__icontains=term)
        
        # Create exclusion query for jobs we want to exclude
        exclusion_query = Q()
        for category in excluded_categories:
            if category in job_categories:
                for term in job_categories[category]:
                    # Only exclude terms that are strong indicators of the category
                    if len(term) > 3:  # Avoid excluding short terms that might have multiple meanings
                        exclusion_query |= Q(title__icontains=term)
        
        # Add individual keyword queries
        keyword_query = Q()
        for keyword in keywords:
            keyword_query |= Q(title__icontains=keyword)
            keyword_query |= Q(description__icontains=keyword)
        
        # Get category-matched jobs first
        category_matches = []
        if matching_categories:
            # First priority: Jobs matching both category and keywords in title
            primary_matches = Job.objects.filter(
                base_query & category_query & keyword_query
            ).order_by('-created_at')
            
            category_matches.extend(list(primary_matches))
            
            # Second priority: Jobs matching category in title
            secondary_matches = Job.objects.filter(
                base_query & category_query & ~Q(pk__in=[job.pk for job in category_matches])
            ).order_by('-created_at')
            
            category_matches.extend(list(secondary_matches))
        
        # Get keyword matches that aren't in category matches
        keyword_matches = Job.objects.filter(
            base_query & keyword_query & 
            ~Q(pk__in=[job.pk for job in category_matches]) &
            ~exclusion_query
        ).order_by('-created_at')
        
        # Combine results with proper prioritization
        combined_jobs = list(phrase_matches)
        
        # Add category matches if not already included
        for job in category_matches:
            if job not in combined_jobs:
                combined_jobs.append(job)
        
        # Add keyword matches if not already included
        for job in keyword_matches:
            if job not in combined_jobs:
                combined_jobs.append(job)
                
        # Final filter to remove jobs that match excluded categories if we have specific category matches
        if matching_categories and excluded_categories:
            filtered_jobs = []
            for job in combined_jobs:
                # Check if job title contains any term from excluded categories
                exclude_job = False
                for category in excluded_categories:
                    if category in job_categories:
                        for term in job_categories[category]:
                            if len(term) > 3 and term in job.title.lower():  # Only consider significant terms
                                exclude_job = True
                                break
                    if exclude_job:
                        break
                
                if not exclude_job:
                    filtered_jobs.append(job)
                    
                # If we're specifically looking for web jobs and not finding enough after filtering,
                # make an exception for jobs with "developer" in the title
                if 'web' in matching_categories and len(filtered_jobs) < 3 and 'developer' in job.title.lower():
                    if job not in filtered_jobs:
                        filtered_jobs.append(job)
            
            combined_jobs = filtered_jobs if filtered_jobs else combined_jobs
        
        # Order by created date and limit results
        combined_jobs = combined_jobs[:limit]
        
        # Format the job information for display
        results = []
        for job in combined_jobs:
            job_info = {
                'id': job.id,
                'title': job.title,
                'company': job.employer.company_name or job.employer.username,
                'location': job.get_location_display(),
                'job_type': job.get_job_type_display(),
                'salary_range': f"{job.min_salary:,} - {job.max_salary:,} VNĐ/tháng",
                'deadline': job.application_deadline.strftime('%d/%m/%Y'),
                'description': job.description[:150] + '...' if len(job.description) > 150 else job.description,
                'posted_date': job.created_at.strftime('%d/%m/%Y'),
                'skills': ', '.join([skill.name for skill in job.skills.all()]) if hasattr(job, 'skills') else ''
            }
            results.append(job_info)
            
        return results
    
    @staticmethod
    def _query_jobs_by_location(location, limit=5):
        """Query jobs by location"""
        # Normalize the location input
        normalized_location = location.strip().lower()
        
        # Create a mapping of normalized location names to location codes
        location_mapping = {}
        for code, name in Job.VIETNAM_LOCATIONS:
            location_mapping[name.lower()] = code
            
            # Add common variations for Hanoi and Ho Chi Minh City
            if name.lower() == "hà nội":
                location_mapping["hanoi"] = code
                location_mapping["ha noi"] = code
            elif name.lower() == "hồ chí minh":
                location_mapping["ho chi minh"] = code
                location_mapping["hcm"] = code
                location_mapping["tphcm"] = code
                location_mapping["tp hcm"] = code
                location_mapping["saigon"] = code
                location_mapping["sài gòn"] = code
        
        # First try exact match
        location_code = location_mapping.get(normalized_location)
        
        # If no exact match, try partial match
        if not location_code:
            for name, code in location_mapping.items():
                if normalized_location in name or name in normalized_location:
                    location_code = code
                    break
        
        # If still no match, try well-known cities
        if not location_code:
            well_known_cities = {
                "hà nội": "HN", 
                "hồ chí minh": "HCM", 
                "đà nẵng": "DN", 
                "nha trang": "NT", 
                "hải phòng": "HP", 
                "cần thơ": "CT", 
                "huế": "HU"
            }
            
            for city_name, city_code in well_known_cities.items():
                if city_name in normalized_location or normalized_location in city_name:
                    location_code = city_code
                    break
                    
        # If no matching location found, return empty list
        if not location_code:
            return []
            
        # Query active jobs in the specified location
        jobs = Job.objects.filter(
            location=location_code,
            status='active',
            application_deadline__gt=timezone.now()
        ).order_by('-created_at')[:limit]
        
        # Format the job information for display
        results = []
        for job in jobs:
            job_info = {
                'id': job.id,
                'title': job.title,
                'company': job.employer.company_name or job.employer.username,
                'location': job.get_location_display(),
                'job_type': job.get_job_type_display(),
                'salary_range': f"{job.min_salary:,} - {job.max_salary:,} VNĐ/tháng",
                'deadline': job.application_deadline.strftime('%d/%m/%Y'),
                'description': job.description[:150] + '...' if len(job.description) > 150 else job.description,
                'posted_date': job.created_at.strftime('%d/%m/%Y'),
                'skills': ', '.join([skill.name for skill in job.skills.all()]) if hasattr(job, 'skills') else ''
            }
            results.append(job_info)
            
        return results
    
    @staticmethod
    def _query_jobs_by_skills(skills, limit=5):
        """Query jobs by required skills"""
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        if not skills_list:
            skills_list = [skills.strip()]
            
        query = Q()
        for skill in skills_list:
            query |= Q(skills__name__icontains=skill)
            
        jobs = Job.objects.filter(
            query,
            status='active',
            application_deadline__gt=timezone.now()
        ).order_by('-created_at')[:limit]
        
        results = []
        for job in jobs:
            job_info = {
                'id': job.id,
                'title': job.title,
                'company': job.employer.company_name or job.employer.username,
                'location': job.get_location_display(),
                'job_type': job.get_job_type_display(),
                'salary_range': f"{job.min_salary:,} - {job.max_salary:,} VNĐ/tháng",
                'deadline': job.application_deadline.strftime('%d/%m/%Y'),
                'description': job.description[:150] + '...' if len(job.description) > 150 else job.description,
                'posted_date': job.created_at.strftime('%d/%m/%Y'),
                'skills': ', '.join([skill.name for skill in job.skills.all()]) if hasattr(job, 'skills') else ''
            }
            results.append(job_info)
            
        return results
    
    @staticmethod
    def _get_job_absolute_url(job_id):
        """Get the absolute URL for a job"""
        relative_url = reverse('job_detail', kwargs={'job_id': job_id})
        return f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}{relative_url}"
    
    @staticmethod
    def _format_job_results(jobs, query_type, query_value):
        """Format job query results into a readable response with clickable links"""
        if not jobs:
            if query_type == 'title':
                return f"""
                <div class="no-jobs-found">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        <span>Tôi không tìm thấy công việc nào liên quan đến '<strong>{query_value}</strong>' trong hệ thống.</span>
                    </div>
                    <p>Bạn có thể thử:</p>
                    <ul>
                        <li>Tìm với từ khóa khác</li>
                        <li>Kiểm tra lại chính tả</li>
                        <li><a href="/jobs/" class="all-jobs-link">Xem tất cả các công việc hiện có</a></li>
                    </ul>
                </div>
                """
            elif query_type == 'location':
                return f"""
                <div class="no-jobs-found">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        <span>Tôi không tìm thấy công việc nào tại '<strong>{query_value}</strong>' trong hệ thống.</span>
                    </div>
                    <p>Bạn có thể thử:</p>
                    <ul>
                        <li>Tìm kiếm ở các thành phố lớn như: Hà Nội, Hồ Chí Minh, Đà Nẵng</li>
                        <li>Kiểm tra lại chính tả địa điểm</li>
                        <li><a href="/jobs/" class="all-jobs-link">Xem tất cả các công việc hiện có</a></li>
                    </ul>
                </div>
                """
            elif query_type == 'skills':
                return f"""
                <div class="no-jobs-found">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        <span>Tôi không tìm thấy công việc nào yêu cầu kỹ năng '<strong>{query_value}</strong>' trong hệ thống.</span>
                    </div>
                    <p>Bạn có thể thử:</p>
                    <ul>
                        <li>Tìm với kỹ năng khác</li>
                        <li>Kiểm tra lại chính tả</li>
                        <li><a href="/jobs/" class="all-jobs-link">Xem tất cả các công việc hiện có</a></li>
                    </ul>
                </div>
                """
        
        # Format a header based on the query type
        if query_type == 'title':
            response = f"""
            <div class="job-search-results">
                <div class="result-header">
                    <h5><i class="bi bi-search me-2"></i>Kết quả tìm kiếm cho '{query_value}'</h5>
                    <p>Tìm thấy {len(jobs)} công việc phù hợp</p>
                </div>
                <div class="job-list">
            """
        elif query_type == 'location':
            response = f"""
            <div class="job-search-results">
                <div class="result-header">
                    <h5><i class="bi bi-geo-alt me-2"></i>Công việc tại '{query_value}'</h5>
                    <p>Tìm thấy {len(jobs)} công việc phù hợp</p>
                </div>
                <div class="job-list">
            """
        elif query_type == 'skills':
            response = f"""
            <div class="job-search-results">
                <div class="result-header">
                    <h5><i class="bi bi-tools me-2"></i>Công việc yêu cầu kỹ năng '{query_value}'</h5>
                    <p>Tìm thấy {len(jobs)} công việc phù hợp</p>
                </div>
                <div class="job-list">
            """
        else:
            response = f"""
            <div class="job-search-results">
                <div class="result-header">
                    <h5><i class="bi bi-list-task me-2"></i>Danh sách công việc</h5>
                    <p>Tìm thấy {len(jobs)} công việc phù hợp</p>
                </div>
                <div class="job-list">
            """
        
        # Add job details with clickable HTML links
        for job in jobs:
            job_url = WebSearchTools._get_job_absolute_url(job['id'])
            
            # Add confidence score display if available
            confidence_display = ""
            if 'confidence_score' in job:
                score_percentage = int(job['confidence_score'] * 100)
                confidence_display = f"""
                <div class="job-confidence">
                    <small>Độ phù hợp: {score_percentage}%</small>
                </div>
                """
            
            # Format as HTML card
            response += f"""
                <div class="job-card">
                    <div class="job-title">
                        <a href="{job_url}" target="_blank" class="job-link"><strong>{job['title']}</strong></a>
                        {confidence_display}
                    </div>
                    <div class="job-company">
                        <i class="bi bi-building me-1"></i> {job['company']}
                    </div>
                    <div class="job-description">
                        {job['description']}
                    </div>
                    <div class="job-details">
                        <div class="job-detail-item">
                            <i class="bi bi-geo-alt me-1"></i> {job['location']}
                        </div>
                        <div class="job-detail-item">
                            <i class="bi bi-briefcase me-1"></i> {job['job_type']}
                        </div>
            """
            
            if job['salary_range']:
                response += f"""
                        <div class="job-detail-item">
                            <i class="bi bi-cash me-1"></i> {job['salary_range']}
                        </div>
                """
            
            if job['skills']:
                response += f"""
                        <div class="job-detail-item skills">
                            <i class="bi bi-tools me-1"></i> {job['skills']}
                        </div>
                """
                
            response += f"""
                        <div class="job-detail-item">
                            <i class="bi bi-calendar-event me-1"></i> Đăng: {job['posted_date']}
                        </div>
                        <div class="job-detail-item">
                            <i class="bi bi-calendar-x me-1"></i> Hạn: {job['deadline']}
                        </div>
                    </div>
                    <div class="job-actions">
                        <a href="{job_url}" target="_blank" class="btn btn-primary btn-sm rounded-pill">
                            <i class="bi bi-eye me-1"></i> Xem chi tiết
                        </a>
                    </div>
                </div>
            """
        
        # Close the job list div and add a footer
        response += """
                </div>
                <div class="result-footer">
                    <p><a href="/jobs/" class="all-jobs-link"><i class="bi bi-search me-1"></i>Xem tất cả công việc</a></p>
                </div>
            </div>
        """
        
        return response
        
    @staticmethod
    def web_search(query: str) -> Dict[str, Any]:
        """
        Search the web for information about trending web technologies
        
        Args:
            query (str): The search query
            
        Returns:
            dict: A dictionary containing search results and metadata
        """
        try:
            # Use ChatGPT to generate information about trending web technologies
            search_prompt = f"""
            Bạn là một chuyên gia về công việc và phát triển phần mềm với kiến thức sâu rộng về các xu hướng công nghệ mới nhất. 
            
            Hãy cung cấp thông tin chuyên sâu về: {query}
            
            Hãy bao gồm các nội dung sau (phù hợp với chủ đề):
            
            1. Tổng quan ngắn gọn về công nghệ/xu hướng
            2. Các công nghệ/framework/thư viện nổi bật và phiên bản mới nhất
               - Ưu điểm chính
               - Mục đích sử dụng
               - Độ phổ biến trong ngành
            3. So sánh khách quan giữa các công nghệ tương tự
               - Ưu điểm và nhược điểm của mỗi công nghệ
               - Trường hợp sử dụng phù hợp nhất
            4. Xu hướng mới nổi trong lĩnh vực này
               - Công nghệ đang được chú ý
               - Dự đoán phát triển trong tương lai gần
            5. Tài nguyên học tập và thực hành
               - Khóa học, sách, tài liệu chính thức
               - Cộng đồng và diễn đàn hỗ trợ
            6. Ví dụ thực tế về dự án sử dụng công nghệ này
            
            Trả lời bằng tiếng Việt, sử dụng định dạng markdown để dễ đọc, tổ chức rõ ràng với các đề mục và gạch đầu dòng.
            Ưu tiên cung cấp thông tin mới nhất, chính xác, khách quan, và hữu ích.
            """
            
            response = chatgpt_helper.ask_gpt(search_prompt)
            
            return {
                "success": True,
                "query": query,
                "results": response,
                "is_markdown": True
            }
            
        except Exception as e:
            logger.error(f"Error in web_search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            } 