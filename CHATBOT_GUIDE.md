# Hướng dẫn sử dụng AI Chatbot

## Tổng quan

AI Chatbot là trợ lý thông minh giúp bạn thao tác với hệ thống phân tích comment ngân hàng **bằng ngôn ngữ tự nhiên** (tiếng Việt).

## Cài đặt Ollama (Bắt buộc)

```bash
# 1. Download Ollama
# Windows: https://ollama.com/download

# 2. Cài đặt Ollama

# 3. Pull model (chọn 1 trong các options sau)
ollama pull llama3.2:3b    # Khuyên dùng (3GB)
ollama pull llama3.2:1b    # Máy yếu (1GB)
ollama pull gemma2:2b      # Alternative (2GB)

# 4. Verify
ollama list
```

## Các Tools Chatbot Hỗ trợ

### 1. **Query & Analysis Tools**

#### 📊 Get Summary Stats
```
User: Cho tôi thống kê tổng quan
User: Tổng hợp dữ liệu hiện tại
```

**Output:**
- Total comments
- Unique topics
- Average sentiment score
- Negative comments count & ratio

#### 🔍 Query Analysis Data
```
User: Có bao nhiêu comment về chuyển tiền?
User: Lọc comments theo topic "App Performance"
User: Tìm comments negative về đăng nhập
```

**Filters:**
- Topic
- Sentiment
- Custom queries

#### 🚨 Get Top Issues
```
User: Top 5 vấn đề tiêu cực là gì?
User: Cho tôi xem 10 issues nghiêm trọng nhất
```

**Parameters:**
- `limit`: Số lượng issues (default: 5)

#### ⚠️ Check Anomalies
```
User: Kiểm tra anomalies
User: Có bất thường nào không?
User: Phát hiện drift
```

**Detects:**
- Sentiment distribution drift
- Topic distribution drift
- Negative sentiment spikes

---

### 2. **Training Tools**

#### 🎓 Train Sentiment Model
```
User: Train sentiment model từ file data/labeled/sentiment_sample.csv
User: Huấn luyện model sentiment với dữ liệu mới
```

**Requirements:**
- CSV file với columns: `comment`, `sentiment_label`
- File path từ thư mục project

**Output:**
- Accuracy
- F1 Macro
- F1 Weighted

#### 🎓 Train Topic Model
```
User: Train topic model từ data/labeled/topic_sample.csv
User: Huấn luyện model topic
```

**Requirements:**
- CSV file với columns: `comment`, `topic_label`

**Output:**
- Accuracy
- F1 Macro

---

### 3. **Export Tools**

#### 💾 Export Report (CSV)
```
User: Export report ra CSV
User: Xuất dữ liệu phân tích
User: Lưu kết quả vào file my_report
```

**Parameters:**
- `format`: "csv" hoặc "json"
- `filename`: Tên file tùy chọn (auto-generate nếu không có)

**Output:**
- CSV: Full data với topics & sentiments
- JSON: Summary statistics

#### 📄 Export Report (JSON)
```
User: Export báo cáo JSON
User: Xuất summary JSON
```

**JSON contains:**
- Total comments
- Unique topics count
- Average sentiment
- Sentiment distribution
- Topic distribution

---

### 4. **Alert Tools**

#### 📧 Create Email Alert
```
User: Gửi email alert về negative spike
User: Tạo email alert: "Phát hiện 50% negative comments"
```

**Requirements:** SMTP config trong `.env`

#### 💬 Create Slack Alert
```
User: Gửi Slack alert
User: Thông báo Slack về vấn đề nghiêm trọng
```

**Requirements:** Slack webhook trong `.env`

#### 📝 Create Log Alert
```
User: Log alert này
User: Ghi lại cảnh báo
```

**Always works** - không cần config

---

### 5. **Management Tools**

#### 🗑️ Clean Models
```
User: Xóa topic models
User: Clean sentiment models
User: Xóa tất cả models
```

**Options:**
- `topic`: Xóa topic models
- `sentiment`: Xóa sentiment models
- `all`: Xóa tất cả

**Use case:** Force retrain với data mới

---

### 6. **Full Analysis Tool**

#### 🔄 Run Full Analysis
```
User: Phân tích file data/raw/comments.csv
User: Chạy analysis đầy đủ cho file mới
User: Analyze comments_new.csv
```

**Steps:**
1. Load & validate CSV
2. Preprocess data
3. Topic modeling (auto clustering)
4. Sentiment analysis
5. Return summary

**Auto-updates:** Chatbot data context

---

## Ví dụ Conversations

### Conversation 1: Quick Stats
```
👤 Cho tôi thống kê tổng quan

🤖 [Calls: get_summary_stats]
   📊 Summary Statistics:
   - Total comments: 150
   - Unique topics: 8
   - Average sentiment: -0.3
   - Negative comments: 67 (44.7%)
```

### Conversation 2: Find Issues
```
👤 Top 3 vấn đề tiêu cực là gì?

🤖 [Calls: get_top_issues with limit=3]
   🚨 Top 3 Negative Issues:

   1. Topic: Transfer Issues | Sentiment: Very Negative
      Comment: Chuyển tiền bị lỗi không thành công...

   2. Topic: App Performance | Sentiment: Negative
      Comment: App lag giật liên tục...

   3. Topic: Login Issues | Sentiment: Very Negative
      Comment: Không thể đăng nhập vào app...
```

### Conversation 3: Train Model
```
👤 Train sentiment model từ data/labeled/sentiment_sample.csv

🤖 [Calls: train_sentiment_model]
   ✅ Sentiment model trained successfully!
   - Accuracy: 0.850
   - F1 Macro: 0.832
   - F1 Weighted: 0.847

   Model đã sẵn sàng sử dụng!
```

### Conversation 4: Export & Alert
```
👤 Export report ra CSV với tên report_final

🤖 [Calls: export_report]
   ✅ Report exported to: data/raw/report_final.csv

👤 Gửi email alert về negative spike

🤖 [Calls: create_alert]
   ✅ Email alert sent successfully!
```

### Conversation 5: Full Workflow
```
👤 Phân tích file data/raw/new_comments.csv

🤖 [Calls: run_full_analysis]
   🔄 Starting analysis on data/raw/new_comments.csv...

   ✅ Step 1: Loaded 200 comments
   ✅ Step 2: Preprocessed data
   ⚙️ Training new topic model...
   ✅ Step 3: Topic analysis complete
   ⚙️ Using fallback sentiment analysis...
   ✅ Step 4: Sentiment analysis complete

   📊 Analysis Summary:
   - Total comments: 200
   - Unique topics: 6
   - Avg sentiment: -0.5
   - Negative comments: 95 (47.5%)

👤 Top 5 issues là gì?

🤖 [Calls: get_top_issues]
   [Shows top 5 negative issues from the new data]

👤 Kiểm tra anomalies

🤖 [Calls: check_anomalies]
   ⚠️ Detected 2 anomalies:
   - negative_spike: Negative sentiment spike: +20%
   - topic_drift: Topic distribution drift: 0.18

👤 Tạo log alert về vấn đề này

🤖 [Calls: create_alert]
   ✅ Alert logged:
   Negative spike detected: 47.5% negative comments

👤 Export báo cáo JSON

🤖 [Calls: export_report]
   ✅ Report exported to: data/raw/analysis_report_20250125_143052.json
```

---

## Tips & Best Practices

### ✅ DO:
- Nói rõ ràng, cụ thể
- Dùng file paths đầy đủ từ thư mục project
- Kiểm tra data trước khi train model
- Export report định kỳ

### ❌ DON'T:
- Đừng dùng path tuyệt đối bên ngoài project
- Đừng train với < 3 samples
- Đừng quên clean models khi cần retrain

### 💡 Pro Tips:
1. **Combine tools**: "Phân tích file mới, tìm top issues, rồi gửi alert"
2. **Use shortcuts**: "Stats" thay vì "Cho tôi thống kê tổng quan"
3. **Clear chat** khi bắt đầu task mới để tránh confusion

---

## Troubleshooting

### Chatbot không phản hồi
**Solution:**
```bash
# Check Ollama running
ollama list

# Restart Ollama
ollama serve
```

### Tool call failed
**Check:**
1. File path đúng chưa?
2. CSV có đúng columns không?
3. Data đủ lớn chưa (≥ 3 samples)?

### Email/Slack alert không hoạt động
**Check `.env`:**
```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

---

## Model Options

Thay đổi model trong `app.py`:

```python
# Line ~316
ChatbotAgent(st.session_state.df_pandas, model="llama3.2:1b")  # Faster
ChatbotAgent(st.session_state.df_pandas, model="llama3.1:8b")  # Smarter
```

**Trade-offs:**
- 1B: Nhanh nhưng ít thông minh
- 3B: Cân bằng (khuyên dùng)
- 8B: Chậm nhưng rất thông minh

---

## Advanced Usage

### Custom System Prompt

Edit `src/chatbot/agent.py` → `SYSTEM_PROMPT`

### Add New Tool

1. Add to `TOOLS_DEFINITION` trong `tools.py`
2. Implement method trong `ChatbotTools`
3. Add case trong `execute_tool()`

### Multi-step Workflows

Chatbot tự động chain tools:
```
User: Phân tích file mới, tìm issues, và alert

AI: [Runs]
    1. run_full_analysis()
    2. get_top_issues()
    3. create_alert()
```

---

Enjoy your AI Chatbot! 🚀
