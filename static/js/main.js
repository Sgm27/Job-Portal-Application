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
        console.log('Home page mode - applying immediate optimizations');
        
        // Set global flag immediately
        window.homePageFullyInitialized = true;
        
        // CRITICAL FIX: Set document flag to prevent any animation initialization on home page
        document.documentElement.dataset.animationsDisabled = 'true';
        
        // Set styles in <head> before DOM is ready to prevent flash and disable ALL animations
        const style = document.createElement('style');
        style.setAttribute('data-critical', 'true');
        style.innerHTML = `
            /* Complete animation disabler for homepage */
            body.homepage-special * {
                animation: none !important;
                transition: none !important;
                opacity: 1 !important;
                transform: none !important;
                animation-duration: 0ms !important;
                animation-delay: 0ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0ms !important;
            }
            
            /* Ensure all page transitions are visible immediately */
            .page-transition {
                opacity: 1 !important;
                transform: translateY(0) !important;
                animation: none !important;
            }
            
            /* Disable AOS animations on homepage */
            [data-aos] {
                opacity: 1 !important;
                transform: none !important;
                transition: none !important;
            }
        `;
        document.head.appendChild(style);
        
        // Apply critical styling immediately 
        document.documentElement.style.opacity = "1";
        document.documentElement.style.visibility = "visible";
    }
})();

// Main JavaScript file for common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on home page (moved here)
    const isHomePage = window.location.pathname === '/' || 
                       window.location.pathname === '/home/' || 
                       window.location.pathname === '/index.html';

    // Only initialize once - prevent multiple runs
    if (window.mainJsInitialized) {
        console.log('Main.js already initialized, preventing duplicate initialization');
        return;
    }
    window.mainJsInitialized = true;

    // CRITICAL FIX: For homepage, immediately force all elements to final state
    if (isHomePage) {
        // Force immediate display of all elements that might be animated
        document.querySelectorAll('.page-transition, .card, .fade-in, .fade-in-up, [data-aos]').forEach(el => {
            // Mark as already animated to prevent any future animations
            el.dataset.animated = "true";
            el.dataset.animating = "true";
            
            // Apply final visual state directly
            el.style.opacity = "1";
            el.style.visibility = "visible";
            el.style.transform = "none";
            el.classList.add('card-visible', 'loaded', 'visible');
            
            // Remove animation-related attributes
            if (el.hasAttribute('data-aos')) {
                el.removeAttribute('data-aos');
            }
        });
    }

    // Function containing UI enhancements
    function runUIEnhancements(isOnHomePage) {
        // Prevent multiple runs of UI enhancements
        if (window.uiEnhancementsInitialized) {
            console.log('UI enhancements already initialized, skipping');
            return;
        }
        window.uiEnhancementsInitialized = true;
        
        // Check if enhanceFormElements exists before calling it
        if (typeof enhanceFormElements === 'function') {
            enhanceFormElements();
        } else {
            console.warn('enhanceFormElements function not found. Skipping form enhancements.');
        }
        
        // For home page, completely skip animations and just set final state
        if (isOnHomePage) {
            // Skip all animation setup for homepage
            console.log('Home page detected: Skipping all animation setup');
            
            // Only run non-animation related functions
            enhanceDropdowns();
            
            // Skip animation-related functions completely for home page
            return;
        }
        
        // Only run these for non-homepage
        setupLazyLoading(isOnHomePage);
        addSmoothScrolling();
        setupCardAnimations(isOnHomePage);
        enhanceDropdowns();
        optimizeImageLoading(isOnHomePage);
        
        // Only setup parallax on larger screens and not on homepage
        if (!isOnHomePage && window.innerWidth >= 992) {
            setupParallaxEffects();
        }
    }

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
    
    // Fix browser caching issues and back navigation
    fixBrowserCacheHandling(); // Run this before enhancements potentially modifying content

    // Run UI enhancements
    if (isHomePage) {
        console.log('Home page: Running UI enhancements synchronously, with animations disabled.');
        runUIEnhancements(true);
    } else {
        console.log('Non-home page: Running UI enhancements with slight delay.');
        // Use setTimeout for non-home pages to potentially improve perceived initial load
        // We can keep a very small delay or 0. The sessionStorage check is removed for simplicity.
        setTimeout(() => runUIEnhancements(false), 50);
    }
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

// Setup card animations and hover effects - optimized for performance
function setupCardAnimations(isOnHomePage) {
    // Skip if already initialized to prevent duplicate animations
    if (window.cardAnimationsInitialized) {
        console.log('Card animations already initialized, skipping');
        return;
    }
    window.cardAnimationsInitialized = true;
    
    // For homepage, completely skip animations to prevent any possibility of multiple loads
    if (isOnHomePage) {
        console.log('Home page detected: Skipping all card animations');
        return;
    }
    
    // For other pages, continue with modified animations
    document.querySelectorAll('.card:not(.stagger-item):not(.card-appear)').forEach((card, index) => {
        // Only apply to cards in the viewport for better performance
        if (isElementInViewport(card)) {
            card.classList.add('stagger-item');
            card.classList.add(`stagger-delay-${(index % 3) + 1}`);
            
            // Apply with delay on other pages for stagger effect
            setTimeout(() => {
                card.classList.add('loaded');
            }, 50 * (index % 3));
        } else {
            // Skip animation for off-screen elements (mark as loaded immediately)
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

// Set up lazy loading for images and content
function setupLazyLoading(isOnHomePage) {
    // For home page, don't use Intersection Observer animations at all
    if (isOnHomePage) {
        document.querySelectorAll('img[data-src]').forEach(img => {
            if (img.dataset.src) {
                // Pre-load images for home page immediately
                img.src = img.dataset.src;
                img.classList.add('loaded');
                img.removeAttribute('data-src');
            }
        });
        
        // Make fade-in elements visible immediately
        document.querySelectorAll('.fade-in-up, .fade-in').forEach(element => {
            element.classList.add('visible');
            element.style.opacity = "1";
            element.style.transform = "translateY(0)";
        });
        
        // Exit early for home page
        return;
    }
    
    // For other pages, proceed with lazy loading via Intersection Observer
    // Check if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        // --- Image Lazy Loading (Keep Observer) ---
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

        // --- Element Fade-In Animation ---
        const animationObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
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
        // Make images visible
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
        });
        // Make fade-in elements visible
        document.querySelectorAll('.fade-in-up').forEach(element => {
            element.classList.add('visible');
        });
    }
}

// Optimize image loading for better performance
function optimizeImageLoading(isOnHomePage) {
    // Add loading="lazy" attribute to all images that don't have it
    document.querySelectorAll('img:not([loading])').forEach(img => {
        img.setAttribute('loading', 'lazy');
    });
    
    // Add fade-in effect to all images, unless on home page
    if (!isOnHomePage) {
        console.log('Non-home page: Applying image fade-in effect.');
        document.querySelectorAll('img').forEach(img => {
            if (!img.complete) { // Only apply to images not already loaded
                img.style.opacity = '0';
                img.style.transition = 'opacity 0.5s ease';
                
                img.addEventListener('load', function() {
                    this.style.opacity = '1';
                }, { once: true }); // Use { once: true } for better performance
            }
        });
    } else {
        console.log('Home page: Skipping image fade-in effect.');
        // Optionally, ensure images are visible if somehow hidden by other CSS
        // document.querySelectorAll('img').forEach(img => { img.style.opacity = '1'; });
    }
}

// Setup parallax effects for applicable sections - completely skip for homepage
function setupParallaxEffects() {
    // Skip entirely for homepage
    if (window.location.pathname === '/' || 
        window.location.pathname === '/home/' || 
        window.location.pathname === '/index.html') {
        return;
    }
    
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
