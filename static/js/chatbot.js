// ...existing code...

// Enhanced CV selection and analysis
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('cv-file-input');
    const uploadButton = document.getElementById('cv-upload-button');
    const selectButton = document.getElementById('cv-select-button');
    const analyzeButton = document.getElementById('cv-analyze-button');
    const fileNameDisplay = document.getElementById('file-name-display');
    const uploadFileNameDisplay = document.getElementById('upload-file-name');
    
    let selectedCV = null;
    let selectedResumeId = null; // Thêm biến để lưu Resume ID
    let uploadedFile = null;
    
    // Connect upload button to file input
    if (uploadButton) {
        uploadButton.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // Handle file selection from upload
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                uploadedFile = fileInput.files[0];
                uploadFileNameDisplay.textContent = uploadedFile.name;
                
                // Clear any selected CV from the list
                const radioButtons = document.querySelectorAll('input[name="cv_selection"]');
                radioButtons.forEach(radio => radio.checked = false);
                selectedCV = null;
                selectedResumeId = null;
                fileNameDisplay.textContent = '';
            } else {
                uploadedFile = null;
                uploadFileNameDisplay.textContent = '';
            }
        });
    }
    
    // Handle CV selection from list
    if (selectButton) {
        selectButton.addEventListener('click', function() {
            const selectedRadio = document.querySelector('input[name="cv_selection"]:checked');
            
            if (selectedRadio) {
                selectedCV = selectedRadio.value;
                selectedResumeId = selectedRadio.getAttribute('data-resume-id');
                fileNameDisplay.textContent = `Đã chọn: ${selectedCV}`;
                
                // Clear any uploaded file
                if (fileInput) {
                    fileInput.value = '';
                    uploadedFile = null;
                    uploadFileNameDisplay.textContent = '';
                }
            } else {
                alert('Vui lòng chọn một CV từ danh sách');
            }
        });
    }
    
    // Handle CV analysis
    if (analyzeButton) {
        analyzeButton.addEventListener('click', function() {
            if (!selectedCV && !uploadedFile) {
                alert('Vui lòng chọn CV từ danh sách hoặc tải lên CV mới');
                return;
            }
            
            // Show loading state
            analyzeButton.disabled = true;
            analyzeButton.textContent = 'Đang phân tích...';
            
            const formData = new FormData();
            
            if (uploadedFile) {
                // If using uploaded file
                formData.append('cv_file', uploadedFile);
                formData.append('source', 'upload');
            } else {
                // If using selected CV from list
                formData.append('resume_id', selectedResumeId); // Sửa từ cv_name thành resume_id
                formData.append('source', 'selection');
            }
            
            // Get additional context if provided
            const userInput = document.querySelector('.user-input')?.value || '';
            if (userInput && userInput.includes('Phân tích CV cho')) {
                formData.append('job_category', userInput.replace('Phân tích CV cho', '').trim());
            }
            
            // Sửa endpoint API - thêm tiền tố /chatbot/api/
            fetch('/chatbot/api/analyze-resume/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken() // Thêm CSRF token
                },
                body: JSON.stringify({
                    resume_id: selectedResumeId,
                    job_category: userInput && userInput.includes('Phân tích CV cho') ? 
                        userInput.replace('Phân tích CV cho', '').trim() : '',
                    conversation_id: window.currentConversationId || ''
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Phản hồi phân tích CV:', data);
                
                // Nếu phân tích đã bắt đầu, kiểm tra trạng thái
                if (data.resume_analysis_started || data.status === 'in_progress') {
                    startStatusCheck(selectedResumeId, data.conversation_id);
                }
                
                // Reset form
                analyzeButton.disabled = false;
                analyzeButton.textContent = 'Phân tích CV';
            })
            .catch(error => {
                console.error('Error analyzing CV:', error);
                alert('Có lỗi xảy ra khi phân tích CV. Vui lòng thử lại sau.');
                analyzeButton.disabled = false;
                analyzeButton.textContent = 'Phân tích CV';
            });
        });
    }
    
    // Thêm hàm kiểm tra trạng thái phân tích
    function startStatusCheck(resumeId, conversationId) {
        const checkInterval = setInterval(() => {
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
                if (data.status === 'completed') {
                    clearInterval(checkInterval);
                    refreshChatMessages(conversationId);
                } else if (data.status === 'failed') {
                    clearInterval(checkInterval);
                    alert(`Phân tích CV thất bại: ${data.error || 'Lỗi không xác định'}`);
                }
            })
            .catch(error => {
                console.error('Lỗi kiểm tra trạng thái:', error);
                clearInterval(checkInterval);
            });
        }, 5000);
    }
    
    // Hàm làm mới tin nhắn chat
    function refreshChatMessages(conversationId) {
        fetch(`/chatbot/api/history/${conversationId}/`)
            .then(response => response.json())
            .then(data => {
                // Hiển thị tin nhắn mới nhất
                if (window.updateChatMessages && data.messages) {
                    window.updateChatMessages(data.messages);
                } else {
                    // Fallback nếu không có hàm cập nhật tin nhắn
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Lỗi làm mới tin nhắn:', error);
            });
    }
    
    // Hàm lấy CSRF token từ cookie
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // Add specific handler for resume selection buttons
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('resume-select-btn')) {
            event.preventDefault();
            const resumeId = event.target.closest('.resume-item').dataset.id;
            const conversationId = window.currentConversationId;
            
            console.log('Resume selection button clicked');
            console.log('Resume ID:', resumeId);
            console.log('Conversation ID:', conversationId);
            
            if (!resumeId) {
                console.error('No resume ID found');
                return;
            }
            
            selectResumeForAnalysis(resumeId, conversationId);
        }
    });

    // Function to handle resume analysis
    window.selectResumeForAnalysis = function(resumeId, conversationId) {
        console.log('Processing resume analysis request');
        console.log('Resume ID:', resumeId);
        console.log('Conversation ID:', conversationId);
        
        // Show loading indicator in chat
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading-message';
        loadingDiv.innerHTML = `
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span>Đang phân tích CV... Quá trình này có thể mất vài phút, vui lòng chờ.</span>
        `;
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Get CSRF token
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
        
        // Send request to server
        fetch('/chatbot/api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                resume_id: resumeId,
                conversation_id: conversationId
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Analysis response received:', data);
            
            // Remove loading indicator
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Update conversation ID if provided
            if (data.conversation_id) {
                window.currentConversationId = data.conversation_id;
            }
            
            // Display the analysis results
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            
            if (data.is_markdown || data.is_html) {
                messageDiv.innerHTML = data.message;
                
                // If it's markdown, we might need to render it
                if (data.is_markdown && typeof marked !== 'undefined') {
                    try {
                        messageDiv.innerHTML = marked.parse(data.message);
                    } catch (e) {
                        console.error('Error rendering markdown:', e);
                    }
                }
            } else {
                messageDiv.textContent = data.message;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => {
            console.error('Error analyzing resume:', error);
            
            // Remove loading indicator
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Display error message
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            messageDiv.textContent = 'Có lỗi xảy ra khi phân tích CV. Vui lòng kiểm tra đường dẫn đến file PDF và thử lại sau.';
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    };
});

// Chatbot main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chatbot.js initialized');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chatMessages');
    
    // Check if elements exist to avoid errors
    if (!chatInput || !sendButton || !chatMessages) {
        console.warn('Some chat elements are missing from DOM');
        return;
    }
    
    // Add click event to send button
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // Add keyup event to input field
    if (chatInput) {
        chatInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Initialize suggestion pills if they exist
    document.querySelectorAll('.suggestion-pill').forEach(pill => {
        pill.addEventListener('click', function() {
            if (chatInput) {
                chatInput.value = this.textContent;
                chatInput.focus();
            }
        });
    });
    
    // Function to send message to server
    function sendMessage() {
        if (!chatInput) return;
        
        const message = chatInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        appendMessage('user', message);
        
        // Clear input
        chatInput.value = '';
        
        // Show loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading-message';
        loadingDiv.innerHTML = `
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span>Đang suy nghĩ...</span>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send message to server
        fetch('/chatbot/api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                message: message,
                conversation_id: window.currentConversationId
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Update conversation ID
            if (data.conversation_id) {
                window.currentConversationId = data.conversation_id;
            }
            
            // Add bot response to chat
            if (data.is_html) {
                appendHTMLMessage('bot', data.message);
            } else {
                appendMessage('bot', data.message);
            }
            
            // Initialize any resume analysis items that were dynamically added
            setupResumeAnalysisItems();
        })
        .catch(error => {
            console.error('Error:', error);
            // Remove loading indicator
            const loadingMessage = document.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Show error message
            appendMessage('bot', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.');
        });
    }
    
    // Function to append message to chat
    window.appendMessage = function(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + (role === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to append HTML message to chat
    window.appendHTMLMessage = function(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + (role === 'user' ? 'user-message' : 'bot-message');
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Execute any scripts in the HTML message
        const scripts = messageDiv.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            Array.from(script.attributes).forEach(attr => {
                newScript.setAttribute(attr.name, attr.value);
            });
            newScript.appendChild(document.createTextNode(script.innerHTML));
            script.parentNode.replaceChild(newScript, script);
        });
    }
    
    // Function to load chat history (can be called from other scripts)
    window.loadChatHistory = function() {
        fetch('/chatbot/api/history/')
            .then(response => response.json())
            .then(data => {
                // Update conversation ID
                if (data.conversation_id) {
                    window.currentConversationId = data.conversation_id;
                }
                
                // Clear chat messages
                chatMessages.innerHTML = '';
                
                // Add messages to chat
                data.messages.forEach(message => {
                    if (message.content.includes('<') && message.content.includes('>')) {
                        appendHTMLMessage(message.role, message.content);
                    } else {
                        appendMessage(message.role, message.content);
                    }
                });
                
                // Initialize any resume analysis items that were loaded
                setupResumeAnalysisItems();
            })
            .catch(error => {
                console.error('Error loading chat history:', error);
            });
    }
    
    // Function to clear chat history (can be called from other scripts)
    window.clearChatHistory = function() {
        if (!confirm('Bạn có chắc chắn muốn xóa toàn bộ cuộc trò chuyện này?')) return;
        
        fetch('/chatbot/api/clear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Clear chat messages
                chatMessages.innerHTML = '';
                
                // Add welcome message
                appendMessage('bot', 'Xin chào! Tôi là trợ lý AI của Job Portal. Tôi có thể giúp bạn tìm kiếm việc làm, chuẩn bị CV, phỏng vấn và tư vấn nghề nghiệp. Bạn cần hỗ trợ gì?');
            }
        })
        .catch(error => {
            console.error('Error clearing chat history:', error);
        });
    }
    
    // Make the updateChatMessages function available globally for resume-analyzer.js to use
    window.updateChatMessages = function(messages) {
        // Clear chat messages
        chatMessages.innerHTML = '';
        
        // Add messages to chat
        messages.forEach(message => {
            if (message.content.includes('<') && message.content.includes('>')) {
                appendHTMLMessage(message.role, message.content);
            } else {
                appendMessage(message.role, message.content);
            }
        });
        
        // Initialize any resume analysis items that were loaded
        setupResumeAnalysisItems();
    };
    
    // Function to setup resume analysis items
    function setupResumeAnalysisItems() {
        document.querySelectorAll('.resume-analysis-item').forEach(item => {
            item.removeEventListener('click', resumeItemClickHandler); // Remove to prevent duplicates
            item.addEventListener('click', resumeItemClickHandler);
        });
    }
    
    function resumeItemClickHandler() {
        const resumeId = this.dataset.resumeId;
        const conversationId = this.dataset.conversationId || window.currentConversationId;
        if (typeof analyzeResume === 'function') {
            analyzeResume(resumeId, conversationId);
        } else {
            console.error('analyzeResume function not found. Make sure resume-analyzer.js is loaded properly.');
        }
    }
    
    // Initialize chat when page loads
    if (window.loadChatHistory) {
        window.loadChatHistory();
    }
    
    // Clear chat button event
    const clearChatButton = document.getElementById('clear-chat-button');
    if (clearChatButton) {
        clearChatButton.addEventListener('click', window.clearChatHistory);
    }
});

// Helper function for CSRF token
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
    return cookieValue || '';
}

// ...existing code...
