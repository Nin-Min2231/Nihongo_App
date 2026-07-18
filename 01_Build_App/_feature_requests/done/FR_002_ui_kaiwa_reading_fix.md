# FR_002 — Đổi màu hệ thống + Fix Kaiwa + Thêm mic Luyện đọc

---

## 1. Loại thay đổi

- [ ] Thêm chức năng mới (new feature)
- [x] Sửa/nâng cấp chức năng có sẵn (update)
- [x] Fix bug
- [x] Thay đổi UI/UX

## 2. Tên chức năng

Gồm 3 thay đổi:
1. Đổi color scheme toàn app
2. Fix nút "Hiển thị tất cả" ở Kaiwa
3. Thêm button luyện đọc có mic ở màn Luyện đọc

## 3. Mô tả ngắn

- Đổi tone màu chủ đạo sang xanh dương (blue) + trắng + cold palette, thay cho tone đỏ hiện tại.
- Nút "Hiển thị tất cả" ở Kaiwa hiện không hoạt động → sửa thành toggle 2 trạng thái (hiện/ẩn).
- Màn Luyện đọc chưa có nút mic riêng để chấm phát âm cả câu → thêm button rõ ràng.

## 4. Hành vi mong muốn (chi tiết)

### 4.1. Đổi màu hệ thống

- `--brand` / `--brand2`: đổi sang tông xanh dương (VD: `#2563eb` / `#3b82f6`)
- `--bg`: trắng hoặc xám rất nhạt lạnh (VD: `#f0f4f8`)
- `--soft`: xanh nhạt lạnh (VD: `#eff6ff`)
- `--accent` (nút đúng/tốt): giữ xanh lá hoặc chỉnh lại cho hài hòa
- Header gradient: xanh dương đậm → xanh dương sáng
- Toàn bộ các element khác (chip, button, card border...) theo palette mới
- Kaiwa bubble: left = xanh nhạt, right = xanh lá nhạt (thay đỏ/xanh cũ)

### 4.2. Fix Kaiwa — nút Hiển thị/Ẩn tất cả

**Hiện tại:** Nút "👁 Hiện tất cả" click không hoạt động (bug).

**Mong muốn:**
- Default: tất cả bubble và nghĩa đều ẨN (chỉ hiện bubble đầu tiên)
- User click nút → **Trạng thái 1: Hiện tất cả** — show toàn bộ bubble + nghĩa. Icon đổi thành "🙈 Ẩn tất cả"
- User click lại → **Trạng thái 2: Ẩn tất cả** — ẩn lại toàn bộ (trừ bubble đầu). Icon đổi thành "👁 Hiện tất cả"
- Toggle qua lại giữa 2 trạng thái mỗi lần click

### 4.3. Màn Luyện đọc — thêm button mic chấm phát âm

**Hiện tại:** Có mic nhưng không nổi bật, user không nhận ra.

**Mong muốn:**
- Thêm 1 button rõ ràng bên dưới câu ví dụ, text: "🎤 Luyện đọc"
- User click "🎤 Luyện đọc" → app bật mic thu giọng → nhận diện giọng nói (SpeechRecognition, lang=ja-JP) → so sánh với câu ví dụ → hiển thị điểm phát âm (similarity score)
- Hiện kết quả: "Bạn đọc: ..." + điểm (≥80 tuyệt, ≥55 khá, <55 thử lại)
- Nếu thiết bị không hỗ trợ mic → ẩn button, không hiện lỗi

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — CSS variables + Kaiwa logic + Reading mic button
- [ ] `build_app.py`
- [ ] `日本語の辞書.xlsx`
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật mô tả màu sắc mới

## 6. Ràng buộc kỹ thuật

- Giữ nguyên hoạt động offline (không fetch thư viện ngoài)
- Giữ nguyên localStorage key `jp_learn_v1` (không mất tiến độ)
- Mic phải request permission đúng cách (đã có logic `requestMicPermission()` — tái sử dụng)
- Tương thích Android Chrome; iOS Safari fallback gracefully (ẩn mic nếu không hỗ trợ)

## 7. Ưu tiên

- [x] Cao — cần ngay
- [ ] Trung bình
- [ ] Thấp

## 8. Ghi chú thêm

- Mục 4.1 (màu): chỉ cần đổi CSS variables trong `:root` + vài chỗ hardcode màu trong bubble kaiwa. Không ảnh hưởng logic.
- Mục 4.2 (Kaiwa): kiểm tra lại selector `#showAll` onclick — có thể bị mất binding hoặc selector sai sau lần build trước.
- Mục 4.3 (Reading mic): logic mic đã có sẵn trong `setupReadingMic()` — cần đảm bảo button hiện rõ ràng hơn với label text thay vì chỉ icon nhỏ.
