# PROJECT — Kokoro Nihongo (ココロ日本語) · Tài liệu handover

> **Mục đích tài liệu:** Ghi lại toàn bộ bản chất vấn đề & quy trình — từ **từ điển Excel** → **build app HTML** → **đóng gói APK Android** → **push GitHub**. Đọc file này là 1 chat Claude mới hiểu ngay context, không cần giải thích lại.
> **Đối tượng đọc:** Claude (chat mới) hoặc chính người dùng.
> **Người dùng:** NguyenNC — PM/BrSE ngành IT (cầu nối VN ⇄ Nhật).
> **Cập nhật lần cuối:** 2026-07-18 — sau khi hoàn thành FR_005 (fix TTS Android bằng plugin native, redesign Flashcard/IT専門/main menu, thêm app icon), đã test thật trên điện thoại và **xác nhận nghe được**.

---

## 1. Tổng quan mục tiêu (Big picture)

```
日本語の辞書.xlsx  (từ điển gốc, 596 từ)
        │  build_app.py
        ▼
Kokoro_Nihongo.html  ← app học, mở trực tiếp bằng trình duyệt (máy tính/điện thoại), KHÔNG cần cài đặt
        │  npx cap sync + gradlew (project Capacitor ở 03_Android_App/)
        ▼
Kokoro_Nihongo.apk  ← app Android thật, cài trực tiếp lên điện thoại — mic chấm điểm phát âm hoạt động thật
```

**Môi trường làm việc hiện tại:** Windows, chạy trực tiếp qua Bash/PowerShell (KHÔNG phải Cowork sandbox kiểu `/sessions/<tên>/mnt/` như tài liệu handover bản cũ từng mô tả — nếu thấy nhắc tới path đó, đó là thông tin CŨ, bỏ qua). Path project cố định: `D:\01_NguyenNC\10_Claude\100_日本語\`.

**Repo GitHub:** https://github.com/Nin-Min2231/Lading_page-VS (đã push, nhánh `main`, commit gốc `70e1fab`). ⚠️ Tên repo không khớp tên dự án (đặt từ trước cho việc khác) — người dùng đã xác nhận dùng tạm repo này, không phải nhầm lẫn.

---

## 2. Cấu trúc thư mục

```
100_日本語/
├── 日本語の辞書.xlsx                      ← Từ điển gốc (596 từ) — KHÔNG dùng openpyxl.save()
├── CLAUDE.md                               ← Quy tắc/kiến trúc dự án
├── PROJECT_日本語学習アプリ_Handover.md    ← File này
├── README.md                               ← Hướng dẫn build/chạy/push GitHub (tiếng Việt, ngắn gọn hơn file này)
├── .gitignore                              ← Loại trừ node_modules/, audio trùng lặp, APK, build artifacts
│
├── 01_Build_App/                           ← App IT専門 (từ vựng) — build từ xlsx
│   ├── Kokoro_Nihongo.html                 ← App đã build (commit vào git, mở trực tiếp được)
│   ├── audio/                              ← (gitignore) copy từ 02_IT_Gyoumuhen/AudioCD, build_app.py tự sync
│   ├── _app_build/
│   │   ├── build_app.py                    ← Script build: xlsx + transcript → JSON → inject template + copy audio
│   │   └── app_template.html                ← TOÀN BỘ CSS+JS của app (~1800+ dòng, sửa file này để thêm tính năng)
│   └── _feature_requests/                  ← FR_001 (mẫu) .. FR_005 (đã xong) — lịch sử yêu cầu tính năng
│
├── 02_IT_Gyoumuhen/                         ← Nguồn dữ liệu module IT業務編 (hội thoại công việc IT)
│   ├── IT_Gyoumuhen.pdf                     ← Sách gốc scan, chỉ tham khảo
│   ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx ← Transcript 38 track (Track|Chương|Unit|...|Nội dung hội thoại|Ghi chú)
│   └── AudioCD/                              ← 38 file mp3 — NGUỒN AUDIO DUY NHẤT của cả dự án
│
├── 04_Image/                                 ← Logo/asset nguồn (không phải code)
│   └── Logo_Tanpopo.png                      ← Logo gốc 1024x1024, dùng làm app icon + favicon
│
└── 03_Android_App/                          ← Project Capacitor — đóng gói HTML thành APK Android
    ├── package.json, capacitor.config.json  ← appId com.kokoronihongo.app, appName "Kokoro Nihongo"
    ├── assets/icon.png                       ← Copy của Logo_Tanpopo.png, nguồn cho `npx capacitor-assets generate`
    ├── www/                                  ← (gitignore) copy Kokoro_Nihongo.html + audio, sync thủ công trước khi build
    ├── android/                              ← Project Android native (Gradle) — mở bằng Android Studio được
    └── Kokoro_Nihongo.apk                     ← (gitignore) APK build sẵn mới nhất, ~76MB
```

**Toolchain Android cài NGOÀI project** (không nằm trong repo, đã cài sẵn trên máy này):
- JDK 21 (Temurin, portable): `D:\Android\jdk21`
- Android SDK (cmdline-tools + platform-tools + platform android-36 + build-tools 36.1.0): `D:\Android\Sdk`
- Gradle cache riêng (tránh phình ổ C:): `D:\Android\gradle-home`

---

## 3. GIAI ĐOẠN ① — Từ điển xlsx (không đổi so với bản cũ)

### 3.1. Cấu trúc `日本語の辞書.xlsx`
Sheet `日本語の辞書`. Row 2 = title/tác giả/ngày. Row 4 = header cột. Row 5+ = dữ liệu.

| Cột | Nội dung |
|---|---|
| B | STT (số) |
| C | Từ vựng (tiếng Nhật) |
| D | 読み方 (cách đọc) |
| E | Nghĩa tiếng Việt |
| F | Tiếng Anh |
| G | Câu ví dụ (N3+) |

### 3.2. QUY TẮC BẤT DI BẤT DỊCH: xlsx = ZIP

`.xlsx` là 1 ZIP chứa XML. `openpyxl.save()` sẽ **rewrite styles.xml/theme1.xml → MẤT màu/border/theme**. Chỉ được sửa raw string trên `xl/worksheets/sheet1.xml` + `xl/sharedStrings.xml`, giữ nguyên byte mọi file khác. Code mẫu đầy đủ: xem lịch sử — pattern đã dùng nhiều lần trong session, tóm tắt:

```python
import zipfile, shutil, re, html
# đọc all_files = {name: bytes} từ ZIP
# lấy s=/t= attribute của row cuối cùng để copy đúng style (không hardcode)
# thêm <si> mới vào sharedStrings trước </sst>, cập nhật count/uniqueCount
# thêm <row> mới vào sheet1 trước </sheetData>
# ghi lại: chỉ writestr() 2 file đã sửa, các file khác giữ nguyên bytes gốc
```

Hiện tại: **596 từ** (STT 1–596, gồm cả セキュリティ/脆弱性 thêm gần đây).

### 3.3. Quy tắc dịch từ mới
Dùng skill `translator-ja-vi-en`. Ưu tiên Hán-Việt, katakana → cột EN ghi từ gốc (セキュリティ→Security), câu ví dụ N3+ thuần Nhật. Chỉ thêm từ **chưa có** (check trùng qua sharedStrings).

---

## 4. GIAI ĐOẠN ② — Build app HTML (`build_app.py` + `app_template.html`)

### 4.1. Kiến trúc chung
1 file HTML tự chứa, JS thuần (không framework), CSS+JS đều trong `app_template.html`. `build_app.py` đọc xlsx + transcript, inject JSON vào 4 placeholder:
- `/*__VOCAB__*/[]` → mảng từ vựng `{id,w,r,vi,en,ex,c}` (c = category tự động: 外来語/漢字/その他)
- `/*__GYOUMU__*/[]` → mảng 38 track IT業務編 `{track,chapter,unit,unitJp,unitVi,type,chars,hasTranscript,lines:[{spk,t}],note}`
- `__GEN_DATE__`, `__COUNT__`

`build_app.py` cũng tự **copy audio** từ `02_IT_Gyoumuhen/AudioCD/` sang `01_Build_App/audio/` (chỉ copy file mới/khác size, không copy lại toàn bộ mỗi lần).

Lệnh build: `cd 01_Build_App/_app_build && python3 build_app.py` — path tự suy từ vị trí file, chạy được ở bất kỳ máy nào.

### 4.2. Kiến trúc điều hướng (menu chính — QUAN TRỌNG, mới đổi gần đây)

`home()` giờ render từ **1 registry `MENU_MODULES`** (không hard-code từng card nữa — đây là điểm mở rộng chính cho tương lai, thêm chủ đề mới chỉ cần thêm 1 phần tử vào mảng):

```js
const MENU_MODULES = [
  {id:'it_senmon', icon:'💻', title:'IT専門', ..., open:homeDashboard},
  {id:'it_gyoumu', icon:'🏢', title:'IT業務編', ..., open:gyoumuDashboard},
  {id:'reading_lib', icon:'📖', title:'Luyện đọc', ..., open:readingLibrary},
  {id:'kaiwa_lib', icon:'💬', title:'Kaiwa', ..., open:kaiwaLibrary},
];
```

Đã bỏ 3 card placeholder cũ (日常生活/N2/面接). Luyện đọc + Kaiwa **không còn nằm trong lưới "Chế độ học" của IT専門** — giờ là mục riêng ở menu chính, mỗi mục có màn chọn "bộ" riêng (`readingLibrary()`/`kaiwaLibrary()`, nguồn `splitDecks(allWithEx())` — toàn bộ từ có câu ví dụ, không lọc category).

**Đã thêm ở FR_005:** `home()` giờ hiện 1 khối thống kê tổng hợp toàn hệ thống ngay trên đầu (tái dùng CSS `.stats`/`.stat` sẵn có) trước khi tới danh sách chủ đề: **Streak** (`store.stats.streak`), **Từ đã thuộc** (`learnedCount()` của IT専門), **Track đã nghe** (`Object.keys(gyStore.listened).length` của IT業務編) — mục đích thay cho khối thống kê đã bỏ khỏi riêng từng module con (mục 4.3).

Luồng đầy đủ:
```
home() → IT専門 → homeDashboard() → [Flashcard/Quiz/Nghe/Nói/⭐Yêu thích] → mode screen
home() → IT業務編 → gyoumuDashboard() → gyoumuTrackList() → gyoumuTrackDetail() → gyoumuReadingMode()
home() → Luyện đọc → readingLibrary() → readingMode(deckList, deckIdx)
home() → Kaiwa → kaiwaLibrary() → kaiwaMode(deckList, deckIdx)
```

### 4.3. Hệ thống "Bộ học" (deck) — quan trọng, ảnh hưởng nhiều logic

**Đã đổi ở FR_005 (2026-07-18):** IT専門 **không còn chip lọc "Chủ đề"** (漢字/外来語/その他 đã bỏ khỏi UI — biến `curCat` vẫn còn trong code nhưng luôn cố định `'ALL'`, chỉ dùng làm namespace key cho `deckDone`, không có UI đổi nữa). Toàn bộ 596 từ được chia **CỐ ĐỊNH đúng 25 từ/bộ, bắt đầu từ #1** bằng hàm riêng `splitDecksStrict(arr, target)` (bộ cuối = phần dư, KHÔNG san đều số dư như trước) → 596 từ = 23 bộ×25 + 1 bộ 21 từ cuối. Hàm `splitDecks()` cũ (san đều số dư) **vẫn giữ nguyên, chỉ dùng cho Luyện đọc/Kaiwa** (`allWithEx()`) — 2 hàm này KHÔNG dùng chung, đừng nhầm lẫn khi sửa.

UI: lưới 4 thẻ/trang (`deckGridHTML()` — component dùng chung cho IT専門/Luyện đọc/Kaiwa), phân trang bằng `‹`/`›`. Bộ đang chọn (`.deck-card.on`) đổi nền **xanh dương nhạt** (`#dbeafe`) để phân biệt rõ với bộ chưa chọn (xanh dương đậm mặc định).

- `curDeck` (global, 'ALL' hoặc index string) — khi chọn 1 bộ cụ thể, 4 mode Flashcard/Quiz/Nghe/Nói dùng **TRỌN VẸN** danh sách bộ đó (không random-sample như khi chọn "Tất cả") → hoàn thành 1 phiên = hoàn thành cả bộ.
- **Hoàn thành bộ** lưu ở `store.deckDone[category][deckIndex][mode] = true`, đánh dấu tập trung trong `finish()` (điểm chung của cả 4 mode). Thẻ bộ hiện icon nhỏ (🗂️✍️🎧🎤) cho mode đã hoàn thành, và **chuyển màu xanh lá** khi đủ cả 4 mode (màu selected `.on` ưu tiên hiển thị trước màu `.done` nếu cả 2 cùng áp dụng).
- Reading/Kaiwa dùng namespace riêng `store.deckDone['_reading']`/`['_kaiwa']` (chỉ 1 "mode" mỗi cái), không đụng tracking của IT専門.
- IT専門 dashboard (`homeDashboard()`) đã bỏ khối thống kê (Tổng từ/Đã thuộc/Streak + progress bar) — số liệu tổng hợp này giờ chuyển sang hiện ở **main menu** (`home()`, mục 4.2), không lặp lại ở từng module con nữa.

### 4.4. Yêu thích & Đã nhớ (mới, trên màn Flashcard)

`store.favorites = {id:true}`, `store.cards[id].mastered = true/false` — **CỜ RIÊNG, không dùng chung với `box` SRS tự nhiên** (tránh từ tự nhiên đạt box cao qua chấm điểm bị loại ngoài ý muốn). Helper: `toggleFavorite/isFavorite/toggleMastered/isMastered`.

- Màn Flashcard có 4 nút, mỗi nút 1 màu cố định để dễ phân biệt (đổi ở FR_005, thay cho việc gộp cùng 1 màu xám trước đó): **Chi tiết/Ẩn** (`.detail-btn`, nền xanh lá nhạt — toggle 2 chiều, đồng bộ với chạm thẻ), **Yêu thích** (`.fav-btn`, nền vàng nhạt), **Đã nhớ** (`.master-btn`, nền cam nhạt), **Tiếp theo →** (`.next-btn`, nền xanh dương đậm — nút hành động chính). Cả 4 nút đều có border màu đậm hơn nền tương ứng. Text rút gọn ("Chi tiết"/"Tiếp theo", không phải "Xem chi tiết"/"Từ tiếp theo") để không xuống dòng ở màn hình hẹp.
- **Hàng nút chấm điểm SRS cũ (また Quên/難しい Khó/できた Được/簡単 Dễ, gọi `reviewCard(id, quality 0-3)`) đã BỎ HẲN ở FR_005** — lý do: 2 hàng nút chồng nhau gây rối UI. Thay vào đó: bấm **"Đã nhớ"** (chuyển từ chưa-đánh-dấu → đã-đánh-dấu) đồng thời gọi `reviewCard(id, 2)` (tương đương mức "Được" cũ) — chỉ tính 1 lần lúc chuyển trạng thái, bỏ đánh dấu lại KHÔNG gọi lại. Bấm **"Tiếp theo"** mà chưa đánh dấu "Đã nhớ" thì KHÔNG đụng SRS (giữ nguyên `box`/`due`). ⚠️ Nghĩa là trong Flashcard, SRS giờ chỉ có 1 tín hiệu duy nhất ("Được") thay vì 4 mức — Quiz/Luyện nghe vẫn giữ nguyên cơ chế 2 mức (đúng/sai → quality 2/0) như cũ, không đổi.
- Từ "Đã nhớ" bị lọc khỏi **CẢ 4 mode** (Flashcard/Quiz/Nghe/Nói) ngay tại bước build `queue` trong từng hàm mode — **KHÔNG lọc ở `pool()`** (nếu lọc ở đó, ranh giới "Bộ N (x-y)" sẽ dịch chuyển liên tục, phá vỡ `deckDone` tracking đang khóa theo index cố định).
- Header Flashcard hiện thêm tên Bộ khi học theo 1 Bộ cụ thể: `"Bộ 2 (26-50) · 3 / 20"` (hàm `curDeckRangeLabel()`, mục 4.3) — học "Tất cả" thì giữ format cũ không hiện tên Bộ.
- `learnedCount()` ("Đã thuộc") tính cả `box>=3 || mastered`.
- Màn Flashcard có link "✅ N từ đã thuộc trong bộ này" → `masteredListScreen()`.
- **⭐ Yêu thích** là 1 mode-card riêng trong `homeDashboard()` (5 ô), mở `favoritesMode()` — **KHÔNG dùng chung `flashMode()`** vì phải tránh kích hoạt `markDeckDone` (favorites không phải 1 "bộ").

### 4.5. Mic / Speech Recognition — kiến trúc quan trọng nhất cần biết

**Android WebView (nơi Capacitor chạy) KHÔNG hề implement Web Speech API** — đây là giới hạn nền tảng vĩnh viễn, không phải bug. App dùng **1 lớp thích ứng dùng chung** (gần đầu `<script>`, cạnh block SPEECH RECOGNITION cũ):

```js
function isNativeApp(){ return !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()); }
function nativeSR(){ return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.SpeechRecognition; }
async function ensureMicReady(){ /* native: checkPermissions/requestPermissions plugin; web: requestMicPermission() cũ */ }
async function recognizeOnce(lang){ /* native: nativeSR().start({...}) trả {matches}; web: new SR() Promise-hóa */ }
function cancelRecognition(){ /* native: nativeSR().stop(); web: activeWebRec.stop() */ }
function hasSR(){ return !!SR || (isNativeApp() && !!nativeSR()); }
```

Cả 4 nơi dùng mic (`speakMode`, `setupReadingMic` IT専門 Reading, `setupPracticeMic` Kaiwa, `setupMic` IT業務編 Reading) đều gọi qua lớp này — **toàn bộ logic chấm điểm (`similarity()`, ngưỡng 90/51 — xem mục 4.7, `reviewCard()`) giữ nguyên, chỉ khác cách lấy `alts`**.

⚠️ **Bug đã gặp & fix:** `await ensureMicReady()` PHẢI nằm trong try/catch cùng với `recognizeOnce()` — nếu để ngoài, exception từ native plugin (unhandled promise rejection) làm nút mic "chết" im lặng không phản hồi, không có thông báo lỗi. Đã fix cả 4 nơi.

**Plugin native dùng:** `@capgo/capacitor-speech-recognition@8.1.10` (gọi thẳng Android `SpeechRecognizer`), cần quyền `RECORD_AUDIO` trong `AndroidManifest.xml` (đã thêm). Permission flow của web (`micPermission`/`requestMicPermission()`) VẪN giữ nguyên cho trường hợp chạy trên browser thường (desktop/Android Chrome) — `speakModeInit()` bỏ qua banner xin quyền khi `isNativeApp()===true` (để plugin tự hiện dialog quyền native đúng lúc bấm mic).

### 4.6. Module IT業務編 (audio hội thoại công việc IT)

Dữ liệu: 38 track mp3 + transcript xlsx (2 chương, 15 unit, xem `02_IT_Gyoumuhen/`). `build_app.py`'s `extract_gyoumu()` parse transcript (tách lời thoại theo `\r\n` + regex `^([^：:]+)[：:]\s*(.*)$` tách tên nhân vật/nội dung — làm ngay lúc build, không phải runtime). Track 9 và 21 thiếu transcript (`hasTranscript=false`, xác định qua nội dung placeholder trong xlsx — không hardcode số track) — vẫn nghe được nhưng bị loại khỏi Luyện đọc.

Player nghe dùng **1 thẻ `<audio>` thật** trong DOM (không sửa `playAudioUrl()` cũ — hàm đó dành riêng cho TTS, sửa sẽ rủi ro). Progress bar bằng `<input type=range>`. `stopSpeech()` (điểm dừng-audio chung) đã mở rộng để pause luôn audio local này khi back ra khỏi màn.

### 4.7. TTS (đọc giọng) — kiến trúc mới sau FR_005, ĐÃ TEST THẬT VÀ XÁC NHẬN HOẠT ĐỘNG

**Lịch sử vấn đề:** ban đầu TTS chỉ dùng Google Translate endpoint (`translate_tts?client=gtx`) → fallback `speechSynthesis` khi lỗi. Trên Android WebView (APK), `speechSynthesis` **không tồn tại** (mục 4.5 cũng nhắc — giới hạn nền tảng vĩnh viễn), nên fallback không bao giờ chạy được. Khi test thật trên điện thoại, phát hiện Google TTS **cũng lỗi luôn trong APK** (toast báo `error:media4` = `MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED` — endpoint không chính thức của Google trả về nội dung không phải audio hợp lệ khi gọi từ WebView đóng gói, khác context so với trình duyệt thật). Tức là **TTS chưa từng hoạt động thật trên APK** cho tới khi fix dưới đây.

**Fix triệt để (đã verify hoạt động — PM xác nhận "Đã nghe được"):** thêm plugin Capacitor chính thức **`@capacitor-community/text-to-speech@8.0.2`** — dùng thẳng engine `TextToSpeech` của hệ điều hành Android (giống hệt cách `@capgo/capacitor-speech-recognition` đã dùng cho mic, mục 4.5). Kiến trúc:

```js
function nativeTTS(){ return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.TextToSpeech; }
async function nativeSpeak(text, rateOverride){
  var tts = nativeTTS();
  if(!tts || !text) return false;
  try{ await tts.speak({text, lang:'ja-JP', rate:rateOverride||ttsSettings.speed||0.9, pitch:ttsSettings.pitch||1.0, volume:1.0}); return true; }
  catch(e){ return false; }
}
```

`speak()`/`speakAsync()` giờ kiểm tra `isNativeApp() && nativeTTS()` **ĐẦU TIÊN**: nếu true → gọi thẳng `nativeSpeak()`, hoàn toàn KHÔNG qua mạng/Google TTS nữa (nếu plugin lỗi, VD máy thiếu gói giọng tiếng Nhật, hiện toast hướng dẫn vào Cài đặt Android bật giọng đọc). Đường Google TTS (`playTTSChunk()`, tự thử 2 endpoint `client=gtx`/`client=tw-ob`) + `deviceSpeak()` (`speechSynthesis`) **CHỈ còn áp dụng cho môi trường web/Chrome** (mở file HTML trực tiếp, không qua APK) — không đổi gì ở nhánh đó. `stopSpeech()` cũng gọi `nativeTTS().stop()` khi native để dừng đúng lượt đọc trước đó.

- Toast lỗi (`showToast()`) hiện khi TTS thất bại (cả 2 nhánh native/web) thay vì im lặng như trước — có mã lỗi cụ thể ở nhánh web (VD `error:timeout`/`error:media2`) để chẩn đoán nếu tái phát.
- Chấm điểm phát âm: `normJa()` bỏ dấu câu → `similarity()` LCS ratio → %. **Ngưỡng đã đổi ở FR_005: ≥90 xuất sắc · ≥51 khá · <51 luyện lại** (trước là ≥80/≥55) — áp dụng đồng bộ ở cả 4 nơi chấm điểm (`speakMode`, `setupReadingMic` IT専門, `setupMic` IT業務編, `setupPracticeMic` Kaiwa). Mỗi lần chấm điểm giờ có thêm **âm thanh phản hồi** qua Web Audio API thuần (`playScoreSound(score)`, hàm `beep()` tự tạo tần số, không cần file âm thanh — 3 mức tương ứng 3 ngưỡng điểm).
- **Verify sau mỗi build:** `node --check` trên phần `<script>` tách ra; `json.loads` JSON vocab/gyoumu đủ số lượng; không còn placeholder `__GEN_DATE__`/`__COUNT__`.
- **Verify riêng cho plugin TTS native (không có device thật):** kiểm tra `TextToSpeechPlugin` có compile vào bytecode APK (`unzip classes*.dex` rồi tìm chuỗi `TextToSpeechPlugin`/`community/tts`) + `npx cap sync` log phải liệt kê đủ 2 plugin (`@capacitor-community/text-to-speech` và `@capgo/capacitor-speech-recognition`) — KHÔNG thay thế test thật, nhưng đủ để verify plugin thực sự được đóng gói.

---

## 5. GIAI ĐOẠN ③ — Đóng gói APK Android (Capacitor)

### 5.1. Vì sao cần APK (không chỉ dùng HTML)
Mở HTML trực tiếp trên Android qua File Manager thường load qua URI `content://` (không phải `file://`) → đường dẫn tương đối tới `audio/` bị gãy, không nghe được. Capacitor đóng gói toàn bộ web assets vào chính APK, phục vụ qua 1 local scheme ổn định → audio luôn phát được, và cho phép dùng plugin mic native (mục 4.5).

### 5.2. Quy trình build lại APK (sau khi sửa `app_template.html`)

```bash
# 1. Build lại HTML
cd 01_Build_App/_app_build && python3 build_app.py

# 2. Copy HTML + audio mới nhất vào project Capacitor
cp ../Kokoro_Nihongo.html ../../03_Android_App/www/index.html
cp ../audio/*.mp3 ../../03_Android_App/www/audio/

# 3. Sync vào project Android native (tự đăng ký plugin, không cần sửa code Java/Kotlin)
cd ../../03_Android_App && npx cap sync android

# 4. Build APK debug (cần JAVA_HOME + GRADLE_USER_HOME trỏ đúng, xem mục 2)
export JAVA_HOME="D:/Android/jdk21"
export GRADLE_USER_HOME="D:/Android/gradle-home"
cd android && ./gradlew.bat assembleDebug

# 5. Copy APK ra vị trí dễ tìm
cp app/build/outputs/apk/debug/app-debug.apk ../Kokoro_Nihongo.apk
```

### 5.3. 2 quirk kỹ thuật quan trọng (trong `03_Android_App/android/gradle.properties`)

```properties
# Bắt buộc cho MỌI máy build — thư mục project chứa 日本語 (non-ASCII), AGP mặc định chặn path này trên Windows
android.overridePathCheck=true

# CHỈ đúng trên máy này — trỏ cứng tới JDK portable. Máy khác cần sửa path này hoặc xóa để Gradle tự tìm JAVA_HOME
org.gradle.java.home=D:\\Android\\jdk21
```

### 5.4. Trạng thái version
APK hiện tại vẫn là bản **test**, `versionCode=1`/`versionName="1.0"` trong `android/app/build.gradle` — **CHƯA bump lên "0.1" chính thức** (theo thỏa thuận trước: chỉ bump sau khi người dùng xác nhận đã test ổn trên điện thoại thật). Nếu người dùng xác nhận, sửa 2 dòng đó rồi build lại là xong, không cần đổi gì khác.

### 5.5. Giới hạn môi trường build hiện tại
Máy chạy Claude **không có thiết bị/emulator Android kết nối** — không thể tự cài & bấm thử trên máy thật. Mọi lần build chỉ verify được: build thành công (`gradlew assembleDebug` exit 0), cấu trúc APK đúng (`aapt dump badging`/`unzip -l` kiểm tra permission, assets, plugin registration), và test logic JS bằng cách **mock `window.Capacitor`** trong Chrome preview (giả lập plugin trả kết quả, xác nhận luồng gọi/xử lý lỗi đúng) — KHÔNG thay thế được test thật trên điện thoại (đặc biệt phần mic/TTS native). **Quy trình thực tế đang dùng:** Claude build + verify tối đa có thể → PM tự cài APK lên điện thoại thật để test → báo lại kết quả (kèm ảnh chụp/toast lỗi cụ thể nếu có) → Claude sửa tiếp dựa trên phản hồi đó. Cách này đã từng cần 2-3 vòng lặp cho 1 bug (VD TTS ở FR_005: vòng 1 chỉ thêm timeout/toast — chưa sửa được gốc; vòng 2 mới thêm plugin native TTS và fix thật, nhờ có mã lỗi cụ thể PM báo lại ở vòng 1).

### 5.6. Công cụ tạo app icon
`@capacitor/assets` (devDependency, `npx capacitor-assets generate --android`) — sinh toàn bộ icon launcher (mọi mật độ, adaptive icon foreground/background) + splash screen sáng/tối từ 1 ảnh nguồn vuông duy nhất `03_Android_App/assets/icon.png` (copy từ `04_Image/Logo_Tanpopo.png`, 1024x1024). Muốn đổi logo: thay file `assets/icon.png` rồi chạy lại lệnh trên, sau đó `npx cap sync android` + build lại APK như quy trình mục 5.2.

---

## 6. GIAI ĐOẠN ④ — Git & GitHub

- Repo local đã `git init` tại `100_日本語/` (không phải trong `03_Android_App/` hay thư mục con nào).
- Git identity **local-only** (không phải global): `user.name=NguyenNC`, `user.email=nguyennc@vi-mash.com`.
- Remote: `origin` → https://github.com/Nin-Min2231/Lading_page-VS.git, nhánh `main`, đã push (commit `70e1fab` trở đi).
- `.gitignore` loại trừ: `node_modules/`, audio trùng lặp (chỉ giữ `02_IT_Gyoumuhen/AudioCD/` làm nguồn duy nhất, bỏ 2 bản copy ở `01_Build_App/audio/` và `03_Android_App/www/`), APK (~73MB), Gradle/Android build artifacts, `local.properties` (machine-specific), `.claude/settings.local.json`.
- Muốn commit thay đổi mới: `git add -A && git commit -m "..."` rồi `git push` như bình thường — không có gì đặc biệt cần nhớ ngoài việc **không commit các thư mục đã gitignore** (nếu thấy chúng xuất hiện trong `git status`, kiểm tra lại `.gitignore` trước khi add).

---

## 7. Checklist cho session mới tiếp tục project

- [ ] Đọc file này (đủ context, không cần đọc lại toàn bộ lịch sử chat cũ).
- [ ] Xác nhận `git status` sạch (`nothing to commit`) trước khi bắt đầu — nếu có thay đổi dở dang từ trước, hỏi người dùng trước khi động vào.
- [ ] Muốn sửa app HTML/logic: sửa `01_Build_App/_app_build/app_template.html`, KHÔNG sửa `Kokoro_Nihongo.html` (bị build đè).
- [ ] Muốn thêm từ mới: skill `translator-ja-vi-en` → ghi bằng raw ZIP/XML (mục 3.2), KHÔNG `openpyxl.save()`.
- [ ] Sau khi sửa: `python3 build_app.py` → verify (`node --check`, đếm JSON) → **test kỹ trong Chrome preview trước khi build APK** (thói quen làm việc người dùng đã yêu cầu rõ — đừng build APK ngay khi chưa được xác nhận).
- [ ] Muốn build APK: theo đúng quy trình mục 5.2, nhớ `export JAVA_HOME`/`GRADLE_USER_HOME` trước khi `gradlew`.
- [ ] Đọc `01_Build_App/_feature_requests/` nếu có FR mới người dùng viết sẵn.
- [ ] Commit + push theo mục 6 nếu người dùng yêu cầu (mặc định KHÔNG tự ý commit/push nếu không được nhắc).

---

## 8. Feature Request — cách yêu cầu thêm/sửa chức năng

Folder `01_Build_App/_feature_requests/`: `TEMPLATE.md` để copy, đặt tên `FR_<số>_<tên>.md`. Lịch sử: FR_002 (đổi màu + fix Kaiwa + mic reading), FR_003 (multi-theme + IT業務編 — Part 1+2 UI/menu đã có sẵn từ trước, Part 3 audio làm ở FR_004), FR_004 (IT業務編 Luyện nghe/Luyện đọc), FR_005 (fix TTS Android bằng plugin native — **đã test thật, PM xác nhận nghe được**; redesign Flashcard/IT専門/main menu; thêm app icon từ `04_Image/Logo_Tanpopo.png`) — tất cả **đã xong**. Không cần viết file FR nếu không muốn — mô tả trong chat theo cấu trúc (làm gì → hành vi cụ thể → ràng buộc) là đủ.

---

## 9. Backlog / ý tưởng nâng cấp tiếp

- Bump version APK lên "0.1" chính thức (chờ người dùng xác nhận test ổn trên điện thoại thật).
- Quiz nội dung + trích từ vựng riêng cho IT業務編 (đã note rõ ngoài phạm vi FR_004, để FR riêng).
- Đồng bộ tiến độ đa thiết bị (cần backend nhẹ / export-import JSON).
- Chế độ viết kanji, ghép câu, nghe chép chính tả.
- Export tiến độ ra file để backup (tránh mất khi xóa cache trình duyệt/gỡ app).
- Bản release APK đã ký (hiện chỉ có debug build).
- Đổi tên GitHub repo cho khớp tên dự án (hiện đang dùng tạm `Lading_page-VS`).
