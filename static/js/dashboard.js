// Dashboard related JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Fix dropdown menu functionality in the dashboard
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get the dropdown menu associated with this toggle
            const dropdownMenu = this.nextElementSibling;
            
            // Toggle the 'show' class on the dropdown menu
            dropdownMenu.classList.toggle('show');
            
            // Handle outside clicks to close the dropdown
            const closeDropdown = function(event) {
                if (!dropdownMenu.contains(event.target) && event.target !== toggle) {
                    dropdownMenu.classList.remove('show');
                    document.removeEventListener('click', closeDropdown);
                }
            };
            
            // Add event listener to close dropdown when clicking outside
            setTimeout(() => {
                document.addEventListener('click', closeDropdown);
            }, 0);
        });
    });

    // Additional fix for table row actions dropdown
    const tableActionDropdowns = document.querySelectorAll('.table .dropdown .dropdown-toggle');
    tableActionDropdowns.forEach(actionToggle => {
        actionToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Close all other dropdowns first
            document.querySelectorAll('.table .dropdown .dropdown-menu.show').forEach(menu => {
                if (menu !== this.nextElementSibling) {
                    menu.classList.remove('show');
                }
            });
            
            // Toggle this dropdown menu
            const actionMenu = this.nextElementSibling;
            actionMenu.classList.toggle('show');
            
            // Set correct position if needed
            if (actionMenu.classList.contains('show')) {
                const buttonRect = this.getBoundingClientRect();
                actionMenu.style.position = 'absolute';
                actionMenu.style.top = `${buttonRect.bottom}px`;
                actionMenu.style.right = '0';
                actionMenu.style.left = 'auto';
            }
            
            // Handle clicking outside to close
            const closeActionDropdown = function(event) {
                if (!actionMenu.contains(event.target) && event.target !== actionToggle) {
                    actionMenu.classList.remove('show');
                    document.removeEventListener('click', closeActionDropdown);
                }
            };
            
            document.addEventListener('click', closeActionDropdown);
        });
    });

    // Job status indicators
    const statusBadges = document.querySelectorAll('.badge');
    statusBadges.forEach(badge => {
        // Add hover effect
        badge.addEventListener('mouseenter', function() {
            if (this.classList.contains('bg-success')) {
                this.setAttribute('data-original-bg', 'bg-success');
                this.classList.replace('bg-success', 'bg-success-light');
            } else if (this.classList.contains('bg-warning')) {
                this.setAttribute('data-original-bg', 'bg-warning');
                this.classList.replace('bg-warning', 'bg-warning-light');
            } else if (this.classList.contains('bg-danger')) {
                this.setAttribute('data-original-bg', 'bg-danger');
                this.classList.replace('bg-danger', 'bg-danger-light');
            } else if (this.classList.contains('bg-info')) {
                this.setAttribute('data-original-bg', 'bg-info');
                this.classList.replace('bg-info', 'bg-info-light');
            } else if (this.classList.contains('bg-primary')) {
                this.setAttribute('data-original-bg', 'bg-primary');
                this.classList.replace('bg-primary', 'bg-primary-light');
            }
        });
        
        badge.addEventListener('mouseleave', function() {
            const originalBg = this.getAttribute('data-original-bg');
            if (originalBg && this.classList.contains(originalBg + '-light')) {
                this.classList.replace(originalBg + '-light', originalBg);
            }
        });
    });

    // Application status update confirmation
    const statusForms = document.querySelectorAll('form[action*="update_application_status"]');
    statusForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const statusValue = this.querySelector('input[name="status"]').value;
            const applicationId = this.action.split('/').filter(Boolean).pop();
            
            // Confirm status changes that are significant
            if (statusValue === 'rejected' || statusValue === 'hired') {
                const applicantName = this.closest('tr').querySelector('td:first-child strong').textContent;
                if (!confirm(`Are you sure you want to mark ${applicantName}'s application as ${statusValue.toUpperCase()}?`)) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    });

    // Job table row highlighting
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Ignore clicks on buttons and links
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || 
                e.target.closest('button') || e.target.closest('a')) {
                return;
            }
            
            // Get the link to job detail
            const jobLink = this.querySelector('td:first-child a');
            if (jobLink) {
                window.location.href = jobLink.href;
            }
        });
        
        // Add pointer cursor to indicate clickable
        row.style.cursor = 'pointer';
        
        // Add hover effect for better UX
        row.addEventListener('mouseenter', function() {
            this.classList.add('table-hover-highlight');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('table-hover-highlight');
        });
    });

    // Add confirmation for delete job action
    const deleteLinks = document.querySelectorAll('a[href*="delete_job"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Stats counter animation
    const counters = document.querySelectorAll('.display-4');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent, 10);
        const duration = 1000; // 1 second
        const step = Math.ceil(target / (duration / 20)); // Update every 20ms
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current > target) current = target;
            counter.textContent = current;
            if (current < target) {
                setTimeout(updateCounter, 20);
            }
        };
        
        // Only start animation when element is in viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(counter);
    });
    
    // Add search functionality to applicant tracking table
    const applicantTable = document.querySelector('.table-responsive .table');
    if (applicantTable) {
        // Create search input
        const searchContainer = document.createElement('div');
        searchContainer.className = 'mb-3 search-box';
        
        const searchIcon = document.createElement('i');
        searchIcon.className = 'bi bi-search';
        searchContainer.appendChild(searchIcon);
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control';
        searchInput.placeholder = 'Search applicants...';
        searchContainer.appendChild(searchInput);
        
        // Insert search box before the table
        const tableParent = applicantTable.parentNode;
        tableParent.insertBefore(searchContainer, applicantTable);
        
        // Add search functionality
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = applicantTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const applicantName = row.querySelector('td:first-child strong').textContent.toLowerCase();
                const applicantEmail = row.querySelector('td:first-child p').textContent.toLowerCase();
                
                if (applicantName.includes(searchTerm) || applicantEmail.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Fix positioning logic for status dropdown
    const statusDropdownButtons = document.querySelectorAll('.show-status-dropdown');
    const statusDropdownsContainer = document.getElementById('status-dropdowns-container');
    
    if (statusDropdownsContainer && statusDropdownButtons.length > 0) {
        // Move container to body to ensure it's not affected by any parent CSS
        document.body.appendChild(statusDropdownsContainer);
        
        statusDropdownButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
    
                const applicationId = this.getAttribute('data-id');
                const buttonRect = this.getBoundingClientRect();
                const dropdownContainer = document.getElementById(`status-dropdown-container-${applicationId}`);
    
                if (!dropdownContainer) return;
    
                // Hide all dropdown containers first
                document.querySelectorAll('.status-dropdown-container').forEach(container => {
                    container.style.display = 'none';
                });
    
                // Show the dropdown container
                statusDropdownsContainer.style.display = 'block';
                dropdownContainer.style.display = 'block';
    
                // Position the dropdown menu
                const dropdownMenu = dropdownContainer.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.classList.add('show'); // Important: add the Bootstrap show class
                    dropdownMenu.style.position = 'absolute';
                    dropdownMenu.style.top = `${buttonRect.bottom + window.scrollY}px`;
                    dropdownMenu.style.left = `${buttonRect.left}px`;
                }
    
                // Close dropdown when clicking outside
                const closeDropdown = function(event) {
                    if (dropdownMenu && !dropdownMenu.contains(event.target) && event.target !== button) {
                        dropdownMenu.classList.remove('show');
                        dropdownContainer.style.display = 'none';
                        document.removeEventListener('click', closeDropdown);
                    }
                };
    
                setTimeout(() => {
                    document.addEventListener('click', closeDropdown);
                }, 100);
            });
        });
    }
});
