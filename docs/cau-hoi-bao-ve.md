# Câu hỏi phản biện & gợi ý trả lời khi bảo vệ đồ án

Đề tài: **Trợ lý AI Hỗ trợ Chẩn đoán Ban đầu và Theo dõi Bệnh Mãn tính cho Người Cao Tuổi ở Nông thôn**
(RAG + LLM, FastAPI + LangChain + Claude)

---

## Nhóm 1 — Kiến trúc & kỹ thuật RAG

**1. RAG là gì, vì sao chọn RAG thay vì fine-tune?**
> RAG (Retrieval-Augmented Generation) là kỹ thuật cho LLM "tra cứu" tài liệu liên quan trước khi trả lời, thay vì chỉ dựa vào kiến thức đã học sẵn. Em chọn RAG vì: (1) fine-tune cần dữ liệu huấn luyện lớn, tốn chi phí, khó cập nhật; (2) RAG cho phép cập nhật kiến thức y khoa chỉ bằng cách thêm tài liệu mới, không cần huấn luyện lại; (3) RAG giảm hallucination vì câu trả lời có căn cứ tài liệu cụ thể, có thể trích nguồn.

**2. Pipeline retrieval hoạt động thế nào? Vì sao k=4?**
> Câu hỏi của người dùng được chuyển thành vector embedding, so khớp cosine similarity với các đoạn tài liệu đã embedding sẵn trong Chroma, lấy ra top-k đoạn gần nhất đưa vào prompt cho Claude. k=4 là số lượng đủ để có ngữ cảnh đa dạng mà không làm prompt quá dài/loãng — em chọn qua thử nghiệm, có thể điều chỉnh tùy độ dài tài liệu.

**3. Vì sao dùng embedding local thay vì API?**
> Để giảm chi phí (không tốn thêm phí gọi API cho mỗi lần embedding) và giảm phụ thuộc mạng cho bước index tài liệu — vốn chỉ cần chạy một lần. Model `all-MiniLM-L6-v2` nhỏ, nhanh, đủ tốt cho bài toán retrieval quy mô nhỏ như đồ án.

**4. Chroma là gì, so với FAISS/Pinecone?**
> Chroma là vector database mã nguồn mở, lưu trữ và tìm kiếm vector embedding theo độ tương đồng. Em chọn Chroma vì dễ tích hợp với LangChain, chạy local không cần server riêng (khác Pinecone là dịch vụ cloud trả phí), phù hợp quy mô đồ án. FAISS chỉ là thư viện index (không có persistence/quản lý metadata tiện như Chroma).

**5. Nếu câu hỏi không liên quan tài liệu thì sao?**
> Retriever sẽ trả về đoạn ít liên quan nhất có sẵn (vì cơ chế top-k luôn trả đủ k đoạn), không tự động "biết" là không liên quan. Đây là giới hạn cần cải thiện: có thể thêm ngưỡng similarity score, nếu điểm quá thấp thì báo "ngoài phạm vi tư vấn" thay vì ép trả lời.

**6. Vì sao tách riêng rule-based threshold?**
> Vì ngưỡng nguy hiểm (huyết áp ≥180/120, đường huyết <54...) là con số y khoa đã được xác định rõ ràng trong y văn, cần độ chính xác tuyệt đối và phản hồi tức thời — không nên phụ thuộc vào việc LLM "diễn giải" đúng ngưỡng mỗi lần, vì LLM có thể tính sai hoặc diễn đạt không nhất quán. Rule-based đảm bảo cảnh báo luôn đúng 100% với input số liệu cụ thể.

## Nhóm 2 — Đánh giá chất lượng

**7. Làm sao biết AI trả lời đúng?**
> Đồ án ở mức prototype nên chưa có bộ test định lượng đầy đủ; em đã test thủ công với các ca triệu chứng mẫu (tăng huyết áp, hạ đường huyết...) đối chiếu tài liệu tham khảo. Hướng tiếp theo: xây tập câu hỏi-đáp án chuẩn cùng chuyên gia y tế để đo Precision/Recall.

**8. Làm sao giảm hallucination?**
> Ràng buộc trong system prompt: chỉ được trả lời dựa trên tài liệu retrieval và thông tin bệnh nhân được cung cấp, không tự bịa thêm. Đây là ràng buộc "mềm" (prompt-based), chưa có cơ chế kiểm chứng cứng (như so khớp câu trả lời với tài liệu nguồn) — là hướng cải thiện tiếp theo.

**9. Nếu 2 tài liệu mâu thuẫn nhau?**
> Hiện tại chưa xử lý — LLM sẽ tự dung hòa hoặc ưu tiên đoạn xuất hiện trước trong prompt. Đây là hạn chế cần thêm metadata độ ưu tiên/nguồn tin cậy cho tài liệu.

**10. Đã test bao nhiêu ca thực tế?**
> Trả lời trung thực theo những gì bạn đã thật sự làm — vd: "Em đã test một số ca mẫu tự soạn dựa trên tài liệu y khoa, chưa có dữ liệu ca bệnh thực tế từ cơ sở y tế do giới hạn thời gian và quyền truy cập dữ liệu y tế."

## Nhóm 3 — Dữ liệu

**11. Nguồn dữ liệu y khoa từ đâu?**
> Trả lời trung thực: tài liệu hiện tại do em tự biên soạn dựa trên kiến thức y khoa phổ thông (ngưỡng huyết áp/đường huyết theo khuyến cáo chung), **chưa được chuyên gia y tế kiểm định** — đây là giới hạn em đã nêu rõ trong báo cáo, hướng tiếp theo là phối hợp với bác sĩ/trạm y tế để xác thực nội dung.

**12. Dữ liệu bệnh nhân lưu trữ/bảo mật thế nào?**
> Hiện lưu trong SQLite local, chưa có mã hóa hay xác thực người dùng — phù hợp phạm vi demo đồ án. Nếu triển khai thật cần: mã hóa dữ liệu, xác thực người dùng, tuân thủ quy định bảo vệ dữ liệu cá nhân/y tế.

**13. Dữ liệu có đại diện cho nông thôn Việt Nam chưa?**
> Chưa — tài liệu hiện là kiến thức y khoa tổng quát, chưa phản ánh đặc thù dịch tễ từng vùng miền. Hướng cải thiện: hợp tác với trạm y tế địa phương để bổ sung dữ liệu phù hợp bối cảnh cụ thể.

## Nhóm 4 — Đạo đức, pháp lý, an toàn

**14. Nếu AI chẩn đoán sai thì ai chịu trách nhiệm?**
> Hệ thống được thiết kế là **công cụ hỗ trợ sàng lọc**, không đưa ra chẩn đoán xác định — mọi câu trả lời đều kèm khuyến nghị gặp bác sĩ. Trách nhiệm y khoa cuối cùng vẫn thuộc về bác sĩ khám trực tiếp; AI chỉ giúp phát hiện sớm để người bệnh không bỏ lỡ thời điểm đi khám.

**15. Ranh giới hành nghề y trái phép ở đâu?**
> Hệ thống không kê đơn thuốc, không khẳng định bệnh cụ thể, chỉ đưa ra "khả năng" và mức độ khẩn cấp kèm khuyến nghị hành động (theo dõi thêm/đi khám/cấp cứu) — tương tự vai trò của công cụ triage/sàng lọc, không thay thế chẩn đoán lâm sàng.

**16. Làm sao tránh người dùng quá tin AI?**
> Mọi câu trả lời đều có disclaimer bắt buộc (đã ràng buộc cứng trong system prompt và hiển thị cố định trên UI), nhắc rõ đây không phải chẩn đoán y khoa.

## Nhóm 5 — Tính khả thi thực tế

**17. Người già khó dùng công nghệ?**
> Đây là hạn chế của bản demo hiện tại (giao diện chat/form text). Hướng phát triển: thêm giọng nói, hoặc để người thân/nhân viên y tế cộng đồng nhập hộ.

**18. Không có mạng thì sao?**
> Hiện tại cần mạng để gọi API Claude. Hướng giải quyết: cache sẵn câu trả lời cho các triệu chứng phổ biến, hoặc dùng model nhỏ chạy local (offline) cho các trường hợp cơ bản, đồng bộ dữ liệu khi có mạng.

**19. Ai chi trả chi phí API?**
> Đồ án là proof-of-concept; nếu triển khai thật cần mô hình tài chính cụ thể (ngân sách y tế công, tài trợ, hoặc dùng model open-source chạy local để giảm chi phí vận hành theo request).

## Nhóm 6 — So sánh & đóng góp

**20. Khác biệt so với Ada Health, Babylon...?**
> Điểm khác biệt em nên nhấn: tập trung cụ thể vào **người cao tuổi nông thôn Việt Nam** — kết hợp cả sàng lọc triệu chứng (RAG) VÀ theo dõi liên tục chỉ số bệnh mãn tính theo thời gian (rule-based alert + biểu đồ xu hướng), trong khi nhiều app quốc tế chỉ tập trung một trong hai, và không tối ưu cho bối cảnh hạn chế công nghệ/kết nối của nông thôn.

**21. Nếu có 1 tuần cải thiện thêm, làm gì trước?**
> Nên chọn 1 câu trả lời thật (không cần học thuộc) — vd: "Em sẽ ưu tiên kiểm định lại nội dung tài liệu y khoa với chuyên gia, vì đó là nền tảng quyết định độ tin cậy của cả hệ thống."

---

## Lưu ý khi trả lời thật

Đừng cố "gồng" trả lời hoàn hảo cho câu hỏi bạn chưa làm — thầy cô đánh giá cao việc **thừa nhận giới hạn rõ ràng + có hướng giải quyết cụ thể** hơn là né tránh hoặc bịa. Câu 7, 10, 11, 13 nên trả lời trung thực theo đúng những gì bạn thực sự đã làm trong đồ án.

---

## Hướng phát triển tương lai & giải pháp nâng cấp

### Nâng cấp RAG
| Vấn đề hiện tại | Giải pháp nâng cấp |
|---|---|
| Retrieval đơn giản (top-k theo cosine similarity) | Thêm **re-ranking** (vd: cross-encoder) sau khi lấy top-k để lọc lại đoạn liên quan nhất |
| Knowledge base ít (5 file mẫu) | Mở rộng bằng tài liệu y khoa chính thức: phác đồ Bộ Y tế, WHO, sách giáo khoa nội khoa — càng nhiều càng cần chunking + metadata tốt (nguồn, ngày cập nhật) |
| Không đánh giá chất lượng RAG | Xây **bộ test câu hỏi-đáp án chuẩn** (do chuyên gia soạn), đo độ chính xác retrieval (Recall@k) và độ đúng câu trả lời cuối (có thể dùng LLM-as-judge) |
| Embedding cố định, không cập nhật | Thử nghiệm embedding model tiếng Việt chuyên biệt để cải thiện độ chính xác truy hồi với câu hỏi tiếng Việt |
| Không có bộ nhớ dài hạn về pattern bệnh nhân | Thêm **retrieval theo lịch sử bệnh nhân** (không chỉ tài liệu y khoa tĩnh) — biến RAG thành "hybrid": tài liệu y khoa + hồ sơ cá nhân hoá |

### Nâng cấp ứng dụng (app)
- **Giọng nói hai chiều**: speech-to-text đầu vào + text-to-speech đầu ra, vì người già khó gõ chữ.
- **Xác thực & phân quyền**: tài khoản người thân/nhân viên y tế cộng đồng quản lý hộ, phân quyền xem dữ liệu.
- **Cảnh báo chủ động**: gửi SMS/Zalo cho người thân hoặc trạm y tế xã khi phát hiện chỉ số nguy hiểm (hiện tại mới chỉ hiển thị trên UI).
- **Hoạt động offline/mạng yếu**: cache câu hỏi thường gặp, đồng bộ dữ liệu khi có mạng trở lại.
- **Mobile app** (React Native/Flutter) thay vì chỉ web, dễ tiếp cận hơn ở nông thôn.
- **Tích hợp thiết bị đo tự động** (máy đo huyết áp/đường huyết Bluetooth) thay vì nhập tay, giảm sai sót.

### Nâng cấp dữ liệu
- Hợp tác với **trạm y tế xã/bệnh viện** để lấy dữ liệu thật (ẩn danh) làm tập test, tăng độ tin cậy khi báo cáo.
- Xây **quy trình cập nhật knowledge base định kỳ** (không hard-code tĩnh mãi), có versioning tài liệu.
- Thu thập **feedback loop**: sau mỗi lần AI tư vấn, hỏi người dùng/bác sĩ "chẩn đoán này đúng không" để tích lũy dữ liệu đánh giá và cải thiện dần.
- Nghiên cứu tuân thủ **quy định bảo vệ dữ liệu sức khỏe** (Nghị định về dữ liệu cá nhân của Việt Nam) trước khi triển khai thật.

Nên chọn ra **2-3 điểm nâng cấp tâm đắc nhất** để nói sâu trong phần "hướng phát triển" của slide — nói dàn trải hết sẽ loãng, hội đồng thường hỏi xoáy vào 1 điểm đã nêu.
