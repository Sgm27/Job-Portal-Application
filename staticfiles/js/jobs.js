// Jobs related JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Prevent duplicate initialization
    if (window.jobsJsInitialized) return;
    window.jobsJsInitialized = true;
    
    console.log('Jobs.js loaded and initialized once');
    
    // Job search form enhancement
    const searchForm = document.querySelector('form[action*="job_list"]');
    if (searchForm) {
        // Check if there's already a clear filters button with ID clearFiltersButton
        const existingClearButton = document.getElementById('clearFiltersButton');
        
        // Only create a new clear filter button if one doesn't already exist
        if (!existingClearButton) {
            // Add clear filter functionality
            const clearFiltersBtn = document.createElement('button');
            clearFiltersBtn.type = 'button';
            clearFiltersBtn.className = 'btn btn-outline-secondary w-100 mt-2';
            clearFiltersBtn.textContent = 'Clear Filters';
            clearFiltersBtn.addEventListener('click', function() {
                // Reset all form fields
                const formInputs = searchForm.querySelectorAll('input, select');
                formInputs.forEach(input => {
                    if (input.type === 'text' || input.tagName === 'SELECT') {
                        input.value = '';
                    }
                });
                // Thêm loading indicator
                showSearchingIndicator();
                // Submit form after clearing
                searchForm.submit();
            });

            const submitButton = searchForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.parentNode.insertBefore(clearFiltersBtn, submitButton.nextSibling);
            }
        }
        
        // Add search functionality while typing (with improved debounce)
        const searchInput = searchForm.querySelector('input[name="search"]');
        if (searchInput) {
            let debounceTimer;
            searchInput.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                // Only enable auto-submit if the feature flag is on
                const autoSubmitEnabled = searchForm.dataset.autoSubmit === 'true';
                
                if (autoSubmitEnabled) {
                    const searchingIndicator = document.getElementById('searchingIndicator');
                    if (this.value.length >= 3) {
                        // Show "đang tìm kiếm..." text
                        if (!searchingIndicator) {
                            showSearchingIndicator();
                        }
                    }
                    
                    debounceTimer = setTimeout(() => {
                        if (this.value.length >= 3 || this.value.length === 0) {
                            searchForm.submit();
                        }
                    }, 800);
                }
            });
        }
        
        // Add form submit handler to show loading state
        searchForm.addEventListener('submit', function() {
            showSearchingIndicator();
        });
    }
    
    // Show loading/searching indicator
    function showSearchingIndicator() {
        const jobListContainer = document.querySelector('.job-list-container');
        if (!jobListContainer) return;
        
        const existingIndicator = document.getElementById('searchingIndicator');
        if (!existingIndicator) {
            const loadingIndicator = document.createElement('div');
            loadingIndicator.id = 'searchingIndicator';
            loadingIndicator.className = 'text-center py-4';
            loadingIndicator.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tìm kiếm...</span>
                </div>
                <p class="mt-2">Đang tìm kiếm...</p>
            `;
            
            // Add fade effect
            jobListContainer.style.opacity = '0.6';
            jobListContainer.style.transition = 'opacity 0.3s ease';
            
            // Insert before the job list
            jobListContainer.parentNode.insertBefore(loadingIndicator, jobListContainer);
        }
    }
    
    // Lazy loading job images for better performance
    const lazyImages = document.querySelectorAll('img[data-src]');
    if (lazyImages.length > 0) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Immediately make all job cards visible first as a fallback
    const jobCards = document.querySelectorAll('.card-animated');
    
    if (jobCards.length > 0) {
        // Apply initial visibility to all cards as a failsafe
        jobCards.forEach((card, index) => {
            // Make them visible with a slight delay for a staggered effect
            setTimeout(() => {
                card.classList.add('card-visible');
            }, index * 50);
        });
        
        // Then use IntersectionObserver for a more refined animation if supported
        if ('IntersectionObserver' in window) {
            const cardObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('card-visible');
                        cardObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '50px'
            });
            
            jobCards.forEach(card => {
                // Stagger the animation delay based on index
                cardObserver.observe(card);
            });
        }
    }
    
    // Job card hover effects
    jobCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)';
        });
    });
    
    // Job application form validation
    const applicationForm = document.querySelector('form[action*="apply"]');
    if (applicationForm) {
        applicationForm.addEventListener('submit', function(e) {
            const coverLetterField = document.getElementById('id_cover_letter');
            
            // Validate cover letter length
            if (coverLetterField && coverLetterField.value.trim().length < 100) {
                e.preventDefault();
                
                // Create error message if it doesn't exist
                let errorMessage = coverLetterField.nextElementSibling;
                if (!errorMessage || !errorMessage.classList.contains('text-danger')) {
                    errorMessage = document.createElement('div');
                    errorMessage.className = 'text-danger mt-1';
                    coverLetterField.parentNode.insertBefore(errorMessage, coverLetterField.nextSibling);
                }
                
                errorMessage.textContent = 'Thư giới thiệu của bạn cần có ít nhất 100 ký tự.';
                coverLetterField.focus();
                return false;
            }
        });
    }
    
    // Share job functionality 
    const shareButtons = document.querySelectorAll('.social-share');
    if (shareButtons.length > 0) {
        shareButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const platform = this.classList.contains('facebook') ? 'facebook' :
                                this.classList.contains('twitter') ? 'twitter' :
                                this.classList.contains('linkedin') ? 'linkedin' : '';
                
                if (platform && typeof shareJob === 'function') {
                    shareJob(platform);
                }
            });
        });
    }
    
    // Save job functionality
    const saveButtons = document.querySelectorAll('.btn-outline-primary .bi-bookmark, .btn-outline-primary.bookmark-btn');
    if (saveButtons.length > 0) {
        saveButtons.forEach(button => {
            const parentButton = button.tagName === 'BUTTON' ? button : button.closest('button') || button.parentElement;
            
            parentButton.addEventListener('click', function(e) {
                e.preventDefault();
                const jobId = this.dataset.jobId;
                if (!jobId) return;
                
                // Toggle visual state immediately for better UX
                const iconElement = this.querySelector('.bi-bookmark, .bi-bookmark-fill') || this;
                const textSpan = this.querySelector('span') || document.createElement('span');
                
                if (iconElement.classList.contains('bi-bookmark')) {
                    iconElement.classList.replace('bi-bookmark', 'bi-bookmark-fill');
                    textSpan.textContent = ' Saved';
                } else {
                    iconElement.classList.replace('bi-bookmark-fill', 'bi-bookmark');
                    textSpan.textContent = ' Save Job';
                }
                
                // Here you would typically make an AJAX call to save/unsave the job
                // For demonstration, we're just showing a toast notification
                showToast(iconElement.classList.contains('bi-bookmark-fill') ? 
                    'Đã lưu công việc thành công!' : 'Đã xóa công việc khỏi danh sách đã lưu');
            });
        });
    }
    
    // Toast notification function
    function showToast(message) {
        // Remove existing toast if present
        const existingToast = document.querySelector('.toast-notification');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Create new toast
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <div class="toast-content">
                <i class="bi bi-check-circle-fill me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
