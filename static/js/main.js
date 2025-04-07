/**
 * Main JavaScript file for JobBoard
 * Version: 3.1.5
 */

// CRITICAL HOME PAGE HANDLER - Check immediately
(function() {
    // Check if we're on home page
    const isHomePage = window.location.pathname === '/' || 
                       window.location.pathname === '/home/' || 
                       window.location.pathname === '/index.html';
    
    if (isHomePage) {
        console.log('Home page mode - disabling animations and multiple loading');
        
        // Set global flag immediately
        window.homePageFullyInitialized = true;
        
        // Apply critical styling immediately
        document.documentElement.style.opacity = "1";
        document.documentElement.style.visibility = "visible";
        document.body.style.opacity = "1";
        document.body.style.visibility = "visible";
    }
})();

// Main JavaScript file for common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any Bootstrap components
    initializeBootstrapComponents();
    
    // Handle flash messages/alerts
    setupAlertDismissal();
    
    // Set up navbar active states
    setActiveNavItem();
    
    // Add responsive behavior for navigation
    setupResponsiveNavigation();
    
    // Initialize any date/time pickers
    initializeDateTimePickers();
    
    // Fix modal backdrop issues
    fixModalBackdropIssue();
    
    // Enhanced UI features
    enhanceFormElements();
    
    // Only run heavy operations if in viewport 
    lazyLoadOperations();
    
    // Fix browser caching issues and back navigation
    fixBrowserCacheHandling();
});

// Initialize Bootstrap components that need JavaScript
function initializeBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize all popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
    
    // Initialize all toasts
    const toastElList = document.querySelectorAll('.toast');
    if (toastElList.length > 0) {
        [...toastElList].map(toastEl => new bootstrap.Toast(toastEl).show());
    }
}

// Fix modal backdrop issues permanently
function fixModalBackdropIssue() {
    // Add style rule to handle modal-backdrop
    const style = document.createElement('style');
    style.textContent = `
        body:not(.modal-open) .modal-backdrop {
            display: none !important;
        }
    `;
    document.head.appendChild(style);
    
    // Handle modal events properly
    document.addEventListener('show.bs.modal', function() {
        // Force check for existing backdrop and remove if any other modal is not open
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length === 0) {
            removeBackdrops();
        }
    }, true);
    
    document.addEventListener('hidden.bs.modal', function() {
        // Add a slight delay to ensure Bootstrap has completed its operations
        setTimeout(function() {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length === 0) {
                removeBackdrops();
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        }, 50);
    }, true);
    
    // Clean up function
    function removeBackdrops() {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            backdrop.parentNode.removeChild(backdrop);
        });
    }
    
    // Cleanup check every 2 seconds (less aggressive than before)
    const intervalCheck = setInterval(function() {
        const openModals = document.querySelectorAll('.modal.show');
        const backdrops = document.querySelectorAll('.modal-backdrop');
        
        if (openModals.length === 0 && backdrops.length > 0) {
            removeBackdrops();
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }
        
        // If page has been active for 30 seconds, stop the interval check
        // This prevents unnecessary checking indefinitely
        if (document.visibilityState === 'visible') {
            setTimeout(() => clearInterval(intervalCheck), 30000);
        }
    }, 2000);
}

// Set up proper handling of browser back/forward cache - improved for performance
function fixBrowserCacheHandling() {
    // When user navigates back
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Page was loaded from cache
            
            // Instead of reloading the entire page, only update dynamic content if needed
            const jobList = document.querySelector('.job-list');
            if (jobList && jobList.children.length === 0) {
                // Only reload if job list should have content but is empty
                refreshJobList();
            }
            
            // Reset any forms that need resetting
            document.querySelectorAll('form').forEach(form => {
                if (!form.classList.contains('no-reset')) {
                    form.reset();
                }
            });
        }
    });
    
    // Check visibility changes for potential cache restoration
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            // Only perform targeted updates if needed, not full page reload
            const jobList = document.querySelector('.job-list');
            if (jobList && jobList.children.length === 0) {
                refreshJobList();
            }
        }
    });
}

// Function to refresh just the job list content without reloading the whole page
function refreshJobList() {
    // Check if we're on a page with job listings
    const jobListContainer = document.querySelector('.job-list');
    if (!jobListContainer) return;
    
    // Show a loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'text-center p-3';
    loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    jobListContainer.appendChild(loadingIndicator);
    
    // Get the current URL
    const currentUrl = window.location.href;
    
    // Fetch only the job list content
    fetch(currentUrl, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-Refresh-Jobs-Only': 'true'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Create a temporary element to parse the HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Extract the job list content
        const newJobList = tempDiv.querySelector('.job-list');
        
        if (newJobList) {
            // Replace the current job list with the new one
            jobListContainer.innerHTML = newJobList.innerHTML;
            
            // Re-initialize any event handlers or animations on job cards
            setupCardAnimations();
        } else {
            // If we couldn't find the job list in the response, fall back to reload
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error refreshing job list:', error);
        // Remove loading indicator on error
        if (loadingIndicator.parentNode) {
            loadingIndicator.parentNode.removeChild(loadingIndicator);
        }
    });
}

// Auto-dismiss alerts after 5 seconds with improved animation
function setupAlertDismissal() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            } else {
                smoothFadeOut(alert);
            }
        }, 5000);
    });
}

// Set active nav item based on current URL
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Setup responsive navigation with enhanced animations
function setupResponsiveNavigation() {
    const navbar = document.querySelector('.navbar-collapse');
    const navToggler = document.querySelector('.navbar-toggler');
    
    if (navbar && navToggler) {
        // Add smooth animation to navbar toggle
        navToggler.addEventListener('click', function() {
            if (!navbar.classList.contains('show')) {
                // Opening: Animate nav items one by one
                setTimeout(() => {
                    const navItems = navbar.querySelectorAll('.nav-item');
                    navItems.forEach((item, index) => {
                        item.style.opacity = '0';
                        item.style.transform = 'translateY(20px)';
                        item.style.transition = `all 0.3s ease ${index * 0.05}s`;
                        
                        setTimeout(() => {
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        }, 50);
                    });
                }, 100);
            }
        });
        
        // Close navbar when clicking outside
        document.addEventListener('click', function(e) {
            if (navbar.classList.contains('show') && 
                !navbar.contains(e.target) && 
                !navToggler.contains(e.target)) {
                navToggler.click();
            }
        });
        
        // Close navbar when a nav-link is clicked (on mobile)
        const navLinks = navbar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992 && navbar.classList.contains('show')) {
                    navToggler.click();
                }
            });
        });
    }
}

// Initialize datetime pickers with improved UI
function initializeDateTimePickers() {
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    if (dateTimeInputs.length > 0) {
        dateTimeInputs.forEach(input => {
            // Add focus animation
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
            
            if (!input.value) {
                // Set default value to current datetime + 7 days (common for job deadlines)
                const now = new Date();
                now.setDate(now.getDate() + 7);
                
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                
                input.value = `${year}-${month}-${day}T${hours}:${minutes}`;
            }
        });
    }
}

// Helper function for smooth fade out animation
function smoothFadeOut(element) {
    element.style.transition = 'opacity 0.5s ease, transform 0.5s ease, max-height 0.5s ease, margin 0.5s ease, padding 0.5s ease';
    element.style.opacity = '0';
    element.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
        element.style.maxHeight = '0';
        element.style.margin = '0';
        element.style.padding = '0';
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    }, 500);
}

// Lazily apply enhanced form elements and effects
function lazyLoadOperations() {
    // Only apply these operations if the user is actually interacting with the page
    // This improves initial page load performance
    const lazyOperationsStarted = sessionStorage.getItem('lazyOperationsStarted');
    
    if (!lazyOperationsStarted) {
        setTimeout(() => {
            enhanceFormElements();
            setupLazyLoading();
            addSmoothScrolling();
            setupCardAnimations();
            enhanceDropdowns();
            optimizeImageLoading();
            
            // Only setup parallax on larger screens
            if (window.innerWidth >= 992) {
                setupParallaxEffects();
            }
            
            sessionStorage.setItem('lazyOperationsStarted', 'true');
        }, 100); // Wait for initial render to complete
    } else {
        // On subsequent page loads, run immediately but in the background
        setTimeout(() => {
            enhanceFormElements();
            setupLazyLoading();
            addSmoothScrolling();
            setupCardAnimations();
            enhanceDropdowns();
            optimizeImageLoading();
            
            // Only setup parallax on larger screens
            if (window.innerWidth >= 992) {
                setupParallaxEffects();
            }
        }, 0);
    }
}

// Apply enhanced animations and interactivity to form elements
function enhanceFormElements() {
    // Add floating label effect to inputs
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(input => {
        // Add focus animation
        input.addEventListener('focus', function() {
            this.classList.add('focused');
            // Add highlight to parent form-group if it exists
            const formGroup = this.closest('.form-group, .mb-3');
            if (formGroup) {
                formGroup.classList.add('focused');
            }
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('focused');
            // Remove highlight from parent form-group
            const formGroup = this.closest('.form-group, .mb-3');
            if (formGroup) {
                formGroup.classList.remove('focused');
            }
        });
    });
    
    // Enhance buttons with feedback on click - prioritize only buttons in view
    const buttons = document.querySelectorAll('.btn:not([type="submit"])');
    buttons.forEach(button => {
        if (isElementInViewport(button)) {
            button.addEventListener('click', function(e) {
                // Create ripple effect
                const ripple = document.createElement('span');
                ripple.classList.add('btn-ripple');
                this.appendChild(ripple);
                
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                ripple.style.left = `${x}px`;
                ripple.style.top = `${y}px`;
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        }
    });
}

// Set up lazy loading for images and content
function setupLazyLoading() {
    // Check if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        const imgObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.src = src;
                        img.classList.add('img-smooth-load');
                        
                        img.onload = function() {
                            img.classList.add('loaded');
                            // Remove the data-src to avoid loading the image again
                            img.removeAttribute('data-src');
                        };
                        
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });
        
        // Target all images with data-src attribute
        document.querySelectorAll('img[data-src]').forEach(img => {
            imgObserver.observe(img);
        });
        
        // Also setup animation for elements with fade-in-up class
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    animationObserver.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '0px',
            threshold: 0.1
        });
        
        document.querySelectorAll('.fade-in-up').forEach(element => {
            animationObserver.observe(element);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
        });
        
        document.querySelectorAll('.fade-in-up').forEach(element => {
            element.classList.add('visible');
        });
    }
}

// Add smooth scrolling to anchor links
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Calculate header height for offset
                const headerHeight = document.querySelector('header').offsetHeight + 20;
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL hash after scrolling
                history.pushState(null, null, targetId);
            }
        });
    });
}

// Setup card animations and hover effects - optimized for performance
function setupCardAnimations() {
    // Add stagger-item class only to visible cards to avoid performance issues
    document.querySelectorAll('.card:not(.stagger-item):not(.card-appear)').forEach((card, index) => {
        // Only apply to cards in the viewport for better performance
        if (isElementInViewport(card)) {
            card.classList.add('stagger-item');
            card.classList.add(`stagger-delay-${(index % 3) + 1}`);
            
            // Mark as loaded after a short delay to trigger animation
            setTimeout(() => {
                card.classList.add('loaded');
            }, 50 * (index % 3));
        } else {
            // Skip animation for off-screen elements
            card.classList.add('loaded');
        }
    });
    
    // Add hover animations only when observed
    if ('IntersectionObserver' in window) {
        const hoverObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const card = entry.target;
                    
                    // Add hover animation handlers
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-5px)';
                        this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '';
                    });
                    
                    hoverObserver.unobserve(card);
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });
        
        // Only observe cards that should have hover effects
        document.querySelectorAll('.job-list .card, .card-hover').forEach(card => {
            hoverObserver.observe(card);
        });
    }
}

// Enhance dropdowns with smooth animations and better mobile support
function enhanceDropdowns() {
    // Instead of managing the dropdown show/hide manually, we'll just add animation effects
    // and let Bootstrap handle the actual dropdown functionality
    document.querySelectorAll('.dropdown-menu').forEach(dropdown => {
        // Add transition styles
        dropdown.style.transition = 'transform 0.2s ease, opacity 0.2s ease';
        
        // Find the parent dropdown container
        const dropdownContainer = dropdown.closest('.dropdown');
        if (!dropdownContainer) return;
        
        // Get the toggle element
        const toggle = dropdownContainer.querySelector('.dropdown-toggle');
        if (!toggle) return;
        
        // Add event listeners to enhance the Bootstrap dropdown
        toggle.addEventListener('show.bs.dropdown', () => {
            dropdown.style.transform = 'translateY(10px)';
            dropdown.style.opacity = '0';
            
            setTimeout(() => {
                dropdown.style.transform = 'translateY(0)';
                dropdown.style.opacity = '1';
            }, 0);
        });
        
        toggle.addEventListener('hide.bs.dropdown', () => {
            dropdown.style.transform = 'translateY(10px)';
            dropdown.style.opacity = '0';
            
            // Don't interfere with Bootstrap's hide mechanism
            // The delay was causing issues
        });
    });
}

// Optimize image loading for better performance
function optimizeImageLoading() {
    // Add loading="lazy" attribute to all images that don't have it
    document.querySelectorAll('img:not([loading])').forEach(img => {
        img.setAttribute('loading', 'lazy');
    });
    
    // Add fade-in effect to all images
    document.querySelectorAll('img').forEach(img => {
        if (!img.complete) {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.5s ease';
            
            img.addEventListener('load', function() {
                this.style.opacity = '1';
            });
        }
    });
}

// Setup parallax effects for applicable sections
function setupParallaxEffects() {
    // Only apply on larger screens to avoid performance issues on mobile
    const parallaxSections = document.querySelectorAll('.profile-header, .jumbotron, [data-parallax="true"]');
    
    if (parallaxSections.length > 0) {
        const parallaxHandler = throttle(() => {
            const scrolled = window.pageYOffset;
            
            parallaxSections.forEach(section => {
                // Only apply parallax if element is in viewport
                const rect = section.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    const rate = scrolled * 0.3;
                    section.style.backgroundPosition = `center ${-rate}px`;
                }
            });
        }, 20); // Throttle to 20ms for smoother performance
        
        window.addEventListener('scroll', parallaxHandler);
    }
}

// Helper function: Is element in viewport?
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Helper function: Throttle function for performance optimization
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
