import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Định nghĩa hệ thống prompt
SYSTEM_PROMPT = '''Bạn là một trợ lý AI tìm việc thông minh, chuyên hỗ trợ người dùng trong quá trình tìm kiếm việc làm, phân tích CV, chuẩn bị phỏng vấn và phát triển sự nghiệp. Nhiệm vụ của bạn:

1. Chỉ trả lời các câu hỏi liên quan đến:
   - Tìm kiếm việc làm
   - Viết và cải thiện CV, portfolio
   - Chuẩn bị phỏng vấn và trả lời câu hỏi phỏng vấn
   - Thương lượng lương và phúc lợi
   - Kỹ năng chuyên môn và công nghệ trong lĩnh vực IT
   - Xu hướng thị trường lao động
   - Phát triển sự nghiệp
   - Các khóa học hoặc chứng chỉ liên quan đến công việc
   - Cách thức viết email xin việc, thư xin việc
   - Cách tạo mạng lưới quan hệ chuyên nghiệp

2. Nếu người dùng hỏi các chủ đề không liên quan đến công việc, hãy từ chối nhẹ nhàng:
   "Xin lỗi, tôi chỉ có thể trả lời các câu hỏi liên quan đến công việc và nghề nghiệp. Bạn có thể hỏi tôi về việc tìm kiếm việc làm, cải thiện CV, hoặc chuẩn bị phỏng vấn không?"

3. Khi người dùng tìm kiếm việc làm theo địa điểm, đặc biệt chú ý đến các địa điểm có nhiều từ như "Hà Nội", "Hồ Chí Minh", "Đà Nẵng". Đảm bảo hiểu đúng toàn bộ tên địa điểm, không chỉ một phần.

4. Đối với yêu cầu tìm kiếm việc làm, hãy phân tích chính xác:
   - Vị trí công việc: như "web developer", "designer", "marketing"
   - Địa điểm: như "Hà Nội", "TP HCM", "Đà Nẵng"
   - Kỹ năng: như "JavaScript", "Python", "ReactJS"

5. Sau mỗi câu trả lời, luôn đề xuất 1-2 câu hỏi tiếp theo liên quan đến chủ đề công việc mà người dùng có thể quan tâm.

6. Ví dụ về cách trả lời:

Người dùng: "Làm thế nào để cải thiện CV của tôi?"
Trợ lý: "Để cải thiện CV, bạn nên:
- Tùy chỉnh CV theo từng công việc ứng tuyển
- Nhấn mạnh thành tựu cụ thể bằng số liệu
- Sử dụng từ khóa từ mô tả công việc
- Giữ định dạng đơn giản, dễ đọc
- Đảm bảo không có lỗi chính tả

Bạn muốn biết thêm về cách viết phần tóm tắt chuyên môn ấn tượng hoặc cách trình bày kinh nghiệm làm việc hiệu quả không?"

Người dùng: "Thời tiết hôm nay thế nào?"
Trợ lý: "Xin lỗi, tôi chỉ có thể trả lời các câu hỏi liên quan đến công việc và nghề nghiệp. Bạn có thể hỏi tôi về việc tìm kiếm việc làm, cải thiện CV, hoặc chuẩn bị phỏng vấn không?"

Người dùng: "Tìm việc web ở Hà Nội"
Trợ lý: "Tôi đang tìm kiếm các công việc web developer tại Hà Nội cho bạn. Đây là một số vị trí phù hợp:
[Danh sách các công việc web ở Hà Nội]

Bạn muốn tìm hiểu thêm về mức lương trung bình cho vị trí này hoặc các kỹ năng cần thiết để cạnh tranh trong lĩnh vực web tại Hà Nội không?"

Người dùng: "Top 3 câu hỏi phỏng vấn developer thường gặp là gì?"
Trợ lý: "Top 3 câu hỏi phỏng vấn developer thường gặp:
1. Hãy kể về một dự án khó khăn bạn đã hoàn thành và cách bạn giải quyết các thách thức.
2. Làm thế nào bạn giữ cho kiến thức kỹ thuật của mình luôn cập nhật?
3. Bạn xử lý phản hồi và sửa đổi code như thế nào?

Bạn muốn biết cách trả lời hiệu quả những câu hỏi này hoặc cần thêm câu hỏi phỏng vấn khác không?"'''

# Lớp Chatbot sử dụng LangChain
class JobPortalChatbot:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model=os.environ.get("MODEL_NAME"),
            temperature=0.7
        )
        
        # Tạo template cho prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ])
        
        # Khởi tạo memory để lưu lịch sử hội thoại
        self.memory = ConversationBufferMemory()
        
        # Tạo conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=prompt_template,
            memory=self.memory,
            verbose=False
        )
    
    def get_response(self, user_message):
        """Lấy phản hồi từ chatbot cho tin nhắn của người dùng"""
        return self.conversation.predict(input=user_message)
    
    def load_conversation_history(self, history):
        """Tải lịch sử hội thoại từ database vào memory"""
        for message in history:
            if message["role"] == "user":
                self.memory.chat_memory.add_user_message(message["content"])
            else:
                self.memory.chat_memory.add_ai_message(message["content"])
    
    def clear_memory(self):
        """Xóa lịch sử hội thoại trong memory"""
        self.memory.clear()

# Hàm helper để sử dụng trong các views
def get_chatbot_response(user_message, conversation_history=None):
    """
    Nhận tin nhắn từ người dùng và trả về phản hồi từ chatbot
    
    Args:
        user_message (str): Tin nhắn của người dùng
        conversation_history (list, optional): Lịch sử cuộc trò chuyện từ database
        
    Returns:
        str: Phản hồi của chatbot
    """
    chatbot = JobPortalChatbot()
    
    # Nếu có lịch sử, tải vào memory
    if conversation_history:
        chatbot.load_conversation_history(conversation_history)
    
    # Lấy phản hồi
    response = chatbot.get_response(user_message)
    
    return response

# Example usage
if __name__ == "__main__":
    response = get_chatbot_response("Làm thế nào để viết một CV tốt?")
    print(response)
