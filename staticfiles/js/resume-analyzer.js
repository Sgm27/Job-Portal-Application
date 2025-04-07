/**
 * Resume Analysis JavaScript Module
 * Handles the analysis of user resumes via the chatbot interface
 */

// Debug flag - change to false in production
const DEBUG = true;

// Debug logger function
function logDebug(message, data = null) {
    if (DEBUG) {
        if (data) {
            console.log(`[CV Analyzer] ${message}`, data);
        } else {
            console.log(`[CV Analyzer] ${message}`);
        }
    }
}

// Function to analyze a selected resume
function analyzeResume(resumeId, conversationId) {
    logDebug(`Starting CV analysis for resumeId=${resumeId}, conversationId=${conversationId}`);
    
    // Get job category from input if available (user might specify a job field in their message)
    const userInput = document.getElementById('chat-input')?.value || '';
    let jobCategory = '';
    
    // Extract job category if the user specified one in their message
    if (userInput && userInput.toLowerCase().includes('cho vị trí')) {
        jobCategory = userInput.split('cho vị trí')[1].trim();
    } else if (userInput && userInput.toLowerCase().includes('cho ngành')) {
        jobCategory = userInput.split('cho ngành')[1].trim();
    } else if (userInput && userInput.toLowerCase().includes('cho lĩnh vực')) {
        jobCategory = userInput.split('cho lĩnh vực')[1].trim();
    }
    
    // Show loading indicator in the chat
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        // Remove any existing loading message first
        const existingLoading = chatMessages.querySelector('.resume-loading-message');
        if (existingLoading) {
            existingLoading.remove();
        }
        
        // Add the loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message resume-loading-message';
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
    
    // Clear the input field
    if (document.getElementById('chat-input')) {
        document.getElementById('chat-input').value = '';
    }
    
    // Disable all resume selection buttons to prevent multiple submissions
    document.querySelectorAll('.select-resume-btn').forEach(btn => {
        btn.disabled = true;
        btn.classList.add('disabled');
    });

    const csrfToken = getCsrfToken();
    logDebug(`CSRF token obtained: ${csrfToken ? 'Yes' : 'No'}`);
    
    // Send request to analyze the resume
    logDebug('Sending analysis request to server', {
        resumeId,
        conversationId,
        jobCategory
    });
    
    fetch('/chatbot/api/analyze-resume/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            resume_id: resumeId,
            conversation_id: conversationId,
            job_category: jobCategory
        })
    })
    .then(response => {
        logDebug(`Server response status: ${response.status}`);
        // Check if the response is ok (status in the range 200-299)
        if (!response.ok) {
            // If not OK, try to parse the error message from the response body
            return response.json().then(errorData => {
                // Throw an error with the message from the server response
                logDebug('Server returned error:', errorData);
                throw new Error(errorData.error || `Lỗi máy chủ: ${response.status}`);
            }).catch(() => {
                 // If parsing JSON fails or no error message, throw a generic error
                 throw new Error(`Yêu cầu phân tích thất bại với mã trạng thái: ${response.status}`);
            });
        }
        // If response is OK, parse the JSON body
        return response.json();
    })
    .then(data => {
        logDebug('Resume analysis initial response:', data);
        
        // Update the loading message to show that processing has started
        updateLoadingMessage('Phân tích đã bắt đầu... Đang xử lý CV của bạn.');
        
        // Start checking the analysis status
        // Use conversation_id from the response if it was newly created
        startAnalysisStatusCheck(resumeId, data.conversation_id || conversationId);
    })
    .catch(error => {
        console.error('Error starting resume analysis:', error);
        // Display the specific error message caught from the .then block or fetch failure
        showErrorMessage('Không thể bắt đầu phân tích CV: ' + error.message);
        // Remove loading indicator on error
        removeLoadingMessage(); 
        enableResumeButtons();
    });
}

// Function to remove the loading message
function removeLoadingMessage() {
    logDebug('Removing loading message');
    const loadingMessage = document.querySelector('.resume-loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Update the loading message with new text
function updateLoadingMessage(message) {
    logDebug(`Updating loading message: ${message}`);
    const loadingMessage = document.querySelector('.resume-loading-message');
    if (loadingMessage) {
        const messageSpan = loadingMessage.querySelector('span');
        if (messageSpan) {
            messageSpan.innerHTML = `<strong>${message}</strong>`;
        }
    }
}

// Re-enable resume selection buttons
function enableResumeButtons() {
    logDebug('Re-enabling resume selection buttons');
    document.querySelectorAll('.select-resume-btn').forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('disabled');
    });
}

// Function to periodically check the status of resume analysis
function startAnalysisStatusCheck(resumeId, conversationId) {
    // Initial delay before first check
    setTimeout(() => {
        checkAnalysisStatus(resumeId, conversationId, 0);
    }, 3000); // Start checking after 3 seconds
}

// Function to check analysis status
function checkAnalysisStatus(resumeId, conversationId, attempt) {
    logDebug(`Checking analysis status: attempt ${attempt + 1}`);
    
    // Get CSRF token for the request
    const csrfToken = getCsrfToken();
    
    fetch('/chatbot/api/analyze-resume/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            resume_id: resumeId,
            conversation_id: conversationId,
            check_status: true
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        logDebug('Analysis status response:', data);
        
        if (data.status === 'completed') {
            // Analysis complete
            logDebug('Analysis complete!');
            
            // Refresh chat messages to show the result
            refreshChatMessages(conversationId);
            
            // Remove loading indicator
            removeLoadingMessage();
        }
        else if (data.status === 'failed') {
            // Analysis failed
            logDebug('Analysis failed:', data.error);
            
            // Show error message
            showErrorMessage(data.error || 'Phân tích CV thất bại. Vui lòng thử lại sau.');
            
            // Remove loading indicator
            removeLoadingMessage();
        }
        else if (attempt >= 30) {
            // Timeout after 30 attempts (about 5 minutes)
            logDebug('Analysis timeout after 30 attempts');
            
            showErrorMessage('Phân tích CV đang mất nhiều thời gian hơn dự kiến. Vui lòng thử lại sau.');
            
            // Remove loading indicator
            removeLoadingMessage();
        }
        else {
            // Still in progress, update loading message and continue checking
            if (attempt % 3 === 0 && attempt > 0) {
                updateLoadingMessage('ChatGPT đang phân tích CV của bạn. Vui lòng đợi...');
            }
            
            // Continue checking with dynamic interval
            setTimeout(() => {
                checkAnalysisStatus(resumeId, conversationId, attempt + 1);
            }, Math.min(5000 + (attempt * 500), 10000)); // From 5s to max 10s
        }
    })
    .catch(error => {
        logDebug('Error checking analysis status:', error);
        
        if (attempt < 5) {
            // Try a few more times if there are network errors
            setTimeout(() => {
                checkAnalysisStatus(resumeId, conversationId, attempt + 1);
            }, 5000);
        } else {
            showErrorMessage('Không thể kiểm tra trạng thái phân tích. Vui lòng thử lại sau.');
            removeLoadingMessage();
        }
    });
}

// Function to refresh chat messages with new content
function refreshChatMessages(conversationId) {
    logDebug(`Refreshing chat messages for conversationId=${conversationId}`);
    fetch(`/chatbot/api/history/${conversationId ? conversationId + '/' : ''}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            logDebug('Refreshed message data:', data);
            
            // Remove the loading message if it exists
            const loadingMessage = document.querySelector('.resume-loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Use the built-in update messages function if available
            if (window.updateChatMessages && data.messages) {
                logDebug(`Updating chat with ${data.messages.length} messages`);
                window.updateChatMessages(data.messages);
            } else {
                // Fallback to manual update if needed
                logDebug('Using fallback updateChatMessagesManually function');
                updateChatMessagesManually(data.messages);
            }
        })
        .catch(error => {
            console.error('Error refreshing chat messages:', error);
            showErrorMessage('Không thể cập nhật cuộc hội thoại. Vui lòng làm mới trang.');
        });
}

// Manual function to update chat messages if needed
function updateChatMessagesManually(messages) {
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages || !messages) return;
    
    // Clear existing messages
    chatMessages.innerHTML = '';
    
    // Add all messages
    messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = msg.role === 'user' ? 'message user-message' : 'message bot-message';
        
        // Check if content is HTML
        if (msg.content.includes('<') && msg.content.includes('>')) {
            messageDiv.innerHTML = msg.content;
        } else {
            messageDiv.textContent = msg.content;
        }
        
        chatMessages.appendChild(messageDiv);
    });
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to display error messages in the chat
function showErrorMessage(errorMsg) {
    logDebug(`Showing error message: ${errorMsg}`);
    
    // Remove any existing loading message first
    const loadingMessage = document.querySelector('.resume-loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
    
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message error';
        errorDiv.innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <strong>Lỗi:</strong> ${errorMsg}
            </div>
        `;
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Helper function to get CSRF token from cookies
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

// Direct delegated event listener for all select-resume-btn clicks
// This will catch all clicks whether buttons exist now or are added later
document.addEventListener('click', function(event) {
    // Check if the clicked element has the select-resume-btn class
    if (event.target && event.target.classList.contains('select-resume-btn')) {
        // Call the handler function
        handleSelectResumeButtonClick(event.target);
    }
});

// Function to handle select resume button clicks
function handleSelectResumeButtonClick(button) {
    // Get data from button
    const resumeId = button.dataset.resumeId;
    const resumeTitle = button.dataset.resumeTitle || 'Selected CV';
    
    // Log the click event for debugging
    logDebug('Resume selection button clicked', {
        resumeId,
        resumeTitle,
        button: button.outerHTML
    });
    
    if (!resumeId) {
        logDebug('Missing resumeId attribute on button');
        showErrorMessage('Cannot analyze CV: Missing resume ID');
        return;
    }
    
    // Find conversation ID 
    let conversationId = null;
    // Try to get from window.currentConversationId (set in chatbot.html)
    if (window.currentConversationId) {
        conversationId = window.currentConversationId;
    }
    
    // Add confirmation message to chat
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        const confirmationDiv = document.createElement('div');
        confirmationDiv.className = 'message bot-message confirmation-message';
        confirmationDiv.innerHTML = `
            <div class="alert alert-success mb-0">
                <div class="d-flex align-items-center">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <div>
                        <strong>Đã chọn CV: ${resumeTitle}</strong>
                        <p class="mb-0 small">Bắt đầu phân tích...</p>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(confirmationDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Disable all selection buttons
    document.querySelectorAll('.select-resume-btn').forEach(btn => {
        btn.disabled = true;
        btn.classList.add('disabled');
    });
    
    // Start the analysis
    analyzeResume(resumeId, conversationId);
}

// Initialize resume analysis event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    logDebug('DOM loaded, initializing CV analyzer');
    
    // Handle any legacy resume analysis items (for backward compatibility)
    function setupResumeAnalysisItems() {
        const items = document.querySelectorAll('.resume-analysis-item');
        if (items.length > 0) {
            logDebug(`Setting up ${items.length} legacy resume analysis items`);
            
            items.forEach(item => {
                item.removeEventListener('click', resumeItemClickHandler);
                item.addEventListener('click', resumeItemClickHandler);
            });
        }
    }
    
    function resumeItemClickHandler() {
        const resumeId = this.dataset.resumeId;
        const conversationId = this.dataset.conversationId;
        
        if (resumeId && conversationId) {
            analyzeResume(resumeId, conversationId);
        }
    }
    
    // Setup legacy items for backward compatibility
    setupResumeAnalysisItems();
    
    // Log that we're ready to handle resume analysis
    logDebug('Resume analyzer initialization complete');
});