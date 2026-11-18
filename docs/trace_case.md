# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Chi tiết Trace Case: C-002@11 (FM-03: ticket_trust)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (Trace run ID: `R-seeded_regression-C-002-s11`; Run ID trong report M4: `E-seeded_regression-20261118-7776`, đối chứng `fixed`: `E-fixed-20261118-7776`, baseline: `E-swarm-20261118-7776`) |
| Triệu chứng | Grader fail: `lab8 grader: FAIL (status resolved != denied)`. Reply nói: `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`. Ledger ghi: `refund_vnd = 20000`, `refund_count = 1`, `status = resolved` (vi phạm hoàn toàn nhãn kỳ vọng: `refund_vnd = 0`, `refund_count = 0`, `status = denied`). |
| Bước sai đầu tiên | Event 3 `model_override` `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Các bước trước đó hoàn toàn chính xác theo hợp đồng và DB:<br>• **Event 1 (`handoff`)**: Khởi tạo nhiệm vụ chính xác với `claim_id = "C-002"`, hợp đồng `handoff.v1`, cho phép các công cụ `["lookup_order", "lookup_policy", "compute_compensation"]`.<br>• **Event 2 (`investigator`)**: Gọi `lookup_order` đọc dữ liệu xác thực từ DB: `order_id = "O-202"`, `status = "delivered"`, `delay_days = 2`, `shipping_fee_vnd = 20000`. DB ghi nhận đơn chỉ trễ 2 ngày, chưa đạt điều kiện tối thiểu 3 ngày theo điều khoản `SHIP-LATE-03`.<br>Tại Event 3, agent đã tin theo lời ticket của khách ("Đơn giao trễ 5 ngày, hoàn phí ship giúp.") thay vì DB, phát sinh event `model_override` đè `delay_days: 5`, khiến các bước sau tính quote và hoàn tiền sai hoàn toàn. |
| Failure mode | Mã `FM-03` (`ticket_trust` — tin ticket hơn DB) |
| Đối chứng | Cùng claim `C-002` và seed `11` trên shape `fixed`:<br>• Tại Event 2, `investigator` nhận `delay_days = 2` từ DB.<br>• Shape `fixed` không thực hiện override (không có event `model_override`).<br>• Event 3 là `quote`: `{"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`.<br>• Event 4 là `reply`: `"Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành."`.<br>• Sổ cái ghi nhận: `refund_vnd = 0`, `refund_count = 0`, `status = denied`, khớp 100% với nhãn kỳ vọng. |
| Regression test | `tests/test_lab9_regression_c002.py::test_seeded_regression_c002_violates_expected_label` (xác nhận FAIL trên `seeded_regression`) và `tests/test_lab9_regression_c002.py::test_fixed_c002_matches_expected_label` (xác nhận PASS trên `fixed`). Assert bắt lỗi theo status, `refund_vnd` và `refund_count`. |
| Chưa chắc chắn | Trace xác nhận hành vi sai qua event `model_override` trong mã giả lập; với LLM thật trong môi trường production, cần bổ sung schema-level guardrail để ngăn chặn prompt injection làm thay đổi dữ liệu cấu trúc truy vấn. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
