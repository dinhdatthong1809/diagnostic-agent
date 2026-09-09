"""RAG pipeline: truy hồi tài liệu y khoa (Chroma + HuggingFace embeddings)
rồi đưa vào Claude (Anthropic) để sinh nhận định sơ bộ + mức độ khẩn cấp.
"""
from typing import List, Dict

from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, CHROMA_DIR

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

SYSTEM_PROMPT = """Bạn là trợ lý AI hỗ trợ SÀNG LỌC BAN ĐẦU và THEO DÕI sức khỏe cho người \
cao tuổi ở nông thôn. Bạn KHÔNG phải bác sĩ và KHÔNG đưa ra chẩn đoán xác định.

QUY TẮC BẮT BUỘC:
- Chỉ dựa trên "Tài liệu y khoa tham khảo" và "Thông tin bệnh nhân" được cung cấp bên dưới, \
không tự bịa thêm thông tin y khoa nằm ngoài tài liệu.
- Luôn nêu rõ đây là nhận định sơ bộ, không phải chẩn đoán xác định.
- Nếu triệu chứng/chỉ số khớp với dấu hiệu nguy hiểm trong tài liệu, phải cảnh báo mức \
"Khẩn cấp" và khuyên đến cơ sở y tế ngay, không trì hoãn.
- Dùng ngôn ngữ đơn giản, dễ hiểu, phù hợp với người cao tuổi và người thân của họ.
- Luôn kết thúc bằng lời nhắc: đây chỉ là công cụ hỗ trợ sàng lọc, không thay thế khám bác sĩ.

Trả lời theo đúng cấu trúc:
1. Nhận định sơ bộ:
2. Mức độ khẩn cấp (Thấp / Trung bình / Cao / Khẩn cấp):
3. Khuyến nghị hành động:
4. Lưu ý:
"""

_embeddings = None
_vectordb = None
_llm = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _embeddings


def get_vectordb():
    global _vectordb
    if _vectordb is None:
        _vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=get_embeddings())
    return _vectordb


def get_retriever(k: int = 4):
    return get_vectordb().as_retriever(search_kwargs={"k": k})


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatAnthropic(
            model=ANTHROPIC_MODEL,
            api_key=ANTHROPIC_API_KEY,
            max_tokens=1024,
        )
    return _llm


def format_patient_summary(patient, recent_vitals: List) -> str:
    lines = [f"Tên: {patient.name}", f"Tuổi: {patient.age or 'không rõ'}"]
    if patient.conditions:
        lines.append(f"Bệnh nền đã biết: {patient.conditions}")
    if recent_vitals:
        lines.append("Chỉ số đo gần đây (mới nhất trước):")
        for v in recent_vitals:
            parts = []
            if v.systolic is not None and v.diastolic is not None:
                parts.append(f"HA {v.systolic}/{v.diastolic} mmHg")
            if v.glucose is not None:
                parts.append(f"Đường huyết {v.glucose} mg/dL")
            if v.heart_rate is not None:
                parts.append(f"Nhịp tim {v.heart_rate} lần/phút")
            lines.append(f"- {v.measured_at.strftime('%d/%m/%Y %H:%M')}: {', '.join(parts)} (mức: {v.severity})")
    else:
        lines.append("Chưa có dữ liệu đo chỉ số sức khỏe.")
    return "\n".join(lines)


def build_prompt(question: str, context_docs: List, patient_summary: str, chat_history: List[Dict]) -> str:
    context_text = "\n\n".join(d.page_content for d in context_docs) or "(không tìm thấy tài liệu liên quan)"
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in chat_history[-6:]) or "(chưa có)"
    return f"""{SYSTEM_PROMPT}

### Thông tin bệnh nhân:
{patient_summary}

### Tài liệu y khoa tham khảo:
{context_text}

### Lịch sử trò chuyện gần đây:
{history_text}

### Câu hỏi/triệu chứng hiện tại của bệnh nhân:
{question}
"""


def ask(question: str, patient_summary: str, chat_history: List[Dict]):
    retriever = get_retriever()
    docs = retriever.invoke(question)
    prompt = build_prompt(question, docs, patient_summary, chat_history)
    response = get_llm().invoke(prompt)
    sources = sorted({d.metadata.get("source", "unknown") for d in docs})
    return response.content, sources
