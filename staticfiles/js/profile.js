// Profile related JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Profile picture preview functionality
    const profilePictureInput = document.getElementById('id_profile_picture');
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const profileImage = document.querySelector('.rounded-circle');
                    if (profileImage) {
                        profileImage.src = e.target.result;
                    } else {
                        // Create a new image if it doesn't exist
                        const newImage = document.createElement('img');
                        newImage.src = e.target.result;
                        newImage.className = 'rounded-circle img-fluid mb-3';
                        newImage.style.maxWidth = '150px';
                        
                        const containerDiv = profilePictureInput.closest('.form-group');
                        if (containerDiv) {
                            containerDiv.insertBefore(newImage, profilePictureInput);
                        }
                    }
                };
                reader.readAsDataURL(this.files[0]);
                
                // Validate image size
                validateFileSize(this.files[0], 2); // 2MB
            }
        });
    }

    // Resume file validation
    const resumeInput = document.getElementById('id_resume');
    if (resumeInput) {
        resumeInput.addEventListener('change', function() {
            const allowedExtensions = /(\.pdf|\.doc|\.docx)$/i;
            
            if (!allowedExtensions.exec(this.value)) {
                showFileError(this, 'Please upload file having extensions .pdf, .doc or .docx only.');
                this.value = '';
                return false;
            }
            
            // Validate file size (5MB)
            if (this.files[0] && !validateFileSize(this.files[0], 5)) {
                this.value = '';
                return false;
            }
            
            // Show success message
            const existingMessage = this.nextElementSibling;
            if (existingMessage && existingMessage.classList.contains('text-success')) {
                existingMessage.remove();
            }
            
            const successMsg = document.createElement('div');
            successMsg.className = 'text-success mt-2';
            successMsg.textContent = 'Resume file is valid and ready to upload.';
            this.parentNode.insertBefore(successMsg, this.nextSibling);
        });
    }

    // Form validation with improved error handling
    const profileForm = document.querySelector('form');
    if (profileForm) {
        // Add validation to individual fields on blur
        const emailInput = document.getElementById('id_email');
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                validateEmail(this);
            });
        }
        
        const phoneInput = document.getElementById('id_phone_number');
        if (phoneInput) {
            phoneInput.addEventListener('blur', function() {
                validatePhone(this);
            });
        }
        
        // Website validation for employers
        const websiteInput = document.getElementById('id_company_website');
        if (websiteInput) {
            websiteInput.addEventListener('blur', function() {
                validateWebsite(this);
            });
        }
        
        // Form submission validation
        profileForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            if (emailInput && !validateEmail(emailInput)) {
                isValid = false;
            }
            
            if (phoneInput && phoneInput.value && !validatePhone(phoneInput)) {
                isValid = false;
            }
            
            if (websiteInput && websiteInput.value && !validateWebsite(websiteInput)) {
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Helper functions
    function validateEmail(input) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        const isValid = re.test(String(input.value).toLowerCase());
        
        if (!isValid && input.value) {
            showInputError(input, 'Please enter a valid email address.');
            return false;
        } else {
            removeError(input);
            return true;
        }
    }

    function validatePhone(input) {
        const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
        const isValid = re.test(String(input.value));
        
        if (!isValid && input.value) {
            showInputError(input, 'Please enter a valid phone number.');
            return false;
        } else {
            removeError(input);
            return true;
        }
    }
    
    function validateWebsite(input) {
        try {
            new URL(input.value);
            removeError(input);
            return true;
        } catch (e) {
            if (input.value) {
                showInputError(input, 'Please enter a valid URL (e.g., https://example.com).');
                return false;
            }
            return true;
        }
    }
    
    function validateFileSize(file, maxSizeMB) {
        if (file.size > maxSizeMB * 1024 * 1024) {
            showFileError(file.input, `File size too large. Please upload a file less than ${maxSizeMB}MB.`);
            return false;
        }
        return true;
    }
    
    function showFileError(input, message) {
        // Remove existing messages
        removeError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-danger mt-2';
        errorDiv.textContent = message;
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
    }
    
    function showInputError(input, message) {
        // Remove existing error
        removeError(input);
        
        input.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
    }
    
    function removeError(input) {
        input.classList.remove('is-invalid');
        
        // Remove any existing error messages
        const nextSibling = input.nextElementSibling;
        if (nextSibling && (nextSibling.classList.contains('invalid-feedback') || 
                           nextSibling.classList.contains('text-danger'))) {
            nextSibling.remove();
        }
    }
});
