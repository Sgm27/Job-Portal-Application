// Special effects for the jobs listing page
document.addEventListener('DOMContentLoaded', function() {
    // CRITICAL FIX: Check for document-level animation disabling flag
    const animationsDisabled = document.documentElement.dataset.animationsDisabled === 'true';
    if (animationsDisabled) {
        console.log('Job page effects skipped: animations are disabled by document flag');
        return;
    }

    // Check if we're on the jobs page
    const isJobsPage = document.body.classList.contains('jobs-page');
    if (!isJobsPage) return;
    
    // CRITICAL FIX: Skip entirely if this is the home page
    const isHomePage = document.body.classList.contains('homepage-special') || 
                       window.location.pathname === '/' || 
                       window.location.pathname === '/home/' || 
                       window.location.pathname === '/index.html';
    if (isHomePage) {
        console.log('Job page effects skipped on homepage');
        return;
    }
    
    // Track page initialization
    if (window.jobPageEffectsInitialized) {
        console.log('Job page effects already initialized.');
        return;
    }
    window.jobPageEffectsInitialized = true;
    
    console.log('Initializing job page effects');
    
    // Apply staggered fade-in to job cards
    function animateJobCards() {
        const jobCards = document.querySelectorAll('.card-animated:not(.card-visible)');
        
        if (jobCards.length === 0) return; // No cards to animate
        
        jobCards.forEach((card, index) => {
            // Skip if already marked with animation state
            if (card.dataset.animating === 'true') return;
            card.dataset.animating = 'true';
            
            // Set initial state
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            // Apply animation with staggered delay
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
                card.classList.add('card-visible');
            }, 100 + (index * 80)); // Stagger by 80ms per card
        });
    }
    
    // Handle skeleton loading transitions
    function setupSkeletonLoading() {
        const searchForm = document.getElementById('jobSearchForm');
        const skeletonLoading = document.getElementById('skeletonLoading');
        const jobListContainer = document.querySelector('.job-list-container');
        
        if (!searchForm || !skeletonLoading || !jobListContainer) return;
        
        // Skip if already set up
        if (searchForm.dataset.skeletonHandled === 'true') return;
        searchForm.dataset.skeletonHandled = 'true';
        
        // Show skeleton on form submission
        searchForm.addEventListener('submit', function() {
            jobListContainer.style.display = 'none';
            skeletonLoading.style.display = 'block';
        });
        
        // Handle pagination transitions
        document.querySelectorAll('.pagination-link').forEach(link => {
            // Skip if already set up
            if (link.dataset.transitionHandled === 'true') return;
            link.dataset.transitionHandled = 'true';
            
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('href');
                
                // Show skeleton loader
                jobListContainer.style.display = 'none';
                skeletonLoading.style.display = 'block';
                
                // Navigate after a short delay
                setTimeout(() => {
                    window.location.href = url;
                }, 300);
            });
        });
    }
    
    // Add page transition effects
    function addPageTransitionEffects() {
        document.querySelectorAll('.page-transition').forEach(element => {
            if (element.dataset.animated === 'true') return; // Skip if already animated
            
            // Mark as animated to prevent duplicate animations
            element.dataset.animated = 'true';
            
            // Apply initial state
            element.style.opacity = '0';
            element.style.transform = 'translateY(15px)';
            
            // Animate with a slight delay for each element
            setTimeout(() => {
                element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100);
        });
    }
    
    // Initialize effects with slight delays for better performance
    setTimeout(addPageTransitionEffects, 100);
    setTimeout(animateJobCards, 300);
    setTimeout(setupSkeletonLoading, 100);
    
    // Reinitialize effects when browser back button is used
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Page was loaded from cache (back button)
            setTimeout(addPageTransitionEffects, 100);
            setTimeout(animateJobCards, 300);
        }
    });
}); 