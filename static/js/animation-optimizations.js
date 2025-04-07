/**
 * Animation Optimizations
 * Provides performance improvements for website animations
 * Version: 1.4.0 - Fixed CV analysis functionality on profile page
 */

(function() {
    'use strict';
    
    // GLOBAL HOME PAGE FLAG - Check immediately at script start
    if (window.homePageFullyInitialized) {
        // If home page is already initialized, exit immediately
        console.log('Home page already initialized, exiting animation script');
        return;
    }
    
    // Immediately detect what page we're on
    const isHomePage = window.location.pathname === '/' || 
                      window.location.pathname === '/home/' || 
                      window.location.pathname === '/index.html';
    const isProfilePage = window.location.pathname.includes('/profile');
    const isJobsPage = window.location.pathname.includes('/job');
    
    // HOME PAGE SPECIAL HANDLING - Apply immediately
    if (isHomePage) {
        // Set global flag to prevent multiple initializations
        window.homePageFullyInitialized = true;
        window.homePageInitialized = true;

        console.log('Initializing home page with NO animations - enforcing single load');

        // IMMEDIATE VISIBILITY: Force immediate display of ALL elements
        document.documentElement.style.opacity = "1";
        document.documentElement.style.visibility = "visible";
        document.body.style.opacity = "1";
        document.body.style.visibility = "visible";
        
        // Add special class to indicate home page
        document.body.classList.add('homepage-special');
        document.body.classList.add('instant-page');
        document.body.setAttribute('data-page', 'home');
        document.body.setAttribute('data-no-animations', 'true');
        
        // CRITICAL: Replace onload and DOMContentLoaded handlers
        // This stops other scripts from adding animations later
        const originalAddEventListener = window.addEventListener;
        window.addEventListener = function(type, listener, options) {
            if (type === 'load' || type === 'DOMContentLoaded') {
                console.log('Blocking event listener:', type);
                // Execute listener immediately if DOM is already loaded
                if (document.readyState !== 'loading') {
                    try {
                        listener.call(window);
                    } catch(e) {
                        console.error('Error executing blocked listener:', e);
                    }
                }
                return;
            }
            
            return originalAddEventListener.call(window, type, listener, options);
        };
        
        // CRITICAL: Disable transition and animation events completely
        const style = document.createElement('style');
        style.textContent = `
            /* Global animation disabler */
            html, body, *, *::before, *::after {
                animation: none !important;
                transition: none !important;
                opacity: 1 !important;
                transform: none !important;
                visibility: visible !important;
                animation-delay: 0s !important;
                transition-delay: 0s !important;
                animation-duration: 0s !important;
                transition-duration: 0s !important;
            }
            
            /* Force all elements visible */
            .fade-in, .animated, [data-animate], [data-aos], .card-animated,
            .glass-container, .jumbotron, .fade-in, .content-visible, 
            .progressive-item, .stagger-item, .card, .card-body,
            .job-list-container, .job-card {
                animation: none !important;
                transition: none !important;
                opacity: 1 !important;
                visibility: visible !important;
                transform: none !important;
                display: initial !important;
            }
            
            /* Specific fix for jumbotron */
            .glass-container.jumbotron.fade-in,
            .glass-container.jumbotron.rounded-lg,
            .glass-container, .jumbotron {
                animation: none !important;
                transition: none !important;
                opacity: 1 !important;
                visibility: visible !important;
                transform: none !important;
                animation-delay: 0s !important;
                transition-delay: 0s !important;
                will-change: auto !important;
            }
            
            /* Disable all animation classes */
            .fade-in, .fade-out, .slide-in, .slide-out,
            .scale-in, .scale-out, .bounce-in, .bounce-out,
            .flip-in, .flip-out {
                animation: none !important;
                transition: none !important;
                opacity: 1 !important;
                transform: none !important;
            }
        `;
        document.head.appendChild(style);

        // Process all elements immediately to ensure immediate display
        function forceElementsVisible() {
            // Force ALL elements to display immediately
            const allElements = document.querySelectorAll('*');
            for (let i = 0; i < allElements.length; i++) {
                const el = allElements[i];
                
                // Set direct style properties
                el.style.opacity = "1";
                el.style.visibility = "visible";
                el.style.animation = "none";
                el.style.transition = "none";
                el.style.transform = "none";
                el.style.animationDelay = "0s";
                el.style.transitionDelay = "0s";
                
                // Remove animation-related attributes
                if (el.hasAttribute('data-aos')) el.removeAttribute('data-aos');
                if (el.hasAttribute('data-animate')) el.removeAttribute('data-animate');
                if (el.hasAttribute('data-animation')) el.removeAttribute('data-animation');
                
                // Mark as processed so other code knows not to animate
                el.setAttribute('data-no-animation', 'true');
            }
            
            // Specifically target all known animation containers
            document.querySelectorAll('.animated, [data-animate], .fade-in, .content-visible, .progressive-item, .stagger-item, .glass-container.jumbotron, .card-animated, .job-card').forEach(el => {
                // Apply direct styles for immediate visibility
                el.style.animation = "none";
                el.style.opacity = "1";
                el.style.transform = "none";
                el.style.transition = "none";
                el.style.visibility = "visible";
                el.style.animationDelay = "0s";
                el.style.transitionDelay = "0s";
                
                // Add stability classes
                el.classList.add('homepage-visible');
                el.classList.add('no-animation');
                
                // Mark as processed
                el.setAttribute('data-animated', 'true');
                el.setAttribute('data-no-animation', 'true');
            });
            
            // Special handling for jumbotron - critical element
            const jumbotron = document.querySelector('.glass-container.jumbotron');
            if (jumbotron) {
                jumbotron.style.opacity = "1";
                jumbotron.style.visibility = "visible";
                jumbotron.style.animation = "none";
                jumbotron.style.transition = "none";
                jumbotron.style.transform = "none";
                jumbotron.style.willChange = "auto";
                jumbotron.classList.add('homepage-visible');
                jumbotron.classList.add('no-animation');
                jumbotron.setAttribute('data-no-animation', 'true');
                
                // Remove any potentially conflicting classes
                jumbotron.classList.remove('fade-in');
                jumbotron.classList.remove('animated');
            }
        }

        // Run immediately
        forceElementsVisible();
        
        // Also run again after a slight delay to catch any late-loaded elements
        setTimeout(forceElementsVisible, 0);
        
        // Run one more time after DOM is fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', forceElementsVisible);
        }
        
        // Disable AOS completely
        if (window.AOS) {
            try {
                if (typeof window.AOS.destroy === 'function') {
                    window.AOS.destroy();
                }
                document.querySelectorAll('[data-aos]').forEach(el => {
                    el.removeAttribute('data-aos');
                    el.style.opacity = "1";
                    el.style.transform = "none";
                });
            } catch (e) {
                console.log('Error disabling AOS:', e);
            }
        }

        // Return early to prevent running any other initialization code
        return;
    }
    
    // PROFILE PAGE HANDLING - Similar to home page, show everything at once
    if (isProfilePage) {
        // Force instant visibility
        document.documentElement.style.opacity = "1";
        document.documentElement.style.visibility = "visible";
        document.body.style.opacity = "1";
        document.body.style.visibility = "visible";
        
        // Add class to mark as instant page
        document.body.classList.add('instant-page');
        
        // Disable animations on DOMContentLoaded
        window.addEventListener('DOMContentLoaded', function() {
            // Disable AOS if it exists
            if (window.AOS) {
                try {
                    if (typeof window.AOS.destroy === 'function') {
                        window.AOS.destroy();
                    }
                    
                    document.querySelectorAll('[data-aos]').forEach(el => {
                        el.removeAttribute('data-aos');
                        el.style.opacity = "1";
                        el.style.transform = "none";
                    });
                } catch (e) {
                    console.log('Error disabling AOS on profile page:', e);
                }
            }
            
            // Show all elements immediately EXCEPT CV analysis elements
            document.querySelectorAll('.animated, [data-animate], .fade-in, .content-visible, .progressive-item, .stagger-item').forEach(el => {
                // Skip CV analysis elements
                if (el.closest('.analysis-result-row') || 
                    el.closest('.analysis-content') || 
                    el.classList.contains('analyze-resume-btn') ||
                    el.closest('.cv-analysis-markdown')) {
                    return;
                }
                
                el.style.animation = "none";
                el.style.opacity = "1";
                el.style.transform = "none";
                el.style.transition = "none";
                el.style.animationDelay = "0s";
                el.style.transitionDelay = "0s";
                el.setAttribute('data-animated', 'true');
                el.classList.add('instant-visible');
            });
            
            // Remove instant-page/animation-disabled class from CV analysis elements
            document.querySelectorAll('.analysis-result-row, .analysis-content, .analyze-resume-btn, [id^="result-row-"], [id^="result-content-"]').forEach(el => {
                el.classList.remove('instant-visible');
                el.classList.remove('homepage-visible');
                if (el.hasAttribute('data-animated')) {
                    el.removeAttribute('data-animated');
                }
                // Remove inline styles that might prevent animations
                el.style.removeProperty('animation');
                el.style.removeProperty('transition');
                el.style.removeProperty('opacity');
                el.style.removeProperty('transform');
            });
            
            // Add style to prevent animations - BUT EXCLUDE CV ANALYSIS ELEMENTS
            if (!document.querySelector('#instant-page-style')) {
                const style = document.createElement('style');
                style.id = 'instant-page-style';
                style.textContent = `
                    body.instant-page * {
                        animation-duration: 0s !important;
                        transition-duration: 0s !important;
                        animation-delay: 0s !important;
                        transition-delay: 0s !important;
                    }
                    
                    body.instant-page [data-animate],
                    body.instant-page .animated,
                    body.instant-page .fade-in,
                    body.instant-page .stagger-item,
                    body.instant-page .progressive-item {
                        opacity: 1 !important;
                        transform: none !important;
                        animation: none !important;
                        transition: none !important;
                    }
                    
                    /* EXCEPTIONS FOR CV ANALYSIS - Allow these elements to animate */
                    body.instant-page .analysis-result-row,
                    body.instant-page .analysis-content,
                    body.instant-page .spinner-border,
                    body.instant-page .cv-analysis-markdown,
                    body.instant-page .markdown-body,
                    body.instant-page .smooth-loader,
                    body.instant-page [id^="result-row-"],
                    body.instant-page [id^="result-content-"],
                    body.instant-page .analyze-resume-btn,
                    body.instant-page button.analyze-resume-btn,
                    body.instant-page button.close-analysis-btn,
                    body.instant-page button.print-analysis-btn,
                    body.instant-page .cv-analysis-card {
                        animation-duration: inherit !important;
                        transition-duration: inherit !important;
                        animation-delay: inherit !important;
                        transition-delay: inherit !important;
                        opacity: inherit !important;
                        transform: inherit !important;
                        animation: inherit !important;
                        transition: inherit !important;
                        visibility: inherit !important;
                        will-change: inherit !important;
                        display: inherit !important;
                        z-index: 100 !important;
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    
                    /* Đảm bảo CV analysis hiển thị đúng kích thước */
                    .cv-analysis-card,
                    .markdown-body,
                    .cv-analysis-markdown,
                    .analysis-content,
                    .analysis-result-row td {
                        width: 100% !important;
                        max-width: 100% !important;
                        display: block !important;
                    }
                    
                    /* Đảm bảo table row hiển thị đúng */
                    .analysis-result-row {
                        display: table-row !important;
                        width: 100% !important;
                    }
                    
                    /* Fix cho table cell */
                    .table .analysis-result-row td {
                        display: table-cell !important;
                        width: 100% !important;
                    }
                    
                    /* Reset transitions for CV analysis elements */
                    .analysis-result-row,
                    .analysis-content,
                    .spinner-border,
                    .cv-analysis-markdown {
                        transition: opacity 0.3s ease, transform 0.3s ease !important;
                        will-change: opacity, transform !important;
                    }
                    
                    /* Fix for analyze buttons to allow their transitions */
                    .analyze-resume-btn,
                    button.analyze-resume-btn,
                    button.close-analysis-btn,
                    button.print-analysis-btn {
                        transition: all 0.3s ease !important;
                        cursor: pointer !important;
                        pointer-events: auto !important;
                        opacity: 1 !important;
                        visibility: visible !important;
                    }
                    
                    /* Fix for spinner animation */
                    @keyframes spinner-border {
                        to { transform: rotate(360deg); }
                    }
                    
                    .spinner-border {
                        animation: spinner-border .75s linear infinite !important;
                    }
                    
                    /* Fix for analysis rows */
                    .analysis-result-row[style*="display: table-row"],
                    .analysis-result-row[style*="display:table-row"] {
                        display: table-row !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                    }
                `;
                document.head.appendChild(style);
            }
            
            // Setup only simplified page transitions
            setupSimplifiedPageTransitions();
            
            // Re-enable functionality for CV analysis components
            const analyzeButtons = document.querySelectorAll('.analyze-resume-btn');
            if (analyzeButtons.length > 0) {
                console.log('Found CV analysis buttons - ensuring they work properly');
                
                // Set proper styles directly to buttons 
                analyzeButtons.forEach(btn => {
                    btn.style.transition = 'all 0.3s ease';
                    btn.style.cursor = 'pointer';
                    btn.style.pointerEvents = 'auto';
                    
                    if (btn.hasAttribute('data-animated')) {
                        btn.removeAttribute('data-animated');
                    }
                    
                    // Add a click event listener to log clicks for debugging
                    btn.addEventListener('click', function(e) {
                        console.log('CV analyze button clicked:', this.getAttribute('data-resume-id'));
                        
                        // Make sure the click is processed properly
                        e.stopPropagation();
                    }, true);
                });
                
                // Fix issues with analysis rows styling
                document.querySelectorAll('.analysis-result-row').forEach(row => {
                    // Set explicit transitions
                    row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    row.style.opacity = row.style.display === 'table-row' ? '1' : '0';
                    
                    // Remove classes that might interfere
                    row.classList.remove('instant-visible');
                    row.classList.remove('homepage-visible');
                    
                    if (row.hasAttribute('data-animated')) {
                        row.removeAttribute('data-animated');
                    }
                });
                
                // Create a MutationObserver to detect when analysis rows become visible
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                            const target = mutation.target;
                            if (target.classList.contains('analysis-result-row') && 
                                target.style.display === 'table-row') {
                                console.log('Analysis row displayed:', target.id);
                                
                                // Force proper display
                                target.style.opacity = '1';
                                target.style.visibility = 'visible';
                                target.style.transform = 'translateY(0)';
                                
                                // Look for the content element and ensure it's visible
                                const content = target.querySelector('.analysis-content');
                                if (content) {
                                    content.style.opacity = '1';
                                    content.style.visibility = 'visible';
                                }
                            }
                        }
                    });
                });
                
                // Observe all analysis rows for style changes
                document.querySelectorAll('.analysis-result-row').forEach(row => {
                    observer.observe(row, { attributes: true });
                });
            }
        });
        
        // Skip normal initialization for profile page
        return;
    }
    
    // Normal script continues here for non-home/non-profile pages
    
    // Check if the script has already been executed - prevent double loading
    if (window.animationOptimizerLoaded) {
        console.log('Animation optimizer already loaded, preventing duplicate initialization');
        return;
    }
    window.animationOptimizerLoaded = true;
    
    // Track if animations have been initialized
    let animationsInitialized = false;
    
    // Track elements that have already been animated to prevent duplicates
    // Use data attributes instead of WeakSet for more reliable tracking
    const ANIMATED_ATTR = 'data-animated';
    const PROGRESSIVE_ATTR = 'data-processed';
    const OBSERVED_ATTR = 'data-image-loaded';
    
    // Store original document classes to prevent removal
    const originalDocClasses = document.documentElement.className;
    
    // Simplified page transitions for instant pages
    function setupSimplifiedPageTransitions() {
        // Only run once
        if (window.simpleTransitionsInitialized) return;
        window.simpleTransitionsInitialized = true;
        
        document.addEventListener('click', function(e) {
            // Only process links
            const link = e.target.closest('a');
            if (!link) return;
            
            // Skip non-navigational links
            if (link.hasAttribute('download') || 
                link.getAttribute('target') === '_blank' || 
                link.getAttribute('rel') === 'external' ||
                link.classList.contains('no-transition') ||
                link.href.startsWith('mailto:') ||
                link.href.startsWith('tel:') ||
                link.href.startsWith('javascript:') ||
                link.href.includes('#')) {
                return;
            }
            
            // Store timestamp for optimization
            try {
                sessionStorage.setItem('lastPageExit', Date.now().toString());
            } catch (e) {
                // Ignore storage errors
            }
        });
    }
    
    // Prefetch common pages to make transitions faster
    const prefetchLinks = () => {
        // Prevent duplicate prefetching
        if (window.prefetchInitialized) return;
        window.prefetchInitialized = true;
        
        // Only prefetch if the browser is idle and not on low-end devices
        if ('requestIdleCallback' in window && 'connection' in navigator && 
            (!navigator.connection.saveData) && 
            (navigator.connection.effectiveType === '4g')) {
            
            requestIdleCallback(() => {
                const links = Array.from(document.querySelectorAll('a:not([data-no-prefetch])'))
                    .filter(link => {
                        // Only internal links from same domain
                        try {
                            const url = new URL(link.href, window.location.origin);
                            return url.origin === window.location.origin;
                        } catch (e) {
                            return false;
                        }
                    })
                    .map(link => link.href)
                    // Remove duplicates
                    .filter((url, index, self) => self.indexOf(url) === index)
                    // Limit to first 5 unique URLs to avoid overloading
                    .slice(0, 5);
                
                links.forEach(url => {
                    // Check if this URL is already being prefetched
                    if (document.querySelector(`link[rel="prefetch"][href="${url}"]`)) return;
                    
                    const link = document.createElement('link');
                    link.rel = 'prefetch';
                    link.href = url;
                    link.as = 'document';
                    document.head.appendChild(link);
                });
            }, { timeout: 2000 });
        }
    };
    
    // Start initial animations immediately, don't wait for full DOM load
    // This reduces perceived lag between page transitions
    (function initializeImmediately() {
        // Only run once
        if (window.immediateInitDone) return;
        window.immediateInitDone = true;
        
        // Check if this is a page navigation from within the site
        const lastPageExit = parseInt(sessionStorage.getItem('lastPageExit') || '0', 10);
        const isInternalNavigation = lastPageExit > 0 && (Date.now() - lastPageExit < 3000);
        
        // Create transition overlay immediately for faster visual feedback
        if (isInternalNavigation) {
            const existingOverlay = document.querySelector('.page-transition-overlay');
            if (!existingOverlay) {
                const overlay = document.createElement('div');
                overlay.className = 'page-transition-overlay';
                document.body.appendChild(overlay);
                
                // Auto-remove overlay after 500ms
                setTimeout(() => {
                    if (overlay && overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 500);
            }
        }
        
        // Force body visibility immediately to prevent flickering
        document.body.style.opacity = "1";
        document.body.style.visibility = "visible";
    })();
    
    // Performance helper - efficiently throttle function calls
    const throttle = (func, limit) => {
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
    };
    
    // Performance helper - efficiently debounce function calls
    const debounce = (func, delay) => {
        let debounceTimer;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(context, args), delay);
        };
    };
    
    // Setup page transitions to improve perceived performance
    const setupPageTransitions = () => {
        // Prevent multiple initializations
        if (window.pageTransitionsInitialized) return;
        window.pageTransitionsInitialized = true;
        
        // Mark the current URL to enable back-button optimizations
        const markCurrentPageVisited = () => {
            try {
                const visitedPages = JSON.parse(sessionStorage.getItem('visitedPages') || '[]');
                const currentUrl = window.location.pathname;
                if (!visitedPages.includes(currentUrl)) {
                    visitedPages.push(currentUrl);
                    sessionStorage.setItem('visitedPages', JSON.stringify(visitedPages));
                }
            } catch (e) {
                console.error('Error managing page history:', e);
            }
        };
        
        markCurrentPageVisited();
        
        // Remove any existing click handlers to prevent duplication
        const oldClickHandler = window._pageTransitionClickHandler;
        if (oldClickHandler) {
            document.removeEventListener('click', oldClickHandler);
        }
        
        // Setup click event handling for all links
        const clickHandler = function(e) {
            // Only process links
            const link = e.target.closest('a');
            if (!link) return;
            
            // Skip non-navigational links
            if (link.hasAttribute('download') || 
                link.getAttribute('target') === '_blank' || 
                link.getAttribute('rel') === 'external' ||
                link.classList.contains('no-transition') ||
                link.href.startsWith('mailto:') ||
                link.href.startsWith('tel:') ||
                link.href.startsWith('javascript:') ||
                link.href.includes('#')) {
                return;
            }
            
            // Get current domain
            const currentDomain = window.location.hostname;
            
            try {
                // Check if link is to same domain (internal)
                const url = new URL(link.href);
                if (url.hostname !== currentDomain) return;
                
                // Store current URL for job page-specific optimizations
                sessionStorage.setItem('previousPage', window.location.pathname);
                
                // Animate the page transition
                e.preventDefault();
                
                // Store the target URL
                const targetHref = link.href;
                
                // Check if overlay already exists
                const existingOverlay = document.querySelector('.page-transition-overlay');
                if (!existingOverlay) {
                    // Create overlay for smoother transition
                    const overlay = document.createElement('div');
                    overlay.className = 'page-transition-overlay';
                    document.body.appendChild(overlay);
                }
                
                // Add transition class
                document.body.classList.add('page-transitioning-out');
                
                // Set navigation timing - shorter for job pages
                const navTime = isJobsPage ? 80 : 100;
                
                // Start prefetching the target page immediately
                const existingPrefetch = document.querySelector(`link[rel="prefetch"][href="${targetHref}"]`);
                if (!existingPrefetch) {
                    const prefetchLink = document.createElement('link');
                    prefetchLink.rel = 'prefetch';
                    prefetchLink.href = targetHref;
                    prefetchLink.as = 'document';
                    document.head.appendChild(prefetchLink);
                }
                
                // Store timestamp for back-button optimization
                sessionStorage.setItem('lastPageExit', Date.now().toString());
                
                // Navigate after short delay for animation
                window.setTimeout(() => {
                    window.location.href = targetHref;
                }, navTime);
            } catch (e) {
                // Fall back to normal navigation if any error occurs
                return true;
            }
        };
        
        // Store handler reference to allow removal later
        window._pageTransitionClickHandler = clickHandler;
        document.addEventListener('click', clickHandler);
        
        // Remove any existing pageshow handlers
        const oldPageShowHandler = window._pageShowHandler;
        if (oldPageShowHandler) {
            window.removeEventListener('pageshow', oldPageShowHandler);
        }
        
        // Optimize back button navigation
        const pageShowHandler = function(event) {
            if (event.persisted) {
                // This is a back/forward navigation from cache (bfcache)
                document.documentElement.classList.remove('page-transitioning-out');
                document.body.classList.remove('page-transitioning-out');
                
                // Apply a brief animation for back navigation if one doesn't exist
                const existingOverlay = document.querySelector('.page-transition-overlay');
                if (!existingOverlay) {
                    const overlay = document.createElement('div');
                    overlay.className = 'page-transition-overlay';
                    document.body.appendChild(overlay);
                    
                    // Clean up after animation completes
                    setTimeout(() => {
                        if (overlay && overlay.parentNode) {
                            overlay.parentNode.removeChild(overlay);
                        }
                    }, 350);
                }
                
                // Force body visibility
                document.body.style.opacity = "1";
                document.body.style.visibility = "visible";
            }
        };
        
        // Store handler reference to allow removal later
        window._pageShowHandler = pageShowHandler;
        window.addEventListener('pageshow', pageShowHandler);
    };
    
    // Clear any existing AOS animations to prevent conflicts
    const clearAOSAnimations = () => {
        if (window.AOS) {
            // Try to find a better way to disable AOS
            try {
                document.querySelectorAll('[data-aos]').forEach(el => {
                    // Remove AOS classes and attributes
                    el.removeAttribute('data-aos');
                    Array.from(el.classList).forEach(cls => {
                        if (cls.startsWith('aos-')) {
                            el.classList.remove(cls);
                        }
                    });
                });
                
                // Try to disable AOS instance
                if (typeof window.AOS.refresh === 'function') {
                    window.AOS.refreshHard = function() {}; // Prevent further refreshes
                }
            } catch (e) {
                console.log('Error disabling AOS animations:', e);
            }
        }
    };
    
    // Fix for flashing elements by forcing stable rendering
    const stabilizeRendering = () => {
        // Add a class to the body that enables more stable rendering
        document.body.classList.add('stable-rendering');
        
        // Force hardware acceleration on the body for smoother transitions
        document.body.style.transform = 'translateZ(0)';
        document.body.style.backfaceVisibility = 'hidden';
        document.body.style.perspective = '1000px';
        
        // Disable any potential conflicting animations
        document.querySelectorAll('.animated, [data-animate], .fade-in, .content-visible')
            .forEach(el => {
                // Only process once
                if (el.hasAttribute(ANIMATED_ATTR)) return;
                el.setAttribute(ANIMATED_ATTR, 'true');
                
                // Force stable state by removing conflicting styles/classes
                el.style.animation = 'none';
                el.style.opacity = '1';
                el.style.transform = 'none';
                
                // Remove potentially conflicting classes
                ['animated', 'animation-running', 'aos-animate', 'fade-in'].forEach(cls => {
                    if (el.classList.contains(cls)) {
                        el.classList.remove(cls);
                    }
                });
            });
    };
    
    // Initialize animations optimally based on device capabilities
    const initAnimations = () => {
        if (animationsInitialized) return;
        
        // Start initialization before DOM is fully ready for better performance
        const earlyInit = () => {
            // Check for reduced motion preference
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            
            // Add performance classes immediately 
            document.documentElement.classList.add(
                prefersReducedMotion ? 'reduced-motion' : 'allows-motion'
            );
            
            // Setup page transitions for better perceived performance
            setupPageTransitions();
            
            // Start prefetching links in idle time
            prefetchLinks();
            
            // Clear conflicting animations early
            clearAOSAnimations();
            
            // Stabilize rendering to prevent flicker
            stabilizeRendering();
        };
        
        // Run early initialization
        earlyInit();
        
        // Full initialization when DOM is interactive
        const fullInit = () => {
            // Check for reduced motion preference
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            
            // Add hardware acceleration class to key elements (but avoid duplicates)
            if (!prefersReducedMotion) {
                document.querySelectorAll('.card, .btn, .navbar, .fade-in, .modal, .dropdown-menu').forEach(el => {
                    if (!el.classList.contains('hardware-accelerated') && !el.hasAttribute(ANIMATED_ATTR)) {
                        el.classList.add('hardware-accelerated');
                        el.setAttribute(ANIMATED_ATTR, 'hardware');
                    }
                });
            }
            
            // Start content animation as early as possible
            if (!document.body.classList.contains('content-visible')) {
                document.body.classList.add('content-visible');
            }
            
            // Only setup animations based on current page type
            if (isJobsPage) {
                // For job pages, use the progressive loading
                setupJobPageAnimations();
            } else {
                // For other pages (that aren't home or profile), use basic animation
                setupBasicAnimations();
            }
            
            // Always optimize image loading
            optimizeImageLoading();
            
            // These optimizations apply for all pages
            fixInputScrollLag();
            optimizeRAF();
            
            // Apply initial page transition
            if (!document.body.classList.contains('page-initialized')) {
                document.body.classList.add('page-initialized');
            }
            
            // Always ensure the body is visible
            document.body.style.opacity = "1";
            document.body.style.visibility = "visible";
            
            // Mark animations as initialized
            animationsInitialized = true;
        };
        
        // Set up job page specific animations
        const setupJobPageAnimations = () => {
            // Show all elements immediately without animations
            const containers = Array.from(document.querySelectorAll('[data-progressive]'));
            
            containers.forEach(container => {
                const children = Array.from(container.children);
                children.forEach(el => {
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
            });
        };
        
        // Basic animations for other pages (not home, profile, or jobs)
        const setupBasicAnimations = () => {
            // Make all elements immediately visible, but with a simple fade
            document.querySelectorAll('[data-animate], [data-progressive] > *, .progressive-item, .stagger-item').forEach(el => {
                if (!el.hasAttribute(ANIMATED_ATTR)) {
                    el.style.opacity = '0';
                    el.style.transition = 'opacity 0.3s ease-out';
                    el.setAttribute(ANIMATED_ATTR, 'true');
                    
                    // Force reflow
                    void el.offsetWidth;
                    
                    setTimeout(() => {
                        el.style.opacity = '1';
                    }, 10);
                }
            });
        };
        
        // Fix for Safari's input lag during scroll
        const fixInputScrollLag = () => {
            // Prevent duplicate initialization
            if (window.inputScrollLagFixed) return;
            window.inputScrollLagFixed = true;
            
            const inputElements = document.querySelectorAll('input, textarea, select, button');
            let isTouching = false;
            
            window.addEventListener('touchstart', () => { isTouching = true; });
            window.addEventListener('touchend', () => { isTouching = false; });
            
            window.addEventListener('scroll', throttle(() => {
                if (isTouching) return;
                
                inputElements.forEach(input => {
                    input.style.transform = 'translateZ(0)';
                    setTimeout(() => {
                        input.style.transform = '';
                    }, 0);
                });
            }, 300), { passive: true });
        };
        
        // Optimize image loading with high priority for visible images
        const optimizeImageLoading = () => {
            // First load visible images immediately
            const loadVisibleImages = () => {
                const images = Array.from(document.querySelectorAll('img[data-src]'))
                    .filter(img => !img.hasAttribute(OBSERVED_ATTR)); // Skip already observed images
                
                // Check which images are in viewport
                const viewportImages = images.filter(img => {
                    const rect = img.getBoundingClientRect();
                    return (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= window.innerHeight &&
                        rect.right <= window.innerWidth
                    );
                });
                
                // Load visible images first with high priority
                viewportImages.forEach(img => {
                    // Mark as observed
                    img.setAttribute(OBSERVED_ATTR, 'true');
                    
                    const src = img.dataset.src;
                    if (!img.src || img.src !== src) {
                        img.src = src;
                        img.style.opacity = '0';
                        
                        img.onload = () => {
                            img.style.transition = 'opacity 0.3s ease';
                            img.style.opacity = '1';
                            img.removeAttribute('data-src');
                        };
                    }
                });
                
                // Return remaining images that haven't been processed
                return images.filter(img => !viewportImages.includes(img));
            };
            
            // Load remaining images lazily
            const remainingImages = loadVisibleImages();
            
            if (remainingImages.length === 0) return;
            
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        
                        // Skip if already processed
                        if (!img.dataset.src || img.hasAttribute(OBSERVED_ATTR)) {
                            imageObserver.unobserve(img);
                            return;
                        }
                        
                        // Mark as observed
                        img.setAttribute(OBSERVED_ATTR, 'true');
                        
                        const src = img.dataset.src;
                        img.src = src;
                        img.style.opacity = '0';
                        
                        img.onload = () => {
                            img.style.transition = 'opacity 0.3s ease';
                            img.style.opacity = '1';
                            img.removeAttribute('data-src');
                        };
                        
                        imageObserver.unobserve(img);
                    }
                });
            }, {
                rootMargin: '200px' // Start loading before images enter viewport
            });
            
            remainingImages.forEach(img => {
                // Skip already observed images
                if (img.hasAttribute(OBSERVED_ATTR)) return;
                imageObserver.observe(img);
            });
        };
        
        // Optimize requestAnimationFrame for better performance
        const optimizeRAF = () => {
            // Prevent duplicate initialization
            if (window.rafOptimized) return;
            window.rafOptimized = true;
            
            let scrolling = false;
            let resizing = false;
            
            window.addEventListener('scroll', () => {
                scrolling = true;
            }, { passive: true });
            
            window.addEventListener('resize', () => {
                resizing = true;
            });
            
            function loop() {
                if (scrolling) {
                    // Dispatch a custom optimized scroll event
                    window.dispatchEvent(new CustomEvent('optimizedScroll'));
                    scrolling = false;
                }
                
                if (resizing) {
                    // Dispatch a custom optimized resize event
                    window.dispatchEvent(new CustomEvent('optimizedResize'));
                    resizing = false;
                }
                
                window.requestAnimationFrame(loop);
            }
            
            window.requestAnimationFrame(loop);
        };
        
        // Run full initialization based on document readiness
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fullInit);
        } else {
            fullInit();
        }
    };
    
    // Call initAnimations immediately
    initAnimations();
    
    // Clear any existing render timers to prevent duplicate animations
    if (window._renderTimer) {
        clearTimeout(window._renderTimer);
    }
    
    // Ensure body visibility after a brief delay (catches any issues with other scripts)
    window._renderTimer = setTimeout(() => {
        document.body.style.opacity = "1";
        document.body.style.visibility = "visible";
    }, 100);
    
    // Expose the API globally
    window.AnimationOptimizer = {
        refresh: function() {
            // Only refresh if explicitly called by code
            initAnimations();
        },
        throttle: throttle,
        debounce: debounce,
        stabilize: function() {
            // Utility to force stabilization manually
            stabilizeRendering();
            document.body.style.opacity = "1";
            document.body.style.visibility = "visible";
        }
    };
})(); 