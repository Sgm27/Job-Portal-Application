# ...existing code...

from flask import request, jsonify, redirect
import os
from werkzeug.utils import secure_filename
import requests

# ...existing code...

@app.route('/analyze-cv', methods=['POST'])
def analyze_cv():
    """
    Legacy route - forwards requests to the Django endpoint
    This is kept for backward compatibility
    """
    try:
        # Forward the request to Django endpoint
        django_url = request.host_url.rstrip('/') + '/chatbot/api/analyze-resume/'
        
        if request.is_json:
            # Forward JSON data
            response = requests.post(
                django_url,
                json=request.json,
                headers={k: v for k, v in request.headers if k.lower() != 'host'}
            )
        else:
            # Forward form data
            files = {}
            if request.files and 'cv_file' in request.files:
                files['cv_file'] = request.files['cv_file']
                
            response = requests.post(
                django_url,
                data=request.form,
                files=files,
                headers={k: v for k, v in request.headers if k.lower() != 'host'}
            )
        
        # Return the Django response
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        # Log the error
        app.logger.error(f"Error forwarding CV analysis request: {str(e)}")
        return jsonify({'error': str(e), 'message': 'Có lỗi xảy ra khi chuyển tiếp yêu cầu'}), 500

# ...existing code...
