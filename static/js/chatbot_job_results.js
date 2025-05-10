/**
 * Chatbot Job Results Renderer
 * Ensures proper formatting and display of job search results in the chatbot
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to initialize formatting for job search results
    function initializeJobSearchResults() {
        // Find all job search result containers
        const jobSearchContainers = document.querySelectorAll('.job-search-results');
        
        if (!jobSearchContainers.length) return;
        
        jobSearchContainers.forEach(container => {
            // Remove all <br> tags from the container
            removeBrTags(container);
            
            // Ensure proper formatting for each job card
            const jobCards = container.querySelectorAll('.job-card');
            jobCards.forEach(card => {
                // Fix any spacing issues
                ensureProperSpacing(card);
                
                // Make sure card elements are correctly structured
                ensureElementStructure(card);
            });
            
            // Clean up any extra whitespace in result headers
            const headers = container.querySelectorAll('.result-header');
            headers.forEach(header => {
                cleanWhitespace(header);
            });
            
            // Fix any footer issues
            const footers = container.querySelectorAll('.result-footer');
            footers.forEach(footer => {
                cleanWhitespace(footer);
            });
        });
    }
    
    // Remove all <br> tags from an element
    function removeBrTags(element) {
        // Use a more direct approach with innerHTML to remove all <br> tags at once
        if (element && element.innerHTML) {
            element.innerHTML = element.innerHTML.replace(/<br\s*\/?>/gi, '');
        }
    }
    
    // Fix spacing issues in elements
    function ensureProperSpacing(element) {
        // Remove any consecutive whitespace
        element.innerHTML = element.innerHTML.replace(/\s{2,}/g, ' ');
        
        // Ensure there's no extra space after icons
        const icons = element.querySelectorAll('i');
        icons.forEach(icon => {
            if (icon.nextSibling && icon.nextSibling.nodeType === 3) {
                icon.nextSibling.nodeValue = icon.nextSibling.nodeValue.replace(/^\s+/, '');
            }
        });
    }
    
    // Ensure elements have the correct structure
    function ensureElementStructure(card) {
        // Make sure job title is properly structured
        const jobTitle = card.querySelector('.job-title');
        if (jobTitle) {
            // Ensure job title and confidence score are properly aligned
            const confidenceScore = jobTitle.querySelector('.job-confidence');
            if (confidenceScore) {
                jobTitle.style.display = 'flex';
                jobTitle.style.justifyContent = 'space-between';
                jobTitle.style.alignItems = 'center';
            }
        }
        
        // Make sure job details have proper layout
        const jobDetails = card.querySelector('.job-details');
        if (jobDetails) {
            jobDetails.style.display = 'flex';
            jobDetails.style.flexWrap = 'wrap';
            jobDetails.style.gap = '8px';
            
            // Ensure each detail item has correct styling
            const detailItems = jobDetails.querySelectorAll('.job-detail-item');
            detailItems.forEach(item => {
                item.style.display = 'flex';
                item.style.alignItems = 'center';
                
                // Ensure icons are properly spaced
                const icon = item.querySelector('i');
                if (icon) {
                    icon.style.marginRight = '5px';
                }
            });
        }
    }
    
    // Clean up whitespace in elements
    function cleanWhitespace(element) {
        // Trim text nodes
        element.childNodes.forEach(node => {
            if (node.nodeType === 3) { // Text node
                node.nodeValue = node.nodeValue.trim();
            }
        });
        
        // Recursively clean child elements
        element.querySelectorAll('*').forEach(el => {
            if (el.firstChild && el.firstChild.nodeType === 3) {
                el.firstChild.nodeValue = el.firstChild.nodeValue.trim();
            }
            if (el.lastChild && el.lastChild.nodeType === 3) {
                el.lastChild.nodeValue = el.lastChild.nodeValue.trim();
            }
        });
    }
    
    // Create a global mutation observer to catch all changes
    const globalObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Look for job-search-results in the modified nodes
                document.querySelectorAll('.job-search-results').forEach(container => {
                    removeBrTags(container);
                });
            }
        });
    });
    
    // Observe the entire document for changes
    globalObserver.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
    
    // Also watch for the specific chat container
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    // Check if any added nodes contain job search results
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && (
                            node.classList.contains('job-search-results') || 
                            node.querySelector('.job-search-results')
                        )) {
                            initializeJobSearchResults();
                        }
                    });
                }
            });
        });
        
        observer.observe(chatMessages, { childList: true, subtree: true });
    }
    
    // Initial run
    initializeJobSearchResults();
    
    // Also run it after a short delay to catch any late-rendered content
    setTimeout(function() {
        document.querySelectorAll('.job-search-results').forEach(container => {
            removeBrTags(container);
        });
    }, 1000);
}); 