document.addEventListener('DOMContentLoaded', function() {
    // Log to confirm script is loaded
    console.log('✅ Resume analyzer script loaded successfully');
    
    // --- Resume Analysis Logic for Profile Page ---
    const analyzeButtons = document.querySelectorAll('.analyze-resume-btn');
    
    console.log('Resume analyzer loaded. Found analyze buttons:', analyzeButtons.length);

    if (analyzeButtons.length === 0) {
        console.error('No analyze buttons found. Make sure the buttons have the correct class: analyze-resume-btn');
    }

    // Add Markdown parser function - depends on marked.js library that needs to be included
    function renderMarkdown(markdown) {
        // If marked library is available
        if (typeof marked !== 'undefined') {
            // Set options for marked (if needed)
            marked.setOptions({
                breaks: true,  // Convert line breaks to <br>
                gfm: true,     // GitHub flavored markdown
                headerIds: true, // Generate IDs for headings
                mangle: false  // Don't escape HTML
            });
            return marked.parse(markdown);
        } else {
            // Fallback simple markdown parser if marked is not available
            return markdown
                .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/- (.*?)$/gm, '<li>$1</li>')
                .replace(/\n\n/g, '<br><br>')
                .replace(/^(\d+)\. (.*?)$/gm, '<li>$1. $2</li>');
        }
    }

    // Function to check for presence of marked.js and load it if not available
    function ensureMarkedLoaded() {
        return new Promise((resolve, reject) => {
            if (typeof marked !== 'undefined') {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Could not load marked.js'));
            document.head.appendChild(script);
        });
    }

    analyzeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default button behavior
            
            const resumeId = this.dataset.resumeId;
            
            const resultRow = document.getElementById(`result-row-${resumeId}`);
            const resultContent = document.getElementById(`result-content-${resumeId}`);
            
            if (!resumeId || !resultRow || !resultContent) {
                console.error('Could not find resume ID or result elements for analysis.');
                alert('Could not analyze resume. Please try again or contact support.');
                return;
            }

            // Toggle result row visibility
            const isVisible = resultRow.style.display !== 'none';
            
            // Hide all other result rows first
            document.querySelectorAll('.analysis-result-row').forEach(row => {
                if (row.id !== `result-row-${resumeId}`) {
                    row.style.display = 'none';
                }
            });
            
            document.querySelectorAll('.analyze-resume-btn').forEach(btn => {
                if (btn !== this) {
                    // Reset other buttons to their original state
                    btn.disabled = false;
                    btn.innerHTML = '<i class="bi bi-clipboard-data"></i> Analyze';
                }
            });

            if (isVisible) {
                resultRow.style.display = 'none'; // Hide if already visible
                this.innerHTML = '<i class="bi bi-clipboard-data"></i> Analyze'; // Reset button text/icon
                this.disabled = false;
            } else {
                // Load marked.js if needed
                ensureMarkedLoaded()
                    .catch(error => {
                        console.warn('Marked library could not be loaded:', error);
                    })
                    .finally(() => {
                        // Show this result row and set loading state
                        resultRow.style.display = 'table-row';
                        resultContent.innerHTML = ` 
                            <div class="d-flex align-items-center text-secondary p-3">
                                <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <i>Đang phân tích CV với ChatGPT để có kết quả chi tiết và đầy đủ. Quá trình này có thể mất vài phút, vui lòng đợi...</i>
                            </div>
                        `;
                        this.disabled = true;
                        this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';

                        // Get CSRF token from cookies
                        function getCookie(name) {
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
                        
                        const csrfToken = getCookie('csrftoken');
                        
                        // Use direct call to chatbot API instead of going through the profile view
                        const baseUrl = window.location.origin;
                        const url = `${baseUrl}/chatbot/api/analyze-resume/`;
                        
                        // Fetch analysis results with proper error handling
                        fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken,
                                'X-Profile-Analysis': 'true' // Special header to indicate profile analysis
                            },
                            credentials: 'same-origin', // Include cookies in the request
                            body: JSON.stringify({
                                'resume_id': resumeId,
                                'job_category': ''
                            })
                        })
                        .then(response => {
                            if (!response.ok) {
                                return response.json().then(errorData => {
                                    throw new Error(errorData.error || `Lỗi máy chủ: ${response.status}`);
                                }).catch(err => {
                                    if (err instanceof SyntaxError) {
                                        throw new Error(`Lỗi máy chủ: ${response.status}`);
                                    }
                                    throw err;
                                });
                            }
                            return response.json();
                        })
                        .then(data => {
                            if ((data.success && data.analysis_html) || 
                                (data.resume_analysis_started && data.status === 'in_progress') ||
                                (data.status === 'completed' && data.analysis_markdown)) {
                                
                                if (data.resume_analysis_started && data.status === 'in_progress') {
                                    // Analysis started but not completed yet - show message and poll for results
                                    resultContent.innerHTML = `
                                        <div class="d-flex flex-column align-items-center text-secondary p-3">
                                            <div class="d-flex align-items-center mb-3">
                                                <div class="spinner-border text-primary me-3" role="status">
                                                    <span class="visually-hidden">Loading...</span>
                                                </div>
                                                <h5 class="m-0">Phân tích CV đang được xử lý...</h5>
                                            </div>
                                            <div class="alert alert-info w-100">
                                                <p><i class="bi bi-info-circle me-2"></i><strong>Thông báo:</strong> ${data.message || 'Đang phân tích CV với ChatGPT để có kết quả chi tiết và đầy đủ. Quá trình này có thể mất vài phút, vui lòng đợi...'}</p>
                                                <div class="progress mt-2" style="height: 5px;">
                                                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                                                </div>
                                                <p class="small mt-2 mb-0 text-muted">Chúng tôi đang sử dụng ChatGPT để phân tích CV của bạn một cách chi tiết và toàn diện. Kết quả sẽ hiển thị tự động sau khi hoàn tất.</p>
                                            </div>
                                        </div>
                                    `;
                                    
                                    // Start polling for status with longer intervals for ChatGPT analysis
                                    pollForAnalysisStatus(resumeId, data.conversation_id, resultContent);
                                    return;
                                }
                                
                                // If the analysis is marked as completed with markdown content
                                if (data.status === 'completed' && data.analysis_markdown) {
                                    // Render markdown result
                                    const renderedHtml = renderMarkdown(data.analysis_markdown);
                                    
                                    // Create a more visually appealing layout for the analysis
                                    resultContent.innerHTML = `
                                        <div class="card mb-0">
                                            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                                                <h5 class="card-title mb-0"><i class="bi bi-file-earmark-text me-2"></i>Phân tích chuyên sâu CV của bạn</h5>
                                                <div>
                                                    <button class="btn btn-sm btn-light print-analysis">
                                                        <i class="bi bi-printer me-1"></i>In
                                                    </button>
                                                    <button class="btn btn-sm btn-light ms-2 close-analysis">
                                                        <i class="bi bi-x-circle me-1"></i>Đóng
                                                    </button>
                                                </div>
                                            </div>
                                            <div class="card-body p-0">
                                                <nav>
                                                    <div class="nav nav-tabs" id="nav-tab" role="tablist">
                                                        <button class="nav-link active" id="nav-analysis-tab" data-bs-toggle="tab" data-bs-target="#nav-analysis" type="button" role="tab" aria-controls="nav-analysis" aria-selected="true">Phân tích</button>
                                                        <button class="nav-link" id="nav-strengths-tab" data-bs-toggle="tab" data-bs-target="#nav-strengths" type="button" role="tab" aria-controls="nav-strengths">Điểm mạnh</button>
                                                        <button class="nav-link" id="nav-improvements-tab" data-bs-toggle="tab" data-bs-target="#nav-improvements" type="button" role="tab" aria-controls="nav-improvements">Cải thiện</button>
                                                    </div>
                                                </nav>
                                                <div class="tab-content p-4" id="nav-tabContent">
                                                    <div class="tab-pane fade show active" id="nav-analysis" role="tabpanel" aria-labelledby="nav-analysis-tab">
                                                        <div class="cv-analysis-markdown">
                                                            ${renderedHtml}
                                                        </div>
                                                    </div>
                                                    <div class="tab-pane fade" id="nav-strengths" role="tabpanel" aria-labelledby="nav-strengths-tab">
                                                        <div id="strengths-content">
                                                            <div class="spinner-border text-primary" role="status">
                                                                <span class="visually-hidden">Loading...</span>
                                                            </div>
                                                            <span class="ms-2">Đang tải điểm mạnh...</span>
                                                        </div>
                                                    </div>
                                                    <div class="tab-pane fade" id="nav-improvements" role="tabpanel" aria-labelledby="nav-improvements-tab">
                                                        <div id="improvements-content">
                                                            <div class="spinner-border text-primary" role="status">
                                                                <span class="visually-hidden">Loading...</span>
                                                            </div>
                                                            <span class="ms-2">Đang tải điểm cần cải thiện...</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                    
                                    // Add event listeners for tab content loading
                                    const strengthsTab = resultContent.querySelector('#nav-strengths-tab');
                                    const improvementsTab = resultContent.querySelector('#nav-improvements-tab');
                                    
                                    strengthsTab.addEventListener('shown.bs.tab', function() {
                                        // Extract strengths section from the markdown content
                                        const strengthsContent = resultContent.querySelector('#strengths-content');
                                        const strengthsSection = extractSectionFromMarkdown(data.analysis_markdown, 'Điểm mạnh nổi bật', 'Notable Strengths');
                                        if (strengthsSection) {
                                            strengthsContent.innerHTML = renderMarkdown(strengthsSection);
                                        } else {
                                            strengthsContent.innerHTML = '<div class="alert alert-info">Không tìm thấy thông tin về điểm mạnh trong phân tích.</div>';
                                        }
                                    });
                                    
                                    improvementsTab.addEventListener('shown.bs.tab', function() {
                                        // Extract improvements sections from the markdown content
                                        const improvementsContent = resultContent.querySelector('#improvements-content');
                                        let improvementsSections = '';
                                        
                                        const weaknessesSection = extractSectionFromMarkdown(data.analysis_markdown, 'Điểm yếu cần cải thiện', 'Areas for Improvement');
                                        const knowledgeGapsSection = extractSectionFromMarkdown(data.analysis_markdown, 'Kiến thức cần bổ sung', 'Knowledge Gaps to Fill');
                                        const cvImprovementSection = extractSectionFromMarkdown(data.analysis_markdown, 'Đề xuất cải thiện CV', 'CV Improvement Suggestions');
                                        
                                        if (weaknessesSection) {
                                            improvementsSections += weaknessesSection + '\n\n';
                                        }
                                        
                                        if (knowledgeGapsSection) {
                                            improvementsSections += knowledgeGapsSection + '\n\n';
                                        }
                                        
                                        if (cvImprovementSection) {
                                            improvementsSections += cvImprovementSection;
                                        }
                                        
                                        if (improvementsSections) {
                                            improvementsContent.innerHTML = renderMarkdown(improvementsSections);
                                        } else {
                                            improvementsContent.innerHTML = '<div class="alert alert-info">Không tìm thấy thông tin về điểm cần cải thiện trong phân tích.</div>';
                                        }
                                    });
                                    
                                    // Add event listener for print button
                                    const printButton = resultContent.querySelector('.print-analysis');
                                    printButton.addEventListener('click', function() {
                                        const printWindow = window.open('', '_blank');
                                        printWindow.document.write(`
                                            <html>
                                                <head>
                                                    <title>Phân tích CV</title>
                                                    <style>
                                                        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                                                        h1, h2, h3, h4 { color: #333; }
                                                        h1 { border-bottom: 1px solid #ddd; padding-bottom: 10px; }
                                                        ul { margin-bottom: 20px; }
                                                        li { margin-bottom: 5px; }
                                                        @media print {
                                                            body { padding: 0; }
                                                            h1 { margin-top: 0; }
                                                        }
                                                    </style>
                                                </head>
                                                <body>
                                                    <h1>Phân tích CV</h1>
                                                    ${renderedHtml}
                                                </body>
                                            </html>
                                        `);
                                        printWindow.document.close();
                                        setTimeout(() => {
                                            printWindow.print();
                                        }, 500);
                                    });
                                    
                                    // Add some styles for the markdown content
                                    const style = document.createElement('style');
                                    style.textContent = `
                                        .cv-analysis-markdown h1 { font-size: 1.8rem; margin-top: 1rem; margin-bottom: 1rem; }
                                        .cv-analysis-markdown h2 { font-size: 1.5rem; margin-top: 1rem; margin-bottom: 0.8rem; color: #333333; }
                                        .cv-analysis-markdown h3 { font-size: 1.3rem; margin-top: 0.8rem; margin-bottom: 0.6rem; }
                                        .cv-analysis-markdown ul, .cv-analysis-markdown ol { margin-bottom: 1rem; padding-left: 2rem; }
                                        .cv-analysis-markdown li { margin-bottom: 0.5rem; }
                                        .cv-analysis-markdown strong { color: #333333; }
                                        .cv-analysis-markdown p { margin-bottom: 1rem; }
                                        .cv-analysis-markdown table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
                                        .cv-analysis-markdown th, .cv-analysis-markdown td { padding: 0.5rem; border: 1px solid #dee2e6; }
                                        .cv-analysis-markdown th { background-color: #f8f9fa; }
                                        .nav-tabs .nav-link { color: #495057; }
                                        .nav-tabs .nav-link.active { font-weight: bold; color: #333333; }
                                    `;
                                    document.head.appendChild(style);

                                    // Add event listener to close button
                                    const closeButton = resultContent.querySelector('.close-analysis');
                                    if (closeButton) {
                                        closeButton.addEventListener('click', function() {
                                            resultRow.style.display = 'none';
                                        });
                                    }
                                }
                                // Old JSON format response (fallback for backward compatibility)
                                else if (data.success && data.analysis_html) {
                                    // Format the analysis result as HTML
                                    let analysisHtml = `
                                        <div class="card mb-0">
                                            <div class="card-body">
                                                <h5 class="card-title"><i class="bi bi-file-earmark-text me-2"></i>CV Analysis Results</h5>
                                                <div class="mt-3">
                                    `;
                                    
                                    // Add overview section
                                    if (data.analysis_html.tổng_quan) {
                                        analysisHtml += `
                                            <div class="alert alert-info">
                                                <strong>Overview:</strong> ${data.analysis_html.tổng_quan}
                                            </div>
                                        `;
                                    }
                                    
                                    // Add strengths section
                                    if (data.analysis_html.điểm_mạnh && data.analysis_html.điểm_mạnh.length > 0) {
                                        analysisHtml += `
                                            <h6 class="mt-3 text-success"><i class="bi bi-check-circle me-2"></i>Strengths</h6>
                                            <ul class="list-group list-group-flush mb-3">
                                        `;
                                        
                                        data.analysis_html.điểm_mạnh.forEach(strength => {
                                            analysisHtml += `<li class="list-group-item">${strength}</li>`;
                                        });
                                        
                                        analysisHtml += `</ul>`;
                                    }
                                    
                                    // Add weaknesses section
                                    if (data.analysis_html.điểm_yếu && data.analysis_html.điểm_yếu.length > 0) {
                                        analysisHtml += `
                                            <h6 class="mt-3 text-warning"><i class="bi bi-exclamation-triangle me-2"></i>Areas to Improve</h6>
                                            <ul class="list-group list-group-flush mb-3">
                                        `;
                                        
                                        data.analysis_html.điểm_yếu.forEach(weakness => {
                                            analysisHtml += `<li class="list-group-item">${weakness}</li>`;
                                        });
                                        
                                        analysisHtml += `</ul>`;
                                    }
                                    
                                    // Add skills to improve
                                    if (data.analysis_html.kỹ_năng_cần_phát_triển && data.analysis_html.kỹ_năng_cần_phát_triển.length > 0) {
                                        analysisHtml += `
                                            <h6 class="mt-3 text-info"><i class="bi bi-lightbulb me-2"></i>Skills to Develop</h6>
                                            <ul class="list-group list-group-flush mb-3">
                                        `;
                                        
                                        data.analysis_html.kỹ_năng_cần_phát_triển.forEach(skill => {
                                            analysisHtml += `<li class="list-group-item">${skill}</li>`;
                                        });
                                        
                                        analysisHtml += `</ul>`;
                                    }
                                    
                                    // Add action items
                                    if (data.analysis_html.hành_động_cụ_thể && data.analysis_html.hành_động_cụ_thể.length > 0) {
                                        analysisHtml += `
                                            <h6 class="mt-3 text-primary"><i class="bi bi-list-check me-2"></i>Action Items</h6>
                                            <ol class="list-group list-group-numbered mb-3">
                                        `;
                                        
                                        data.analysis_html.hành_động_cụ_thể.forEach(action => {
                                            analysisHtml += `<li class="list-group-item">${action}</li>`;
                                        });
                                        
                                        analysisHtml += `</ol>`;
                                    }
                                    
                                    // Close div containers
                                    analysisHtml += `
                                                </div>
                                                <div class="text-end mt-3">
                                                    <button class="btn btn-sm btn-outline-secondary close-analysis">
                                                        <i class="bi bi-x-circle me-1"></i>Close
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                    
                                    resultContent.innerHTML = analysisHtml;
                                }
                                
                                // Add event listener to close button
                                const closeButton = resultContent.querySelector('.close-analysis');
                                if (closeButton) {
                                    closeButton.addEventListener('click', function() {
                                        resultRow.style.display = 'none';
                                    });
                                }
                            } else if (data.error) {
                                resultContent.innerHTML = `<div class="alert alert-danger mb-0"><i class="bi bi-exclamation-triangle-fill me-2"></i>${data.error}</div>`;
                            } else {
                                resultContent.innerHTML = `<div class="alert alert-danger mb-0"><i class="bi bi-exclamation-triangle-fill me-2"></i>Không nhận được kết quả phân tích hợp lệ.</div>`;
                            }
                        })
                        .catch(error => {
                            console.error('Analysis fetch error:', error);
                            resultContent.innerHTML = `<div class="alert alert-danger mb-0"><i class="bi bi-exclamation-triangle-fill me-2"></i>Lỗi khi phân tích CV: ${error.message}</div>`;
                        })
                        .finally(() => {
                            // Re-enable button but keep the icon as Analyze
                            this.disabled = false;
                            this.innerHTML = '<i class="bi bi-clipboard-data"></i> Analyze'; 
                        });
                    });
            }
        });
    });

    // Function to poll for analysis status when analysis is started but not completed
    function pollForAnalysisStatus(resumeId, conversationId, resultContent, attempt = 0) {
        // Increase maximum polling attempts to accommodate for longer GPT processing time
        const MAX_ATTEMPTS = 30; // Up to 5 minutes of processing
        
        if (attempt > MAX_ATTEMPTS) {
            resultContent.innerHTML = `<div class="alert alert-warning mb-0">
                <i class="bi bi-clock-history me-2"></i>Phân tích CV đang mất nhiều thời gian hơn dự kiến. 
                <p>ChatGPT có thể đang xử lý nhiều yêu cầu. Vui lòng thử lại sau hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục.</p>
                <button class="btn btn-sm btn-primary mt-2 retry-analysis" data-resume-id="${resumeId}">
                    <i class="bi bi-arrow-repeat me-1"></i>Thử lại
                </button>
            </div>`;
            
            // Add event listener for retry button
            const retryButton = resultContent.querySelector('.retry-analysis');
            if (retryButton) {
                retryButton.addEventListener('click', function() {
                    const resumeId = this.getAttribute('data-resume-id');
                    const analyzeButton = document.querySelector(`.analyze-resume-btn[data-resume-id="${resumeId}"]`);
                    if (analyzeButton) {
                        analyzeButton.click();
                    }
                });
            }
            
            return;
        }
        
        const baseUrl = window.location.origin;
        const url = `${baseUrl}/chatbot/api/analyze-resume/`;
        
        // Get CSRF token
        function getCookie(name) {
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
        
        const csrfToken = getCookie('csrftoken');
        
        // Dynamic polling interval - start with 5 seconds, increase gradually
        const pollInterval = Math.min(5000 + (attempt * 1000), 10000); // From 5s to max 10s
        
        // Check analysis status
        setTimeout(() => {
            // Simple loading indicator without percentage
            if (attempt % 3 === 0 && attempt > 0) {
                resultContent.innerHTML = `
                    <div class="d-flex flex-column align-items-center text-secondary p-3">
                        <div class="d-flex align-items-center mb-3">
                            <div class="spinner-border text-primary me-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <h5 class="m-0">Phân tích CV đang được xử lý...</h5>
                        </div>
                        <div class="alert alert-info w-100">
                            <p><i class="bi bi-info-circle me-2"></i><strong>Thông báo:</strong> ChatGPT đang phân tích CV của bạn.</p>
                            <p class="small mt-2 mb-0 text-muted">Quá trình này có thể mất vài phút, vui lòng đợi.</p>
                        </div>
                    </div>
                `;
            }
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Profile-Analysis': 'true'
                },
                credentials: 'same-origin',
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
                if (data.status === 'completed' && (data.analysis_markdown || data.analysis_html)) {
                    // Analysis complete - check if it's markdown or HTML format
                    if (data.is_markdown && data.analysis_markdown) {
                        // Render the markdown content
                        const renderedHtml = renderMarkdown(data.analysis_markdown);
                        
                        resultContent.innerHTML = `
                            <div class="card mb-0">
                                <div class="card-body">
                                    <h5 class="card-title mb-4"><i class="bi bi-file-earmark-text me-2"></i>CV Analysis Results</h5>
                                    <div class="cv-analysis-markdown">
                                        ${renderedHtml}
                                    </div>
                                    <div class="text-end mt-4">
                                        <button class="btn btn-sm btn-outline-secondary close-analysis">
                                            <i class="bi bi-x-circle me-1"></i>Close
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // Add some styles for the markdown content
                        const style = document.createElement('style');
                        style.textContent = `
                            .cv-analysis-markdown h1 { font-size: 1.8rem; margin-top: 1rem; margin-bottom: 1rem; }
                            .cv-analysis-markdown h2 { font-size: 1.5rem; margin-top: 1rem; margin-bottom: 0.8rem; }
                            .cv-analysis-markdown h3 { font-size: 1.3rem; margin-top: 0.8rem; margin-bottom: 0.6rem; }
                            .cv-analysis-markdown ul, .cv-analysis-markdown ol { margin-bottom: 1rem; padding-left: 2rem; }
                            .cv-analysis-markdown li { margin-bottom: 0.5rem; }
                            .cv-analysis-markdown strong { color: #333333; }
                        `;
                        document.head.appendChild(style);
                    }
                    // Legacy HTML format (for backward compatibility)
                    else if (data.analysis_html) {
                        let analysisHtml = `
                            <div class="card mb-0">
                                <div class="card-body">
                                    <h5 class="card-title"><i class="bi bi-file-earmark-text me-2"></i>CV Analysis Results</h5>
                                    <div class="mt-3">
                        `;
                        
                        // Add overview section
                        if (data.analysis_html.tổng_quan) {
                            analysisHtml += `
                                <div class="alert alert-info">
                                    <strong>Overview:</strong> ${data.analysis_html.tổng_quan}
                                </div>
                            `;
                        }
                        
                        // Add strengths section
                        if (data.analysis_html.điểm_mạnh && data.analysis_html.điểm_mạnh.length > 0) {
                            analysisHtml += `
                                <h6 class="mt-3 text-success"><i class="bi bi-check-circle me-2"></i>Strengths</h6>
                                <ul class="list-group list-group-flush mb-3">
                            `;
                            
                            data.analysis_html.điểm_mạnh.forEach(strength => {
                                analysisHtml += `<li class="list-group-item">${strength}</li>`;
                            });
                            
                            analysisHtml += `</ul>`;
                        }
                        
                        // Add weaknesses section
                        if (data.analysis_html.điểm_yếu && data.analysis_html.điểm_yếu.length > 0) {
                            analysisHtml += `
                                <h6 class="mt-3 text-warning"><i class="bi bi-exclamation-triangle me-2"></i>Areas to Improve</h6>
                                <ul class="list-group list-group-flush mb-3">
                            `;
                            
                            data.analysis_html.điểm_yếu.forEach(weakness => {
                                analysisHtml += `<li class="list-group-item">${weakness}</li>`;
                            });
                            
                            analysisHtml += `</ul>`;
                        }
                        
                        // Add skills to improve
                        if (data.analysis_html.kỹ_năng_cần_phát_triển && data.analysis_html.kỹ_năng_cần_phát_triển.length > 0) {
                            analysisHtml += `
                                <h6 class="mt-3 text-info"><i class="bi bi-lightbulb me-2"></i>Skills to Develop</h6>
                                <ul class="list-group list-group-flush mb-3">
                            `;
                            
                            data.analysis_html.kỹ_năng_cần_phát_triển.forEach(skill => {
                                analysisHtml += `<li class="list-group-item">${skill}</li>`;
                            });
                            
                            analysisHtml += `</ul>`;
                        }
                        
                        // Add action items
                        if (data.analysis_html.hành_động_cụ_thể && data.analysis_html.hành_động_cụ_thể.length > 0) {
                            analysisHtml += `
                                <h6 class="mt-3 text-primary"><i class="bi bi-list-check me-2"></i>Action Items</h6>
                                <ol class="list-group list-group-numbered mb-3">
                            `;
                            
                            data.analysis_html.hành_động_cụ_thể.forEach(action => {
                                analysisHtml += `<li class="list-group-item">${action}</li>`;
                            });
                            
                            analysisHtml += `</ol>`;
                        }
                        
                        // Close div containers
                        analysisHtml += `
                                    </div>
                                    <div class="text-end mt-3">
                                        <button class="btn btn-sm btn-outline-secondary close-analysis">
                                            <i class="bi bi-x-circle me-1"></i>Close
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        resultContent.innerHTML = analysisHtml;
                    }
                    
                    // Add event listener to close button
                    const closeButton = resultContent.querySelector('.close-analysis');
                    if (closeButton) {
                        closeButton.addEventListener('click', function() {
                            resultContent.closest('tr').style.display = 'none';
                        });
                    }
                } else if (data.status === 'failed') {
                    // Analysis failed
                    resultContent.innerHTML = `<div class="alert alert-danger mb-0">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>${data.error || 'Phân tích CV thất bại. Vui lòng thử lại sau.'}
                    </div>`;
                } else {
                    // Still processing, continue polling
                    pollForAnalysisStatus(resumeId, conversationId, resultContent, attempt + 1);
                }
            })
            .catch(error => {
                console.error('Error checking analysis status:', error);
                resultContent.innerHTML = `<div class="alert alert-danger mb-0">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>Lỗi khi kiểm tra trạng thái phân tích: ${error.message}
                    <button class="btn btn-sm btn-primary mt-2 retry-analysis" data-resume-id="${resumeId}">
                        <i class="bi bi-arrow-repeat me-1"></i>Thử lại
                    </button>
                </div>`;
                
                // Add event listener for retry button
                const retryButton = resultContent.querySelector('.retry-analysis');
                if (retryButton) {
                    retryButton.addEventListener('click', function() {
                        const resumeId = this.getAttribute('data-resume-id');
                        const analyzeButton = document.querySelector(`.analyze-resume-btn[data-resume-id="${resumeId}"]`);
                        if (analyzeButton) {
                            analyzeButton.click();
                        }
                    });
                }
            });
        }, pollInterval); // Use dynamic polling interval
    }

    // Function to extract a specific section from markdown content
    function extractSectionFromMarkdown(markdown, viTitle, enTitle) {
        // Check for both Vietnamese and English section titles
        const titleRegexes = [
            new RegExp(`## (?:\\d+\\.\\s*)?${viTitle}[\\s\\S]*?(?=## \\d+\\.|$)`, 'i'),
            new RegExp(`## (?:\\d+\\.\\s*)?${enTitle}[\\s\\S]*?(?=## \\d+\\.|$)`, 'i')
        ];
        
        for (const regex of titleRegexes) {
            const match = markdown.match(regex);
            if (match && match[0]) {
                return match[0];
            }
        }
        
        return null;
    }
});