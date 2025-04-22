# Job Portal Application

A comprehensive web application built with Django designed to connect job seekers with employers. This platform features advanced job management, user roles (job seeker, employer), AI-powered CV analysis, application tracking, an integrated chatbot, and a REST API.

## Features

### General & Core
*   **Homepage:** Displays featured jobs or a general overview.
*   **Job Listing:** Publicly viewable list of available jobs.
*   **Job Search & Filtering:** Search for jobs by keywords, location, type, and other relevant criteria.
*   **Job Details:** View detailed information about a specific job posting.
*   **Django Admin Interface:** For site administration and data management.

### User Authentication & Profiles
*   **User Roles:** Distinct functionalities for Job Seekers and Employers.
*   **Registration:** Secure user account creation.
*   **Login/Logout:** Standard email/username and password authentication.
*   **Social Login (Google):** Optional login/registration using Google accounts (via `django-allauth`).
*   **User Profile:** View and manage personal information.
*   **Resume Management (Job Seeker):**
    *   Upload multiple resumes (PDF, DOC, DOCX).
    *   Delete uploaded resumes.
    *   Set a primary resume for quick applications.
*   **AI-Powered Resume Analysis:**
    *   Analyze uploaded resumes using OpenAI/LangChain to extract key information (skills, experience, etc.).
    *   Accessed via the user profile or potentially through the chatbot API.

### Job Seeker Features
*   **Job Application:** Apply for jobs using a selected resume.
*   **Application History:** View a list of submitted applications and their current status.
*   **View Applied Resume:** See the specific resume used for a past application.

### Employer Features
*   **Job Management:**
    *   Post new job openings.
    *   Edit existing job details.
    *   Delete job postings.
*   **Employer Dashboard:** Centralized view for managing posted jobs and applications.
*   **View Posted Jobs:** List jobs associated with the specific employer account.
*   **Applicant Tracking System (ATS):**
    *   View list of applicants for each job posting.
    *   Update the status of applications (e.g., Received, Under Review, Interviewing, Hired, Rejected).
    *   Add internal notes to applications.
    *   View the resume submitted by each applicant.

### Notifications
*   **In-App Notifications:** Receive updates (e.g., application status changes).
*   **View Notifications:** Access a dedicated page to view all notifications.
*   **Mark as Read:** Manage notification status.

### API (Django REST Framework & SimpleJWT)
*   **RESTful Endpoints:**
    *   `/api/users/`: CRUD operations for User data.
    *   `/api/jobs/`: CRUD operations for Job data.
    *   `/api/applications/`: CRUD operations for Application data.
*   **JWT Authentication:**
    *   `/api/token/`: Obtain JWT access and refresh tokens.
    *   `/api/token/refresh/`: Refresh expired access tokens.
*   **Browsable API:** Interactive API documentation and testing interface provided by DRF.

### Chatbot
*   **Interactive Chat Interface:** Engage with an AI assistant.
*   **Chatbot API:** Endpoints for sending messages, retrieving history, and potentially integrating other features like resume analysis.
*   **Conversation Management:** View history and clear conversations.

## Technologies Used

*   **Backend:** Python, Django, Django REST Framework
*   **Database:** Configured for SQLite by default, with support for PostgreSQL (requires `psycopg2-binary`).
*   **Authentication:** Django Allauth (for social login), django-rest-framework-simplejwt (for API JWT)
*   **AI/ML:** OpenAI API, LangChain, PyPDF2, langdetect
*   **Frontend:** Django Templates, HTML, CSS, JavaScript
*   **API:** Django REST Framework, django-filter
*   **Environment Management:** python-dotenv
*   **File/Image Handling:** Pillow, python-magic (likely for resume type detection)
*   **Other:** Markdown-it-py, Cryptography

## Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   `virtualenv` (Recommended for isolating project dependencies)
*   PostgreSQL (Optional, if you choose to use it instead of the default SQLite)
*   An OpenAI API Key (for CV analysis and chatbot features)

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and fill in the required values:
        *   `SECRET_KEY`: **Required.** Generate a strong secret key (e.g., using Django's `get_random_secret_key()` or an online generator).
        *   `DEBUG`: Set to `True` for development, `False` for production.
        *   `DATABASE_URL`: (Optional) If using PostgreSQL, set the URL (e.g., `postgres://user:password@host:port/dbname`). Defaults to `db.sqlite3` if empty.
        *   `OPENAI_API_KEY`: **Required** for AI features. Your API key from OpenAI.
        *   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: (Optional) For Google social login. Get these from the Google Cloud Console.
        *   `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames (e.g., `127.0.0.1,localhost`). Important for deployment.
        *   Refer to `settings.py` and `.env.example` for other potential variables.

5.  **Run Database Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an administrator account.

7.  **Collect Static Files (Required for production, recommended for development):**
    ```bash
    python manage.py collectstatic --noinput
    ```

## Running the Application

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```

2.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000/`.
    *   Admin Interface: `http://127.0.0.1:8000/admin/`

## Environment Variables (`.env`)

The `.env` file is crucial for managing configuration secrets and settings outside of version control.

*   `SECRET_KEY`: **Critical for security.** Keep this value private and unique for your deployment.
*   `DEBUG`: Enables/disables detailed error pages and other development features. **Must be `False` in production.**
*   `DATABASE_URL`: Defines the connection to your database.
*   `OPENAI_API_KEY`: Enables CV analysis and chatbot functionalities.
*   `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`: Credentials for Google OAuth2 integration.
*   `ALLOWED_HOSTS`: Security measure to prevent HTTP Host header attacks. List all domains/IPs that should serve your application.

Refer to `.env.example` for a comprehensive template.

## API Usage

The REST API allows programmatic interaction with the application's core resources (Users, Jobs, Applications).
*   Authentication is typically done by obtaining a JWT token pair from `/api/token/` using user credentials.
*   Include the obtained access token in the `Authorization` header of subsequent API requests as a Bearer token: `Authorization: Bearer <your_access_token>`.
*   Explore the browsable API (usually available at `/api/` or `/api/auth/login/` when `DEBUG=True`) for endpoint details and testing.

## Utility Scripts

The project includes several utility scripts (e.g., `cv_analyzer.py`, `reset_jobs.py`, `check_jobs.py`, `list_accounts.py`, `list_jobs.py`). Examine these scripts directly to understand their specific functions, which might include data processing, background tasks, or administrative actions.
