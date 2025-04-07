$(document).ready(function() {
    // CV analysis button click handler
    $('.analyze-cv-btn').on('click', function() {
        const cvId = $(this).data('cv-id');
        const analyzeBtn = $(this);
        
        // Disable button and show loading state
        analyzeBtn.prop('disabled', true);
        analyzeBtn.html('<i class="fa fa-spinner fa-spin"></i> Đang phân tích...');
        
        // Send AJAX request to analyze CV - Using updated endpoint
        $.ajax({
            url: '/chatbot/api/analyze-resume/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'resume_id': cvId,
                'job_category': '',
                'user_type': 'employer'
            }),
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            success: function(response) {
                // Show success message
                showNotification('Phân tích CV hoàn tất!', 'success');
                
                // If analysis was started successfully but is still processing
                if (response.resume_analysis_started || response.status === 'in_progress') {
                    startStatusCheck(cvId, response.conversation_id);
                }
                // If results are immediately available
                else if (response.message) {
                    $('#analysis-result-' + cvId).html(response.message);
                    $('#analysis-container-' + cvId).removeClass('d-none');
                }
            },
            error: function() {
                showNotification('Có lỗi xảy ra khi phân tích CV!', 'error');
                // Reset button state
                analyzeBtn.prop('disabled', false);
                analyzeBtn.html('Chọn');
            }
        });
    });
    
    // Function to check the status of an analysis in progress
    function startStatusCheck(resumeId, conversationId) {
        const checkInterval = setInterval(() => {
            $.ajax({
                url: '/chatbot/api/analyze-resume/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    'resume_id': resumeId,
                    'conversation_id': conversationId,
                    'check_status': true
                }),
                headers: {
                    'X-CSRFToken': getCsrfToken()
                },
                success: function(data) {
                    if (data.status === 'completed') {
                        clearInterval(checkInterval);
                        // Update UI with analysis results
                        if (data.message) {
                            $('#analysis-result-' + resumeId).html(data.message);
                            $('#analysis-container-' + resumeId).removeClass('d-none');
                        }
                        // Reset button state
                        $('.analyze-cv-btn[data-cv-id="' + resumeId + '"]').prop('disabled', false)
                            .html('Chọn');
                    } else if (data.status === 'failed') {
                        clearInterval(checkInterval);
                        showNotification(`Phân tích CV thất bại: ${data.error || 'Lỗi không xác định'}`, 'error');
                        // Reset button state
                        $('.analyze-cv-btn[data-cv-id="' + resumeId + '"]').prop('disabled', false)
                            .html('Chọn');
                    }
                },
                error: function() {
                    clearInterval(checkInterval);
                    showNotification('Không thể kiểm tra trạng thái phân tích CV', 'error');
                    // Reset button state
                    $('.analyze-cv-btn[data-cv-id="' + resumeId + '"]').prop('disabled', false)
                        .html('Chọn');
                }
            });
        }, 5000);
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val() || document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1] || '';
    }
    
    // Helper function to show notifications
    function showNotification(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const notification = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;
        
        // Add notification to the page
        $('#notification-area').html(notification);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            $('.alert').alert('close');
        }, 5000);
    }
});
