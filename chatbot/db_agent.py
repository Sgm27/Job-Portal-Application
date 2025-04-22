from jobs.models import Job
from django.db.models import Q
from django.utils import timezone
import re
from django.urls import reverse
from django.conf import settings
from chatbot.chatgpt_helper import chatgpt_helper
from accounts.models import Resume

class JobDatabaseAgent:
    """Agent for querying job-related information from the database"""
    
    @staticmethod
    def query_jobs_by_title(title_keywords, limit=5):
        """
        Query jobs by title keywords
        
        Args:
            title_keywords (str): Keywords to search in job titles
            limit (int): Maximum number of jobs to return
            
        Returns:
            list: List of job dictionaries with relevant information
        """
        # Create a Q object for each keyword to search in title and description
        keywords = [keyword.strip() for keyword in title_keywords.split() if keyword.strip()]
        query = Q()
        for keyword in keywords:
            query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
            
        # Filter active jobs that haven't passed deadline
        jobs = Job.objects.filter(
            query,
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
    def query_jobs_by_location(location, limit=5):
        """
        Query jobs by location
        
        Args:
            location (str): Location name to search for
            limit (int): Maximum number of jobs to return
            
        Returns:
            list: List of job dictionaries with relevant information
        """
        # Normalize the location input by removing extra whitespace and converting to lowercase
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
        
        # If still no match, try fuzzy match with well-known cities
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
    def query_jobs_by_skills(skills, limit=5):
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
    def detect_job_query_intent(message):
        """
        Detect if the user message is asking for job listings
        
        Args:
            message (str): User message
            
        Returns:
            tuple: (intent_detected (bool), query_type (str), query_value (str))
        """
        # Don't process educational queries as job searches
        if JobDatabaseAgent.is_educational_query(message):
            return False, None, None
        
        # Normalize message to improve matching
        normalized_message = message.lower()
        
        # Direct AI detection (common case)
        ai_keywords = ['ai', 'a.i', 'a.i.', 'artificial intelligence', 'trí tuệ nhân tạo', 'machine learning', 'ml']
        for keyword in ai_keywords:
            if keyword in normalized_message:
                return True, 'title', keyword
                
        # Enhanced patterns for different types of job queries
        title_patterns = [
            r'(?:tìm|liệt kê|danh sách|có những|hiển thị).*(?:công việc|job|việc làm).*?([\w\s.]+?)(?:\s|$|không|\?)',
            r'(?:tìm|liệt kê|danh sách|có những|hiển thị).* ([\w\s.]+?) (?:jobs|công việc|việc làm)',
            r'(?:có|còn).* ([\w\s.]+?) (?:jobs|công việc|việc làm).*(?:nào|không)',
            r'(?:tìm|kiếm).* ([\w\s.]+?)(?:\s|$)',
            r'(?:liệt kê|show).* ([\w\s.]+?)(?:\s|$)',
            r'jobs? (?:về|liên quan đến|cho|là) ([\w\s.]+?)(?:\s|$|không|\?)',
            r'(?:việc làm|công việc) (?:về|liên quan đến|cho|là) ([\w\s.]+?)(?:\s|$|không|\?)',
            r'có.* ([\w\s.]+?) (?:jobs|công việc|việc làm).* (?:nào|không)',
            # Special pattern to capture "muốn tìm công việc liên quan đến X"
            r'muốn tìm.*(?:công việc|job|việc làm).*(?:về|liên quan đến|cho|là) ([\w\s.]+?)(?:\s|$|không|\?)',
        ]
        
        # Improved location patterns to handle multi-word locations like "Hà Nội"
        location_patterns = [
            r'(?:tìm|liệt kê|danh sách|có những|hiển thị).*(?:công việc|job|việc làm).*(?:tại|ở) ([\w\s]+?)(?:\.|\s|$|không|\?|và|hoặc)',
            r'(?:có|còn).*(?:công việc|job|việc làm).*(?:tại|ở) ([\w\s]+?)(?:\.|\s|$|không|\?|và|hoặc)',
            r'(?:tìm|liệt kê|danh sách).*(?:tại|ở) ([\w\s]+?)(?:\.|\s|$|không|\?|và|hoặc)',
            r'(?:job|việc|việc làm).* ([\w\s]+? city|tỉnh [\w\s]+?|thành phố [\w\s]+?)(?:\.|\s|$|không|\?|và|hoặc)',
            # Specific patterns for common Vietnamese cities
            r'(?:tìm|liệt kê|danh sách|có những|hiển thị).*(?:ở|tại) (hà nội|hồ chí minh|đà nẵng|nha trang|hải phòng|cần thơ|huế)(?:\.|\s|$|không|\?|và|hoặc)',
            r'(hà nội|hồ chí minh|đà nẵng|nha trang|hải phòng|cần thơ|huế)(?:\.|\s|$|không|\?|có)',
            # Pattern for "web ở hà nội" type queries
            r'(\w+) (?:ở|tại) (hà nội|hồ chí minh|đà nẵng|nha trang|hải phòng|cần thơ|huế)(?:\.|\s|$|không|\?|và|hoặc)',
        ]
        
        skill_patterns = [
            r'(?:tìm|liệt kê|danh sách).*(?:công việc|job|việc làm).*(?:yêu cầu|cần|kỹ năng|skill) ([\w\s,]+?)(?:\s|$|không|\?)',
            r'(?:công việc|job|việc làm).*(?:biết|có kỹ năng|có kinh nghiệm về) ([\w\s,]+?)(?:\s|$|không|\?)',
            r'(?:tìm|liệt kê|danh sách).*(?:với|dùng|sử dụng|yêu cầu) kỹ năng ([\w\s,]+?)(?:\s|$|không|\?)'
        ]
        
        # Special pattern for "tìm việc [job_type] ở [location]" format
        combined_pattern = r'(?:tìm|kiếm).*(?:việc|job) ([\w\s]+?) (?:ở|tại) ([\w\s]+?)(?:\.|\s|$|không|\?|và|hoặc)'
        match = re.search(combined_pattern, normalized_message, re.IGNORECASE)
        if match:
            job_type = match.group(1).strip()
            location = match.group(2).strip()
            
            # Prioritize job type with location if both are valid
            if job_type and len(job_type) > 1 and location and len(location) > 1:
                if location.lower() in ['hà nội', 'hồ chí minh', 'đà nẵng', 'nha trang', 'hải phòng', 'cần thơ', 'huế']:
                    # Use location-based search for well-known cities
                    return True, 'location', location
                else:
                    # For other cases, search by job type as it's more specific
                    return True, 'title', job_type
        
        # Check for location queries with multi-word location awareness
        for pattern in location_patterns:
            match = re.search(pattern, normalized_message, re.IGNORECASE)
            if match:
                if pattern.endswith(r'(\w+) (?:ở|tại) (hà nội|hồ chí minh|đà nẵng|nha trang|hải phòng|cần thơ|huế)(?:\.|\s|$|không|\?|và|hoặc)'):
                    # Handle special pattern that captures both job type and location
                    job_type = match.group(1).strip()
                    location = match.group(2).strip()
                    return True, 'title', job_type  # Prioritize job type for search
                else:
                    location = match.group(1).strip()
                    # Validate location is meaningful
                    if location and len(location) > 1:
                        # Identify well-known Vietnamese cities and handle them specifically
                        if location.lower() in ['hà nội', 'hồ chí minh', 'đà nẵng', 'nha trang', 'hải phòng', 'cần thơ', 'huế']:
                            return True, 'location', location
                        else:
                            return True, 'location', location

        # Check for title queries with improved filtering
        for pattern in title_patterns:
            match = re.search(pattern, normalized_message, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                # Skip common words that aren't job titles but keep important keywords
                skip_words = ['job', 'việc', 'nào', 'những', 'các', 'liên', 'quan', 'đến', 'về']
                if query and len(query) > 1 and query.lower() not in skip_words:
                    # Check for common job field abbreviations
                    if query.lower() in ['ai', 'ml', 'ui', 'ux', 'qa', 'ba', 'hr', 'it', 'vr', 'ar', 'dev', 'seo']:
                        return True, 'title', query
                    # For other queries, ensure they're significant enough
                    elif len(query) > 2:
                        return True, 'title', query
                        
        # Check for skill queries
        for pattern in skill_patterns:
            match = re.search(pattern, normalized_message, re.IGNORECASE)
            if match:
                skills = match.group(1).strip()
                if skills and len(skills) > 2:
                    return True, 'skills', skills
        
        # Fallback for simple keywords in the message
        important_job_keywords = ['developer', 'engineer', 'analyst', 'manager', 'designer', 
                                 'ai', 'python', 'java', 'web', 'mobile', 'data', 'cloud', 'devops']
        
        for keyword in important_job_keywords:
            if keyword in normalized_message:
                return True, 'title', keyword
                
        # Additional check for location-based queries for common cities
        common_cities = ['hà nội', 'hồ chí minh', 'đà nẵng', 'nha trang', 'hải phòng', 'cần thơ', 'huế']
        for city in common_cities:
            if city in normalized_message:
                # If city is mentioned but no job type is found, default to a general job search in that location
                return True, 'location', city
        
        return False, None, None
    
    @staticmethod
    def is_educational_query(message):
        """
        Detect if the user message is asking for educational information rather than job listings
        
        Args:
            message (str): User message
            
        Returns:
            bool: True if message is an educational query, False otherwise
        """
        normalized_message = message.lower()
        
        # Specific common tech learning queries
        tech_learning_queries = [
            'học ai',
            'học machine learning',
            'học python',
            'học data science',
            'học blockchain',
            'học cloud computing',
            'học devops',
            'học web development',
            'học ios',
            'học android',
            'học flutter',
            'học react',
            'học angular',
            'học vue',
            'học aws',
            'học azure',
            'học gcp',
            'học frontend',
            'học backend',
            'học fullstack',
            'muốn học ai',
            'chuẩn bị học ai',
            'kiến thức học ai',
            'kiến thức để học',
            'lộ trình học',
            'cải thiện kỹ năng',
            'nâng cao kỹ năng',
            'phát triển kỹ năng',
            'học hỏi thêm',
            'muốn cải thiện',
            'muốn nâng cao',
            'muốn phát triển',
            'nâng cao trình độ',
            'tự học'
        ]
        
        # Check for direct tech learning queries first
        for query in tech_learning_queries:
            if query in normalized_message:
                return True
        
        # Educational query indicators
        educational_indicators = [
            r'(?:học|đi học|theo học)',
            r'(?:chuẩn bị|cần chuẩn bị)',
            r'(?:kiến thức|kien thuc)',
            r'(?:nên học|nen hoc)',
            r'(?:bằng cấp|bang cap)',
            r'(?:khóa học|khoa hoc|khoá học)',
            r'(?:học phí|hoc phi)',
            r'(?:giáo trình|giao trinh)',
            r'(?:ngành học|nganh hoc)',
            r'(?:chương trình|chuong trinh)',
            r'(?:kỹ năng|ky nang) (?:gì|nào|cần|phải)',
            r'(?:đại học|dai hoc)',
            r'(?:thạc sĩ|thac si)',
            r'(?:tiến sĩ|tien si)',
            r'(?:chứng chỉ|chung chi)',
            r'(?:làm thế nào để|lam the nao de) (?:học|trở thành)',
            r'(?:cải thiện|nâng cao|phát triển) (?:kỹ năng|trình độ)',
            r'(?:tự|tự học|tự trau dồi)',
        ]
        
        # Questions about career paths or learning, but not job listings
        career_education_phrases = [
            'nên học gì',
            'cần học gì',
            'phải học gì',
            'chuẩn bị gì',
            'kiến thức gì',
            'nên chuẩn bị',
            'để trở thành',
            'kỹ năng cần có',
            'kỹ năng nào',
            'kỹ năng gì',
            'tôi muốn học',
            'tôi muốn theo học',
            'môn học nào',
            'học ngành',
            'đi thực tập',
            'để đi thực tập',
            'muốn biết',
            'tôi cần biết',
            'cần chuẩn bị những',
            'cần chuẩn bị các',
            'trang bị kiến thức',
            'lộ trình',
            'roadmap',
            'career path',
            'hướng dẫn học',
            'cải thiện kỹ năng',
            'nâng cao kỹ năng',
            'phát triển kỹ năng',
            'tôi muốn cải thiện',
            'tôi muốn nâng cao',
            'tôi muốn phát triển',
            'tự học'
        ]
        
        # Check for educational intent markers
        for pattern in educational_indicators:
            if re.search(pattern, normalized_message, re.IGNORECASE):
                return True
                
        # Check for educational phrases
        for phrase in career_education_phrases:
            if phrase in normalized_message:
                return True
        
        return False
    
    @staticmethod
    def get_job_absolute_url(job_id):
        """
        Generate absolute URL for a job
        
        Args:
            job_id (int): Job ID
            
        Returns:
            str: Absolute URL for the job
        """
        relative_url = reverse('job_detail', kwargs={'job_id': job_id})
        return f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}{relative_url}"
    
    @staticmethod
    def format_job_results(jobs, query_type, query_value):
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
            job_url = JobDatabaseAgent.get_job_absolute_url(job['id'])
            
            # Format as HTML card
            response += f"""
                <div class="job-card">
                    <div class="job-title">
                        <a href="{job_url}" target="_blank" class="job-link"><strong>{job['title']}</strong></a>
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

class CVAnalysisAgent:
    """Agent for analyzing CVs/Resumes within the chat interface"""
    
    @staticmethod
    def analyze_resume(user, resume_id=None):
        """
        Analyze a resume or return a list of available resumes for selection
        
        Args:
            user: The user object making the request
            resume_id (optional): The ID of the resume to analyze, if already selected
            
        Returns:
            dict: Response with either resume list or analysis results
        """
        if not resume_id:
            # Return list of available resumes for the user
            return CVAnalysisAgent.get_resume_list(user)
        else:
            # Analyze specific resume
            return CVAnalysisAgent.analyze_specific_resume(user, resume_id)
    
    @staticmethod
    def get_resume_list(user):
        """
        Get list of available resumes for the user
        
        Args:
            user: The user object
            
        Returns:
            dict: Response with success status and list of resumes or error
        """
        return chatgpt_helper.analyze_resume_for_chatbot(user)
    
    @staticmethod
    def analyze_specific_resume(user, resume_id):
        """
        Analyze a specific resume
        
        Args:
            user: The user object
            resume_id: The ID of the resume to analyze
            
        Returns:
            dict: Analysis results or error
        """
        return chatgpt_helper.analyze_resume_for_chatbot(user, resume_id)
    
    @staticmethod
    def detect_resume_analysis_intent(message):
        """
        Detect if the user message is asking for resume analysis
        
        Args:
            message (str): User message
            
        Returns:
            bool: True if message is asking for resume analysis, False otherwise
        """
        # Normalize message to improve matching
        normalized_message = message.lower()
        
        # Patterns for resume analysis requests
        resume_patterns = [
            r'(?:phân tích|analyze|đánh giá|review|xem xét).*(?:cv|resume|hồ sơ)',
            r'(?:cv|resume|hồ sơ).*(?:phân tích|analyze|đánh giá|review|xem xét)',
            r'(?:giúp|help|xem|check).*(?:cv|resume|hồ sơ)',
            r'(?:cv|resume|hồ sơ).*(?:của tôi|của mình|my)',
            r'(?:cải thiện|nâng cấp|improve).*(?:cv|resume|hồ sơ)',
            r'(?:cv|resume|hồ sơ).*(?:thế nào|như thế nào|ra sao|nhận xét)',
            r'(?:nhận xét|góp ý|comment|feedback).*(?:cv|resume|hồ sơ)',
        ]
        
        # Check for resume analysis intent
        for pattern in resume_patterns:
            if re.search(pattern, normalized_message, re.IGNORECASE):
                return True
                
        return False
