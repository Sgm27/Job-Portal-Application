# Job Portal Application

A comprehensive web application built with Django designed to connect job seekers with employers. This platform features job listings, user management with social login options, application tracking, CV analysis powered by AI, and an integrated chatbot.

## Features

*   **User Authentication:** Secure registration and login for candidates and employers using Django Allauth. Supports email/username login and Google social login.
*   **Job Management:** Employers can post, edit, and manage job listings.
*   **Job Search & Filtering:** Candidates can search for jobs using various filters (keywords, location, type, etc.).
*   **User Profiles:** Dedicated profiles for both candidates and employers.
*   **CV Upload & AI Analysis:** Candidates can upload their CVs (PDF, DOC, DOCX). The system utilizes OpenAI and LangChain for intelligent CV parsing and analysis.
*   **Application Tracking:** Candidates can apply for jobs, and employers can manage applications received.
*   **REST API:** Provides API endpoints built with Django REST Framework and secured with JWT for potential integrations or frontend frameworks.
*   **Chatbot Integration:** Includes a chatbot feature to assist users.
*   **Admin Panel:** Django's built-in admin interface for site administration.

## Technologies Used

*   **Backend:** Python, Django, Django REST Framework
*   **Database:** Configured for SQLite by default, with support for PostgreSQL (requires `psycopg2-binary`).
*   **Authentication:** Django Allauth, django-rest-framework-simplejwt
*   **AI/ML:** OpenAI API, LangChain, PyPDF2, langdetect
*   **Frontend:** Django Templates, HTML, CSS, JavaScript
*   **API:** Django REST Framework, django-filter
*   **Environment Management:** python-dotenv
*   **Image Handling:** Pillow
*   **Other:** Markdown-it-py, Cryptography

## Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   `virtualenv` (Recommended for isolating project dependencies)
*   PostgreSQL (Optional, if you choose to use it instead of the default SQLite)

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
        *   `SECRET_KEY`: Generate a strong secret key.
        *   `DEBUG`: Set to `True` for development, `False` for production.
        *   `DATABASE_URL`: (Optional) If using PostgreSQL, set the URL (e.g., `postgres://user:password@host:port/dbname`). Otherwise, the project defaults to `db.sqlite3`.
        *   `OPENAI_API_KEY`: Your API key from OpenAI for CV analysis and chatbot features.
        *   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: (Optional) If you want to enable Google social login, get these from the Google Cloud Console.
        *   Other variables as needed.

5.  **Run Database Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an administrator account.

7.  **Collect Static Files (Recommended for Production):**
    ```bash
    python manage.py collectstatic
    ```

## Running the Application

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```

2.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000/`.

## Environment Variables (`.env`)

The `.env` file is used to manage sensitive configuration and API keys. Key variables include:

*   `SECRET_KEY`: Crucial for security. Keep it secret!
*   `DEBUG`: Controls Django's debug mode.
*   `DATABASE_URL`: Specifies the database connection (defaults to SQLite if not set).
*   `OPENAI_API_KEY`: Required for AI features.
*   `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`: For Google login integration.
*   `ALLOWED_HOSTS`: Specify allowed hostnames (important for deployment).

Refer to `.env.example` for a full list of potential variables.

## API Endpoints

The application includes RESTful API endpoints managed by Django REST Framework. Authentication is handled via JWT. Refer to the `api/urls.py` file or relevant documentation (if available) for specific endpoint details.

## Utility Scripts

The project contains several utility scripts in the root directory and `utils/` or `jobs/` folders (e.g., `cv_analyzer.py`, `reset_jobs.py`). These scripts likely perform specific tasks like data processing, analysis, or maintenance. Explore their code for detailed functionality.
