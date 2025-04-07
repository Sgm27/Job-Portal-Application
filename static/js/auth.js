// Authentication related JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Form validation for registration
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        // Add input validations with real-time feedback
        const formFields = registerForm.querySelectorAll('input');
        formFields.forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });
        });

        registerForm.addEventListener('submit', function(e) {
            const password1 = document.getElementById('id_password1');
            const password2 = document.getElementById('id_password2');
            const username = document.getElementById('id_username');
            const email = document.getElementById('id_email');
            
            // Validate all fields before submission
            let isValid = true;
            
            // Validate username
            if (username && username.value.length < 4) {
                e.preventDefault();
                showError(username, 'Username must be at least 4 characters long.');
                isValid = false;
            }
            
            // Validate email
            if (email && !validateEmail(email.value)) {
                e.preventDefault();
                showError(email, 'Please enter a valid email address.');
                isValid = false;
            }
            
            // Validate password match
            if (password1 && password2 && password1.value !== password2.value) {
                e.preventDefault();
                showError(password2, 'Passwords do not match.');
                isValid = false;
            }
            
            // Validate password length (simplified - only 8+ characters needed)
            if (password1 && password1.value.length < 8) {
                e.preventDefault();
                showError(password1, 'Password must be at least 8 characters long.');
                isValid = false;
            }
            
            return isValid;
        });
        
        // Add user type toggle UI enhancement
        const userTypeField = document.getElementById('id_user_type');
        if (userTypeField && userTypeField.tagName === 'SELECT') {
            const container = document.createElement('div');
            container.className = 'btn-group w-100 mb-3';
            container.setAttribute('role', 'group');
            
            const employerBtn = document.createElement('button');
            employerBtn.type = 'button';
            employerBtn.className = 'btn btn-outline-primary';
            employerBtn.textContent = 'Employer';
            employerBtn.addEventListener('click', () => {
                userTypeField.value = 'employer';
                updateActiveButton();
            });
            
            const jobSeekerBtn = document.createElement('button');
            jobSeekerBtn.type = 'button';
            jobSeekerBtn.className = 'btn btn-outline-primary';
            jobSeekerBtn.textContent = 'Job Seeker';
            jobSeekerBtn.addEventListener('click', () => {
                userTypeField.value = 'job_seeker';
                updateActiveButton();
            });
            
            container.appendChild(employerBtn);
            container.appendChild(jobSeekerBtn);
            
            userTypeField.parentNode.insertBefore(container, userTypeField);
            userTypeField.style.display = 'none';
            
            function updateActiveButton() {
                if (userTypeField.value === 'employer') {
                    employerBtn.classList.add('active');
                    jobSeekerBtn.classList.remove('active');
                } else {
                    jobSeekerBtn.classList.add('active');
                    employerBtn.classList.remove('active');
                }
            }
            
            // Initial state
            updateActiveButton();
        }
        
        // Add password strength meter
        const password1 = document.getElementById('id_password1');
        if (password1) {
            const strengthMeter = document.createElement('div');
            strengthMeter.className = 'progress mt-2';
            strengthMeter.style.height = '5px';
            
            const strengthBar = document.createElement('div');
            strengthBar.className = 'progress-bar';
            strengthBar.style.width = '0%';
            strengthBar.setAttribute('role', 'progressbar');
            
            strengthMeter.appendChild(strengthBar);
            password1.parentNode.insertBefore(strengthMeter, password1.nextSibling);
            
            password1.addEventListener('input', function() {
                updatePasswordStrength(this.value, strengthBar);
            });
        }
    }

    // Form validation for login
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('id_username');
            const password = document.getElementById('id_password');
            
            if (username && username.value.trim() === '') {
                e.preventDefault();
                showError(username, 'Please enter your username or email.');
                return false;
            }
            
            if (password && password.value.trim() === '') {
                e.preventDefault();
                showError(password, 'Please enter your password.');
                return false;
            }
        });
        
        // Add "remember me" checkbox
        const submitButton = loginForm.querySelector('button[type="submit"]');
        if (submitButton) {
            const rememberMeDiv = document.createElement('div');
            rememberMeDiv.className = 'form-check mb-3';
            
            const rememberMeInput = document.createElement('input');
            rememberMeInput.className = 'form-check-input';
            rememberMeInput.type = 'checkbox';
            rememberMeInput.id = 'rememberMe';
            rememberMeInput.name = 'remember_me';
            
            const rememberMeLabel = document.createElement('label');
            rememberMeLabel.className = 'form-check-label';
            rememberMeLabel.htmlFor = 'rememberMe';
            rememberMeLabel.textContent = 'Remember me';
            
            rememberMeDiv.appendChild(rememberMeInput);
            rememberMeDiv.appendChild(rememberMeLabel);
            
            submitButton.parentNode.insertBefore(rememberMeDiv, submitButton);
        }
    }

    // Helper functions
    function showError(input, message) {
        // Remove existing error message if any
        const existingError = input.nextElementSibling;
        if (existingError && existingError.classList.contains('text-danger')) {
            existingError.remove();
        }
        
        input.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-danger';
        errorDiv.textContent = message;
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
        
        // Focus the input
        input.focus();
    }

    function validateEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    function isStrongPassword(password) {
        // Simplified - just check if it's at least 8 characters
        return password.length >= 8;
    }
    
    function validateField(field) {
        // Clear previous errors
        const existingError = field.nextElementSibling;
        if (existingError && existingError.classList.contains('text-danger')) {
            existingError.remove();
        }
        field.classList.remove('is-invalid');
        
        // Validate based on field type
        if (field.name === 'username' && field.value.length < 4 && field.value.length > 0) {
            showError(field, 'Username must be at least 4 characters long.');
        } else if (field.name === 'email' && field.value && !validateEmail(field.value)) {
            showError(field, 'Please enter a valid email address.');
        } else if (field.name === 'password1' && field.value && field.value.length < 8) {
            showError(field, 'Password must be at least 8 characters long.');
        } else if (field.name === 'password2') {
            const password1 = document.getElementById('id_password1');
            if (password1 && field.value && password1.value !== field.value) {
                showError(field, 'Passwords do not match.');
            }
        }
    }
    
    function updatePasswordStrength(password, strengthBar) {
        // Simplified strength calculation - only based on length
        let strength = 0;
        if (password.length >= 8) strength = 100; // Full strength if 8+ characters
        else if (password.length > 0) strength = (password.length / 8) * 100; // Partial strength based on length
        
        // Update the strength bar
        strengthBar.style.width = strength + '%';
        
        // Update color based on strength
        if (strength < 50) {
            strengthBar.className = 'progress-bar bg-danger';
        } else if (strength < 75) {
            strengthBar.className = 'progress-bar bg-warning';
        } else {
            strengthBar.className = 'progress-bar bg-success';
        }
    }
});
