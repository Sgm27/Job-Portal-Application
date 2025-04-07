document.addEventListener('DOMContentLoaded', function() {
    // Create chat widget HTML structure
    const chatWidgetHTML = `
        <div class="chat-widget-container">
            <div class="chat-widget-button" id="chat-widget-button">
                <i class="bi bi-chat-dots-fill"></i>
            </div>
            <div class="chat-widget-popup" id="chat-widget-popup">
                <div class="chat-widget-header">
                    <h3>Trợ lý AI của Job Portal</h3>
                    <button class="chat-widget-close" id="chat-widget-close">×</button>
                </div>
                <div class="chat-widget-messages" id="chat-widget-messages">
                    <!-- Messages will be populated here -->
                </div>
                <div class="chat-widget-input-container">
                    <input type="text" class="chat-widget-input" id="chat-widget-input" placeholder="Hỏi điều gì đó...">
                    <button class="chat-widget-send" id="chat-widget-send">
                        <i class="bi bi-send-fill"></i>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Insert chat widget to the body
    document.body.insertAdjacentHTML('beforeend', chatWidgetHTML);

    // Get widget elements
    const chatButton = document.getElementById('chat-widget-button');
    const chatPopup = document.getElementById('chat-widget-popup');
    const chatClose = document.getElementById('chat-widget-close');
    const chatInput = document.getElementById('chat-widget-input');
    const chatSend = document.getElementById('chat-widget-send');
    const chatMessages = document.getElementById('chat-widget-messages');

    // Add welcome message
    addMessageToWidget('assistant', 'Xin chào! Tôi là trợ lý ảo của Job Portal. Tôi có thể giúp gì cho bạn về tìm kiếm việc làm, viết CV hay quá trình ứng tuyển?');

    // Toggle chat popup when button is clicked
    chatButton.addEventListener('click', function() {
        chatPopup.classList.toggle('active');
        if (chatPopup.classList.contains('active')) {
            loadConversationHistory();
            chatInput.focus();
            
            // Remove unread indicator if exists
            const unreadIndicator = chatButton.querySelector('.unread-indicator');
            if (unreadIndicator) {
                unreadIndicator.remove();
            }
        }
    });

    // Close chat popup when close button is clicked
    chatClose.addEventListener('click', function() {
        chatPopup.classList.remove('active');
    });

    // Send message on button click
    chatSend.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    // Function to send message
    function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        // Add user message to UI
        addMessageToWidget('user', message);
        
        // Clear input
        chatInput.value = '';
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add typing indicator
        const typingElement = document.createElement('div');
        typingElement.className = 'chat-widget-message assistant chat-widget-typing';
        typingElement.innerHTML = `
            <div class="chat-widget-message-content">
                <div class="chat-widget-typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send to API
        fetch('/chatbot/api/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            const typingIndicators = document.querySelectorAll('.chat-widget-typing');
            typingIndicators.forEach(indicator => {
                indicator.remove();
            });
            
            // Add bot response to UI
            if (data.message) {
                addMessageToWidget('assistant', data.message);
                
                // If chat is not open, show unread indicator
                if (!chatPopup.classList.contains('active')) {
                    if (!chatButton.querySelector('.unread-indicator')) {
                        const unreadIndicator = document.createElement('div');
                        unreadIndicator.className = 'unread-indicator';
                        unreadIndicator.innerHTML = '1';
                        chatButton.appendChild(unreadIndicator);
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            
            // Remove typing indicator
            const typingIndicators = document.querySelectorAll('.chat-widget-typing');
            typingIndicators.forEach(indicator => {
                indicator.remove();
            });
            
            // Show error message
            addMessageToWidget('assistant', 'Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại sau.');
        });
    }

    // Function to add message to widget
    function addMessageToWidget(role, content) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-widget-message ${role}`;
        
        const now = new Date();
        const time = now.getHours().toString().padStart(2, '0') + ':' + 
                    now.getMinutes().toString().padStart(2, '0');
        
        // Process markdown formatting
        const formattedContent = formatMarkdown(content);
        
        messageElement.innerHTML = `
            <div class="chat-widget-message-content">
                ${formattedContent}
                <div class="chat-widget-time">${time}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to format markdown text
    function formatMarkdown(text) {
        if (!text) return '';
        
        // Handle headings
        text = text.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
        text = text.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        text = text.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        text = text.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
        
        // Handle bold text (**text**)
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Handle italic text (*text*)
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Handle code blocks (```code```)
        text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Handle inline code (`code`)
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Handle line breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    // Function to load conversation history
    function loadConversationHistory() {
        fetch('/chatbot/api/history/')
            .then(response => response.json())
            .then(data => {
                chatMessages.innerHTML = '';
                
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        const date = new Date(msg.timestamp);
                        const time = date.getHours().toString().padStart(2, '0') + ':' + 
                                    date.getMinutes().toString().padStart(2, '0');
                        
                        const messageElement = document.createElement('div');
                        messageElement.className = `chat-widget-message ${msg.role}`;
                        
                        // Format the content with markdown
                        const formattedContent = formatMarkdown(msg.content);
                        
                        messageElement.innerHTML = `
                            <div class="chat-widget-message-content">
                                ${formattedContent}
                                <div class="chat-widget-time">${time}</div>
                            </div>
                        `;
                        
                        chatMessages.appendChild(messageElement);
                    });
                    
                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                } else {
                    // If no messages, add welcome message
                    addMessageToWidget('assistant', 'Xin chào! Tôi là trợ lý ảo của Job Portal. Tôi có thể giúp gì cho bạn về tìm kiếm việc làm, viết CV hay quá trình ứng tuyển?');
                }
            })
            .catch(error => console.error('Error loading conversation history:', error));
    }

    // Function to get CSRF token
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
});