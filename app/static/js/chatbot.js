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
});

// ...existing code...
