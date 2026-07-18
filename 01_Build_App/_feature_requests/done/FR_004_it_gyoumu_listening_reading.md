# FR_004 — IT業務編: Chi tiết Luyện nghe (聞き取り練習) & Luyện đọc (読み練習)

> Tài liệu này CHI TIẾT HÓA mục 4.4.1–4.4.3 của `FR_003_multi_theme_it_gyoumuhen.md` (đã tồn tại, ưu tiên Cao).
> Đọc FR_003 trước để nắm tổng thể (UI button, màn hình chọn chủ đề); FR_004 chỉ tập trung vào 3 yêu cầu cụ thể:
> **3.2.1** Đề xuất chức năng học dựa trên nội dung folder `02_IT_Gyoumuhen` · **3.2.2** Luyện nghe (AudioCD, hiện/ẩn transcript) · **3.2.3** Luyện đọc (kiểm tra đúng nội dung).
> Mục tiêu: đủ chi tiết để Claude Code implement thẳng, không cần đoán thêm.

---

## 0. 変更履歴 (Lịch sử thay đổi)

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-07-17 | Tạo FR_004 dựa trên khảo sát thực tế dữ liệu trong `02_IT_Gyoumuhen` | NguyenNC (qua Claude) |

## 1. Loại thay đổi

- [x] Thêm chức năng mới (new feature)

## 2. Tên chức năng

Module **IT業務編 — Luyện nghe & Luyện đọc** từ nguồn AudioCD (38 mp3) + Transcript (xlsx) đã có sẵn.

## 3. Dữ liệu nguồn đã khảo sát

| File | Nội dung | Số lượng |
|---|---|---|
| `IT_Gyoumuhen.pdf` | Sách scan 104 trang — chỉ dùng tham khảo, KHÔNG parse text | — |
| `AudioCD/*.mp3` | Audio, tên file `XX Track X.mp3` (01–38) | 38 file, ~69MB |
| `IT_Gyoumuhen_AudioCD_Transcript.xlsx` | Transcript đã soạn sẵn theo từng Track | 38 dòng dữ liệu (row 4–41), 9 cột |

**Cột transcript:** `Track | Chương | Unit | Tên Unit (日本語) | Tên Unit (VI) | Loại nội dung | Nhân vật | Nội dung hội thoại (JP) | Ghi chú`

**Quy luật cấu trúc phát hiện được:**
- 2 chương: Chương 1 = Unit 1–5, Chương 2 = Unit 1–15.
- Mỗi Unit có **2 track**: 1 track `モデル会話` (hội thoại mẫu, đọc chuẩn) + 1 track `聞き取り練習` (luyện nghe, tốc độ tự nhiên) — **trừ** Unit 1/Chương 1 chỉ có 1 track (quảng cáo radio DJ, độc thoại).
- Nhân vật xuyên suốt: リー (Li, kỹ sư TQ), ラジュ (Raju, kỹ sư Ấn Độ) — 2 nhân vật chính học việc; 大沢, 田口, 井出, 新山 — đồng nghiệp/quản lý Nhật.

**⚠️ Edge case quan trọng — 2 track KHÔNG có transcript** (audio vẫn có, nhưng cột "Nội dung hội thoại" chỉ ghi placeholder do PDF scan thiếu trang gốc):

| Track | Chương/Unit | Loại | Ghi chú gốc trong xlsx |
|---|---|---|---|
| 9 | Chương 2 / Unit 1 | モデル会話 | PDF nhảy từ trang 31 → 38, thiếu trang |
| 21 | Chương 2 / Unit 7 | モデル会話 | PDF nhảy từ trang 57 → 60, thiếu trang |

**Bảng mapping đầy đủ 38 track** (để build_app.py đối chiếu khi implement):

| Track | Chương | Unit | Tên Unit (JP) | Tên Unit (VI) | Loại nội dung | Có transcript |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 求人ポスター | Bảng tin tuyển dụng | 聞き取り練習 | ✅ |
| 2 | 1 | 2 | 電話で問い合わせる | Gọi điện hỏi thông tin | モデル会話 | ✅ |
| 3 | 1 | 2 | 電話で問い合わせる | Gọi điện hỏi thông tin | 聞き取り練習 | ✅ |
| 4 | 1 | 3 | 職務経歴書 | Sơ yếu lý lịch | 聞き取り練習 | ✅ |
| 5 | 1 | 4 | 面接 | Phỏng vấn | モデル会話 | ✅ |
| 6 | 1 | 4 | 面接 | Phỏng vấn | 聞き取り練習 | ✅ |
| 7 | 1 | 5 | ビザの取得 | Xin visa | モデル会話 | ✅ |
| 8 | 1 | 5 | ビザの取得 | Xin visa | 聞き取り練習 | ✅ |
| 9 | 2 | 1 | 自己紹介 | Tự giới thiệu | モデル会話 | ❌ thiếu |
| 10 | 2 | 1 | 自己紹介 | Tự giới thiệu | 聞き取り練習 | ✅ |
| 11 | 2 | 2 | 要件定義書の読解 | Đọc hiểu yêu cầu | モデル会話 | ✅ |
| 12 | 2 | 2 | 要件定義書の読解 | Đọc hiểu yêu cầu | 聞き取り練習 | ✅ |
| 13 | 2 | 3 | 内容確認 | Xác nhận nội dung | モデル会話 | ✅ |
| 14 | 2 | 3 | 内容確認 | Xác nhận nội dung | 聞き取り練習 | ✅ |
| 15 | 2 | 4 | 担当業務の通知 | Thông báo công việc | モデル会話 | ✅ |
| 16 | 2 | 4 | 担当業務の通知 | Thông báo công việc | 聞き取り練習 | ✅ |
| 17 | 2 | 5 | 詳細設計書を書く | Viết thiết kế chi tiết | モデル会話 | ✅ |
| 18 | 2 | 5 | 詳細設計書を書く | Viết thiết kế chi tiết | 聞き取り練習 | ✅ |
| 19 | 2 | 6 | 仕様変更 | Thay đổi spec | モデル会話 | ✅ |
| 20 | 2 | 6 | 仕様変更 | Thay đổi spec | 聞き取り練習 | ✅ |
| 21 | 2 | 7 | 単体テスト終了報告 | Báo cáo Unit Test | モデル会話 | ❌ thiếu |
| 22 | 2 | 7 | 単体テスト終了報告 | Báo cáo Unit Test | 聞き取り練習 | ✅ |
| 23 | 2 | 8 | 進捗状況の報告 | Báo cáo tiến độ | モデル会話 | ✅ |
| 24 | 2 | 8 | 進捗状況の報告 | Báo cáo tiến độ | 聞き取り練習 | ✅ |
| 25 | 2 | 9 | 遅延報告 | Báo cáo chậm tiến độ | モデル会話 | ✅ |
| 26 | 2 | 9 | 遅延報告 | Báo cáo chậm tiến độ | 聞き取り練習 | ✅ |
| 27 | 2 | 10 | 担当モジュール完成報告 | Hoàn thành module | モデル会話 | ✅ |
| 28 | 2 | 10 | 担当モジュール完成報告 | Hoàn thành module | 聞き取り練習 | ✅ |
| 29 | 2 | 11 | 結合テスト | Kiểm thử tích hợp | モデル会話 | ✅ |
| 30 | 2 | 11 | 結合テスト | Kiểm thử tích hợp | 聞き取り練習 | ✅ |
| 31 | 2 | 12 | デバッグ終了報告とシステムテストの準備 | Báo cáo debug & chuẩn bị System Test | モデル会話 | ✅ |
| 32 | 2 | 12 | デバッグ終了報告とシステムテストの準備 | Báo cáo debug & chuẩn bị System Test | 聞き取り練習 | ✅ |
| 33 | 2 | 13 | システムテスト | Kiểm thử hệ thống | モデル会話 | ✅ |
| 34 | 2 | 13 | システムテスト | Kiểm thử hệ thống | 聞き取り練習 | ✅ |
| 35 | 2 | 14 | オペレーションデモの準備 | Chuẩn bị demo | モデル会話 | ✅ |
| 36 | 2 | 14 | オペレーションデモの準備 | Chuẩn bị demo | 聞き取り練習 | ✅ |
| 37 | 2 | 15 | オペレーションデモ | Demo vận hành | モデル会話 | ✅ |
| 38 | 2 | 15 | オペレーションデモ | Demo vận hành | 聞き取り練習 | ✅ |

## 4. 3.2.1 — Đề xuất chức năng học (phân tích theo nội dung)

Dữ liệu là hội thoại workplace IT thực tế (tuyển dụng → phỏng vấn → nhận việc → viết spec/design → test → báo cáo tiến độ → demo), có bản model dialogue chuẩn + bản luyện nghe. Đề xuất mode theo độ ưu tiên:

| # | Chức năng | Mô tả | Ưu tiên |
|---|---|---|---|
| 1 | **Luyện nghe (Listening)** | Nghe theo track, toggle hiện/ẩn transcript, tốc độ phát | Cao — bắt buộc (3.2.2) |
| 2 | **Luyện đọc (Reading/Shadowing)** | Đọc theo từng câu transcript, chấm điểm phát âm | Cao — bắt buộc (3.2.3) |
| 3 | Quiz hiểu nội dung | Trắc nghiệm sau khi nghe/đọc (ai nói, tình huống gì, xin/từ chối...) | Trung bình — FR riêng sau |
| 4 | Từ vựng theo Unit | Trích thuật ngữ IT từ transcript, đưa vào SRS riêng | Trung bình — FR riêng sau |
| 5 | Kaiwa nhập vai | User chọn đóng 1 nhân vật, TTS đọc phần còn lại | Thấp — mở rộng của Reading |
| 6 | Dictation (nghe — chép lại) | Nghe câu → gõ lại → so khớp | Thấp — cần bàn phím JP, khó cho MVP |

**Phạm vi FR_004 chỉ code #1 và #2.** #3–#6 để FR riêng (đã note trong FR_003 mục 8).

## 5. 3.2.2 — Chi tiết chức năng Luyện nghe

### 5.1 Luồng người dùng
```
Dashboard IT業務編 → chọn Chương → chọn Unit → danh sách Track của Unit (1–2 track) → chọn Track → màn hình Player
```

### 5.2 UI màn hình Player
- Header: tên Unit (JP + VI), badge loại track (モデル会話 / 聞き取り練習).
- Nút toggle **"🔒 Ẩn transcript" / "👁 Hiện transcript"** — mặc định **ẨN**.
- Audio controls: Play/Pause, progress bar + thời gian hiện tại/tổng, nút Replay (về 0:00), chọn tốc độ 0.75x / 1x / 1.25x.
- Khi hiện transcript: hiển thị toàn bộ hội thoại, mỗi lời thoại 1 dòng, tên nhân vật in đậm ở đầu dòng (tách theo `\n` trong dữ liệu gốc).
- Track không có transcript (9, 21): disable toggle, hiện note "Transcript không khả dụng cho track này (thiếu trang scan gốc)" — vẫn cho nghe audio bình thường.

### 5.3 Kỹ thuật
- Mở rộng `playAudioUrl()` (đã có sẵn, dòng 341 `app_template.html`) thành audio controller đầy đủ: hiện tại chỉ có play-to-end Promise, cần thêm `pause()`, `seek()`, `currentTime/duration` binding cho progress bar, và `audio.playbackRate` cho tốc độ phát.
- Transcript render: split theo `\n`, mỗi dòng match regex `^([^：:]+)[：:]\s*(.*)$` để tách tên nhân vật/nội dung, bôi đậm phần tên.

## 6. 3.2.3 — Chi tiết chức năng Luyện đọc (kiểm tra đúng nội dung)

### 6.1 Vấn đề cần giải quyết
Transcript là hội thoại nhiều nhân vật, nhiều dòng dài (289–621 ký tự/track) — khác với "câu ví dụ" ngắn ở mode Reading hiện tại của IT専門. **Phải tách transcript thành từng lời thoại riêng** (mỗi dòng bắt đầu bằng `Tên：`) để luyện đọc từng câu một.

### 6.2 Luồng người dùng
```
Chọn Unit → chọn Track (chỉ track CÓ transcript) → màn hình đọc từng câu
  → hiện câu hiện tại (kèm tên nhân vật) → nghe mẫu (TTS) → bấm mic đọc to
  → SpeechRecognition (ja-JP) nhận dạng → so khớp → hiện điểm + feedback → câu tiếp theo
  → hết track → màn hình tổng kết (điểm trung bình)
```
Tái sử dụng gần như 100% cấu trúc `readingMode()` / `finishReading()` đã có trong `app_template.html`, chỉ đổi nguồn dữ liệu từ `v.ex` (câu ví dụ từ vựng) sang từng dòng hội thoại đã tách.

### 6.3 Thuật toán so khớp (kiểm tra đúng nội dung)
- Tái sử dụng nguyên hàm `similarity(a,b)` + `normJa()` đã có (LCS ratio, loại bỏ dấu câu) — **không viết lại từ đầu**.
- Bổ sung 1 bước: loại bỏ prefix `"Tên："` trước khi so sánh — regex `^[^：:]+[：:]\s*`.
- Giữ nguyên ngưỡng điểm cũ: ≥80 tốt · ≥55 khá · <55 luyện lại.
- Audio gốc không thể cắt theo từng câu (chỉ có theo track) → nghe mẫu từng câu dùng TTS (`speak()`), không dùng file mp3 gốc.

### 6.4 Giới hạn kỹ thuật cần lưu ý khi code
- SpeechRecognition tiếng Nhật với câu dài + nhiều thuật ngữ IT ngoại lai (katakana) → độ chính xác nhận dạng thực tế sẽ thấp hơn từ vựng đơn — cần test thật trước khi chốt ngưỡng điểm.
- Track 9, 21 (không có transcript) → loại khỏi danh sách chọn cho Reading mode.
- Track 1 (quảng cáo DJ, độc thoại, không có prefix tên nhân vật rõ ràng) → xử lý như 1 "câu" duy nhất.

## 7. Ảnh hưởng đến file nào

- [x] `app_template.html` — thêm dashboard IT業務編, Player nghe, Reading mode theo dòng hội thoại, mở rộng audio controller
- [x] `build_app.py` — thêm hàm `extract_gyoumu()` đọc `IT_Gyoumuhen_AudioCD_Transcript.xlsx` (parse XML thô như `extract_vocab()` hiện tại, **KHÔNG dùng `openpyxl.save()`**, chỉ đọc), inject JSON `GYOUMU_DATA`
- [x] Cần xử lý vị trí file audio khi build (xem Rủi ro #1 ở mục 9)
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật kiến trúc multi-module

## 8. Ràng buộc kỹ thuật

- localStorage riêng cho module này: `kokoro_gyoumu_v1` (không đụng `jp_learn_v1` của IT専門)
- Giữ 100% offline cho phần IT専門 hiện tại — không ảnh hưởng
- Tốc độ phát dùng `audio.playbackRate` (HTML5 Audio API, không cần thư viện ngoài)
- SpeechRecognition tái sử dụng `requestMicPermission()` / `SR` đã có
- Tương thích Android Chrome + iOS Safari

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro

| # | Nội dung | Mức độ | Đề xuất xử lý |
|---|---|---|---|
| 1 | **Vị trí file audio khi build:** `AudioCD/` nằm ở `02_IT_Gyoumuhen`, ngoài `01_Build_App`. Nếu build script chỉ tham chiếu path tương đối, app sẽ lỗi khi user chỉ copy riêng file HTML sang điện thoại (cách dùng hiện tại). | **Cao** | Copy `AudioCD/` vào `01_Build_App/audio/` khi chạy `build_app.py` (không base64 — 38 file ~69MB sẽ đội file HTML lên >90MB, không khả thi) |
| 2 | 2 track không có transcript (Track 9, 21) — cho nghe nhưng ẩn hoàn toàn khỏi Reading mode, đã quyết định ở mục 6.4. Cần PM xác nhận lại là đủ, không cần transcript giả/AI tái tạo. | Cao | Xác nhận với PM trước khi code |
| 3 | Transcript không có timestamp theo câu → không thể tự động highlight câu đang phát khi nghe audio gốc (kiểu karaoke). MVP: hiện toàn bộ transcript tĩnh, không sync theo thời gian thực. | Trung bình | Chấp nhận cho MVP; version sau nếu cần sync phải tự đánh timestamp từng dòng (tốn công) |
| 4 | Độ chính xác SpeechRecognition với câu dài + thuật ngữ IT ngoại lai chưa được test thực tế | Trung bình | Test thử với vài track trước khi chốt ngưỡng điểm 80/55 |
| 5 | Unit 1/Chương 1 chỉ có 1 track (không có cặp モデル会話/聞き取り練習 như unit khác) | Thấp | UI danh sách track phải xử lý số lượng biến thiên (1 hoặc 2), không hardcode 2 |

## 10. Ưu tiên

- [x] Cao — cần ngay (nối tiếp FR_003)

## 11. Ghi chú thêm — thứ tự triển khai đề xuất

1. Copy `AudioCD/` vào `01_Build_App/audio/` (thủ công hoặc script) + xử lý trong `build_app.py`
2. Viết `extract_gyoumu()` trong `build_app.py`, inject `GYOUMU_DATA` JSON
3. Build UI dashboard IT業務編 (danh sách Chương → Unit → Track)
4. Build Player nghe (5.2, 5.3) — mở rộng audio controller
5. Build Reading mode theo dòng hội thoại (6.2, 6.3)
6. Build & verify: check JS syntax, check `GYOUMU_DATA` count = 38, test thử nghe + đọc trên vài track thật
