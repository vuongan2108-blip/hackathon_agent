# Knowledge Base — Available Capabilities (allowlist)

> KB này CHỈ note những cái đã available. Quy tắc chung: point trong request
> KHÔNG khớp KB này → flag "cần confirm".

---

## 1. SCHEME — Game Type (đã available)

| Game Type |
|---|
| lucky wheel |
| loyal |
| leaderboard |
| referral |
| lottery |

**Rule:** Game Type trong request không thuộc danh sách trên → **cần confirm**.

---

## 2. TASK — Trigger type (đã available + keyword nhận diện)

> Xác định trigger bằng cách quét tên/description của task tìm keyword.

| Trigger type | Keyword nhận diện |
|---|---|
| payment | thanh toán, mua, nạp, đặt |
| checkin | điểm danh |
| openlink | ghé thăm, mở, khám phá |
| referral | mời |

**Rule:** Description task không khớp keyword nào ở trên → không xác định được trigger → **cần confirm**.

---

## 3. REWARD — Loại quà (đã available)

| Loại quà |
|---|
| voucher |
| xu |
| cashback |
| merchant code |

**Rule:** Loại quà trong request không thuộc danh sách trên → **cần confirm**.

---

## Khối machine-readable (để vibe code parse trực tiếp)

```json
{
  "scheme_game_type": ["lucky wheel", "loyal", "leaderboard", "referral", "lottery"],
  "task_trigger": {
    "payment":  ["thanh toán", "mua", "nạp", "đặt"],
    "checkin":  ["điểm danh"],
    "openlink": ["ghé thăm", "mở", "khám phá"],
    "referral": ["mời"]
  },
  "reward_type": ["voucher", "xu", "cashback", "merchant code"],
  "rule": "point không khớp allowlist tương ứng => flag 'cần confirm'"
}
```
