# FR_008 — Bỏ module Kaiwa và Luyện đọc câu

> Trạng thái: **Đã code xong, đã test qua trình duyệt desktop (2026-09-12). Chưa build APK cho gói Phase 2.**
> Thuộc gói Phase 2, cài APK một lần cùng FR_009 → FR_012.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-09-11 | Tạo FR_008. PM xác nhận không còn dùng 2 module này. Lý do: Kaiwa ghép 4–6 câu ví dụ rời rạc thành hội thoại giả, nội dung không liên quan logic với nhau; Luyện đọc câu trùng mục đích với Luyện nói. | NguyenNC (qua Claude Cowork) |

## 1. Loại thay đổi

- [x] Sửa/nâng cấp chức năng có sẵn — gỡ 2 module khỏi menu chính

## 2. Tên chức năng

Gỡ bỏ module **Luyện đọc** (`reading_lib`) và **Kaiwa** (`kaiwa_lib`)

## 3. Mô tả ngắn

Menu chính hiện có 4 module. Sau FR này còn 2: IT専門 và IT業務編. Hai module bị gỡ không còn xuất hiện ở màn hình chọn chủ đề và toàn bộ code của chúng được xóa khỏi `app_template.html`.

## 4. Hành vi mong muốn (chi tiết)

### 4.1 Menu chính

- Xóa 2 phần tử `reading_lib` và `kaiwa_lib` khỏi mảng `MENU_MODULES`.
- `home()` không cần sửa gì thêm — nó render động từ mảng này.
- Sau khi xóa, màn hình chọn chủ đề còn đúng 2 thẻ: IT専門 và IT業務編.

### 4.2 Xóa code

Xóa hẳn các hàm sau (không để lại code chết):

| Hàm | Dòng hiện tại (tham khảo) |
|---|---|
| `readingLibrary()` | ~971 |
| `readingMode()` | ~1684 |
| `finishReading()` | ~1766 |
| `kaiwaLibrary()` | ~990 |
| `kaiwaMode()` | ~1786 |
| `finishKaiwa()` | ~1983 |

Xóa 2 biến toàn cục không còn ai dùng: `readingDeckPage`, `kaiwaDeckPage`.

### 4.3 Những thứ PHẢI GIỮ LẠI

- **`allWithEx()` GIỮ NGUYÊN** — FR_009 (Điền từ vào câu) sẽ dùng lại hàm này. Đừng xóa theo.
- **`splitDecks()` GIỮ NGUYÊN** — dù hiện chỉ Reading/Kaiwa dùng, giữ lại để không phải viết lại nếu sau này cần. Nếu muốn gọn có thể xóa, nhưng phải chắc chắn không còn chỗ nào gọi.
- **Dữ liệu localStorage của 2 module KHÔNG XÓA.** Trong `store.deckDone` có 2 namespace `_reading` và `_kaiwa`. Giữ nguyên, không dọn, không viết code migrate xóa chúng. Lý do: dung lượng không đáng kể, và nếu PM đổi ý muốn khôi phục thì dữ liệu vẫn còn.
- **CSS của Kaiwa (bong bóng chat A/B)** có thể giữ lại, không bắt buộc xóa. Nếu xóa thì phải chắc không class nào bị dùng chung với màn khác.

### 4.4 Kiểm tra sau khi xóa

Bắt buộc chạy đủ 3 bước trước khi báo xong:

1. `python3 build_app.py` chạy sạch, ra đúng 667 từ.
2. `node --check` trên khối `<script>` của `Kokoro_Nihongo.html` — không lỗi cú pháp.
3. Tìm trong `app_template.html` các chuỗi sau, phải **không còn kết quả nào**:
   `readingLibrary` · `readingMode` · `finishReading` · `kaiwaLibrary` · `kaiwaMode` · `finishKaiwa` · `readingDeckPage` · `kaiwaDeckPage` · `reading_lib` · `kaiwa_lib`
4. Mở app bằng trình duyệt: menu chính hiện đúng 2 thẻ, bấm vào cả hai đều vào được, bấm Back về được trang chủ.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — xóa 6 hàm, 2 biến, 2 phần tử mảng
- [ ] `build_app.py` — không ảnh hưởng
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [x] `CLAUDE.md` — cập nhật bảng "4 Module" thành 2 module
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật sau khi xong

## 6. Ràng buộc kỹ thuật

- Không đổi cấu trúc `localStorage`, không xóa dữ liệu cũ của user.
- Không đụng module IT専門 và IT業務編.
- Giữ nguyên cơ chế registry `MENU_MODULES` — sau này thêm module mới vẫn chỉ cần thêm 1 phần tử mảng.
- App vẫn phải chạy offline, không thêm thư viện ngoài.

## 7. Ưu tiên

- [x] Cao — làm trước FR_009 để code gọn lại rồi mới thêm mode mới

## 8. Ghi chú thêm — đã chốt với PM

- PM xác nhận trực tiếp: **không dùng Kaiwa và Luyện đọc câu nữa**.
- **IT業務編 — Luyện đọc theo thoại** (`gyoumuReadingMode`) **GIỮ LẠI**, không nằm trong phạm vi FR này. Đây là bài đọc theo transcript thật của giáo trình, khác hẳn Luyện đọc câu ví dụ.
- Gỡ 2 module này làm `app_template.html` ngắn đi khoảng 250–300 dòng, dễ thêm 2 mode mới ở FR_009 và FR_010 hơn.

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro

| # | Nội dung | Mức | Quyết định |
|---|---|---|---|
| 1 | User đang có `deckDone` cho namespace `_reading` / `_kaiwa` — xóa module thì dữ liệu này thành rác. | Thấp | **Giữ nguyên, không dọn.** Không ảnh hưởng gì, và giữ đường lùi nếu PM đổi ý. |
| 2 | `allWithEx()` chỉ được Reading và Kaiwa dùng, xóa 2 module thì hàm này thành code chết. | Trung bình | **Giữ lại** — FR_009 sẽ dùng để lọc các từ có câu ví dụ. |
| 3 | `finish()` nhận tham số `mode`, và nút "Học tiếp" gọi `startMode(mode)`. Reading/Kaiwa dùng `finishReading`/`finishKaiwa` riêng nên không ảnh hưởng. | Thấp | Không cần xử lý. Xóa 2 hàm finish riêng là đủ. |
| 4 | Menu chỉ còn 2 thẻ, màn hình trông thưa hơn. | Thấp | Chấp nhận. FR_012 sẽ thêm lối vào màn hình Thống kê, menu đầy lại. |
| 5 | Nếu sau này PM muốn khôi phục, phải viết lại code. | Thấp | Code cũ vẫn nằm trong lịch sử git. Nhắc PM commit trước khi xóa. |
