# Agent Spec — Setup Campaign Assistant (v1.1)

> Nguồn sự thật cho vibe code. Đã chốt đủ thông tin.

---

## 1. Tổng quan

| Trường | Nội dung |
|---|---|
| Tên agent | Setup Campaign Assistant |
| Phiên bản | v1.1 |
| Người dùng chính | Ops (hỏi); PO (Ops tự hỏi khi agent báo không có trong KB) |
| Ngày | 2026-06-14 |

**Một câu mô tả:** Agent trả lời câu hỏi của Ops về cách setup tool bằng cách RAG knowledge base nội bộ, kèm nguồn cụ thể; không tìm thấy thì báo text để Ops biết cần hỏi PO, tuyệt đối không bịa. Rút thời gian reply từ 2 tiếng xuống ~15 phút.

---

## 2. Use case

- **Vấn đề:** Ops đợi PO giải thích từng trường hợp setup, ~2 tiếng, không nhất quán.
- **Người dùng:** Ops (đặt câu hỏi).
- **Khi nào dùng:** Khi Ops cần biết cách setup một hạng mục trên tool.
- **Ngoài phạm vi:** Agent KHÔNG thao tác setup, KHÔNG trả lời ngoài KB, KHÔNG suy diễn khi KB không có, KHÔNG tự đẩy thông báo cho PO (chỉ báo text cho Ops).

---

## 3. Input

| # | Tên | Kiểu | Bắt buộc? | Mô tả |
|---|---|---|---|---|
| 1 | question | text | có | Câu hỏi của Ops về cách setup |
| 2 | context | text/file | không | Request/campaign liên quan (optional — MVP thường không dùng) |

**Phạm vi câu hỏi (KB phủ):**
- Hướng dẫn setup từng step của **từng Game Type**.
- Cách setup task — **từng dạng task** (theo trigger).
- Cách setup reward — **từng dạng reward**.

**Câu hỏi mẫu thật:**
```
- cách setup Game Type: lucky wheel
- cách setup task trigger payment
- các loại reward có thể setup
```

> MVP: bỏ qua context, chỉ xử lý câu hỏi text. Thêm context sau.

---

## 4. Output

**Định dạng:** câu trả lời + nguồn.

1. **Trả lời** — các bước setup, bám đúng nội dung KB, không thêm thắt.
2. **Nguồn** — **link Confluence + tên section** của đúng trang KB đã dùng.

Không hiển thị mức độ tự tin (confidence).

**Khi KB không có / không chắc → KHÔNG bịa.** Báo text cho Ops:
```
Mình không tìm thấy thông tin này trong KB nội bộ. Bạn cần hỏi PO để xác nhận nhé.
```
(Chỉ báo text — agent KHÔNG tự gửi message/notify cho PO.)

---

## 5. Tools / RAG

| Tool | Loại | Dùng để làm gì | Tham số |
|---|---|---|---|
| KB nội bộ (Confluence) | RAG | Tra cứu cách setup theo câu hỏi | query (câu hỏi) |

- **KB:** cùng nguồn Confluence với UC1, nhưng phạm vi rộng hơn (nội dung hướng dẫn chi tiết).
- **Cấu trúc:** một KB gồm nhiều trang nhỏ — mỗi Game Type / dạng task / dạng reward một trang (= 1 chunk RAG tự đủ nghĩa). Danh mục (index) các trang này đồng thời là allowlist của UC1 → hai agent chung một nguồn, không lệch.
- **Ngưỡng "không RAG được" → báo cần hỏi PO** (thỏa BẤT KỲ điều kiện nào):
  - Không có chunk nào liên quan, **hoặc**
  - Điểm tương đồng cao nhất **< 70**, **hoặc**
  - Nhiều chunk mâu thuẫn nhau.
- **Ngoại lệ — General Info:** phần "General Info" (Campaign Name, Marketing Code, Test Date, Start/End Date, TnC Link...) gần như giống hệt nhau giữa cả 5 scheme **một cách có chủ đích**. Vì vậy điều kiện "nhiều chunk tương đương/mâu thuẫn" **KHÔNG áp dụng** cho General Info — gặp nhiều kết quả gần trùng ở phần này thì **không** coi là "không RAG được"; agent trả lời thẳng General Info của đúng scheme mà câu hỏi nhắm tới (dựa vào tên scheme trong câu hỏi). **Quyết định:** GIỮ NGUYÊN General Info trong từng trang scheme, **KHÔNG tách** thành một trang "General Info chung".

---

## 6. Logic xử lý

1. Nhận `question` → tạo query → RAG KB.
2. Đánh giá kết quả:
   - Có chunk liên quan, điểm ≥ 70, không mâu thuẫn → soạn trả lời **chỉ dựa trên chunk đó** + đính link nguồn (Confluence + section).
   - Thỏa bất kỳ điều kiện "không RAG được" ở mục 5 → báo text "không tìm thấy, cần hỏi PO".
3. Không bao giờ trả lời từ kiến thức ngoài KB.
4. **Cảnh báo cấp scheme (chỉ nói khi đúng chủ đề):** một số chunk có note cảnh báo. Agent **chỉ** đưa note này vào câu trả lời khi câu hỏi đúng phạm vi của note; **không** chủ động chèn vào các câu trả lời khác. Note vẫn luôn nằm sẵn trong KB (trang scheme) bất kể agent có nói hay không.
   - Hỏi về **reward / phát quà của Leaderboard** → nói rõ: Leaderboard CHƯA có cơ chế tự phát quà, phải phát **manual qua CRM Tool**.
   - Hỏi về **Reward Module / phiên bản reward / Reward V1** → nói rõ: **Reward Module V1 sắp khai tử**, scheme mới đều dùng **V2** (V1 chỉ còn ở Interactive Game, Stamp Exchange).
   - Các câu hỏi khác → không tự nhắc hai cảnh báo này.

---

## 7. Trường hợp lỗi & biên (edge cases)

| Tình huống | Agent phải làm gì |
|---|---|
| Câu hỏi mơ hồ / thiếu ngữ cảnh | Hỏi lại + **gợi ý sẵn phạm vi KB**: "Câu hỏi đang chưa rõ, bạn muốn hỏi về gì? Mình có thông tin về cách setup **scheme / task / reward**." → nhận input mới → nếu vẫn không RAG được thì lặp lại vòng này; nếu RAG được thì trả info. |
| KB có nhưng thông tin cũ/mâu thuẫn | Coi là "không RAG được" (nhiều chunk mâu thuẫn) → báo cần hỏi PO |
| Câu hỏi nhiều ý | Tách từng ý; ý nào KB có thì trả lời + nguồn, ý nào không thì báo cần PO |
| RAG KB lỗi / không truy cập được | Báo lỗi, không bịa câu trả lời |

---

## 8. Tiêu chí hoàn thành (Definition of Done)

- [ ] Trả lời đúng + đính **nguồn cụ thể** (link Confluence + section) cho câu hỏi KB có.
- [ ] Khi KB không có / điểm < 70 / mâu thuẫn → báo text cần hỏi PO, **không bịa** (tiêu chí cốt lõi).
- [ ] Câu hỏi mơ hồ → gợi ý phạm vi scheme/task/reward và lặp đúng vòng làm rõ.
- [ ] **Trả lời đúng kèm nguồn ≥ 90% trên bộ câu hỏi mẫu.**
- [ ] Xử lý đúng edge case ở mục 7.
