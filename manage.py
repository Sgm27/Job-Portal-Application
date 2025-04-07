#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc

    # Create necessary directories for static and media files
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(BASE_DIR, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'img'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'media', 'profile_pics'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'media', 'resumes'), exist_ok=True)

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
