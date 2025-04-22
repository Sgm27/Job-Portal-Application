// Jobs related JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // CRITICAL HOME PAGE CHECK - Exit immediately if on home page
    const isHomePage = window.location.pathname === '/' || 
                      window.location.pathname === '/home/' || 
                      window.location.pathname === '/index.html';
    
    if (isHomePage && window.homePageFullyInitialized) {
        console.log('Jobs.js - Home page already initialized, skipping all animations');
        return;
    }
    
    // Prevent duplicate initialization by adding a flag to the window object
    if (window.jobsJsInitialized) {
        console.log('Jobs.js already initialized, skipping.');
        return;
    }
    window.jobsJsInitialized = true;
    
    console.log('Jobs.js loaded and initialized once');
    
    // Keep track of job cards to avoid duplicates
    window.loadedJobIds = window.loadedJobIds || new Set();
    
    // Remove any duplicate job cards that might exist
    removeDuplicateJobCards();
    
    // Check if we're on the home page
    if (isHomePage) {
        // Show all job cards immediately with no animations
        const jobCards = document.querySelectorAll('.job-card, .card');
        jobCards.forEach(card => {
            card.style.opacity = '1';
            card.style.transform = 'none';
            card.style.transition = 'none';
            card.classList.remove('card-animated');
        });
        
        // Exit early to prevent other animations
        return;
    }
    
    // Show all job cards immediately without animation on home page
    const jobCards = document.querySelectorAll('.job-card, .card');
    jobCards.forEach(card => {
        card.style.opacity = '1';
        card.style.transform = 'none';
        if (isHomePage) {
            card.style.transition = 'none';
            card.classList.remove('card-animated');
        }
    });
    
    // Job search form enhancement
    const searchForm = document.querySelector('form#jobSearchForm');
    if (searchForm) {
        console.log('Found search form:', searchForm);
        
        // Get the existing clear filters button
        const clearFiltersBtn = document.getElementById('clearFiltersButton');
        if (clearFiltersBtn) {
            console.log('Found clear filters button:', clearFiltersBtn);
            
            clearFiltersBtn.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent any default action
                console.log('Clear filters button clicked');
                
                // Reset all form fields
                const formInputs = searchForm.querySelectorAll('input, select, textarea');
                formInputs.forEach(input => {
                    console.log('Resetting field:', input.name || input.id);
                    if (input.type === 'text' || input.type === 'search' || input.type === 'hidden') {
                        input.value = '';
                    } else if (input.type === 'checkbox' || input.type === 'radio') {
                        input.checked = false;
                    } else if (input.tagName === 'SELECT') {
                        input.selectedIndex = 0; // Select first option
                    } else if (input.tagName === 'TEXTAREA') {
                        input.value = '';
                    }
                });
                
                // Add loading indicator
                showSearchingIndicator();
                
                // Instead of submitting the form, redirect to the base job list URL
                const jobListUrl = searchForm.getAttribute('action');
                console.log('Redirecting to base job list URL:', jobListUrl);
                window.location.href = jobListUrl;
            });
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
    setupLazyImageLoading();
    
    // Apply animations to job cards with optimizations
    optimizeJobCardDisplay();
    
    // Add job card hover effects
    addJobCardHoverEffects();
    
    // Fix for browser back button issues
    fixBrowserBackButton();
    
    // Job application form validation
    setupJobApplicationValidation();
    
    // Job sharing and saving functionality
    setupJobSharingAndSaving();
});

// Function to remove any duplicate job cards
function removeDuplicateJobCards() {
    const jobList = document.querySelector('.job-list');
    if (!jobList) return;
    
    // Find all job cards
    const jobCards = jobList.querySelectorAll('.card[data-job-id]');
    const processedIds = new Set();
    
    jobCards.forEach(card => {
        const jobId = card.getAttribute('data-job-id');
        if (jobId) {
            // If we've already seen this job ID or it's already in our global tracking
            if (processedIds.has(jobId) || window.loadedJobIds.has(jobId)) {
                console.log('Removing duplicate job card with ID:', jobId);
                card.parentNode.removeChild(card);
            } else {
                processedIds.add(jobId);
                window.loadedJobIds.add(jobId);
            }
        }
    });
}

// Setup lazy loading for images
function setupLazyImageLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    if (lazyImages.length === 0) return;
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    img.classList.add('img-loaded');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });
        
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// Optimize job card display and animations
function optimizeJobCardDisplay() {
    const jobCards = document.querySelectorAll('.card-animated');
    if (jobCards.length === 0) return;
    
    // First make all cards visible with minimal animation
    jobCards.forEach((card, index) => {
        // Use a small timeout to stagger appearance slightly without performance impact
        setTimeout(() => {
            card.classList.add('card-visible');
        }, Math.min(index * 30, 300)); // Cap maximum delay at 300ms
    });
    
    // Use IntersectionObserver for more refined animations if available
    if ('IntersectionObserver' in window) {
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('card-visible');
                    // Stop observing once animation is applied
                    cardObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        // Only observe cards that aren't already visible
        jobCards.forEach(card => {
            if (!card.classList.contains('card-visible')) {
                cardObserver.observe(card);
            }
        });
    }
}

// Add hover effects to job cards
function addJobCardHoverEffects() {
    const jobCards = document.querySelectorAll('.job-list .card, .card-hover');
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
}

// Fix for browser back button issues - improved for better performance
function fixBrowserBackButton() {
    // When user navigates using browser back/forward buttons
    window.addEventListener('pageshow', function(event) {
        // Page was restored from bfcache
        if (event.persisted) {
            console.log('Page loaded from back/forward cache, keeping state intact');
            
            // Check if we need to refresh any specific content
            const jobList = document.querySelector('.job-list');
            if (jobList && jobList.children.length === 0) {
                // Only refresh job list if it's empty
                if (typeof refreshJobList === 'function') {
                    refreshJobList();
                }
            }
            
            // Restore scroll position if needed
            if (sessionStorage.getItem('scrollPosition')) {
                window.scrollTo(0, sessionStorage.getItem('scrollPosition'));
                sessionStorage.removeItem('scrollPosition');
            }
        }
    });
    
    // Save scroll position before leaving page
    document.querySelectorAll('.job-card a, .job-title a').forEach(link => {
        link.addEventListener('click', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });
}

// Job application form validation
function setupJobApplicationValidation() {
    const applicationForm = document.querySelector('form[action*="apply"]');
    if (!applicationForm) return;
    
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

// Job sharing and saving functionality
function setupJobSharingAndSaving() {
    // Share job functionality 
    const shareButtons = document.querySelectorAll('.social-share');
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
    
    // Save job functionality
    const saveButtons = document.querySelectorAll('.btn-outline-primary .bi-bookmark, .btn-outline-primary.bookmark-btn');
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

// Function to share job on social media (implementation would depend on your requirements)
function shareJob(platform) {
    const currentUrl = window.location.href;
    const jobTitle = document.querySelector('h1, .job-title')?.textContent || 'Job Opening';
    
    let shareUrl;
    switch(platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentUrl)}&text=${encodeURIComponent(jobTitle)}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(currentUrl)}`;
            break;
    }
    
    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
        showToast(`Đã chia sẻ trên ${platform}`);
    }
}
