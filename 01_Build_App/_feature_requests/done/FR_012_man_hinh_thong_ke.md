# FR_012 — Màn hình Thống kê và lịch sử học

> Trạng thái: **Đã code xong, đã test qua trình duyệt desktop (2026-09-12). Chưa build APK cho gói Phase 2.**
> Thuộc gói Phase 2. Làm cuối cùng trong gói.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-09-11 | Tạo FR_012. PM chọn bổ sung màn hình thống kê riêng. Kèm sửa lỗi streak không tính khi học IT業務編. | NguyenNC (qua Claude Cowork) |

## 1. Loại thay đổi

- [x] Thêm chức năng mới — màn hình thống kê
- [x] Fix bug — streak chỉ tăng khi học IT専門

## 2. Tên chức năng

**Thống kê và lịch sử học** (統計・履歴)

## 3. Mô tả ngắn

Hiện app chỉ có 3 ô số ở trang chủ và không lưu lịch sử theo ngày. FR này thêm một màn hình riêng với lịch nhiệt 12 tuần, phân bố từ theo trạng thái, và dự báo số thẻ phải ôn trong 7 ngày tới.

## 4. Hành vi mong muốn (chi tiết)

### 4.1 Thêm lịch sử theo ngày vào localStorage

Hiện `store.stats` chỉ có `{studied, streak, lastDay}` — biết tổng số lượt nhưng không biết lượt nào rơi vào ngày nào, nên không vẽ được lịch nhiệt.

Thêm `store.stats.history` dạng `{"YYYY-MM-DD": số_lượt}`:

```javascript
if(!store.stats.history) store.stats.history = {};   // migrate cho user cũ
```

Đặt cạnh 2 dòng migrate đã có (`if(!store.deckDone)...`, `if(!store.favorites)...`).

Trong `bumpStudied()`, thêm một dòng ghi lịch sử:

```javascript
var t = today();
store.stats.history[t] = (store.stats.history[t]||0) + 1;
```

**Không dựng lại lịch sử quá khứ.** Dữ liệu cũ không có thông tin ngày, đoán ra là bịa. Lịch nhiệt bắt đầu trống và đầy dần từ hôm nay — nói rõ điều này bằng một dòng chú thích trên màn hình.

### 4.2 Fix bug streak

`bumpStudied()` hiện chỉ được gọi từ trong `reviewCard()`. Nghĩa là học IT業務編 (nghe track, luyện đọc theo thoại) **không tính vào streak** — học cả buổi mà chuỗi ngày vẫn đứng yên.

Sửa: tách `bumpStudied()` ra gọi độc lập, và gọi thêm ở:

- Khi đánh dấu một track IT業務編 là **đã nghe**
- Khi hoàn thành một lượt **luyện đọc theo thoại** của IT業務編

Cẩn thận: `bumpStudied()` cũng tăng `store.stats.studied`. Nếu không muốn lượt nghe track tính chung vào số lượt ôn thẻ thì tách thành 2 hàm: một hàm chỉ cập nhật streak và history, một hàm tăng `studied`. Chọn cách nào cũng được, miễn **streak và history phản ánh đúng mọi ngày có học**.

### 4.3 Lối vào màn hình

Ở `home()`, biến khối 3 ô thống kê thành **bấm được**: chạm vào cả khối thì mở màn hình Thống kê. Thêm mũi tên nhỏ `›` ở góc phải khối để người dùng biết bấm được.

Không thêm thẻ module mới vào `MENU_MODULES` — Thống kê không phải nội dung học.

### 4.4 Nội dung màn hình Thống kê

Hàm mới `statsScreen()`, `onBack = home`.

**Khối 1 — Chuỗi ngày**
- Số ngày liên tiếp cỡ lớn, lấy `store.stats.streak`.
- Dòng phụ: tổng số ngày có học, đếm `Object.keys(store.stats.history).length`.

**Khối 2 — Lịch nhiệt 12 tuần**
- Lưới 7 hàng × 13 cột, mỗi ô là một ngày, ô vuông khoảng 12px, bo góc nhẹ.
- Xếp theo cột, mỗi cột một tuần, hàng trên cùng là thứ Hai.
- 4 mức màu theo số lượt trong ngày:

| Số lượt | Màu |
|---|---|
| 0 | xám nền `var(--line)` |
| 1–7 | xanh lá rất nhạt |
| 8–19 | xanh lá vừa |
| 20 trở lên | xanh lá đậm |

- Ngày trong tương lai để trong suốt.
- `title` của mỗi ô ghi `YYYY-MM-DD: N lượt` để rê chuột xem được trên máy tính.
- Bọc trong `overflow-x:auto` để không tràn màn hình điện thoại.
- Dòng chú thích nhỏ bên dưới: `Lịch sử bắt đầu ghi từ ngày cập nhật app, các ngày trước đó không có dữ liệu.`

**Khối 3 — Phân bố từ theo trạng thái**
- 4 thanh ngang, mỗi thanh một trạng thái, kèm số từ và phần trăm:

| Trạng thái | Điều kiện | Màu |
|---|---|---|
| Đã thuộc | `box >= 3` hoặc `mastered` | xanh lá |
| Đang học | có trong `store.cards`, `box < 3`, chưa `mastered` | xanh dương |
| Từ khó | `c.seen >= 5` và `c.correct / c.seen < 0.5` | đỏ cam |
| Chưa học | không có trong `store.cards` | xám |

- "Từ khó" ưu tiên cao hơn "Đang học" khi một từ thỏa cả hai, để mỗi từ chỉ đếm vào đúng một nhóm và tổng luôn bằng `VOCAB.length`.

**Khối 4 — Dự báo tải ôn 7 ngày tới**
- Biểu đồ cột 7 cột: Hôm nay, +1, +2 … +6.
- Đếm số thẻ trong `store.cards` có `due` rơi vào từng ngày. Thẻ quá hạn (`due` trước hôm nay) gộp hết vào cột Hôm nay.
- Ghi số ngay trên đầu mỗi cột, dùng `font-variant-numeric: tabular-nums` cho thẳng hàng.
- Cột Hôm nay tô màu khác để nổi bật.
- Mục đích: nhìn trước biết ngày nào tải nặng để chủ động sắp lịch.

### 4.5 Không thêm gì khác

Không thêm biểu đồ đường, không thêm điểm số, không thêm huy hiệu. Người trưởng thành duy trì thói quen bằng số liệu thật chứ không bằng phần thưởng kiểu game trẻ em.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — thêm `statsScreen()`, sửa `bumpStudied()`, thêm migrate `history`, sửa `home()` cho khối thống kê bấm được, thêm CSS lịch nhiệt và biểu đồ cột
- [ ] `build_app.py` — không ảnh hưởng
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [x] `CLAUDE.md` — bổ sung `stats.history` vào mô tả schema
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật sau khi xong

## 6. Ràng buộc kỹ thuật

- **Không thêm thư viện biểu đồ.** Lịch nhiệt vẽ bằng CSS grid, biểu đồ cột bằng div có chiều cao tính theo phần trăm. App phải giữ nguyên nguyên tắc 1 file, offline, không fetch gì.
- **Migrate phải an toàn tuyệt đối**: user cũ không có `stats.history` thì tạo `{}`, không đụng vào bất kỳ trường nào khác của `store`.
- Không dựng lại lịch sử quá khứ.
- `history` chỉ tăng thêm khóa mỗi ngày một lần, không làm phình `localStorage` đáng kể (1 năm khoảng 365 khóa, vài KB).
- Dùng ES5 cho đồng nhất với code cũ.

## 7. Ưu tiên

- [x] Trung bình — làm sau FR_011 và 2 mode mới

## 8. Ghi chú thêm

- Số liệu tham chiếu tính trên 667 từ: nếu nạp 5 từ mới mỗi ngày thì ở trạng thái ổn định phải ôn khoảng 20–30 thẻ mỗi ngày. Khối dự báo 7 ngày giúp thấy trước con số này thay vì bị bất ngờ.
- Lỗi streak ở mục 4.2 tồn tại từ lâu và có thể là lý do PM thấy chuỗi ngày không phản ánh đúng công sức bỏ ra. Đáng sửa cùng dịp này.
- Ngưỡng "Từ khó" ở mục 4.4 là đề xuất mới, app hiện chưa có khái niệm này. Nếu PM thấy ngưỡng chưa hợp lý thì chỉnh lại sau khi dùng thử 2 tuần.

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro

| # | Nội dung | Mức | Quyết định |
|---|---|---|---|
| 1 | Lịch nhiệt trống trơn ở lần đầu mở, người dùng tưởng mất tiến độ. | **Cao** | Bắt buộc có dòng chú thích giải thích lịch sử chỉ bắt đầu ghi từ hôm nay. Khối "Từ đã thuộc" vẫn hiện đúng số cũ nên nhìn vào là yên tâm. |
| 2 | `bumpStudied()` cũng tăng `studied` — gọi thêm ở IT業務編 sẽ làm số lượt ôn thẻ bị thổi lên. | Trung bình | Tách thành 2 hàm: một cho streak và history, một cho `studied`. IT業務編 chỉ gọi hàm đầu. |
| 3 | Một từ có thể thỏa cả "Đang học" và "Từ khó", đếm 2 lần thì tổng vượt 667. | Trung bình | Ưu tiên "Từ khó" trước. Mỗi từ chỉ vào đúng một nhóm, kiểm tra tổng phải bằng `VOCAB.length`. |
| 4 | Thẻ quá hạn từ lâu (`due` cách đây nhiều tháng) làm cột Hôm nay cao vọt, biểu đồ mất ý nghĩa. | Trung bình | Vẫn gộp vào cột Hôm nay vì đó là sự thật, nhưng ghi rõ số quá hạn thành dòng riêng dưới biểu đồ: `Trong đó <N> thẻ đã quá hạn`. |
| 5 | Thiết bị đổi múi giờ hoặc đổi ngày hệ thống làm `today()` nhảy. | Thấp | Không xử lý đặc biệt. `today()` dùng `toISOString().slice(0,10)` như code hiện tại, giữ nguyên cho nhất quán. |
| 6 | `history` phình to sau nhiều năm. | Thấp | 365 khóa mỗi năm, vài KB. Không cần dọn. Nếu sau này cần thì cắt bớt khóa cũ hơn 2 năm. |
| 7 | Lịch nhiệt 13 cột trên điện thoại hẹp sẽ tràn ngang. | Thấp | Bọc `overflow-x:auto`, chỉ khối lịch nhiệt cuộn ngang, thân trang không cuộn ngang. |
