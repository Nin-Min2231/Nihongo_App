# FR_005 — Fix TTS trên Android + Redesign màn hình Flashcard + Fix màn hình Luyện nghe

> Trạng thái: **HOÀN THÀNH — ĐÃ XÁC NHẬN HOẠT ĐỘNG TRÊN ĐIỆN THOẠI THẬT (2026-07-18).** PM báo "Đã nghe được" sau khi cài bản APK có plugin TTS native (`@capacitor-community/text-to-speech`).
> Đã đối chiếu với code hiện tại trong `app_template.html` (bản mới nhất, có deck/Bộ, mastered, favorites) để chẩn đoán nguyên nhân trước khi đề xuất hướng fix.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-07-18 | Tạo FR_005 theo yêu cầu bug report + redesign Flashcard | NguyenNC (qua Claude) |
| 2026-07-18 | Triển khai xong: timeout+toast cho TTS, fix guard sai ở Luyện nghe, redesign Flashcard (header Bộ, gộp nút, "Đã nhớ"=reviewCard quality 2). PM xác nhận: giữ đề xuất mặc định ở mục 9.1, môi trường test là "cả 2" (Chrome + APK) ở mục 9.2. | NguyenNC (qua Claude) |
| 2026-07-18 | Bổ sung theo phản hồi sau khi test bản đầu: (1) đổi màu 4 nút Flashcard cho phân biệt rõ theo trạng thái; (2) xác nhận banner "Quyền microphone bị từ chối" trong ảnh chụp là do mở bằng Chrome (không phải APK) — đúng thiết kế (code có `if(isNativeApp()){speakMode(list);return;}` nên banner này không thể xuất hiện trong APK); PM xác nhận Luyện nói hoạt động tốt trên APK; (3) thêm âm thanh phản hồi theo điểm phát âm (Web Audio API, không cần file âm thanh ngoài), đổi ngưỡng điểm từ 80/55 sang 90/51 theo yêu cầu, áp dụng đồng bộ cho cả 4 nơi chấm điểm phát âm (Luyện nói, Luyện đọc IT専門, Luyện đọc IT業務編, Kaiwa). Đã build lại APK debug (`03_Android_App/Kokoro_Nihongo.apk`) với đầy đủ các fix. | NguyenNC (qua Claude) |
| 2026-07-18 | PM test bản APK ở trên **thật** trên điện thoại, phát hiện âm thanh TTS **hoàn toàn không phát** (toast "Không phát được âm thanh, kiểm tra kết nối mạng" dù mạng đã kết nối) — tức root cause gốc (Google TTS lỗi trên Android WebView) **chưa từng được fix thật sự**, bản trước chỉ thêm timeout+toast báo lỗi thay vì im lặng, không sửa được nguyên nhân. Do không có thiết bị Android thật để debug trực tiếp (xem mục 5.5 handover), đã áp dụng các cải tiến hợp lý nhất có thể kiểm chứng qua code: tăng timeout 5s→8s (giảm khả năng timeout giả do mạng di động chậm), thêm tự động thử lại với endpoint Google TTS dự phòng (`client=tw-ob` thay vì `client=gtx`) trước khi coi là lỗi hẳn, và hiện **mã lỗi cụ thể** trong toast (VD "error:timeout"/"error:media2"/"error:play(...)") để có dữ liệu chẩn đoán chính xác hơn ở lần test tiếp theo nếu vẫn còn lỗi. Đồng thời làm 3 yêu cầu UI khác: (a) IT専門 — bỏ khối thống kê + progress bar đầu trang (giữ Chủ đề/Bộ học/Chế độ học), đổi màu Bộ đang chọn thành xanh nhạt; (b) Flashcard — rút gọn text nút ("Xem chi tiết"→"Chi tiết", "Từ tiếp theo"→"Tiếp theo") để không xuống dòng, đổi màu cố định 3 nút (Chi tiết=xanh lá, Yêu thích=vàng, Đã nhớ=cam), thay cho màu theo trạng thái của bản trước; (c) Main menu — redesign, thêm khối thống kê tổng hợp toàn hệ thống (Streak / Từ đã thuộc IT専門 / Track đã nghe IT業務編) thay cho khối thống kê đã bỏ khỏi IT専門. Đã build lại APK debug lần nữa. **Lưu ý quan trọng: fix âm thanh lần này là cải tiến chẩn đoán + giảm rủi ro, KHÔNG có gì đảm bảo đã hết lỗi hẳn vì chưa test được trên thiết bị thật — cần PM test lại và báo đúng mã lỗi hiện trong toast nếu vẫn lỗi.** | NguyenNC (qua Claude) |
| 2026-07-18 | PM test lại trên máy thật, âm thanh **vẫn lỗi** — lần này toast hiện rõ mã lỗi `error:media4` (MediaError.code=4 = MEDIA_ERR_SRC_NOT_SUPPORTED, cả 2 endpoint Google TTS gtx/tw-ob đều bị). Kết luận: nguồn Google Translate TTS (endpoint không chính thức) **không đáng tin cậy trong Android WebView đóng gói** — có thể do server trả về nội dung không phải audio hợp lệ khi request từ WebView (khác context so với trình duyệt thật). **Fix triệt để lần này**: bỏ hẳn phụ thuộc vào Google TTS network endpoint khi chạy native — thêm plugin Capacitor chính thức `@capacitor-community/text-to-speech@8.0.2` (dùng thẳng engine TextToSpeech của Android, y hệt cách `@capgo/capacitor-speech-recognition` đã dùng cho mic và đã xác nhận hoạt động tốt). `speak()`/`speakAsync()` giờ kiểm tra `isNativeApp()` trước tiên: nếu native → gọi `nativeSpeak()` qua plugin (không qua mạng, không phụ thuộc Google); nếu lỗi (VD thiếu gói giọng đọc tiếng Nhật) → toast hướng dẫn vào Cài đặt Android bật giọng đọc. Đường Google TTS + device speechSynthesis cũ **vẫn giữ nguyên cho môi trường web/Chrome** (không đổi gì ở nhánh đó). Đã verify: plugin compile thành công vào APK (class `TextToSpeechPlugin` có trong classes3.dex/classes5.dex qua kiểm tra bytecode), test logic bằng mock `window.Capacitor.Plugins.TextToSpeech` trong Chrome preview — `speak()` gọi đúng plugin với `{text,lang:'ja-JP',rate,pitch,volume}`, xử lý lỗi đúng. Đồng thời làm thêm 3 yêu cầu khác: (a) IT専門 — bỏ hẳn phần "Chủ đề", đổi cách chia Bộ từ "chia đều dồn số dư" sang **chia cố định đúng 25 từ/Bộ bắt đầu từ #1** (hàm `splitDecksStrict()`, verify 596 từ = 23 Bộ×25 + 1 Bộ 21 từ cuối, label/deckPool khớp nhau); (b) Flashcard — thêm border màu cho cả 4 nút (Chi tiết=viền xanh lá, Yêu thích=viền vàng, Đã nhớ=viền cam, Tiếp theo=viền xanh dương đậm hơn nền); (c) Thêm logo `04_Image/Logo_Tanpopo.png` làm app icon Android (dùng `@capacitor/assets` generate đủ mọi mật độ + adaptive icon + splash screen sáng/tối, verify icon đúng kích thước trong APK) và làm favicon (nhúng base64 64x64) cho bản HTML mở trực tiếp bằng trình duyệt. Đã build lại APK debug lần 3, verify package/permission/version không đổi, plugin TTS + icon mới đều có trong APK. **Vẫn cần PM test thật trên điện thoại để xác nhận native TTS phát được tiếng — đây là lần đầu dùng đường native, có khả năng cần cài thêm gói giọng tiếng Nhật trên máy nếu thiết bị chưa có (Cài đặt → Ngôn ngữ → Chuyển văn bản thành giọng nói → tải giọng Nhật) — nếu native TTS vẫn lỗi, toast lần này sẽ hướng dẫn đúng chỗ cần vào.** | NguyenNC (qua Claude) |
| 2026-07-18 | **PM xác nhận trên điện thoại thật: "Đã nghe được."** → plugin native TTS (`@capacitor-community/text-to-speech`) hoạt động đúng, fix gốc rễ thành công. FR_005 đóng, chuyển trạng thái **HOÀN THÀNH**. Đã cập nhật `PROJECT_日本語学習アプリ_Handover.md` (mục 4.3/4.4/4.7/5.5/5.6) để phản ánh đúng kiến trúc TTS native + chia Bộ cố định 25 từ + màu nút mới + app icon, tránh tài liệu bị lệch so với code thực tế. Commit toàn bộ thay đổi lên git. | NguyenNC (qua Claude) |

## 1. Loại thay đổi

- [x] Fix bug
- [x] Sửa/nâng cấp chức năng có sẵn (update)
- [x] Thay đổi UI/UX

## 2. Tên chức năng

1. Fix bug: icon loa (🔊) không phát ra tiếng trên Android
2. Redesign màn hình Flashcard (header hiện Bộ đang học, gộp 2 hàng nút thành 1)
3. Fix màn hình Luyện nghe (sai tên hiển thị + báo lỗi TTS sai)

## 3. Mô tả ngắn

Cả 3 vấn đề có **chung 1 nguyên nhân gốc**: đoạn code `if(!('speechSynthesis' in window))` dùng để "gác cổng" cho tính năng nghe, trong khi cơ chế TTS chính của app là Google Translate TTS (phát qua thẻ `<audio>`, KHÔNG cần `speechSynthesis`) — `speechSynthesis` (Web Speech API nội bộ trình duyệt) chỉ là phương án dự phòng khi offline. Trên Android, đặc biệt nếu app được đóng gói native (thấy `isNativeApp()`/Capacitor trong code), WebView hệ thống Android **thường KHÔNG hỗ trợ `speechSynthesis`** dù vẫn phát `<audio>` bình thường — dẫn đến việc gác cổng sai và fallback câm lặng.

## 4. Hành vi mong muốn (chi tiết) — đã triển khai

### 4.1. Bug: Icon loa không phát tiếng trên Android

- Đã thêm timeout 5s cho `playAudioUrl()` (hằng số `TTS_TIMEOUT_MS`) — quá thời gian mà chưa `onended`/`onerror` thì coi như lỗi, fallback ngay, không treo vô thời hạn (test bằng URL không route được: resolve 'error' đúng lúc ~timeout, không treo).
- Khi cả Google TTS lẫn device TTS (`speechSynthesis`) đều thất bại/không khả dụng → hiện toast "Không phát được âm thanh, kiểm tra kết nối mạng" (hàm `showToast()`) thay vì im lặng. Đã test bằng cách giả lập xoá `speechSynthesis` + ép `playAudioUrl` lỗi → toast hiện đúng.
- Mục cấu hình Android native (permission INTERNET, network_security_config.xml) nằm ngoài phạm vi `app_template.html`, cần kiểm tra riêng trong `03_Android_App/`.

### 4.2. Redesign màn hình Flashcard

- Header hiện tên Bộ khi học theo Bộ cụ thể: `"Bộ 2 (26-50) · 3 / 20"` (hàm `curDeckRangeLabel()`); học "Tất cả" giữ nguyên format cũ. Đã test: chọn Bộ 2 → header hiện đúng "Bộ 2 (26-50) · 1 / 25".
- Đã xoá dòng `<div class="counter">Chạm thẻ để xem nghĩa</div>` (dư thừa vì đã có nút "👁 Xem chi tiết").
- Đã bỏ hàng nút SRS (Quên/Khó/Được/Dễ), chỉ còn 1 hàng 4 nút (Xem chi tiết / Yêu thích / Đã nhớ / Từ tiếp theo). CSS `.card-actions` đổi thành `repeat(4,1fr)` 1 hàng.
- **Màu 4 nút phân biệt theo trạng thái** (bổ sung sau phản hồi test): "Xem chi tiết" trung tính; "Yêu thích" chuyển hồng (`.fav-btn.active`) khi đã đánh dấu; "Đã nhớ" chuyển xanh lá (`.master-btn.active`) khi đã đánh dấu; "Từ tiếp theo" luôn xanh dương đậm (`.next-btn`) vì là hành động chính. Đã test click từng nút, màu đổi đúng theo state.

### 4.3. Fix màn hình Luyện nghe

- `setHeader('Luyện nghe',...)` được gọi ngay đầu hàm `listenMode()`, trước mọi return.
- Đã bỏ hẳn guard `if(!('speechSynthesis' in window))...` (nguyên nhân gây báo sai tên màn hình + báo lỗi TTS oan). Đã test: xoá `speechSynthesis` rồi vào thẳng Luyện nghe → header hiện đúng "Luyện nghe", màn hình hoạt động bình thường (không còn bị chặn).

### 4.4. Banner "Quyền microphone bị từ chối" ở Luyện nói — kết luận

PM báo lỗi kèm ảnh chụp banner này ở màn Luyện nói. Rà code: `speakModeInit()` có `if(isNativeApp()){ speakMode(list); return; }` ngay đầu hàm — banner web-permission này **không thể xuất hiện khi chạy trong APK** (bị bỏ qua hoàn toàn). PM xác nhận ảnh chụp là mở bằng **Chrome** (không phải APK), và trên APK Luyện nói **hoạt động bình thường**. Kết luận: không phải bug — đây là hành vi chuẩn của trình duyệt khi mic bị từ chối (banner + nút "Bắt đầu luyện nói" để tiếp tục không chấm điểm vẫn đúng thiết kế). Không cần sửa gì thêm cho mục này.

### 4.5. Âm thanh phản hồi theo điểm phát âm (bổ sung mới)

- Thêm hàm `playScoreSound(score)` dùng Web Audio API (oscillator + gain envelope) — không cần file âm thanh ngoài, giữ nguyên tắc offline/self-contained.
- 3 mức: **<51** — 2 nốt trầm xuống (nhắc thử lại) · **51-89** — 1 nốt trung (khá tốt) · **≥90** — chuỗi 3 nốt lên (xuất sắc), theo đúng thang điểm PM yêu cầu (thay ngưỡng cũ 55/80 bằng 51/90 luôn, để khớp với text feedback hiển thị).
- Áp dụng đồng bộ ở cả 4 nơi chấm điểm phát âm bằng `similarity()`: Luyện nói (`speakMode`), Luyện đọc IT専門 (`readingMode`/`setupReadingMic`), Luyện đọc IT業務編 (`gyoumuReadingMode`/`setupMic`), Kaiwa (`setupPracticeMic`). Đã test qua mock ghi âm: điểm 30/70/95 → đúng cả text tier lẫn `playScoreSound()` được gọi đúng tham số.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — đã sửa `playAudioUrl()`/`deviceSpeak()`/`deviceSpeakAsync()`/`speak()`/`speakAsync()` (timeout + toast), thêm `showToast()`, thêm `curDeckRangeLabel()`, sửa `listenMode()` (setHeader đầu hàm + bỏ guard sai), sửa `flashMode()` (header Bộ, xoá text thừa, gộp nút, màu nút theo state, "Đã nhớ" gọi `reviewCard(id,2)`), thêm `playScoreSound()`/`beep()`/`getSfxCtx()`, cập nhật ngưỡng điểm phát âm 55/80 → 51/90 ở 4 nơi chấm điểm
- [ ] `build_app.py` — không ảnh hưởng
- [x] `03_Android_App/` — đã `npx cap sync android` + build lại APK debug (`gradlew assembleDebug`) với đầy đủ các fix trên, copy ra `03_Android_App/Kokoro_Nihongo.apk`. Cấu hình Android native (permission, network_security_config) đã kiểm tra sẵn có INTERNET/RECORD_AUDIO, không cần sửa.

## 6. Ràng buộc kỹ thuật

- Không đổi cơ chế lưu trữ `localStorage` (`jp_learn_v1`) — đã verify: toggle "Đã nhớ" ghi đúng `box`/`due`/`correct`/`seen`; bỏ đánh dấu không gọi lại `reviewCard`; "Từ tiếp theo" không đánh dấu thì không đụng SRS.
- Giữ nguyên hành vi Quiz/Listening mode (vẫn gọi `reviewCard()` bình thường) — không đổi.

## 7. Ưu tiên

- [x] Cao — đã xử lý

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro — kết quả xác nhận với PM (2026-07-18)

| # | Nội dung | Quyết định |
|---|---|---|
| 1 | Cách xử lý mất input SRS khi bỏ hàng Quên/Khó/Được/Dễ | **Chọn phương án đề xuất mặc định**: "Đã nhớ" gọi `reviewCard(id,2)` (như "Được") + set mastered; "Từ tiếp theo" khi chưa đánh dấu Đã nhớ thì KHÔNG gọi `reviewCard` (giữ nguyên box/due). |
| 2 | Môi trường test Android | **Cả 2** — vừa mở Chrome trực tiếp vừa test qua APK đóng gói (Capacitor, `03_Android_App/`). Fix JS trong `app_template.html` áp dụng cho cả 2 trường hợp; phần cấu hình Android native (nếu cần) để kiểm tra riêng. |
| 3 | Format "Bộ N (start-end)" ở header Flashcard | Đã code `curDeckRangeLabel()` tái sử dụng logic `splitDecks()`/`pool()` sẵn có, không cần đổi signature `flashMode()`. |
| 4 | Timeout Google TTS gây fallback nhầm khi mạng chậm | Chọn 5000ms (`TTS_TIMEOUT_MS`) làm mặc định, nằm giữa khoảng đề xuất 4-6s. |
