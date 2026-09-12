# FR_006 — Tự động focus vào Bộ nhỏ nhất chưa hoàn thành (IT専門)

> Trạng thái: **Đã chốt yêu cầu — sẵn sàng triển khai** (chưa code). Toàn bộ điểm rà soát ở mục 9 đã được PM xác nhận.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-07-26 | Tạo FR_006 theo yêu cầu PM. Đã hỏi lại và chốt phạm vi: chỉ áp dụng module IT専門; auto-chọn sẵn nhưng vẫn cho đổi thủ công; điều kiện hoàn thành = đủ 4 chế độ Flashcard/Quiz/Luyện nghe/Luyện nói. | NguyenNC (qua Claude) |
| 2026-07-26 | PM xác nhận toàn bộ 4 điểm rà soát: (1) auto-focus tính lại mỗi lần vào IT専門, không giữ lựa chọn thủ công cũ; (2) khi hoàn thành hết 24/24 Bộ thì giữ ở Bộ cuối cùng; (3) "hoàn thành" chỉ cần đã làm qua 1 lượt (giữ nguyên định nghĩa hiện có, không thêm ngưỡng điểm số); (4) `deckPage` phải tự nhảy sang trang chứa Bộ đang focus (VD Bộ 15 → tự chuyển tới trang chứa Bộ 15) để user thấy ngay, không cần bấm "Tiếp" dò tìm. FR chuyển trạng thái sẵn sàng triển khai. | NguyenNC (qua Claude) |

## 1. Loại thay đổi

- [x] Sửa/nâng cấp chức năng có sẵn (update logic chọn Bộ trong `homeDashboard()`)

## 2. Tên chức năng

Tự động focus vào Bộ nhỏ nhất chưa hoàn thành (module IT専門)

## 3. Mô tả ngắn

Khi vào màn hình IT専門, app tự động chọn sẵn **Bộ có số thứ tự nhỏ nhất trong các Bộ chưa hoàn thành đủ 4 chế độ học** (Flashcard → Quiz → Luyện nghe → Luyện nói), thay vì để user tự dò tìm hoặc mặc định "Tất cả". Khi Bộ đang focus đã hoàn thành đủ 4 chế độ, lần vào tiếp theo app tự chuyển focus sang Bộ kế tiếp (theo thứ tự Bộ 1 → Bộ 2 → ...) chưa hoàn thành.

## 4. Hành vi mong muốn (chi tiết)

- Chỉ áp dụng cho module **IT専門** (`homeDashboard()`), dùng đúng cơ chế chia Bộ hiện có (`splitDecksStrict()`, mỗi Bộ 25 từ, Bộ cuối 21 từ).
- "Hoàn thành 1 Bộ" = đủ 4 cờ `deckDoneModes(curCat, i)`: `done.flash && done.quiz && done.listen && done.speak` (đã có sẵn, không cần thêm dữ liệu mới).
- Logic: duyệt Bộ theo thứ tự tăng dần (Bộ 1, Bộ 2, ...) → tìm Bộ đầu tiên **chưa** đủ 4 cờ trên → set `curDeck` = index Bộ đó làm giá trị mặc định khi vào màn hình.
- Đây là **auto-chọn sẵn, không khóa cứng**: user vẫn bấm vào deck-card của Bộ khác để đổi `curDeck` như hành vi hiện tại, không bị disable/ẩn Bộ nào.
- Auto-focus được **tính lại mỗi lần vào IT専門** (mỗi lần gọi `homeDashboard()` từ Home) — không giữ lựa chọn thủ công của lần trước, kể cả khi user vừa tự chọn Bộ khác rồi quay lại.
- Nếu tất cả Bộ đã hoàn thành đủ 4/4 chế độ (không còn Bộ nào để focus) → giữ `curDeck` ở **Bộ cuối cùng** (VD Bộ 24 với 596 từ) để user tiện ôn tập.
- `deckPage` (phân trang lưới chọn Bộ, `DECK_GRID_PAGE_SIZE=4`) phải **tự nhảy tới trang chứa Bộ đang được focus** — ví dụ rule tính ra Bộ 15 thì `deckPage` phải tự đặt về trang chứa Bộ 15 (`Math.floor(14/4)=3` → trang 4), để user vào là thấy ngay Bộ đang học được tô sáng, không phải tự bấm "Tiếp theo" dò tìm.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — sửa `homeDashboard()`: thêm hàm tính Bộ focus (VD `autoFocusDeck(decks)`) chạy trước khi render, set `curDeck` + đồng bộ `deckPage`.
- [ ] `build_app.py` — không ảnh hưởng
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [ ] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật sau khi triển khai xong (mục mô tả IT専門/Bộ)

## 6. Ràng buộc kỹ thuật

- Không đổi cấu trúc `localStorage` (`jp_learn_v1`, key `deckDone`) — chỉ đọc thêm để tính Bộ focus, không ghi mới.
- Không phá hành vi chọn Bộ thủ công hiện có (`c.onclick=function(){curDeck=c.dataset.key; homeDashboard();}` vẫn giữ nguyên).
- Không ảnh hưởng IT業務編 / Luyện đọc / Kaiwa — các module này giữ nguyên hành vi chọn bộ/track thủ công như hiện tại.

## 7. Ưu tiên

- [ ] Cao / [ ] Trung bình / [ ] Thấp — PM điền khi xác nhận triển khai

## 8. Ghi chú thêm — đã chốt với PM

- **Phạm vi:** chỉ IT専門 (không áp dụng IT業務編, Luyện đọc, Kaiwa).
- **Mức khóa:** tự động chọn sẵn Bộ theo rule, user vẫn bấm đổi sang Bộ khác được nếu muốn — không ẩn/disable Bộ nào.
- **Điều kiện "hoàn thành 1 Bộ":** đủ 4 chế độ Flashcard + Quiz + Luyện nghe + Luyện nói (không tính Yêu thích, vì Yêu thích không phải chế độ học tuần tự).
- **Tần suất tính lại:** mỗi lần vào IT専門 đều tính lại auto-focus theo rule, không giữ lựa chọn thủ công của lần trước.
- **Khi hoàn thành hết:** giữ ở Bộ cuối cùng để ôn tập.
- **Điều kiện "hoàn thành":** chỉ cần đã làm qua 1 lượt (giữ nguyên định nghĩa `deckDoneModes` hiện có), không thêm ngưỡng điểm số/chất lượng.
- **Phân trang lưới chọn Bộ:** `deckPage` tự nhảy sang trang chứa Bộ đang focus.

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro — đã xác nhận với PM (2026-07-26)

| # | Nội dung | Mức ảnh hưởng | Quyết định |
|---|---|---|---|
| 1 | User đã tự bấm chọn 1 Bộ khác (không phải Bộ auto-focus) rồi rời màn hình — quay lại IT専門 thì app auto-focus lại theo rule, hay tôn trọng lựa chọn thủ công gần nhất trong phiên? | Cao | **Auto-focus lại theo rule mỗi lần vào IT専門** — không giữ lựa chọn thủ công của lần trước. |
| 2 | Khi tất cả Bộ đã hoàn thành 4/4 chế độ (596/596 từ xong hết, không còn Bộ nào để focus) thì `curDeck` nên là gì? | Trung bình | **Giữ ở Bộ cuối cùng** (Bộ 24) để user tiện ôn tập. |
| 3 | `deckDoneModes` là cờ boolean (đã làm qua 1 lần là tính "done" vĩnh viễn, không phân biệt làm đúng nhiều hay ít). Có cần thêm điều kiện chất lượng (VD % câu trả lời đúng tối thiểu) để tính "hoàn thành" không? | Thấp | **Không** — giữ nguyên định nghĩa "hoàn thành" hiện có của app (đã làm qua ít nhất 1 lượt), không mở rộng thêm điều kiện. |
| 4 | Lưới chọn Bộ có phân trang (`DECK_GRID_PAGE_SIZE=4`) — khi auto-focus rơi vào Bộ ở trang khác (VD Bộ 15), `deckPage` có cần tự chuyển sang đúng trang đó không? | Trung bình | **Có** — `deckPage` tự nhảy sang trang chứa Bộ đang focus (VD Bộ 15 → tự chuyển tới trang chứa Bộ 15), user không cần bấm "Tiếp theo" dò tìm. |
| 5 | Nếu sau này thêm Bộ mới vào giữa (VD thêm từ vựng làm số Bộ thay đổi), rule "Bộ nhỏ nhất" có cần tính lại từ đầu không? | Thấp | Không cần xử lý đặc biệt — rule luôn tính động từ `deckDoneModes` hiện tại mỗi lần vào màn hình, tự thích ứng nếu số Bộ thay đổi. |
