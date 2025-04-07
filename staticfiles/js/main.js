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
    
    // Setup back-to-top button
    setupBackToTop();
    
    // Khắc phục triệt để vấn đề modal-backdrop
    fixModalBackdropIssue();
});

// Initialize Bootstrap components that need JavaScript
function initializeBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize all popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Initialize all toasts
    const toastElList = document.querySelectorAll('.toast');
    [...toastElList].map(toastEl => new bootstrap.Toast(toastEl).show());
}

// Cách giải quyết mới và mạnh hơn cho vấn đề modal-backdrop
function fixModalBackdropIssue() {
    // Thêm một style tag vào head để đặt z-index cho modal-backdrop thấp hơn
    const style = document.createElement('style');
    style.textContent = `
        body:not(.modal-open) .modal-backdrop {
            display: none !important;
        }
    `;
    document.head.appendChild(style);
    
    // Thêm các xử lý sự kiện để đảm bảo modal-backdrop được xóa
    const modalButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    modalButtons.forEach(button => {
        const targetId = button.getAttribute('data-bs-target');
        if (targetId) {
            const modal = document.querySelector(targetId);
            if (modal) {
                // Xử lý khi modal được đóng
                modal.addEventListener('hidden.bs.modal', function() {
                    // Xóa modal-backdrop
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => {
                        backdrop.parentNode.removeChild(backdrop);
                    });
                    
                    // Khôi phục trạng thái body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                });
                
                // Sửa lỗi khi nút đóng được nhấn
                const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(btn => {
                    btn.addEventListener('click', function() {
                        setTimeout(() => {
                            const backdrops = document.querySelectorAll('.modal-backdrop');
                            backdrops.forEach(backdrop => {
                                backdrop.parentNode.removeChild(backdrop);
                            });
                            document.body.classList.remove('modal-open');
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                        }, 200);
                    });
                });
            }
        }
    });
    
    // Bắt sự kiện toàn cục để xử lý modal-backdrop nếu còn tồn tại
    document.addEventListener('click', function(event) {
        // Kiểm tra nếu không có modal nào đang mở nhưng vẫn còn backdrop
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length === 0) {
            const backdrops = document.querySelectorAll('.modal-backdrop');
            if (backdrops.length > 0) {
                backdrops.forEach(backdrop => {
                    backdrop.parentNode.removeChild(backdrop);
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        }
    });
    
    // Thêm sự kiện định kỳ kiểm tra và xóa modal-backdrop
    setInterval(function() {
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length === 0) {
            const backdrops = document.querySelectorAll('.modal-backdrop');
            if (backdrops.length > 0) {
                backdrops.forEach(backdrop => {
                    backdrop.parentNode.removeChild(backdrop);
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        }
    }, 1000);
}

// Auto-dismiss alerts after 5 seconds
function setupAlertDismissal() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            } else {
                fadeOut(alert);
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

// Setup responsive navigation
function setupResponsiveNavigation() {
    const navbar = document.querySelector('.navbar-collapse');
    const navToggler = document.querySelector('.navbar-toggler');
    
    if (navbar && navToggler) {
        document.addEventListener('click', function(e) {
            // Close navbar when clicking outside
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

// Initialize datetime pickers
function initializeDateTimePickers() {
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    if (dateTimeInputs) {
        dateTimeInputs.forEach(input => {
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

// Setup back to top button
function setupBackToTop() {
    // Create back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'backToTop';
    backToTopBtn.className = 'btn btn-primary back-to-top';
    backToTopBtn.innerHTML = '&uarr;';
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    
    // Scroll to top when button is clicked
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Helper function to fade out elements
function fadeOut(element) {
    let opacity = 1;
    const timer = setInterval(function() {
        if (opacity <= 0.1) {
            clearInterval(timer);
            element.style.display = 'none';
        }
        element.style.opacity = opacity;
        opacity -= 0.1;
    }, 50);
}
