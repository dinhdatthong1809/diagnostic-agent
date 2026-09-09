# Trợ lý AI Hỗ trợ Chẩn đoán Ban đầu và Theo dõi Bệnh Mãn tính cho Người Cao Tuổi ở Nông thôn

Đồ án môn Tư duy AI (UIT). Hệ thống dùng kiến trúc **RAG (Retrieval-Augmented Generation) + LLM**
để hỗ trợ sàng lọc triệu chứng ban đầu và theo dõi các chỉ số sức khỏe (huyết áp, đường huyết,
nhịp tim) theo thời gian cho người cao tuổi, đặc biệt phù hợp bối cảnh nông thôn (ít tiếp cận
y tế thường xuyên).

**Đây là công cụ hỗ trợ sàng lọc, không thay thế chẩn đoán và điều trị của bác sĩ.**

## 1. Kiến trúc hệ thống

```
                     ┌────────────────────┐
 Người dùng ────────▶│   Frontend (web)    │  chat + form nhập chỉ số + biểu đồ lịch sử
                     └─────────┬──────────┘
                               │ REST API (JSON)
                     ┌─────────▼──────────┐
                     │   FastAPI backend   │
                     │  ┌────────────────┐ │
                     │  │ Rule-based     │ │  ngưỡng huyết áp / đường huyết / nhịp tim
                     │  │ threshold check│ │  (app/thresholds.py)
                     │  └────────────────┘ │
                     │  ┌────────────────┐ │
                     │  │ RAG chain      │ │  Chroma (vector DB) + HuggingFace embeddings
                     │  │ (LangChain)    │──┼──▶ truy hồi tài liệu y khoa liên quan
                     │  └───────┬────────┘ │
                     │          ▼          │
                     │   Claude (Anthropic)│  sinh nhận định sơ bộ + mức độ khẩn cấp
                     └─────────┬──────────┘
                               ▼
                     SQLite: Patient / VitalRecord / ChatMessage
```

**Vì sao kết hợp RAG + rule-based** (điểm nên nhấn mạnh khi bảo vệ):
- LLM một mình dễ "ảo giác" (hallucinate) thông tin y khoa sai → RAG buộc mô hình trả lời
  bám vào tài liệu y khoa đã được nạp sẵn (`backend/app/rag/knowledge_base/*.md`).
- Các ngưỡng nguy hiểm (vd: huyết áp ≥ 180/120) được xử lý bằng **rule cứng** thay vì để LLM tự
  suy luận, vì đây là các mốc đã được y văn xác định rõ ràng, cần độ tin cậy tuyệt đối và tốc độ
  xử lý tức thời — không phụ thuộc vào việc LLM "diễn giải" đúng hay sai.

## 2. Cấu trúc thư mục

```
backend/
  app/
    main.py              # khởi tạo FastAPI, mount routers + frontend
    config.py             # đọc biến môi trường (.env)
    database.py            # SQLAlchemy engine/session
    models.py               # Patient, VitalRecord, ChatMessage
    schemas.py                # Pydantic request/response
    thresholds.py               # rule-based cảnh báo chỉ số sức khỏe
    rag/
      chain.py                    # RAG pipeline (Chroma + Claude)
      knowledge_base/*.md           # tài liệu y khoa tham khảo (dữ liệu mẫu)
    routers/
      patients.py, vitals.py, chat.py
  scripts/ingest.py         # nạp knowledge_base vào vector store
frontend/
  index.html, static/app.js, static/style.css   # web app (chat, nhập chỉ số, biểu đồ)
```

## 3. Cài đặt & chạy thử

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt

cp ../.env.example ../.env
# mở file .env, điền ANTHROPIC_API_KEY của bạn

# Bước 1: nạp tài liệu y khoa vào vector store (chạy 1 lần, hoặc lại mỗi khi sửa knowledge_base)
python -m scripts.ingest

# Bước 2: chạy server (API + frontend cùng một cổng)
uvicorn app.main:app --reload
```

Mở trình duyệt tại `http://localhost:8000` để dùng web app.

## 4. Luồng sử dụng demo cho báo cáo

1. Tạo bệnh nhân mẫu (tên, tuổi, bệnh nền — vd "tăng huyết áp").
2. Tab **Nhập chỉ số sức khỏe**: nhập huyết áp 190/125 → hệ thống cảnh báo "Khẩn cấp" ngay
   (minh chứng rule-based threshold hoạt động độc lập với LLM).
3. Tab **Trò chuyện chẩn đoán**: mô tả triệu chứng (vd "đau đầu dữ dội, nhìn mờ") → AI trả lời có
   cấu trúc: Nhận định sơ bộ / Mức độ khẩn cấp / Khuyến nghị / Lưu ý, dựa trên tài liệu đã nạp.
4. Tab **Lịch sử & biểu đồ**: nhập vài lần đo khác nhau để thấy biểu đồ xu hướng huyết áp/đường
   huyết theo thời gian — minh họa phần "theo dõi bệnh mãn tính" của đề tài.

## 5. Giới hạn cần nêu rõ khi bảo vệ (để không bị "hỏi khó")

- **Knowledge base hiện là dữ liệu mẫu do nhóm biên soạn**, chưa qua kiểm định của chuyên gia y tế
  — cần thay bằng nguồn y văn chính thức (Bộ Y tế, WHO, phác đồ điều trị) trước khi triển khai thật.
- Hệ thống **không có xác thực người dùng thật** (chưa làm auth) — phù hợp phạm vi demo đồ án,
  cần bổ sung nếu triển khai thực tế vì liên quan dữ liệu sức khỏe nhạy cảm.
- Embedding chạy local (sentence-transformers) để tránh phụ thuộc thêm một API trả phí; LLM sinh
  câu trả lời dùng Claude (Anthropic) — cần API key và kết nối mạng khi chạy.
- Đây là công cụ **sàng lọc**, không phải chẩn đoán xác định — mọi câu trả lời của AI đều phải
  kèm khuyến nghị gặp bác sĩ khi cần, đã ràng buộc trong system prompt (`app/rag/chain.py`).
