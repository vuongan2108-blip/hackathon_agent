# Agent Spec — Review Request Setup Campaign Assistant (v1.1)

> Nguồn sự thật cho vibe code. Bản rút gọn: 3 point, đối chiếu KB allowlist.

---

## 1. Tổng quan

| Trường | Nội dung |
|---|---|
| Tên agent | Review Request Setup Campaign Assistant |
| Phiên bản | v1.1 |
| Người dùng chính | PO / Ops |
| Ngày | 2026-06-14 |

**Một câu mô tả:** Agent đọc request setup campaign (Confluence), trích 3 point (Game Type / Trigger từng task / Loại quà), đối chiếu KB allowlist; point nào không có trong KB → liệt kê để PO confirm. Rút review từ 1 ngày xuống ~15 phút.

---

## 2. Use case

- **Vấn đề:** Request phải đợi PO review thủ công ~1 ngày; hạng mục chưa hỗ trợ chỉ phát hiện khi đọc tay.
- **Người dùng:** PO / Ops.
- **Khi nào dùng:** Có request mới cần kiểm tra trước khi confirm.
- **Ngoài phạm vi:** Agent KHÔNG confirm/duyệt/sửa request, không quyết định thay PO. Chỉ phân loại và liệt kê point cần confirm.

---

## 3. Input & các point cần trích

| # | Tên | Kiểu | Bắt buộc? | Mô tả |
|---|---|---|---|---|
| 1 | request_page | Confluence page | có | Trang request theo template (cột field + cột description) |

**3 point agent trích từ request:**

| Nhóm | Point | Cách lấy từ request |
|---|---|---|
| SCHEME | Game Type | Đọc trực tiếp trường Game Type |
| TASK | Trigger type (mỗi dòng task) | Suy ra từ tên/description task bằng keyword |
| REWARD | Loại quà | Đọc loại phần thưởng (voucher / xu / cashback / vé / merchant code) |

---

## 4. Output

**Định dạng:** danh sách text, chia 2 phần — đã hỗ trợ và cần confirm (hiển thị CẢ HAI).

Mỗi point ở phần "cần confirm" kèm:
1. **Tên point** (vd: "Game Type", "Task #3 — Trigger").
2. **Nội dung trong request.**
3. **Lý do flag** — một trong:
   - `Không có trong KB allowlist`
   - `Không xác định được trigger` (description không khớp keyword nào)
4. **Câu hỏi cho PO:** "Point này với request này đã available trên tool chưa?"

**Mẫu output (lấy từ request Lucky Wheel):**
```
=== REVIEW: [DGS_260520_585] OTA - Lucky Wheel Vé hè 0đ ===
Tổng point: <n> | Đã hỗ trợ: <a> | Cần confirm: <b>

--- ĐÃ HỖ TRỢ ---
[SCHEME] Game Type = Lucky Wheel ✅ (có trong allowlist)
[TASK] "Nạp điện thoại" → trigger = payment ✅ (keyword "nạp")
[TASK] "Điểm danh hàng ngày" → trigger = checkin ✅ (keyword "điểm danh")
[TASK] "Ghé thăm Fanpage Zalopay" → trigger = openlink ✅ (keyword "ghé thăm")
[TASK] "Mời bạn bè tham gia" → trigger = referral ✅ (keyword "mời")
[REWARD] Voucher OTA → voucher ✅
[REWARD] 10 xu / 100 xu → xu ✅

--- CẦN PO CONFIRM ---
1. [TASK] "Đặt vé máy bay hè"
   Nội dung: tên task "Đặt vé máy bay hè"
   Lý do: Không xác định được trigger — không khớp keyword nào (payment chỉ có "thanh toán/mua/nạp")
   Hỏi PO: Trigger cho task "đặt vé" này đã available trên tool chưa?

2. [REWARD] "Vé cứng CGV miễn phí"
   Nội dung: loại quà = vé / voucher?
   Lý do: Không rõ thuộc "vé" hay "voucher" trong allowlist
   Hỏi PO: Loại quà "vé cứng CGV" map vào loại nào đã available?
```

---

## 5. Tools / KB

| Tool | Loại | Dùng để làm gì |
|---|---|---|
| Confluence page reader | Tool call | Đọc request page, trích 3 point |
| KB allowlist | Lookup + keyword match | Đối chiếu point với danh sách available |

- KB là **allowlist** (file `kb_campaign_available.md`): chỉ note cái đã available.
- **Cách match:**
  - Game Type & Loại quà: so khớp trực tiếp với danh sách (có chuẩn hóa hoa/thường, dấu).
  - Trigger: quét tên/description task tìm keyword theo bảng trong KB.
- **Quy tắc flag:** point không khớp allowlist tương ứng → **cần confirm**.

---

## 6. Logic xử lý

1. Đọc `request_page` → trích Game Type, danh sách task, danh sách loại quà.
2. **Game Type:** có trong allowlist? → hỗ trợ : cần confirm.
3. **Mỗi task:** quét tên/description tìm keyword trigger → match được & available → hỗ trợ; không khớp keyword nào → cần confirm.
4. **Mỗi loại quà:** có trong allowlist? → hỗ trợ : cần confirm.
5. Gom thành output mục 4 (cả 2 nhóm).

---

## 7. Trường hợp lỗi & biên (edge cases)

| Tình huống | Agent phải làm gì |
|---|---|
| Request page sai cấu trúc / không đọc được | Báo lỗi rõ ràng, không đoán point |
| Description task khớp nhiều keyword khác trigger | Liệt kê cả các trigger khả dĩ, flag cần confirm |
| Loại quà nằm giữa 2 nhóm (vd "vé" vs "voucher") | Flag cần confirm, nêu các khả năng |
| KB allowlist trống / không đọc được | Báo lỗi, không kết luận |

---

## 8. Tiêu chí hoàn thành (Definition of Done)

- [ ] Trích đúng 3 point từ request mẫu.
- [ ] Liệt kê **đầy đủ** point không có trong allowlist (không bỏ sót — tiêu chí cốt lõi).
- [ ] Hiển thị cả point đã hỗ trợ và point cần confirm, mỗi point cần confirm đủ 4 thành phần ở mục 4.
- [ ] **Phát hiện đúng ≥ 95% point chưa available trên bộ 10 request mẫu** (đo recall).
- [ ] Xử lý đúng edge case ở mục 7.
