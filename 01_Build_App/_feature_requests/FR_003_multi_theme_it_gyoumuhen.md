# FR_003 — Thêm màn hình chính phân chia theo chủ đề + Tích hợp IT業務編 + Chỉnh UI button

---

## 1. Loại thay đổi

- [x] Thêm chức năng mới (new feature)
- [x] Sửa/nâng cấp chức năng có sẵn (update)
- [x] Thay đổi UI/UX

## 2. Tên chức năng

Gồm 3 nhóm thay đổi:
1. Chỉnh UI button Setting + button Back
2. Thêm màn hình chính phân chia theo chủ đề (Topic Selection Screen)
3. Tích hợp chủ đề IT業務編 (しごとの日本語 IT業務編) với audio + transcript

## 3. Mô tả ngắn

- Chỉnh lại style cho button Settings (⚙️) và button Back (← 戻る) cho hài hòa hơn.
- Thêm một màn hình **chọn chủ đề** trước khi vào các mode học. Mỗi chủ đề là một bộ nội dung riêng biệt.
- Chủ đề đầu tiên (IT専門) chính là toàn bộ hệ thống hiện tại (giữ nguyên 100%).
- Chủ đề thứ hai (IT業務編) dựa vào sách "しごとの日本語 IT業務編" — có file AudioCD (38 track mp3) + transcript (xlsx) + PDF (104 trang scan).
- 3 chủ đề còn lại (日常生活, N2, 面接) placeholder để phát triển sau.

## 4. Hành vi mong muốn (chi tiết)

### 4.1. Chỉnh UI button

#### Button Settings (⚙️):
- Background: `#d6e1fa`
- Màu icon: màu đậm hơn, phù hợp với background (VD: `#1e40af`)
- Thêm text `設定` bên cạnh icon ⚙️
- Giữ nguyên vị trí (header, bên phải)

#### Button Back (← 戻る):
- Background: `#d6e1fa`
- Text color: `#1e40af`
- Giữ nguyên vị trí và chức năng

### 4.2. Màn hình chính — Chọn chủ đề (Topic Selection Screen)

**Flow điều hướng mới:**
```
App mở → [Màn hình chọn chủ đề] → User chọn chủ đề → [Dashboard / Mode học của chủ đề đó]
```

**Giao diện màn hình chọn chủ đề:**
- Header: "ココロ日本語" (giữ nguyên header hiện tại)
- Hiện danh sách các chủ đề dạng card lớn, mỗi card gồm:
  - Icon / emoji đại diện
  - Tên chủ đề (tiếng Nhật + tiếng Việt)
  - Mô tả ngắn 1 dòng
  - Badge "Coming soon" nếu chưa phát triển

**Danh sách chủ đề:**

| # | Tên chủ đề | Tiếng Việt | Icon | Trạng thái |
|---|---|---|---|---|
| 1 | IT専門 | Từ vựng IT chuyên ngành | 💻 | ✅ Active — chính là hệ thống hiện tại |
| 2 | IT業務編 | Tiếng Nhật công việc IT | 🏢 | ✅ Active — FR này sẽ xây dựng |
| 3 | 日常生活 | Giao tiếp hàng ngày | 🏠 | 🔜 Coming soon |
| 4 | N2 | Luyện thi JLPT N2 | 📝 | 🔜 Coming soon |
| 5 | 面接 | Phỏng vấn xin việc | 🤝 | 🔜 Coming soon |

- User tap vào chủ đề Active → chuyển sang dashboard / mode tương ứng
- User tap vào chủ đề Coming soon → hiện toast "Đang phát triển, hãy chờ nhé!"

### 4.3. Chủ đề IT専門 (3.1)

- **Giữ nguyên 100%** toàn bộ hệ thống hiện tại: dashboard, 6 mode học (Flashcard, Quiz, Listening, Speaking, Reading, Kaiwa), SRS, TTS, settings.
- Chỉ cần wrap vào trong scope của chủ đề IT専門.

### 4.4. Chủ đề IT業務編 (3.2)

#### Nguồn dữ liệu:
- **PDF**: `D:\01_NguyenNC\10_Claude\100_日本語\02_IT_Gyoumuhen\IT_Gyoumuhen.pdf` (104 trang scan — dùng làm tham khảo, không parse text)
- **AudioCD**: `D:\01_NguyenNC\10_Claude\100_日本語\02_IT_Gyoumuhen\AudioCD\` (38 file mp3, tổng ~69MB)
- **Transcript**: `D:\01_NguyenNC\10_Claude\100_日本語\02_IT_Gyoumuhen\IT_Gyoumuhen_AudioCD_Transcript.xlsx`

#### Cấu trúc nội dung (từ transcript):
Sách gồm 15 Unit chia thành nhiều chương, bao gồm các chủ đề IT workplace thực tế:

| Unit | Tên (日本語) | Tên (Tiếng Việt) | Track |
|---|---|---|---|
| 1 | 求人ポスター | Bảng tin tuyển dụng | 1 |
| 2 | 電話で問い合わせる | Gọi điện hỏi thông tin | 2-3 |
| 3 | 職務経歴書 | Sơ yếu lý lịch | 4 |
| 4 | 面接 | Phỏng vấn | 5-6 |
| 5 | ビザの取得 | Xin visa | 7-8 |
| 6 | 自己紹介 | Tự giới thiệu | 9-11 |
| 7 | 要件定義書の読解 | Đọc yêu cầu định nghĩa | 12-13 |
| 8 | 内容確認 | Xác nhận nội dung | 14-15 |
| 9 | 担当業務の通知 | Thông báo công việc | 16-17 |
| 10 | 詳細設計書を書く | Viết thiết kế chi tiết | 18-19 |
| 11 | 仕様変更 | Thay đổi spec | 20-21 |
| 12 | 単体テスト終了報告 | Báo cáo Unit Test | 22-23 |
| 13 | 進捗状況の報告 | Báo cáo tiến độ | 24-25 |
| 14 | 遅延報告 | Báo cáo chậm tiến độ | 26-27 |
| 15 | 担当モジュール完成報告 | Hoàn thành module | 28-29 |
| ... | 結合テスト〜オペレーションデモ | Test tích hợp〜Demo | 30-38 |

#### Chức năng cho IT業務編:

**4.4.1 Phân tích nội dung → đề xuất chức năng học phù hợp:**

Dựa vào nội dung sách (hội thoại workplace IT: yêu cầu, thiết kế, test, báo cáo...), các mode học phù hợp:

- **Luyện nghe (聞き取り練習)**: Nghe audio track mp3 + hiển thị/ẩn transcript
- **Đọc hội thoại (会話練習)**: Hiện transcript, luyện đọc theo từng câu
- **Từ vựng IT業務 (語彙)**: Trích từ vựng chuyên ngành từ transcript (nếu có)
- **Quiz nội dung**: Câu hỏi kiểm tra hiểu biết sau khi nghe/đọc

**4.4.2 Luyện nghe (聞き取り練習) — QUAN TRỌNG:**

- User chọn Unit → chọn Track → app play file mp3 tương ứng
- **Chế độ hiển thị:**
  - 🔒 Ẩn transcript (chỉ nghe, không nhìn chữ) — mặc định
  - 👁 Hiện transcript (vừa nghe vừa đọc theo)
  - Toggle qua lại bằng 1 nút
- **Controls:**
  - Play / Pause / Stop
  - Thanh progress bar + thời gian
  - Nút replay (nghe lại từ đầu)
  - Tốc độ phát: 0.5x / 0.75x / 1x / 1.25x
- **Lưu ý kỹ thuật:** File mp3 nằm trong folder `AudioCD/`, cần tham chiếu đúng đường dẫn tương đối từ file HTML output.

**4.4.3 Luyện đọc (読み練習):**

- Hiện transcript của Unit/Track đã chọn
- User đọc từng câu → app thu giọng qua SpeechRecognition (ja-JP)
- So sánh nội dung nhận diện được với transcript gốc → hiện điểm (similarity score)
- Highlight câu đang luyện, cho phép chuyển câu tiếp theo
- Nút phát mẫu (nghe lại câu đó từ TTS hoặc audio gốc nếu có thể map)

### 4.5. Chủ đề 日常生活 / N2 / 面接 (3.3, 3.4, 3.5)

- Chỉ hiện card trên màn hình chọn chủ đề với badge "Coming soon"
- Tap vào → toast "Đang phát triển, hãy chờ nhé! 🚧"
- Không cần code logic gì bên trong

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — UI button, thêm màn hình chọn chủ đề, thêm module IT業務編
- [x] `build_app.py` — có thể cần update để inject thêm dữ liệu transcript IT業務編
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật kiến trúc mới (multi-theme)
- [x] Khác: `IT_Gyoumuhen_AudioCD_Transcript.xlsx` — đọc dữ liệu đầu vào; thư mục `AudioCD/` — file mp3 nguồn

## 6. Ràng buộc kỹ thuật

- Giữ nguyên hoạt động offline cho phần IT専門 (không ảnh hưởng hệ thống cũ)
- File mp3 AudioCD khá lớn (~69MB tổng), cần cân nhắc:
  - **Option A**: Link trực tiếp file mp3 từ folder (dùng đường dẫn tương đối) — file HTML không phình to, nhưng phải giữ folder AudioCD cùng thư mục
  - **Option B**: Nhúng base64 vào HTML — hoạt động offline hoàn toàn nhưng file sẽ rất lớn (~92MB+)
  - **Khuyến nghị**: Option A — tham chiếu tương đối, kèm hướng dẫn user đặt folder AudioCD đúng vị trí
- Giữ nguyên localStorage key `jp_learn_v1` cho IT専門 (không mất tiến độ)
- IT業務編 nên dùng localStorage key riêng (VD: `kokoro_gyoumu_v1`)
- Tương thích Android Chrome + iOS Safari
- SpeechRecognition cho luyện đọc: reuse logic `requestMicPermission()` đã có

## 7. Ưu tiên

- [x] Cao — cần ngay

## 8. Ghi chú thêm

- **Thứ tự triển khai đề xuất:**
  1. Chỉnh UI button (nhỏ, làm trước)
  2. Thêm màn hình chọn chủ đề + wrap IT専門
  3. Build module IT業務編: parse transcript → luyện nghe → luyện đọc
  4. Build & verify toàn bộ

- **Dữ liệu transcript đã có sẵn** trong `IT_Gyoumuhen_AudioCD_Transcript.xlsx` với cấu trúc:
  - Cột: Track | Chương | Unit | Tên Unit (JP/VN) | Loại nội dung | Nhân vật | Nội dung hội thoại | Ghi chú
  - 38 track, 15 Unit, nội dung hội thoại đầy đủ bằng tiếng Nhật
  - Một số track bị thiếu trong PDF scan (Unit 7, Unit 12 track đầu) — đã ghi chú trong xlsx

- **Lưu ý 2 track thiếu transcript:** Unit 7 (Track 22) và Unit 6 (Track 9) bị thiếu trang trong PDF gốc. Nếu audio vẫn có thì cho phép nghe nhưng ghi chú "Transcript không khả dụng".

- **Audio mapping:** Tên file mp3 theo format `XX Track X.mp3` (01-38). Cần map chính xác Track number trong transcript với file mp3.

- **Scope FR này KHÔNG bao gồm:** trích từ vựng từ transcript (có thể tạo FR riêng sau), quiz nội dung (FR riêng sau).
