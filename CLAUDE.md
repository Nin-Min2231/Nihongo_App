# CLAUDE.md — Kokoro Nihongo Project

## Project Overview

App học tiếng Nhật offline, dùng cho PM/BrSE ngành IT làm việc với đối tác Nhật. Có 2 hình thức chạy: file HTML tự chứa (mở trực tiếp bằng trình duyệt) hoặc APK Android thật (đóng gói bằng Capacitor, có mic/TTS native).

```
日本語の辞書.xlsx  →  build_app.py  →  Kokoro_Nihongo.html  →  (Capacitor) →  Kokoro_Nihongo.apk
```

Đọc file này trước khi sửa code. Muốn hiểu sâu lịch sử quyết định/lý do kỹ thuật: đọc `PROJECT_日本語学習アプリ_Handover.md`. Muốn hướng dẫn build/chạy chi tiết từng bước: đọc `README.md`.

> **Gói Phase 2 (FR_008 → FR_012) + FR_006/FR_007 + redesign dashboard (bảng màu "giấy washi" + trang chủ hero) đã code xong và test qua trình duyệt.** Xem mục "Feature Requests" cuối file + mục UI bên dưới. FR_007 code theo **bản rút gọn** (không cắt audio theo lượt thoại — xem ghi chú đầu file `done/FR_007_reading_real_audio_segments.md`). Redesign dashboard: **PM đã duyệt áp dụng cho toàn app** (2026-09-12), gộp từ 1 worktree khác (`japanese-learning-app-handover-e2f2a1`) vào worktree này — 2 việc không đụng chạm cùng chỗ trong code nên gộp bằng `git apply` sạch, không conflict. **Đã build APK cho gói này (2026-09-12 tối)** — `03_Android_App/Kokoro_Nihongo.apk`, versionCode 1 / versionName "1.0" (chưa bump, theo mục 5.4 handover). Trong lúc build phát hiện `@capacitor/filesystem`/`@capacitor/share` (dùng cho xuất/nhập tiến độ FR_011) đã khai trong `package.json` nhưng **chưa từng `npm install` thật** — mọi bản APK trước đó build thiếu 2 plugin này. Đã `npm install` lại, `npx cap sync` xác nhận đủ 4 plugin, verify bytecode trong APK có cả 4 class plugin + đúng 663 từ + 38 track + quyền RECORD_AUDIO. **CHƯA cài/test trên điện thoại thật** — xem mục ⚠ ngay dưới đây trước khi cài.

## Cấu trúc thư mục

```
100_日本語/
├── 日本語の辞書.xlsx              ← Từ điển gốc (667 từ, chỉ đọc, KHÔNG dùng openpyxl.save())
├── CLAUDE.md                      ← File này
├── PROJECT_日本語学習アプリ_Handover.md  ← Tài liệu handover chi tiết (lịch sử, kiến trúc sâu)
├── README.md                      ← Hướng dẫn build/chạy từng bước
├── _KHAO_SAT/                     ← Khảo sát hiện trạng + kế hoạch gộp (2026-09-11), tài liệu tham khảo
├── 01_Build_App/
│   ├── Kokoro_Nihongo.html        ← App output (build từ template + vocab JSON, KHÔNG sửa tay)
│   ├── audio/                     ← (gitignore) copy từ 02_IT_Gyoumuhen/AudioCD, build_app.py tự sync
│   ├── _app_build/
│   │   ├── app_template.html      ← Template chính (CSS + JS, ~2000 dòng) — SỬA FILE NÀY để thêm tính năng
│   │   ├── build_app.py           ← Script build v2: đọc xlsx + transcript → inject JSON → output HTML
│   │   ├── _id_lock.json          ← ⚠ SỔ KHÓA ID — từ vựng → id cố định. KHÔNG xóa, KHÔNG sửa tay. Commit vào git.
│   │   └── _last_build_report.txt ← (gitignore) báo cáo chất lượng dữ liệu lần build gần nhất
│   └── _feature_requests/
│       ├── TEMPLATE.md            ← Copy file này ra để viết yêu cầu tính năng mới
│       └── done/                  ← FR đã hoàn thành (FR_002..FR_012 + _PHASE2_GOI_CAI_MOT_LAN.md) — lịch sử tham khảo
├── 02_IT_Gyoumuhen/                ← Nguồn dữ liệu module IT業務編 (hội thoại công việc IT)
│   ├── IT_Gyoumuhen.pdf                    ← Sách scan, chỉ tham khảo
│   ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx ← Transcript 38 track
│   └── AudioCD/                             ← 38 file mp3 — NGUỒN AUDIO DUY NHẤT của cả dự án
├── 03_Android_App/                 ← Project Capacitor — đóng gói HTML thành APK Android
│   ├── package.json, capacitor.config.json
│   ├── assets/icon.png            ← Nguồn app icon (copy từ 04_Image/Logo_Tanpopo.png)
│   ├── www/                        ← (gitignore) copy Kokoro_Nihongo.html + audio trước khi build
│   │   └── index.html             ← ⚠ Bản 596 từ mà APK hiện tại được build ra — nguồn seed của _id_lock.json
│   ├── android/                    ← Project Android native (Gradle), mở được bằng Android Studio
│   └── Kokoro_Nihongo.apk          ← (gitignore) APK build sẵn mới nhất
└── 04_Image/
    └── Logo_Tanpopo.png            ← Logo gốc 1024x1024, nguồn cho app icon + favicon
```

## Quy trình Build

```bash
cd 01_Build_App/_app_build
python3 build_app.py
```

Các cờ khác:

| Lệnh | Tác dụng |
|---|---|
| `python3 build_app.py` | Đọc từ điển, kiểm tra dữ liệu, build ra HTML |
| `python3 build_app.py --check` | Chỉ đọc và in báo cáo, **KHÔNG ghi file nào**. Chạy bao nhiêu lần cũng an toàn. |
| `python3 build_app.py --force` | Bỏ qua lỗi chặn (từ trùng, STT trùng), vẫn build |
| `python3 build_app.py --seed-lock <file.html>` | Tạo `_id_lock.json` từ một bản app đã build. Chỉ dùng 1 lần, đã chạy rồi. |

Build script (path tự suy từ vị trí file, chạy được ở bất kỳ máy nào):
1. Đọc `日本語の辞書.xlsx` + `02_IT_Gyoumuhen/IT_Gyoumuhen_AudioCD_Transcript.xlsx` (parse ZIP/XML trực tiếp, KHÔNG dùng openpyxl)
2. Tìm cột **theo tên tiêu đề** ở dòng 4, không hardcode B/C/D/E/F/G
3. In **báo cáo chất lượng dữ liệu**: ô thiếu, từ trùng, STT trùng/hụt, câu ví dụ không có ký tự tiếng Nhật
4. Gán `id` **theo sổ khóa `_id_lock.json`**, không theo STT (xem quy tắc #7)
5. Trích vocab → JSON array `[{id, w, r, vi, en, ex, c}, ...]` (c = category tự động: 外来語/漢字/その他), trích 38 track IT業務編 → JSON `GYOUMU_DATA`
6. Replace placeholder trong `app_template.html`: `/*__VOCAB__*/[]`, `/*__GYOUMU__*/[]`, `__GEN_DATE__`, `__COUNT__`
7. Tự copy audio từ `02_IT_Gyoumuhen/AudioCD/` → `01_Build_App/audio/`
8. Output → `Kokoro_Nihongo.html`

**Verify sau build (bắt buộc):**
```bash
# Check JS syntax (dùng file cục bộ, không dùng /tmp/ — trên Windows Git Bash /tmp/ không luôn ghi được)
python3 -c "import re; html=open('../Kokoro_Nihongo.html',encoding='utf-8').read(); m=re.search(r'<script>(.*?)</script>',html,re.DOTALL); open('_verify.js','w',encoding='utf-8').write(m.group(1))" && node --check _verify.js && rm _verify.js

# Check vocab count
python3 -c "
import json
html=open('../Kokoro_Nihongo.html',encoding='utf-8').read()
idx=html.find('/*__VOCAB__*/')
s=html.index('[',idx); d=0
for i in range(s,len(html)):
    if html[i]=='[': d+=1
    elif html[i]==']': d-=1
    if d==0: print('OK:',len(json.loads(html[s:i+1])),'words'); break
"
```

Muốn build APK Android (sau khi sửa xong + verify + test kỹ trong trình duyệt): xem quy trình đầy đủ ở `README.md` mục 4.3 hoặc `PROJECT_日本語学習アプリ_Handover.md` mục 5.2. **Đừng build APK ngay khi chưa test kỹ trong trình duyệt trước** — đây là thói quen làm việc người dùng đã yêu cầu rõ.

**⚠ Khi cài APK mới lên điện thoại: CÀI ĐÈ, tuyệt đối không gỡ app ra cài lại.** Người dùng đang có rất nhiều tiến độ học trong `localStorage` của WebView. Gỡ app là mất sạch. Nếu lúc cài báo `App not installed` thì dừng lại hỏi người dùng.

**Ngay sau khi cài APK gói Phase 2 xong: mở app → ⚙️ Cài đặt → 📤 Xuất tiến độ** (FR_011) và lưu chuỗi JSON lại — từ lúc đó tiến độ mới thực sự có bản sao lưu.

## Quy tắc QUAN TRỌNG

### 1. xlsx = ZIP — KHÔNG dùng openpyxl.save()
File `.xlsx` là archive ZIP chứa XML. `openpyxl.save()` rewrite styles → **MẤT màu, border, theme**.
Chỉ sửa raw string trên `xl/worksheets/sheet1.xml` và `xl/sharedStrings.xml`, giữ nguyên byte tất cả file khác.
Chi tiết code pattern: xem `PROJECT_日本語学習アプリ_Handover.md` mục 3.2.

Tầng đọc trong `build_app.py` v2 hỗ trợ **cả 3 kiểu ô** của chuẩn OOXML — `t="s"` (sharedStrings), `t="inlineStr"`, `t="str"`/số — kèm rich text và ô tự đóng. Đừng rút gọn lại thành 1 kiểu: từ điển đã từng đổi từ sharedStrings sang inlineStr và làm chết build suốt gần 2 tháng.

### 2. App template — single file, offline
- Toàn bộ CSS + JS trong 1 file HTML (`app_template.html`), không dùng framework
- Không fetch thư viện ngoài (kể cả icon/favicon đều nhúng base64)
- Vocab data nhúng dạng JSON (`/*__VOCAB__*/[]`), gyoumu data (`/*__GYOUMU__*/[]`)
- SRS data lưu `localStorage` key `jp_learn_v1`; IT業務編 progress lưu key riêng `kokoro_gyoumu_v1`
- TTS settings lưu `localStorage` key `kokoro_tts_settings`
- Cỡ chữ + thời gian phản xạ lưu `localStorage` key riêng `kokoro_ui_settings` (`{fontScale, reflexSec}`, xem `loadUI()`/`saveUI()` — FR_011)
- Viết code mới bằng **ES5** (`var`, `function`) cho đồng nhất với ~2000 dòng đang có

### 3. Sửa app = sửa `app_template.html`, KHÔNG sửa `Kokoro_Nihongo.html`
`Kokoro_Nihongo.html` luôn bị `build_app.py` ghi đè mỗi lần build. Muốn thêm/sửa tính năng: sửa `app_template.html` rồi `python3 build_app.py` lại.

### 4. TTS trên Android APK dùng plugin native, KHÔNG dùng Google TTS
Android WebView (nơi Capacitor chạy) **không hề implement Web Speech API**, và endpoint Google Translate TTS (không chính thức) **cũng không đáng tin cậy** khi gọi từ WebView đóng gói (đã xác nhận lỗi thật trên máy — xem `PROJECT_...Handover.md` mục 4.7). App dùng `isNativeApp()` để phát hiện môi trường: native → gọi thẳng plugin `@capacitor-community/text-to-speech` (engine TextToSpeech hệ thống, không qua mạng); web/Chrome → vẫn dùng Google TTS + `speechSynthesis` fallback như cũ. **Đừng quay lại dùng Google TTS làm đường chính cho native** — đã thử và không hoạt động.

### 5. Mic cũng dùng plugin native tương tự
`@capgo/capacitor-speech-recognition` cho native (Android WebView không có Web Speech Recognition API), fallback `SpeechRecognition`/`webkitSpeechRecognition` cho web. Xem `isNativeApp()`/`nativeSR()`/`nativeTTS()` trong `app_template.html`.

### 6. Xuất tiến độ trên native dùng `@capacitor/filesystem` + `@capacitor/share`, KHÔNG dùng `<a download>`
`<a download>`/`Blob` không hoạt động trong WebView đóng gói (giống lý do TTS/mic ở quy tắc #4/#5). Native: `Filesystem.writeFile()` ghi ra `Directory.Cache` (không cần xin quyền lưu trữ) rồi `Share.share()` mở hộp thoại Chia sẻ hệ thống để người dùng chọn nơi lưu. Web vẫn dùng `Blob`+`<a download>` như cũ. Xem `nativeFilesystem()`/`nativeShare()` trong `app_template.html` và FR_011 mục 0/4.1 (đổi 2026-09-12 sau khi PM test bản đầu thấy copy/dán thủ công tốn công — bản đầu KHÔNG dùng 2 plugin này, chỉ textarea+clipboard). Nhập tiến độ dùng `<input type="file">` cho cả web lẫn native (Capacitor Android hỗ trợ sẵn, không cần plugin riêng); textarea dán tay vẫn giữ làm đường lùi cho cả xuất lẫn nhập.

### 7. `_id_lock.json` — KHÔNG xóa, KHÔNG sửa tay
Tiến độ học trong `localStorage` khóa theo `id` (`store.cards[id]`, `store.favorites[id]`).

Bản build cũ lấy `id` = STT cột B. Xóa hoặc chèn một dòng giữa file Excel là mọi `id` phía sau dịch theo, và tiến độ của từ A lặng lẽ gắn sang từ B, không báo gì. **Đã xảy ra thật**: so bản APK 2026-07-18 (596 từ) với từ điển 2026-09-11 (667 từ), có **47 trong 596 id trỏ sang từ khác** do 3 dòng bị xóa ở giữa.

`build_app.py` v2 giữ sổ khóa `_id_lock.json` ánh xạ **từ vựng → id cố định**:
- Từ đã có trong sổ → giữ nguyên id đó vĩnh viễn, dù chuyển lên xuống bao nhiêu dòng
- Từ mới → cấp id kế tiếp chưa ai dùng (`next_id`)
- Id của từ đã xóa khỏi Excel → **không bao giờ cấp lại** cho từ khác
- Từ chỉ bị sửa phần chú thích trong ngoặc (ví dụ `（が）見当たらない` → `見当たらない`) được nhận ra là cùng một từ và giữ nguyên id

Hệ quả: **số `#id` hiển thị trên thẻ không còn khớp STT trong Excel** — đây là đánh đổi có chủ ý, giữ tiến độ quan trọng hơn giữ con số hiển thị.

Xóa `_id_lock.json` = mất ánh xạ = build lại sẽ đánh số từ đầu = tiến độ trong app gắn sai hết. File này **phải commit vào git**.

### 8. Lưới chọn Bộ giữ đúng 4 icon
`deckGridHTML()` tô thẻ Bộ thành xanh lá khi **tất cả** icon truyền vào đều đã xong. Hiện có 4 icon 🗂️✍️🎧🎤 ứng với 4 mode `flash`/`quiz`/`listen`/`speak`.

Thêm icon thứ 5 cho mode mới sẽ làm **mọi Bộ người dùng đã hoàn thành lập tức mất màu xanh**, nhìn như mất tiến độ. Mode mới vẫn được ghi cờ vào `deckDone` để dành sau này, nhưng **không hiển thị icon và không tính vào điều kiện Bộ đã xong**. Điều kiện "hoàn thành 1 Bộ" của FR_006 cũng giữ nguyên đúng 4 mode cũ.

`cloze` (FR_009) và `reflex` (FR_010) tuân theo đúng quy tắc này: cả 2 đều gọi `markDeckDone()` nhưng `homeDashboard()` chỉ truyền đúng 4 icon cũ vào `deckGridHTML()` — không thêm icon thứ 5/6.

## Kiến trúc App (app_template.html)

### Navigation flow
```
home() → [chọn 1 trong 2 module] → dashboard riêng của module → mode học → back → home
```

IT専門 (`homeDashboard()`) tự động chọn sẵn **Bộ nhỏ nhất chưa hoàn thành đủ 4 mode** mỗi lần vào (FR_006, `autoFocusDeckIndex()`) — xem quy tắc #8 cho định nghĩa "hoàn thành". Chọn thủ công 1 Bộ khác trong phiên vẫn được, nhưng bị tính lại từ đầu khi rời màn hình rồi vào lại.

IT業務編 (`gyoumuDashboard()`) vào thẳng **`gyoumuUnitScreen(chapter,unit)`** — 1 màn hình gộp (FR_007, bản rút gọn) thay cho luồng List→Detail cũ: phần trên "🎧 Luyện nghe" là accordion (mở đúng 1 track tại 1 thời điểm), phần dưới "🎤 Luyện đọc câu" là tab chọn track có transcript, luyện đọc từng câu (TTS mẫu + nút nghe nguyên track thật `gyoumuTrackAudioSrc()` + mic chấm điểm). 2 phần render/bind độc lập (`renderListen()`/`renderRead()`, không dùng chung 1 hàm render) để không làm gián đoạn audio đang phát của phần kia.

### 2 Module (Menu chính — registry `MENU_MODULES`, thêm module mới chỉ cần thêm 1 phần tử)
| Module | Trạng thái | Dashboard |
|---|---|---|
| IT専門 (từ vựng IT, 667 từ) | ✅ Active | `homeDashboard()` |
| IT業務編 (hội thoại công việc IT, 38 track) | ✅ Active | `gyoumuDashboard()` |

> **FR_008 đã gỡ bỏ** module Luyện đọc (`readingLibrary()`) và Kaiwa (`kaiwaLibrary()`) — không dùng nữa, PM xác nhận trùng mục đích với Luyện nói / nội dung ghép giả. Dữ liệu `deckDone._reading` / `deckDone._kaiwa` cũ vẫn còn trong `localStorage` của user cũ nhưng không dùng tới nữa.

Main menu (`home()`) có 1 khối thống kê tổng hợp đầu trang: Streak / Từ đã thuộc (IT専門) / Track đã nghe (IT業務編) — **bấm được** (mũi tên `›`), mở màn hình `statsScreen()` (FR_012, xem mục riêng bên dưới).

### 7 Mode học của IT専門
- **Flashcard + SRS**: Leitner system (box 0-6, intervals [0,1,2,4,7,15,30]). 4 nút: Chi tiết/Yêu thích/Đã nhớ/Tiếp theo — bấm "Đã nhớ" tính 1 lượt SRS mức "Được" (`reviewCard(id,2)`), không còn hàng nút Quên/Khó/Được/Dễ riêng.
- **Quiz**: Trắc nghiệm JP↔VI
- **🧩 Điền từ** (`cloze`, FR_009): che 1 đoạn trong câu ví dụ bằng `＿＿＿`, chọn lại từ đúng trong 4 phương án. Thuật toán dò ô trống `findCloze()`/`clozeCandidates()` (đặt cạnh `allWithEx()`) phủ được 629/667 từ (94,3%) — **không sửa lại logic** nếu không đo lại tỉ lệ phủ. Có nút Gợi ý 3 bậc (nghĩa → ký tự đầu → cách đọc), không thu lại được.
- **Luyện nghe**: Nghe TTS → chọn nghĩa
- **Luyện nói**: Đọc theo → nhận diện giọng → chấm điểm (LCS ratio, ngưỡng ≥90 xuất sắc/≥51 khá/<51 luyện lại) + âm thanh phản hồi (`playScoreSound()`)
- **⚡ Phản xạ Ns** (`reflex`, FR_010): hiện nghĩa tiếng Việt, vòng đếm ngược SVG (mặc định 3s, chỉnh được 3/5/8s trong Cài đặt qua `uiSettings.reflexSec`), người học tự chấm "Bật ra được / Chưa bật ra được". **Không dùng mic** (cố ý — nhận giọng mất 1-2s khởi động, phá hỏng phép đo phản xạ). `setInterval` phải `clearInterval` ở mọi lối thoát — mỗi nhịp tự kiểm tra phần tử SVG còn trong DOM không.
- **⭐ Yêu thích**: xem lại từ đã đánh dấu yêu thích

IT専門 chia thành các **Bộ cố định đúng 25 từ, bắt đầu từ #1** (667 từ = 26 Bộ×25 + 1 Bộ 17 từ cuối, hàm `splitDecksStrict()`), không còn lọc theo "Chủ đề" (漢字/外来語/その他).

**Header + tag hiển thị đồng bộ ở cả 6 mode (2026-09-12)**: mọi mode (Flashcard/Quiz/Cloze/Luyện nghe/Luyện nói/Phản xạ) đều hiện `curDeckRangeLabel()` ("Bộ N (start-end)") ở đầu subtitle header khi đang học theo 1 Bộ cụ thể (rỗng nếu học "Tất cả", không đổi hành vi cũ), và mọi từ đều có `<span class="tag">v.c · #v.id</span>` hiện category + STT từ điển ngay trên thẻ/câu hỏi — Flashcard/Favorites đã có sẵn từ trước, giờ thêm cho Quiz/Cloze/Luyện nghe/Luyện nói/Phản xạ (riêng Phản xạ chỉ hiện tag ở pha 2 - pha hiện đáp án, không hiện ở pha 1 để không lộ gợi ý trước khi đoán).

### SRS — điểm cần biết
`reviewCard(id, quality)` nhận 4 mức (0 lùi 1 box, 1 giữ nguyên, 2 lên 1 box, 3 lên 2 box), **nhưng UI chỉ phơi ra mức 2**. Mức 1 và 3 hiện không có đường nào gọi tới — code chết. Hệ quả: mọi từ lên bậc với cùng một tốc độ, không phân biệt dễ khó. Đây là điểm làm giảm hiệu quả của giãn cách, cân nhắc mở FR riêng để thêm lại nút "Khó".

`bumpStudied()` (tăng `stats.studied` + gọi `bumpStreak()`) chỉ được gọi từ `reviewCard()`. Học IT業務編 (nghe track lần đầu / hoàn thành 1 lượt luyện đọc theo thoại) gọi thẳng `bumpStreak()` (streak + `stats.history`, **không** cộng vào `studied` — xem FR_012) — đã fix bug streak không tính khi học IT業務編.

### Màn hình Thống kê (`statsScreen()`, FR_012)
- **Chuỗi ngày**: `store.stats.streak` + tổng số ngày có học (`Object.keys(store.stats.history).length`)
- **Lịch nhiệt 12 tuần**: lưới 7×13 (CSS grid, không thư viện), Thứ Hai ở hàng trên cùng, 4 mức xanh theo `store.stats.history[YYYY-MM-DD]`. **Không dựng lại lịch sử quá khứ** — chỉ bắt đầu ghi từ ngày cập nhật app (migrate `if(!store.stats.history) store.stats.history={}`).
- **Phân bố trạng thái**: Đã thuộc / Đang học / Từ khó (`seen>=5 && correct/seen<0.5`) / Chưa học — mỗi từ chỉ tính đúng 1 nhóm (thứ tự ưu tiên: Đã thuộc > Từ khó > Đang học > Chưa học), tổng luôn = `VOCAB.length`.
- **Dự báo tải ôn 7 ngày**: đếm `store.cards[*].due` rơi vào từng ngày, thẻ quá hạn gộp vào cột "Hôm nay".
- Không thư viện biểu đồ — heatmap bằng CSS grid, cột bằng div chiều cao tính %.

### TTS System
- **Native (Android APK)**: `@capacitor-community/text-to-speech` — engine TextToSpeech hệ thống, không qua mạng (xem quy tắc #4).
- **Web/browser**: Google Translate TTS (thử 2 endpoint `client=gtx`/`client=tw-ob`) → fallback `speechSynthesis` khi lỗi.
- Cả 2 nhánh: nếu thất bại hoàn toàn → toast báo lỗi (không im lặng).
- Settings: speed (0.5-1.5), pitch (0.5-2.0), gender (male/female), voice picker.

### UI
- **Color scheme: tông "giấy washi" ấm** (đổi 2026-09-12, PM đã duyệt áp dụng cho **toàn app**, thay hẳn tông xanh dương Bootstrap cũ) — `--brand:#1F5673`, `--brand2:#2E7194`, `--bg:#F5F6F1`, `--warn:#9C6B12`, `--bad:#B7412C`, `--good`/`--accent:#4B7A4E`, `--soft:#E7EEF0`, header gradient `#153F55→#1F5673`. Toàn app dùng chung 1 bộ biến `:root` này (không tách riêng theo màn hình) — đổi 1 chỗ là mọi màn hình (Quiz, mic, header, Bộ đang chọn...) đổi theo. Font vẫn hệ thống (không tải Google Fonts) — chỉ lấy bảng màu/bố cục từ demo khảo sát, không lấy font.
  - **4 chỗ dùng màu cứng (hex) bị bản redesign gốc bỏ sót đã fix thêm (2026-09-12)** — không theo biến `:root` nên không tự đổi theo: `.backbtn` (nút "← 戻る"), `.settings-btn` (nút "⚙️ Cài đặt") — 2 nút này xuất hiện ở **mọi màn hình**; `.mic-banner` (banner xin quyền mic); `.tts-ok` + `.topic-card.active .tc-badge` (chấm trạng thái TTS + badge "✅ Sẵn sàng"). Cả 4 đều đổi sang cặp `var(--soft)`/`var(--brand)`, `var(--warn)`, hoặc `var(--good)` tương ứng — không tự bịa hex mới, tái dùng đúng token đã có trong `:root`.
- Bộ đang chọn: nền `var(--soft)` để phân biệt với Bộ chưa chọn (trước là `#dbeafe` xanh dương nhạt, nay đổi theo bảng màu mới)
- Flashcard 4 nút: Chi tiết (xanh lá) / Yêu thích (vàng) / Đã nhớ (cam) / Tiếp theo, đều có border màu đậm hơn nền — 4 màu này **không** nằm trong phạm vi redesign, giữ nguyên như cũ
- **Trang chủ (`home()`) viết lại thành "hero card"** (thay khối `.stats`/`.stats-block` phẳng cũ): số thẻ IT専門 đến hạn ôn hôm nay (`dueCount(VOCAB)`) hiện to, tô đỏ nếu >0 + nút CTA "Bắt đầu ôn tập ngay →" (vào thẳng `flashMode(VOCAB)` ưu tiên thẻ đến hạn); due=0 thì hiện 🎉 + nút "Luyện thêm từ vựng" (mở `homeDashboard()`). Bên dưới là lưới 3 ô Streak/Từ đã thuộc/Track đã nghe + link "Xem thống kê chi tiết ›", cả 2 đều mở `statsScreen()` (FR_012, không đổi hành vi, chỉ đổi giao diện).
- Mobile-first, max-width 560px
- App icon + favicon: dùng `04_Image/Logo_Tanpopo.png` (xem `03_Android_App/assets/icon.png` + `npx capacitor-assets generate`)

## Feature Requests

Xem folder `01_Build_App/_feature_requests/`. Format: `FR_<số>_<tên>.md` theo `TEMPLATE.md`. FR đã hoàn thành nằm trong `done/`. **Hiện không có FR nào pending.**

### Gói Phase 2 + FR_006/007 — đã code + test qua trình duyệt xong, CHƯA build APK

Đọc `done/_PHASE2_GOI_CAI_MOT_LAN.md` để biết thứ tự triển khai và các ràng buộc xuyên suốt đã áp dụng.

| FR | Nội dung | Trạng thái |
|---|---|---|
| FR_006 | IT専門: tự động focus vào Bộ nhỏ nhất chưa hoàn thành | ✅ Xong — test qua Browser pane |
| FR_007 | IT業務編: màn hình Unit gộp Luyện nghe + Luyện đọc câu | ✅ Xong — **bản rút gọn**, đọc câu dùng nguyên audio track thật thay vì đoạn cắt sẵn (dữ liệu cắt không có trong repo, xem ghi chú đầu `done/FR_007_reading_real_audio_segments.md`) |
| FR_008 | Bỏ module Kaiwa và Luyện đọc câu | ✅ Xong — menu chính còn đúng 2 thẻ |
| FR_011 | Xuất / Nhập tiến độ, cỡ chữ, thời gian phản xạ | ✅ Xong — đã test round-trip xuất/nhập |
| FR_009 | Chế độ mới: Điền từ vào câu (穴埋め) | ✅ Xong — phủ 629/667 từ (94,3%) |
| FR_010 | Chế độ mới: Phản xạ 3 giây (瞬間作文) | ✅ Xong |
| FR_012 | Màn hình Thống kê + fix lỗi streak | ✅ Xong |

**Trước khi build APK**: chạy đủ 6 bước nghiệm thu ở `done/_PHASE2_GOI_CAI_MOT_LAN.md` mục "Nghiệm thu trước khi build APK" (đã chạy qua trình duyệt desktop trong phiên code; còn cần tự kiểm tra lại trên thiết bị/khổ máy thật trước khi build) — cộng thêm tự test tay 3 việc mới: IT専門 auto-focus Bộ (FR_006), màn hình Unit IT業務編 (FR_007), và bảng màu mới hiển thị đúng trên khổ máy thật (mic banner, toast, Quiz đúng/sai — những chỗ có màu cứng hex không đổi theo biến, xem mục UI).

## Ngôn ngữ & Convention

- Comment code: tiếng Anh hoặc tiếng Việt
- UI text: tiếng Việt (cho user) + tiếng Nhật (cho nội dung học)
- Tài liệu: tiếng Việt, thuật ngữ Nhật/Anh giữ nguyên
- Biến/hàm JS: camelCase, tiếng Anh
