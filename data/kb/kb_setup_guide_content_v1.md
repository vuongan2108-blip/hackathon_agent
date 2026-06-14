# Knowledge Base — Setup Guide Content (v1.1)

> Trích từ User Guide của Events Tool / Merchant Tool. Quy tắc đã áp dụng:
> - Chỉ lấy **step + field name + description**. Field **không có description → đã bỏ**, không đưa vào KB.
> - Phần **TASK** và **REWARD** được gom riêng (Part B, Part C). Nội dung task/reward nằm trong doc của scheme cũng được gom về đó, kèm note thuộc scheme nào. Mỗi Part có 1 trang **core** (B0 = Task Module, C0 = Reward Module).
> - **Ngoại lệ:** step chỉ *hiển thị* prize/quà nhưng bản chất là **UI** (vd Lottery Step 4 "Ticket & Prize Info") được giữ lại trong trang scheme, KHÔNG gom vào Part C.
> - Mỗi scheme = một "trang" (Part A). Danh mục trang này đồng thời là allowlist của UC1.

---
---

# PART A — SCHEME PAGES

## A1. [SCHEME] Lucky Wheel
- source: https://events-tool.zalopay.vn/ (Package Scheme: Lucky Wheel)
- status: current (IN REVIEW)
- aliases: [setup lucky wheel, vòng quay may mắn, lucky wheel v2, game vòng quay]
- precondition: Tạo Reward Pool V2, Tạo Task List V2, Tạo User Condition
- note: Lucky Wheel có 5 dạng UI: Lucky Wheel, Lucky Grid, Slot Machine, Mystery Box, Scratch Card

**Step 0 — Create:** Truy cập events-tool → campaign management → "Create New Campaign" → chọn "Lucky Wheel V2".

**Step 1 — General Info**
- Campaign Name — Tên chương trình
- Marketing Code — Marketing Code
- Test Date — Ngày Start Test. Trong thời gian test, chỉ user trong whitelist mới có thể tham gia. Add/Remove qua global-whitelist
- Start Date — Ngày kết thúc Test & Bắt đầu live camp
- End Date — Ngày kết thúc campaign
- TnC Link — Link advertising ads

**Step 2 — Mechanism**
- Join Condition — Các điều kiện để tham gia (RISK / SEGMENT / RULE). Tạo như mục User Condition. Nếu không dùng điều kiện gì → không chỉnh sửa & Save
- SegmentID — Segment để lưu log User Join Campaign. Tạo Segment Dimension whitelist ở CRM tool
- Turn — Bật Universal Turn: dùng chung lượt chơi với chương trình khác → chọn thông tin lượt chơi trong drop list. Tắt: dùng lượt chơi riêng → để mặc định, hệ thống tự tạo thông tin lượt chơi

**Step 5 — UI Config** (xác định game play; 5 dạng UI)
- *Landing Page UI:* Banner — Banner chương trình; Background — Background chương trình; TnC icon — Icon Thể lệ; History icon — Icon Lịch sử; Primary Text Color — Màu tên nhiệm vụ; Secondary Text Color — Màu của "+x lượt"; Footer Text Color — Màu chữ Thể lệ
- *Lucky Wheel UI:* Edge Background Image — Hình vòng quay; Stand Background Image — Đế vòng quay (có thể để trống); Arrow Background Image — Hình kim quay; Arrow Text Color — Màu text trong khung kim quay; Wheel Piece Color 1 — Màu của từng mảnh vòng quay
- *Lucky Grid UI:* Spin Button — Hình nút nhấn; Cell Background — Khung màu nâu khi chưa sáng đèn; Active Cell Background — Khung màu vàng khi sáng đèn; Lucky Grid Background — Background chứa các grid; Turn Text Color — Màu chữ "Có x lượt"; Turn Number Color — Màu số lượt
- *Slot Machine UI:* Edge background image — Hình cái máy; Spin button — Hình nút "Chơi ngay"; Turn background — Màu khung lượt chơi; Turn border color — Viền khung lượt chơi; Turn Text Color — Màu chữ khung lượt chơi; Turn Number Color — Màu số lượt
- *Mystery Box UI:* Layout Type — Số lượng hộp quà (hàng x cột): 1x1, 2x2, 2x3, 3x3; Required Press Count — Số lần nhấn để mở quà; Reduction Percentage — Tốc độ giảm
- *Piece UI:* Piece Icon — Hình hiển thị trên game (Lucky wheel → mảnh quà; Lucky Grid → icon grid; Slot Machine → icon slot; Mystery Box → hình hộp quà); Reward Mapping — Chọn quà tặng tương ứng với icon
- *Popup UI:* Popup Background Color — Màu bg popup chúc mừng; Popup Stroke Color — Màu viền popup; Header Ribbon Background — Hình header popup; Header Ribbon Text Color — Màu text header popup; Reward Name Text Color — Màu Reward Name; Reward Description Text Color — Màu Description; Continue Button Text Color — Màu text CTA tiếp tục; Continue Button BG Color — Màu bg CTA tiếp tục; View Reward Button Text Color — Màu text CTA xem quà
- *Bottom Sheet UI (Task List):* Bottom sheet header background — Hình header Task List; Bottom Sheet Header Text Color — Màu text header; Bottom sheet background color — Màu bg khung nhiệm vụ; Card background color — Màu bg thẻ nhiệm vụ; Stroke color — Màu viền khung & thẻ nhiệm vụ; CTA background color — Màu bg CTA nhiệm vụ; CTA Text color — Màu text CTA nhiệm vụ
- *Entry Point UI:* Entry Point Background Color — Màu BG khung entry point; Entry Point Stroke Color — Màu stroke đổ shadow; Entry-Point Image Url — Hình hiển thị (min 2, max 5); CTA ZPI Link — Link ZPI; CTA ZPA Link — Link ZPA

**Step 7 — Review & Create:** Lấy link vào chương trình. Nhấn Sync sau mỗi lần create/update.

> Step 3 (Reward Config) → xem Part C. Step 4 (Task Config) → xem Part B. Step 6 (Popup Config / chọn quà) → xem Part C.

---

## A2. [SCHEME] Loyal
- source: https://merchant-tool.zalopay.vn/ (Package Scheme: Loyal)
- status: current (APPROVED)
- aliases: [setup loyal, loyalty, game tích điểm milestone, mốc quà]

**Create:** merchant-tool → campaign management → "Create New Campaign" → chọn "Loyal".

**Step 1 — General Info**
- Campaign Name — Tên chương trình
- Marketing Code — Marketing Code
- Test Date — Ngày Start Test. Trong test chỉ user whitelist tham gia. Add/Remove qua global-whitelist
- Start Date — Ngày kết thúc Test & Bắt đầu live camp
- End Date — Ngày kết thúc campaign
- TnC Link — Link advertising ads

**Step 2 — Mechanism**
- Record Joining — Segment để lưu log User Join Campaign. Tạo Segment Dimension whitelist ở CRM tool
- Check Joining Condition — Các điều kiện để tham gia (RISK / SEGMENT)

**Step 3 — Visualize Info**
- Banner — Banner của chương trình
- Background — Màu background
- Color Text — Màu Text
- Color Header — Màu của header
- Color Header Title — Màu header title
- Color Frame Background — Màu background khung
- Color Box Content — Màu của các nhiệm vụ
- Footer Color — Màu footer
- Footer Icon — Icon footer
- CTA Float Title — CTA Title
- CTA Float ZPI Link — CTA ZPI Link
- CTA Float ZPA Link — CTA ZPA Link
- CTA Float Color — CTA BG Color
- Display Instruction Info — Hiển thị phần UI Instruction
- Display Milestone & Task — Hiển thị phần UI task
- Display CTA Float — Hiển thị Floating Button

**Step 4 — Milestone & Task** (xác định hình thức campaign & logic)
- Sequence Type — Có 2 dạng: Sequence (tuần tự) / Non-sequence (không tuần tự)
- Quest Title Header Background — Background Header
- Quest Title Content — Nội dung chứa trong header
- Complete Icon — Icon hoàn thành
- Milestone Progress Color — Màu thanh progress
- Collection Milestone — Auto select -1
- *Progress Banner:* Progress Banner — Banner của progress banner; Progress Background — Background progress banner; Progress Color — Màu active progress; Bar Color — Màu thanh progress; Text Color — Màu chữ trên banner; Visible — Hiển thị/không; Visible Title — Hiển thị tên milestone title hay không
- (Task List Title — xem Part B)

**Step 6 — Review & Create.**

> Step 4 "Task List Title" → Part B. Reward trong Milestone (PresentID/Reward...) đều không có description nên đã bỏ theo quy tắc.

---

## A3. [SCHEME] Leaderboard
- source: https://events-tool.zalopay.vn/ (Package Scheme: Leaderboard)
- status: current (IN REVIEW)
- aliases: [setup leaderboard, bảng xếp hạng, leader board]
- precondition: Tạo Task List, Tạo User Condition
- ⚠️ NOTE quan trọng: Leaderboard **CHƯA CÓ** cơ chế tự động phát quà cho user trong top → cần phát quà **manual qua CRM Tool**

**Step 0 — Create:** events-tool → "Create New Campaign" → chọn "LeaderBoard".

**Step 1 — General Info**
- Campaign Name — Tên chương trình
- Marketing Code — Marketing Code
- Test Date — Ngày Start Test. Trong test chỉ user whitelist tham gia. Add/Remove qua global-whitelist
- Start Date — Ngày kết thúc Test & Bắt đầu live camp
- End Date — Ngày kết thúc campaign
- TnC Link — Link advertising ads

**Step 2 — Mechanism**
- Session Config — Config thời gian chạy 1 session; có thể config nhiều session trong 1 campaign
- Check Landing Point Condition — Chọn campaign có check segment để được vào campaign hay không
- Segments Code for Landing Point — Các điều kiện để tham gia. Phải tạo trước ở Segment Management; vào hệ thống sẽ tự dropdown ở RuleID; có thể dùng segment tạo sẵn
- Segment Code for Record Joining — Khi user vào campaign sẽ được thêm vào segment này. Phải tạo trước ở Segment trong CRM tool

**Step 3 — Visualize Information**
- General UI customization — Config background và chữ của campaign
- Card Frame UI customization — Setup card vị trí của người không lọt top 3
- Leader Board UI customization — Config từng vị trí của người nằm trong top
- CTA UI customization — Config CTA trong campaign
- Footer UI customization — Config footer UI của campaign
- Bottom Sheet UI customization — Config từng giải thưởng cho session

**Step 6 — Review & QR.**

> Step 4 (Conversion Rate — Task ID, Formula Type) → Part B. Step 5 (Prize Information) → Part C.

---

## A4. [SCHEME] Lottery
- source: https://events-tool.zalopay.vn/ (Package Scheme: Lottery)
- status: current (IN REVIEW)
- aliases: [setup lottery, xổ số, mã dự thưởng, quay số trúng giải]
- precondition: Tạo Reward Pool V2, Tạo Task List V1, Tạo User Condition
- note: User vào game, làm task để nhận mã dự thưởng; cuối chương trình hệ thống random mã trúng giải & phát quà

**Step 0 — Create:** events-tool → "Create New Campaign" → chọn "Lottery".

**Step 1 — General Info**
- Campaign Name — Tên chương trình
- Marketing Code — Marketing Code
- Test Date — Ngày Start Test. Trong test chỉ user whitelist tham gia. Add/Remove qua global-whitelist
- Start Date — Ngày kết thúc Test & Bắt đầu live camp
- End Date — Ngày kết thúc campaign
- TnC Link — Link advertising ads

**Step 2 — Mechanism**
- Add Session — Click to add new session. 1 session = 1 khung thời gian nhận mã dự thưởng
- Session Title — Tên session - hiển thị trên UI đến user
- Start Date — Thời gian bắt đầu session
- End Date — Thời gian kết thúc session
- Operation — Edit / Delete
- Check Join Condition — Các điều kiện để tham gia (RULE). Tạo như mục User Condition. Nếu không dùng → không chỉnh sửa & Save
- Record Joining — Segment để lưu log User Join Campaign. Tạo Segment Dimension whitelist ở CRM tool

**Step 3 — Visualize Info**
- Banner — Banner ở top trang
- Background Color — Màu nền trang
- Color Text — Màu chữ nội dung
- Color Header — Màu nền header các phần
- Color Header Title — Màu chữ header các phần
- Color Frame Background — Màu nền zone các phần
- Color Box Content — Màu nền content card
- Footer Color — Màu chữ TnC
- Footer Icon — Hình TnC + trade mark
- CTA Float Title — Text CTA cuối trang
- CTA Float ZPI Link — Link CTA
- CTA Float ZPA Link — Link CTA
- CTA Float Color — Màu nền CTA button
- Display Prize Info — ON/OFF hiện/ẩn thông tin quà (config step 4)
- Display Instruction Info — ON/OFF hiện/ẩn hướng dẫn (config step 5)
- Display Task Info — ON/OFF hiện/ẩn list nhiệm vụ (config step 5)
- Display User's Lottery Info — ON/OFF hiện/ẩn thông tin vé lottery của user
- Display Lottery Prize Info — ON/OFF hiện/ẩn thông tin kết quả trúng giải (config step 7)
- Display CTA Float — ON/OFF hiện/ẩn CTA cuối trang

**Step 4 — Ticket & Prize Info**
- Ticket Title — Title text ở mục Mã dự thưởng
- Ticket Description — Desc. dưới title Mã dự thưởng
- Prize Title — Title text ở mục Giải thưởng
- Title Text Color — Màu chữ tên giải
- Title Box Color — Màu nền box tên giải
- Title Stroke Color — Màu stroke box tên giải
- *List Prize:* Session ID — Chọn Session; Title — Tên giải; Name — Tên quà; Icon Prize — Hình quà

**Step 5 — Introduction** (phần hướng dẫn; phần Task Config → Part B)
- Instruction Title — Title text ở mục Hướng dẫn
- Instruction Config — Click Add to add step (Left icon / Content / Right icon)
- Task Title — Title text ở mục Nhiệm vụ
- CTA Color — Màu button CTA Nhiệm vụ
- CTA Text Color — Màu chữ CTA nhiệm vụ

**Step 7 — Winner** (cập nhật user trúng giải theo session)
- Mode phát quà = AUTO: hệ thống tự động input; MANUAL: manual input
- Ticket Code — Mã dự thưởng
- User Name — Tên Zalopay của user
- Phone Number — SĐT user
- User ID — Zalopay user ID

**Step 8 — Review:** nhấn Sync sau mỗi lần create/update.

> Step 4 (Ticket & Prize Info) đã nằm ngay trong trang scheme này (bản chất là UI). Step 6 (Draw Configs) → Part C. Step 5 (Task Config) → Part B.

---

## A5. [SCHEME] Referral / Affiliate
- source: https://events-tool.zalopay.vn/ (Package Scheme: Referral/Affiliate)
- status: current (IN REVIEW)
- aliases: [setup referral, affiliate, mời bạn, giới thiệu bạn bè, sender receiver]

**Step 1 — General Info**
- Campaign Name — Tên chương trình (show trên tool)
- Campaign ID — Auto generated
- Campaign Description — Tên chương trình (show cho user)
- Marketing Code — Marketing Code
- Test Date — Ngày Start Test. Trong test chỉ user whitelist tham gia. Add/Remove qua global-whitelist
- Start Date — Ngày kết thúc Test & Bắt đầu live camp
- End Date — Ngày kết thúc campaign
- Meta Data — Auto generated
- TnC Link — Link advertising ads

**Step 2 — Campaign Rule**
- Segment ID Join Landing Page — Condition để join campaign (đang setup bằng segment V1)
- Segment ID Accept Referral — Segment để record user đã join (đang setup bằng segment V1)
- Segment code — Segment cho từng type (sender/receiver)
- Rule description — Manual input
- Rule type — REFERREE: RECEIVER; REFERRER: SENDER
- Rule content title — Show khi user không pass segment code
- Rule content description — Show khi user không pass segment code
- Rule content image — Show khi user không pass segment code
- Auto redirect CTA in 3000ms — Redirect khi user không pass segment code
- Rule content CTA Text — Show khi user không pass segment code
- CTA action type — INTERNAL: đến 1 service in app; EXTERNAL: out app
- Rule content CTA ZPI Link — Redirect khi user không pass segment code
- Rule content CTA ZPA Link — Redirect khi user không pass segment code
- Tracking config - View page fail rule — Config as UI cho SENDER và RECEIVER

**Step 3 — Referral Config**
- Referral ID — auto generated
- Referral key — auto generated
- Referral Action Type — FIRST_CLICK: người được mời đã nhận 1 lời mời KHÔNG THỂ nhận lời người khác (trừ khi expire); LAST_CLICK: CÓ THỂ nhận lời người khác (ghi nhận lần cuối)
- Counting on Task IDs — not required
- Use Affiliate Order Mode — off
- Use Referral Partnership — off
- Use Referral Code — off

**Step 4 — General UI Config**
- Campaign Banner — Banner của màn hình sender
- Campaign Background Color — Màu background của campaign
- ZPA T&C link — Link TnC
- ZPI T&C link — Link TnC
- Sector Title Color — Màu text tên chương trình
- Sector Background Color — Màu background tên chương trình

**Step 5 — Sender UI Config**
- Show construction — Bật/tắt

**Step 6 — Receiver UI Config**
- Dynamic task UI — Content đổi theo trạng thái hoàn thành task của receiver

**Step 7 — All Sharing Content Config**
- Campaign path — auto generated
- Default sub path — 0
- Using onelink — Nếu dùng onelink để config thì bật lên

**Step 9 — Review and QR link.**

> Step 3 "Scenario code" (sinh task sender/receiver) → Part B.

---
---

# PART B — TASK (gom chung, kèm note scheme)

## B0. [TASK] Task Module (core)
- source: https://events-tool.zalopay.vn/w/modules/view/task-modules (Task Module V1) · https://events-tool.zalopay.vn/w/task-list/view (Task Module V2)
- status: current (IN REVIEW)
- aliases: [task module, tạo task, tạo nhiệm vụ, scenario code, task list, task config, milestone config, trigger task]
- note: Task Module dùng để tạo & quản lý nhiệm vụ user thực hiện trong app để nhận thưởng — tạo nhiệm vụ với điều kiện cụ thể (hành động, đối tượng, thời gian) và gán phần thưởng tương ứng.

**Phân biệt V1 vs V2:**
- Task Module V1 — dùng cho hầu hết game-play: Loyal, Leaderboard, Lottery, Referral, Interactive Game, Stamp Exchange.
- Task Module V2 (NEW) — dùng cho nhiệm vụ đứng độc lập và game-play: Lucky Wheel.

---

### Task Module V1

**1. Create a Scenario Code (Task List)**
- *General Info:*
  - Scenario Code — Input value = Campaign Code (_suffix nếu có). Phải unique. KHÔNG editable sau khi tạo
  - Campaign Code — Input value = MKT Code do biz request / set up trên Promotion Tool
  - Universal Task Mode — ON/OFF. OFF: task chỉ dùng cho 1 campaign. ON: task dùng cho nhiều campaign HOẶC dùng độc lập không cần gameplay. Nếu ON → bắt buộc nhập Start–End date, task chỉ active trong khoảng start–end
  - Active Duration (days) — Input number, CHỈ DÙNG nếu giới hạn thời gian làm task. VD: user chỉ được làm nhiệm vụ trong 7 ngày → input 7
  - Save — Click để lưu data
- *Collection Config:* (1 Collection = 1 nhóm user thoả điều kiện setup; 1 user phải thuộc 1 Collection mới thấy & làm được task; Collection được check theo Order — Order=0 NOT PASS thì check tiếp Order=1...)
  - Add — Click để thêm collection mới
  - Collection ID — Input unique value
  - Collection Description — Input mô tả
  - Collection Segment Code — Drop list, chọn ALL điều kiện user phải pass
  - Collection Milestone ID — Drop list, chọn Milestone ID (nếu có). Xem mục Milestone Config
  - Order — Input thứ tự check collection, start = 0
  - Save — Click để lưu collection
  - Cancel — Click để huỷ thay đổi

**2. Create a Task Config** (*Luôn click SAVE + SYNC sau mỗi lần thay đổi config*)
- Save — Click để lưu configs
- Sync — Click để sync data sang go-live campaign
- Add — Click để thêm task mới
- *Display Info:*
  - Task ID — Input value. Phải unique trong 1 Scenario Code. KHÔNG edit được sau khi save
  - Task Name — Input value, dùng để tracking. Recommend English / Tiếng Việt không dấu, không khoảng cách
  - Task Title — Tên nhiệm vụ, hiển thị đến user
  - Task Description — Mô tả nhiệm vụ, hiển thị đến user
  - Task CTA text — Chữ trên CTA, hiển thị đến user
  - Task CTA TYPE — Dạng CTA. Thực hiện & Điều hướng: "Xem 1 trang... để nhận quà". Chỉ Thực hiện: "Check-in nhận quà". Chỉ Điều hướng: "Thực hiện 1 action Thanh toán/Mở tài khoản... để nhận quà". Xem Ads: "Xem quảng cáo nhận quà"
  - Task Logo — Logo nhiệm vụ, hiển thị đến user
  - Task CTA ZPI Link — Link Zalopay trên Zalo, dẫn user đến trang khi click CTA
  - Task CTA ZPA Link — Link trên app Zalopay, dẫn user đến trang khi click CTA
  - Task Reward — Mô tả quà tặng, hiển thị đến user
  - Highlight — ON/OFF highlight nhiệm vụ, hiển thị đến user
  - Visible — ON/OFF hiển thị nhiệm vụ đến user
- *Task Mechanism Info:*
  - Enabled — ON = Active task / OFF = Inactive
  - Require Claim Reward — ON = user phải click "Nhận quà" để claim sau khi done task / OFF = auto phát quà sau khi done
  - Interactive Mode — ON = user phải click "Thực hiện" trước khi làm task để record actions / OFF = auto record actions
  - Allow Duplicated Transaction — ON = cho phép 1 thanh toán done nhiều task trong 1 chương trình / OFF = thanh toán chỉ done 1 task
  - Push result to Common Trigger — ON = forward thông tin done task về Core system (Common Trigger) / OFF = không forward
  - Source Types — Open API: nhiệm vụ "Xem 1 trang / Check-in / Xem ads". Trigger: nhiệm vụ "Thực hiện 1 action Thanh toán / Mở tài khoản"
  - Trigger ID — Nhập ID Trigger của action làm nhiệm vụ. *Lấy từ Promotion Tool
  - Collection IDS — Chọn các Collection ID được phép thấy & làm nhiệm vụ. User thoả 1 trong các Collection = thoả
  - Segment Codes — Chọn điều kiện user phải thoả ALL mới được thấy & làm. User thoả ALL = thoả
  - Limit Component ID — Tạo & Chọn giới hạn làm nhiệm vụ. Lấy từ Rule trên Promotion Tool
  - Resolve IDS — Tạo & Chọn hành động sau khi user hoàn thành. Phát quà = Issue Reward; Gửi notification in app = Push Notification

**3. Create a Milestone Config**
- Task Names — Chọn thứ tự các nhiệm vụ. User phải làm task theo sequence: hoàn thành task 1, hệ thống mới bắt đầu ghi nhận progress task 2...

---

### Task Module V2

**STEP 1 — Create a Task List** (events-tool → /w/task-list/view → "Add New")
- Task List Name — Name of Task List
- MKT Code — MKT Code
- Scenario Code — Auto fill theo MKT Code
- Test Date — Ngày/giờ bắt đầu phase test → ALL user trong WHITE LIST làm được task trong test
- Start Date — Ngày/giờ task list active → ALL user làm được task
- End Date — Ngày/giờ kết thúc campaign
- Task Config — TAB để config chi tiết task
- Milestone Config — TAB để config Milestone, CHỈ DÙNG nếu yêu cầu nhiệm vụ thực hiện theo thứ tự
- Visualization Config — TAB để config UI

**STEP 2 — Task Config** (sau khi save Step 1 → nút "+ Add Task" enable → click để thêm task)
- Task Name — Name of the task
- Task ID — Auto-filled theo Task Name
- *A. Mechanism:*
  - Task Segment — Điều kiện user phải thoả để được thấy & hoàn thành task
  - Add Trigger — Chọn Trigger Type phù hợp. Nếu chưa định nghĩa → chọn Others → Input NBA Flow ID
  - Require Claim Reward — Toggle ON/OFF (Default OFF). Nếu ON, user phải click CTA để nhận thưởng sau khi done task
  - Reward Pool — Input pool reward user nhận được sau khi done task
  - Frequency — Tần suất task/action được trigger trong 1 khoảng thời gian (per campaign / day / week / month). Khi setup sẽ auto create rule trên Promotion Tool với cùng MKT code
  - Require User Click CTA — Toggle ON/OFF (Default OFF). Nếu ON, user phải click CTA trước khi hoàn thành task
  - Expire after (days) — Chỉ hiện nếu Require User Click CTA = ON. Default 30. Reset CTA nếu task không hoàn thành trong thời gian set (VD: CTA "Làm task" → "Làm tiếp" → hết hạn reset về "Làm task")
  - Advanced Conditions to Do task — Chọn 1 user condition. User phải pass cả condition này VÀ task segment mới record done task
  - Trigger to Close Task — Chọn 1 action (= NBA flow). User không còn làm được task nếu action được config xảy ra
  - Task Done Notification — Input Noti ID, gửi noti khi user done task
- *B. Display:*
  - Task Title — Tên task hiển thị trên UI
  - Task Description — Hiển thị dưới Task Title
  - Task CTA Text — Text nút CTA user click để hoàn thành task
  - Task Icon — Icon task hiển thị trên UI
  - Task CTA ZPI Link — ZPI link trigger khi click CTA
  - Task CTA ZPA Link — ZPA link trigger khi click CTA
  - Reward Text — Hiển thị dưới Task Title & Description, mô tả phần thưởng khi hoàn thành
  - Reward Icon — Icon reward hiển thị trên UI

---

## B1. [TASK] Task Config — (Lucky Wheel)
- Scenario Code — Chọn từ drop-down, nhập Scenario Code (Task List ID) để filter. Chỉ được chọn 1 List Task cho 1 chương trình

## B2. [TASK] Task List Title — (Loyal)
- Task List Title — Title task list → "Danh sách nhiệm vụ"

## B3. [TASK] Conversion Rate (task → điểm) — (Leaderboard)
- Task ID — Phải tạo trước ở Task Module với cùng MKTCode; vào hệ thống tự dropdown ở Task ID
- Formula Type — DEFAULT: tính điểm theo task (user hoàn thành nhiệm vụ → lấy 'Expression value' tích lũy vào điểm). EXPRESSION: tính điểm theo số tiền (min conversion value: số tiền thấp nhất; min score: số điểm quy đổi). VD: mỗi 10.000đ = 1 điểm

## B4. [TASK] Task Config — (Lottery)
- Task Config — Click Add to choose a task
- Task ID — choose from Scenario Code
- Generate Type — AUTO: hệ thống tự gen mã dự thưởng; TRANSACTION: mã dự thưởng lấy theo trans ID

## B5. [TASK] Scenario code (referral tasks) — (Referral)
- Scenario code — Auto generated 2 scenario code cho sender & receiver: MARKETINGCODE_REFEREE (RECEIVER) và MARKETINGCODE_REFERER (SENDER)
- REFEREE (RECEIVER) — Auto generated task ACCEPT_REFERRAL
- REFERER (SENDER) — Config as normal

---
---

# PART C — REWARD (gom chung, kèm note scheme)

## C0. [REWARD] Reward Module (core)
- source: https://events-tool.zalopay.vn/w/reward-pools/view (Reward Module)
- status: current (IN REVIEW)
- aliases: [reward pool, reward module, tạo pool quà, loại quà]
- Reward Module V1 (to be retired) — dùng cho game-play: Interactive Game, Stamp Exchange
- Reward Module V2 — dùng cho Task Module V2 và game-play: Lucky Wheel, Loyal, Lottery, Referral
- *Operation Notes:*
  - Chỉ apply cho present tạo trên Promotion Tool với quantity = UNLIMITED
  - Tên quà + Logo trong Reward Pool: tự động điền VÀ cho phép chỉnh sửa
  - VOUCHER — Tên quà + Logo lấy từ REWARD ID \Thông tin hiển thị khuyến mãi. Tên quà = "Voucher" + Tên Brand + Tên Promotion + Mô tả chi tiết
  - MERCHANT CODE — Tên quà + Logo lấy từ MERCHANT CODE. Tên quà = "Voucher" + Merchant Name + Promotion Name + Promotion Description
  - CÒN LẠI — Tên quà lấy từ PRESENT ID (field Mô tả). Logo: default theo loại quà

## C1. [REWARD] Reward Config — (Lucky Wheel, Step 3)
- Condition — Chọn điều kiện tham gia (RISK / SEGMENT / RULE). Có thể chọn nhiều; user phải thoả tất cả mới PASS. Nếu không dùng → default = ALL USERS
- Pool ID — Chọn từ drop-down (nhập ID/Tên pool để filter). Chỉ chọn 1 Pool ID cho 1 User Profile. Chỉ hiển thị Pool ID có phương thức phát quà = RANDOM

## C2. [REWARD] Popup Config (hiển thị quà) — (Lucky Wheel, Step 6)
- Default: Tên quà hiển thị = Reward Desc. trong Reward Pool; CTA text = "Xem quà"; CTA link theo reward type (Coin → lịch sử xu; Cash → lịch sử giao dịch; Voucher → ví ưu đãi). Chỉ config nếu muốn khác default
- Reward — Chọn quà tặng
- Popup Description — Mô tả của quà → hiển thị cho user
- Popup CTA — CTA "Xem quà" gồm: CTA Title ("Xem quà"), ZPI Link, ZPA Link

## C3. [REWARD] Prize Information — (Leaderboard, Step 5)
- Session ID — Lấy từ Step 2
- Set up reward — Set up reward theo từng session
- (Lưu ý scheme: Leaderboard chưa tự phát quà → phát manual qua CRM Tool)

## C4. [REWARD] Draw Configs — (Lottery, Step 6)
- Header Title — Title text ở mục Kết quả trúng giải
- Prize Type — AUTO: hệ thống tự random user trúng & tự phát quà; MANUAL: biz random user trúng & phát quà
- Prize Selection Option — EARLIEST CODE: mã sớm nhất trúng; EARLIEST USER: user sớm nhất tham gia trúng; RANDOM CODE: random theo mã dự thưởng; RANDOM USER: random theo user có mã dự thưởng
- Segment Codes — = BLACKLIST. User thuộc 1 trong các Segment sẽ không được trúng giải
- *List Prize (theo Session):* Active — ON: có random user trúng + phát quà / OFF: không; Number of Prize — Số giải thưởng; Pool ID — Chọn Pool quà phát cho user trúng; Notification ID — Noti ID (Promotion Tool) gửi cho user khi trúng; Prize Image + Name — Thông tin quà hiển thị cho user
