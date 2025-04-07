// CV Analysis Integration for Chatbot
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chatbot Resume Analyzer initialized');
    
    // Function to handle resume selection
    window.handleResumeSelection = function(button) {
        console.log('Resume selection handler called with button:', button);
        
        const resumeId = button.getAttribute('data-resume-id');
        let resumeTitle = button.getAttribute('data-resume-title');
        
        if (!resumeTitle) {
            // Try to get title from nearby elements if not directly on button
            const row = button.closest('tr');
            if (row) {
                const titleCell = row.querySelector('td:first-child');
                if (titleCell) {
                    resumeTitle = titleCell.textContent.trim();
                }
            }
        }
        
        if (!resumeId) {
            console.error('Resume ID not found');
            return;
        }

        // Create context input for job specification
        const contextInputHtml = `
            <div class="job-context-input-container mt-3 mb-3">
                <div class="form-group">
                    <label for="job-context-input"><strong>Thêm thông tin về vị trí/lĩnh vực công việc (tùy chọn):</strong></label>
                    <input type="text" id="job-context-input" class="form-control mt-2" 
                        placeholder="Ví dụ: Frontend Developer, Data Analyst, vị trí quản lý...">
                    <small class="form-text text-muted">
                        Cung cấp thông tin thêm giúp phân tích CV phù hợp hơn với vị trí bạn mong muốn.
                    </small>
                </div>
                <div class="d-flex justify-content-between mt-3">
                    <button class="btn btn-secondary cancel-analysis-btn">Hủy</button>
                    <button class="btn btn-primary analyze-resume-btn" data-resume-id="${resumeId}">
                        <i class="bi bi-search me-2"></i>Phân tích CV
                    </button>
                </div>
            </div>
        `;
        
        // Find bot message containing CV selection options
        const botMessages = document.querySelectorAll('.bot-message');
        let targetMessage = null;
        
        // Find the last bot message with CV selection buttons
        for (let i = botMessages.length - 1; i >= 0; i--) {
            if (botMessages[i].querySelector('.select-resume-btn')) {
                targetMessage = botMessages[i];
                break;
            }
        }
        
        if (targetMessage) {
            // Store original content for restoration if needed
            if (!targetMessage.hasAttribute('data-original-content')) {
                targetMessage.setAttribute('data-original-content', targetMessage.innerHTML);
            }
            
            // Show selected CV and context input
            const selectedResumeHeader = `
                <div class="selected-resume-info alert alert-info">
                    <i class="bi bi-file-earmark-text me-2"></i>
                    <strong>CV đã chọn:</strong> ${resumeTitle || 'Selected CV'}
                </div>
            `;
            targetMessage.innerHTML = selectedResumeHeader + contextInputHtml;
            
            // Add event listeners to new buttons
            const analyzeButton = targetMessage.querySelector('.analyze-resume-btn');
            if (analyzeButton) {
                analyzeButton.addEventListener('click', function() {
                    const jobContext = targetMessage.querySelector('#job-context-input').value.trim();
                    analyzeResumeFromChatbot(resumeId, jobContext, window.currentConversationId);
                });
            }
            
            const cancelButton = targetMessage.querySelector('.cancel-analysis-btn');
            if (cancelButton) {
                cancelButton.addEventListener('click', function() {
                    // Restore original content
                    targetMessage.innerHTML = targetMessage.getAttribute('data-original-content');
                    
                    // Re-attach click handlers to restored buttons
                    targetMessage.querySelectorAll('.select-resume-btn').forEach(btn => {
                        btn.addEventListener('click', function() {
                            window.handleResumeButtonClick(btn);
                        });
                    });
                });
            }
        } else {
            console.error('Could not find message containing CV selection options');
        }
    };
    
    // Function to analyze resume from chatbot interface
    function analyzeResumeFromChatbot(resumeId, jobContext, conversationId) {
        console.log('Starting CV analysis:', { resumeId, jobContext, conversationId });
        
        // Show loading state
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message bot-message loading-message';
            loadingDiv.innerHTML = `
                <div class="alert alert-info mb-0 d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm text-primary me-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span><strong>Đang phân tích CV...</strong> Quá trình này có thể mất 30-60 giây. Vui lòng đợi.</span>
                </div>
            `;
            chatMessages.appendChild(loadingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Start analysis request
        fetch('/chatbot/api/analyze-resume/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                resume_id: resumeId,
                job_category: jobContext,
                conversation_id: conversationId
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Analysis response:', data);
            
            // Remove loading message
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            if (data.error) {
                // Show error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message bot-message';
                errorDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        <strong>Lỗi:</strong> ${data.error}
                    </div>
                `;
                chatMessages.appendChild(errorDiv);
            } else if (data.resume_analysis_started) {
                // Start polling for status
                pollAnalysisStatus(resumeId, data.conversation_id);
            }
        })
        .catch(error => {
            console.error('Error analyzing resume:', error);
            // Show error message in chat
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message bot-message';
            errorDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <strong>Lỗi:</strong> Không thể phân tích CV. Vui lòng thử lại sau.
                </div>
            `;
            chatMessages.appendChild(errorDiv);
            
            // Remove loading message
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        });
    }
    
    // Function to poll for analysis status
    function pollAnalysisStatus(resumeId, conversationId, attempts = 0) {
        console.log(`Polling for CV analysis status, attempt ${attempts + 1}`);
        
        fetch('/chatbot/api/analyze-resume/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                resume_id: resumeId,
                conversation_id: conversationId,
                check_status: true
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Poll response:', data);
            
            if (data.status === 'completed' && data.message) {
                // Remove any existing loading message
                const loadingMessages = document.querySelectorAll('.loading-message, .analysis-processing');
                loadingMessages.forEach(msg => msg.closest('.bot-message')?.remove());
                
                // Show the completed analysis
                const chatMessages = document.querySelector('.chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot-message';
                messageDiv.innerHTML = data.message;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else if (data.status === 'failed') {
                // Remove loading message
                const loadingMessages = document.querySelectorAll('.loading-message, .analysis-processing');
                loadingMessages.forEach(msg => msg.closest('.bot-message')?.remove());
                
                // Show error message
                const chatMessages = document.querySelector('.chat-messages');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message bot-message';
                errorDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        <strong>Lỗi:</strong> ${data.error || 'Phân tích CV thất bại. Vui lòng thử lại sau.'}
                    </div>
                `;
                chatMessages.appendChild(errorDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else if (attempts >= 30) {
                // Timeout after 30 attempts (about 5 minutes)
                const chatMessages = document.querySelector('.chat-messages');
                const timeoutDiv = document.createElement('div');
                timeoutDiv.className = 'message bot-message';
                timeoutDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-clock-history me-2"></i>
                        Phân tích CV đang mất nhiều thời gian hơn dự kiến. Vui lòng thử lại sau.
                    </div>
                `;
                chatMessages.appendChild(timeoutDiv);
            } else {
                // Continue polling
                setTimeout(() => {
                    pollAnalysisStatus(resumeId, conversationId, attempts + 1);
                }, Math.min(5000 + (attempts * 500), 10000)); // Dynamic polling intervals
                
                // Update loading message periodically to show activity
                if (attempts % 3 === 0 && attempts > 0) {
                    const loadingMessages = document.querySelectorAll('.loading-message');
                    loadingMessages.forEach(msg => {
                        msg.innerHTML = `
                            <div class="alert alert-info mb-0 d-flex align-items-center">
                                <div class="spinner-border spinner-border-sm text-primary me-3" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <span><strong>Đang phân tích CV...</strong> ChatGPT đang phân tích CV của bạn. Vui lòng đợi.</span>
                            </div>
                        `;
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error checking analysis status:', error);
        });
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});