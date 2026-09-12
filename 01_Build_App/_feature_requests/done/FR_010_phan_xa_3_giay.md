# FR_010 — Chế độ học mới: Phản xạ 3 giây (瞬間作文)

> Trạng thái: **Đã code xong, đã test qua trình duyệt desktop (2026-09-12). Chưa build APK cho gói Phase 2.**
> Thuộc gói Phase 2. Làm sau FR_009 để dùng lại khuôn code đã quen.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-09-11 | Tạo FR_010. PM chọn bài này làm bài bổ sung số 2, phục vụ mục tiêu nghe nói phản xạ khi họp với đối tác Nhật. | NguyenNC (qua Claude Cowork) |

## 1. Loại thay đổi

- [x] Thêm chức năng mới — chế độ học thứ 7 của module IT専門

## 2. Tên chức năng

**Phản xạ 3 giây** (瞬間作文) — mode id `reflex`

## 3. Mô tả ngắn

Hiện nghĩa tiếng Việt, người học phải **đọc to** từ tiếng Nhật trước khi vòng đếm 3 giây chạy hết, rồi tự chấm mình có bật ra được hay chưa. Bài này luyện đúng kỹ năng cần khi họp: nhớ ra từ dưới áp lực thời gian, chứ không phải nhận ra từ khi nhìn thấy nó.

## 4. Hành vi mong muốn (chi tiết)

### 4.1 Vào bài

- Thêm nút thứ 7 vào lưới `.modes` trong `homeDashboard()`, đặt **sau Luyện nói**, trước Yêu thích:

```
'<button class="mode" data-mode="reflex">'+
  '<span class="ico">⚡</span><div class="mt">Phản xạ '+(uiSettings.reflexSec||3)+'s</div><div class="md">Thấy nghĩa, nói ra từ</div></button>'+
```

- Thêm nhánh vào `startMode()`: `else if(m==='reflex') reflexMode(list);`
- Hàm `reflexMode(list)` đặt sau `speakMode()`.

### 4.2 Khác Luyện nói ở chỗ nào

| | Luyện nói (`speak`) | Phản xạ (`reflex`) |
|---|---|---|
| Đề bài | Hiện sẵn từ tiếng Nhật, nghe mẫu rồi đọc theo | Chỉ hiện nghĩa tiếng Việt, phải tự nhớ ra từ |
| Dùng mic | Có, chấm bằng nhận giọng | **Không dùng mic** |
| Chấm điểm | Máy chấm LCS 0–100 | **Người học tự chấm 2 mức** |
| Sức ép thời gian | Không | Có, vòng đếm ngược |
| Luyện cái gì | Cơ miệng, phát âm | Tốc độ nhớ ra từ |

**Không dùng mic là cố ý.** Nhận giọng mất 1–2 giây khởi động, phá hỏng việc đo phản xạ. Tự chấm nhanh và trung thực hơn cho mục đích này.

### 4.3 Màn hình câu hỏi — pha 1

- `setHeader('Phản xạ '+sec+' giây', (i+1)+' / '+queue.length, true)`
- Hiện nghĩa tiếng Việt `v.vi` cỡ chữ lớn, khoảng 22–24px, căn giữa.
- Dòng hướng dẫn nhỏ phía trên: `Đọc to từ tiếng Nhật trước khi hết giờ`
- **Vòng đếm ngược hình tròn** vẽ bằng SVG, đường kính khoảng 104px, đặt giữa màn hình:
  - 1 vòng nền màu `var(--line)`, 1 vòng chạy màu đỏ cam, dùng `stroke-dasharray` và `stroke-dashoffset` để rút dần.
  - Giữa vòng hiện số giây còn lại, làm tròn lên.
  - Cập nhật bằng `setInterval` khoảng 60ms. **Bắt buộc `clearInterval` khi rời màn hình hoặc khi chuyển câu** — nếu quên, interval chạy nền gây tụt pin và lỗi lạ.
  - Chống chạy tiếp khi user đã rời màn: đầu mỗi nhịp kiểm tra phần tử SVG còn tồn tại không, không thì `clearInterval` rồi `return`.
- Nút **Xem đáp án ngay** — bấm là bỏ qua phần còn lại của vòng đếm, sang pha 2 luôn.
- Hết giờ → tự sang pha 2.

### 4.4 Màn hình đáp án — pha 2

- `clearInterval` trước tiên.
- Hiện đầy đủ: `v.w` cỡ lớn, `v.r` bên dưới, `v.vi`, và `v.en` nếu có.
- Nút loa đọc `v.w`.
- Câu hỏi tự chấm: `Anh có bật ra được từ này trong ... giây không?`
- 2 nút, cùng hàng, rộng bằng nhau:
  - **Chưa bật ra được** → `reviewCard(v.id,0)`
  - **Bật ra được** → `reviewCard(v.id,2)`, `score++`
- Bấm nút nào cũng sang câu tiếp theo ngay, không chờ.

### 4.5 Chọn từ và kết thúc

- Lọc bỏ từ đã đánh dấu đã nhớ: `!isMastered(v.id)`.
- Số câu: `curDeck==='ALL'` thì lấy 12 câu ngẫu nhiên, học theo Bộ thì lấy hết bộ.
- Cần tối thiểu 4 từ, không đủ thì báo `'<div class="note">Bộ này cần ít nhất 4 từ chưa thuộc.</div>'` — nhớ `setHeader` trước khi `return`.
- Kết thúc: `finish('reflex', queue.length, score);`

### 4.6 Thời gian đếm ngược chỉnh được

- Đọc từ `uiSettings.reflexSec`, mặc định **3**. Ba mức cho chọn: **3 / 5 / 8 giây**.
- Ô chỉnh nằm trong màn hình Cài đặt — **do FR_011 làm**, cùng chỗ với cỡ chữ. FR này chỉ đọc giá trị.
- Nếu FR_011 chưa xong thì tạm hardcode 3 giây, nhưng phải đọc qua biến để sau nối vào không phải sửa lại.
- Lý do cho chỉnh: tốc độ truy xuất từ chậm dần theo tuổi là chuyện bình thường, không phải kém. 3 giây quá gấp thì nới ra 5 hoặc 8, vẫn giữ được tác dụng luyện phản xạ.

### 4.7 KHÔNG thêm icon vào lưới chọn Bộ

Giống FR_009 mục 4.7: **giữ nguyên đúng 4 icon** 🗂️✍️🎧🎤 trong `deckGridHTML()`. Mode `reflex` vẫn ghi cờ `deckDone` nhưng không hiển thị icon, để không làm các Bộ đã hoàn thành mất màu xanh.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — thêm `reflexMode()`, 1 nút mode, 1 nhánh `startMode()`, CSS cho vòng đếm
- [ ] `build_app.py` — không ảnh hưởng
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [x] `CLAUDE.md` — cập nhật danh sách mode
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật sau khi xong

## 6. Ràng buộc kỹ thuật

- **Không dùng mic**, không gọi `nativeSR()` hay `SpeechRecognition` — xem 4.2.
- Không thêm thư viện ngoài. Vòng đếm vẽ bằng SVG viết tay, không dùng thư viện chart.
- Không đổi cấu trúc `localStorage` (chỉ đọc thêm `uiSettings.reflexSec` do FR_011 tạo).
- Không phá `deckGridHTML()`.
- `clearInterval` đầy đủ ở mọi lối thoát: bấm Back, bấm Xem đáp án, hết giờ, chuyển câu, kết thúc bài.
- Dùng ES5 cho đồng nhất với code cũ.

## 7. Ưu tiên

- [x] Cao — bài hiệu quả nhất cho mục tiêu nói phản xạ

## 8. Ghi chú thêm

- Dùng `v.vi` làm đề bài nên bài này chạy được với **cả 667 từ**, không lọc bỏ từ nào (cột E không có ô trống nào).
- Bài này đặc biệt hợp buổi sáng: ôn lại đúng những từ đã nạp tối hôm trước, lúc trí nhớ vừa được củng cố qua giấc ngủ.
- Tự chấm chỉ 2 mức là cố ý. Bốn mức làm người học phải cân nhắc, mà cân nhắc thì mất luôn cảm giác phản xạ vừa đo được.

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro

| # | Nội dung | Mức | Quyết định |
|---|---|---|---|
| 1 | `setInterval` không được dọn khi user bấm Back giữa chừng → chạy nền, tụt pin, có thể lỗi khi render màn khác. | **Cao** | Bắt buộc `clearInterval` ở mọi lối thoát, và mỗi nhịp kiểm tra phần tử SVG còn tồn tại không. |
| 2 | Tự chấm thì người học có thể tự dễ dãi với mình. | Trung bình | Chấp nhận. Đây là bài tự luyện, không phải bài thi. Câu hỏi đặt rõ "có bật ra được không" giúp tự đánh giá trung thực hơn. |
| 3 | 3 giây quá ngắn, dễ nản. | Trung bình | Cho chỉnh 3 / 5 / 8 giây. Mặc định 3, nới ra được ngay trong Cài đặt. |
| 4 | Thêm icon thứ 5 vào lưới Bộ sẽ làm Bộ đã xong mất màu xanh. | **Cao** | Giữ đúng 4 icon, xem 4.7. |
| 5 | Nút loa đọc `v.w` — với từ katakana thì cách đọc trùng luôn mặt chữ, nghe không thêm thông tin gì. | Thấp | Vẫn để nút loa, không phân biệt. Nghe lại vẫn có ích cho việc nhớ âm. |
| 6 | FR_011 chưa xong thì `uiSettings` chưa tồn tại → lỗi `undefined`. | Trung bình | Đọc phòng thủ: `(typeof uiSettings!=='undefined' && uiSettings.reflexSec) || 3`. |
| 7 | Vòng đếm chạy mượt trên máy tính nhưng có thể giật trên điện thoại yếu. | Thấp | 60ms một nhịp là đủ mượt và nhẹ. Nếu giật thì nới lên 100ms, không ảnh hưởng chức năng. |
