# Hướng dẫn cài đặt Ollama cho AI Chatbot

## Ollama là gì?

Ollama cho phép chạy Large Language Models (LLMs) như Llama, Mistral, v.v. **hoàn toàn FREE** và **LOCAL** trên máy tính của bạn.

## Bước 1: Cài đặt Ollama

### Windows:

1. Download Ollama từ: https://ollama.com/download
2. Chạy file installer `OllamaSetup.exe`
3. Ollama sẽ tự động khởi động và chạy trong background

### macOS:

```bash
brew install ollama
```

### Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Bước 2: Pull model

Mở terminal/command prompt và chạy:

```bash
ollama pull llama3.2:3b
```

**Các model khác bạn có thể dùng:**
- `llama3.2:3b` - Nhẹ, nhanh (3GB RAM) - **Khuyên dùng**
- `llama3.2:1b` - Rất nhẹ (1GB RAM) - Cho máy yếu
- `gemma2:2b` - Alternative (2GB RAM)
- `llama3.1:8b` - Mạnh hơn (8GB RAM) - Nếu máy khỏe

## Bước 3: Kiểm tra Ollama đang chạy

```bash
ollama list
```

Bạn sẽ thấy danh sách models đã pull.

Hoặc test chat:
```bash
ollama run llama3.2:3b
```

Nhập "xin chào" để test → Ctrl+D để thoát

## Bước 4: Chạy Chatbot trong App

```bash
cd C:\Users\PC\bank-text-demo
streamlit run app.py
```

Vào tab **💬 AI Chatbot** và bắt đầu chat!

## Troubleshooting

### Lỗi: "Ollama không khả dụng"

**Solution 1:** Kiểm tra Ollama đang chạy
```bash
# Windows
tasklist | findstr ollama

# Linux/macOS
ps aux | grep ollama
```

**Solution 2:** Start Ollama manually
```bash
ollama serve
```

**Solution 3:** Kiểm tra port 11434
```bash
curl http://localhost:11434/api/tags
```

### Lỗi: Model quá chậm

- Dùng model nhỏ hơn: `ollama pull llama3.2:1b`
- Update app.py để dùng model mới:
  ```python
  ChatbotAgent(df_pandas, model="llama3.2:1b")
  ```

### Lỗi: Out of memory

- Close các app khác
- Dùng model 1B hoặc 2B
- Tăng RAM nếu có thể

## Tính năng Chatbot

**Chatbot có thể:**
- ✅ Truy vấn data: "Cho tôi thống kê tổng quan"
- ✅ Tìm issues: "Top 5 vấn đề tiêu cực là gì?"
- ✅ Check anomalies: "Kiểm tra anomalies"
- ✅ Lọc data: "Có bao nhiêu comment về chuyển tiền?"
- ✅ Quản lý models: "Xóa topic models"

**Ví dụ conversation:**

```
User: Cho tôi thống kê tổng quan
AI: 📊 Summary Statistics:
    - Total comments: 100
    - Unique topics: 8
    - Average sentiment: -0.5
    - Negative comments: 45 (45%)

User: Top 3 vấn đề tiêu cực là gì?
AI: 🚨 Top 3 Negative Issues:
    1. Topic: Transfer Issues | Sentiment: Very Negative
       Comment: Chuyển tiền bị lỗi...
    2. Topic: App Performance | Sentiment: Negative
       Comment: App lag giật...
    ...

User: Kiểm tra anomalies
AI: ⚠️ Detected 2 anomalies:
    - sentiment_drift: Sentiment distribution drift detected: 0.234
    - negative_spike: Negative sentiment spike: +15%
```

## Thay đổi model trong code

Mở `app.py`, tìm dòng:
```python
st.session_state.chatbot_agent = ChatbotAgent(st.session_state.df_pandas)
```

Sửa thành:
```python
st.session_state.chatbot_agent = ChatbotAgent(st.session_state.df_pandas, model="llama3.2:1b")
```

## Resources

- Ollama docs: https://ollama.com/docs
- Model library: https://ollama.com/library
- GitHub: https://github.com/ollama/ollama
