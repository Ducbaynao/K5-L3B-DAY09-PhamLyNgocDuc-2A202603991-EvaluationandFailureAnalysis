# Judge audit

Chạy kiểm tra:
```bash
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

## Bảng tổng hợp Calibration

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | ĐẠT (κ=0.757 ≥ 0.6, P=0.857 ≥ 0.8, R=0.800 ≥ 0.7) | **dùng** (trong phạm vi replay) |
| helpful | 100 | 0.375 | 1.000 | 0.300 | KHÔNG ĐẠT (κ=0.375 < 0.6, R=0.300 < 0.7) | **loại** |

---

## ≥5 case audit thủ công (đối chiếu toàn bộ nội dung reply)

> **Quy ước nguồn gốc thông tin:**
> - **[Bằng chứng CSV/Code]**: Ghi nhận trực tiếp từ cột `note`, `human_failure` trong CSV hoặc sự kiện trace trong code.
> - **[Suy luận phân tích]**: Diễn giải và đề xuất cải tiến rubric bổ sung dựa trên quan sát văn bản.

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & Đề xuất sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` (tone) | PASS | FAIL | Người đúng | **Reply**: *"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."*<br>• **[Bằng chứng CSV]**: Ghi chú CSV ghi nhận: `xưng 'em' + 'nha', quá suồng sã với khách; judge coi là thân thiện`.<br>• **[Suy luận phân tích]**: Judge không phân biệt được phong cách giao tiếp cá nhân thân mật với quy chuẩn dịch vụ khách hàng (CS) thương hiệu.<br>• **Sửa rubric**: Cấm xưng hô tự phát (`anh/em/nha`), bắt buộc dùng đại từ quy chuẩn (`LogiX - anh/chị` hoặc `quý khách`). |
| 2 | `H-029` (tone) | PASS | FAIL | Người đúng | **Reply**: *"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."*<br>• **[Bằng chứng CSV]**: Ghi chú CSV ghi nhận: `giọng ra lệnh ('không cần nhắn thêm'); judge chỉ thấy 'Dạ, vui lòng'`.<br>• **[Suy luận phân tích]**: Judge bị thiên kiến bởi các từ ngữ lịch sự bề nổi ở đầu câu, bỏ qua sắc thái tiêu cực/mệnh lệnh ở vế sau.<br>• **Sửa rubric**: Bổ sung tiêu chí cấm các cụm từ mang tính mệnh lệnh tiêu cực hoặc hạn chế tương tác của khách. |
| 3 | `H-042` (tone) | FAIL | PASS | Người đúng | **Reply**: *"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."*<br>• **[Bằng chứng CSV]**: Ghi chú CSV ghi nhận: `ngắn nhưng đủ ý; judge phạt vì 'thiếu xin lỗi'`.<br>• **[Suy luận phân tích]**: Judge áp đặt tiêu chí xin lỗi một cách máy móc ngay cả khi yêu cầu bồi thường đã được giải quyết trọn vẹn và khách không phàn nàn gắt gao.<br>• **Sửa rubric**: Quy định rõ lời xin lỗi là tùy chọn (optional) khi thông báo hoàn tiền thành công, tránh phạt oan các câu trả lời ngắn gọn, chuẩn mực. |
| 4 | `H-070` (tone) | PASS | FAIL | Người đúng | **Reply**: *"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"*<br>• **[Bằng chứng CSV]**: Ghi chú CSV ghi nhận: `emoji không phù hợp ngữ cảnh khiếu nại`.<br>• **[Suy luận phân tích]**: Kênh bồi thường tài chính đòi hỏi tính nghiêm túc; việc sử dụng emoji cười cợt thể hiện sự thiếu tôn trọng sự phiền toái của khách hàng.<br>• **Sửa rubric**: Cấm tuyệt đối emoji đùa cợt (`😂😂`, `🤣`, `😜`) trong các luồng hỗ trợ bồi hoàn tiền và khiếu nại. |
| 5 | `HL-015` (helpful) | PASS | FAIL | Người đúng | **Reply**: *"Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ."*<br>• **[Bằng chứng CSV]**: Cột `human_failure` ghi `sai tiền`; cột `note` ghi `ledger ghi 40.000đ` (reply báo hoàn 55.000đ nhưng sổ cái thực tế chỉ hoàn 40.000đ).<br>• **[Suy luận phân tích]**: LLM judge không được cấp context sổ cái (un-grounded) nên chỉ đánh giá câu chữ có vẻ hữu ích mà không biết nghiệp vụ bị sai lệch (FM-08).<br>• **Sửa rubric/kiến trúc**: Tiêu chí hữu ích liên quan đến số tiền bắt buộc phải dùng code grader hoặc LLM judge có cung cấp context snapshot sổ cái. |
| 6 | `HL-028` (helpful) | PASS | FAIL | Người đúng | **Reply**: *"Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này và rất trân trọng sự kiên nhẫn của anh/chị. LogiX đã hoàn 50.000đ cho đơn O-677. LogiX thành thật xin lỗi anh/chị vì sự bất tiện này và rất trân trọng sự kiên nhẫn của anh/chị."*<br>• **[Bằng chứng CSV]**: Cột `human_failure` ghi `sai tiền`; cột `note` ghi `ledger ghi 35.000đ` (reply báo hoàn 50.000đ nhưng ledger chỉ ghi 35.000đ).<br>• **[Suy luận phân tích]**: Văn bản chứa lỗi lặp nguyên văn câu xin lỗi (degeneration), nhưng judge vẫn cho PASS vì bị đánh lừa bởi văn phong lịch sự.<br>• **Sửa rubric**: Thêm ràng buộc phát hiện câu lặp và bắt buộc đối chiếu số liệu tiền hoàn với hệ thống. |

---

## Kết luận

### 1. Phân tích số liệu và quyết định tiêu chí

- **Tiêu chí `tone_ok` — ĐƯỢC DÙNG (Giới hạn trong phạm vi dữ liệu replay công khai):**
  - **Số liệu đo đạc**: $n = 100$, ma trận nhầm lẫn `{"tp": 24, "fp": 4, "fn": 6, "tn": 66}`.
  - Tỷ lệ lỗi quan sát $0.28$; tỷ lệ lỗi hiệu chỉnh qua Rogan–Gladen là $0.30$ (khớp tỷ lệ thực tế của con người: $30/100$).
  - Chỉ số thỏa thuận Cohen's $\kappa = 0.757 \ge 0.6$, Precision $= 0.857 \ge 0.8$, Recall $= 0.800 \ge 0.7$ (đạt cả 3 sàn).
  - **Phạm vi hiệu lực**: Quyết định dùng `judge_tone` chỉ được khẳng định trong phạm vi tập dữ liệu calibration replay công khai (`data/eval/judge_tone_public.csv`). Trên môi trường production, cần kiểm định lại trên dữ liệu mới chưa công khai (held-out) để tránh hiện tượng rò rỉ dữ liệu hoặc overfitting bộ mẫu.

- **Tiêu chí `helpful` — BỊ LOẠI HOÀN TOÀN:**
  - **Số liệu đo đạc**: $n = 100$, ma trận nhầm lẫn `{"tp": 9, "fp": 0, "fn": 21, "tn": 70}`.
  - Chỉ số Cohen's $\kappa = 0.375 < 0.6$, Recall $= 0.300 < 0.7$ (vi phạm nghiêm trọng ngưỡng tối thiểu).
  - Tỷ lệ lỗi quan sát chỉ là $0.09$ (trong khi tỷ lệ lỗi thực tế là $0.30$).
  - **Bằng chứng từ CSV**: Toàn bộ $21$ ca judge bỏ sót ($fn=21$) đều có `human_failure` là `sai tiền` (18 ca) hoặc `sai xưng hô` (3 ca). Cột `note` của CSV chứng minh rõ ràng: reply luôn tuyên bố số tiền hoàn cao hơn số tiền ghi trong ledger (ví dụ: `ledger ghi 35.000đ` nhưng reply nói 50.000đ).
  - **Nguyên nhân cốt lõi**: Judge không có cơ chế đối chiếu với cơ sở dữ liệu sổ cái (`refund_ledger`). Judge bị đánh lừa bởi văn phong xin lỗi thống thiết, lịch sự mà bỏ qua hoàn toàn sai phạm về số tiền (lỗi FM-08 misreport). Việc dùng một judge có recall chỉ $30\%$ làm gate sẽ tạo cảm giác an toàn giả và để lọt đa số lỗi nghiệp vụ nguy hiểm.

### 2. Rủi ro còn lại & Khuyến nghị
- **Rủi ro Replay**: Dữ liệu kiểm chuẩn hiện tại là dữ liệu replay tĩnh đã công khai. Prompt của judge có thể vô tình trùng khớp với phong cách viết trong bộ dữ liệu này.
- **Khuyến nghị**: Để triển khai an toàn, các kiểm tra liên quan đến số tiền và trạng thái giao dịch phải được đảm nhận bởi code grader (như `refund_amount_correct` và `reply_amount_correct`). `judge_tone` chỉ nên dùng như một bộ lọc bổ trợ cho ngôn phong và phải được định kỳ đánh giá lại bằng nhãn người trên tập held-out độc lập.
