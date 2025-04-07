# ...existing code...

import os

# ...existing code...

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define UPLOAD_FOLDER as a module-level variable that can be imported elsewhere
# This replaces the Flask-style app.config approach which was causing errors

# ...existing code...
