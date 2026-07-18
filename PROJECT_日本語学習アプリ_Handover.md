# PROJECT — Kokoro Nihongo (ココロ日本語) · Tài liệu handover

> **Mục đích tài liệu:** Ghi lại toàn bộ bản chất vấn đề & quy trình — từ **từ điển Excel** → **build app HTML** → **đóng gói APK Android** → **push GitHub**. Đọc file này là 1 chat Claude mới hiểu ngay context, không cần giải thích lại.
> **Đối tượng đọc:** Claude (chat mới) hoặc chính người dùng.
> **Người dùng:** NguyenNC — PM/BrSE ngành IT (cầu nối VN ⇄ Nhật).
> **Cập nhật lần cuối:** 2026-07-18 — sau khi hoàn thành FR_004 (IT業務編), đóng gói APK Capacitor, hệ thống Bộ học/Yêu thích/Đã nhớ, và push code lên GitHub.

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
│   └── _feature_requests/                  ← FR_001 (mẫu) .. FR_004 (đã xong) — lịch sử yêu cầu tính năng
│
├── 02_IT_Gyoumuhen/                         ← Nguồn dữ liệu module IT業務編 (hội thoại công việc IT)
│   ├── IT_Gyoumuhen.pdf                     ← Sách gốc scan, chỉ tham khảo
│   ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx ← Transcript 38 track (Track|Chương|Unit|...|Nội dung hội thoại|Ghi chú)
│   └── AudioCD/                              ← 38 file mp3 — NGUỒN AUDIO DUY NHẤT của cả dự án
│
└── 03_Android_App/                          ← Project Capacitor — đóng gói HTML thành APK Android
    ├── package.json, capacitor.config.json  ← appId com.kokoronihongo.app, appName "Kokoro Nihongo"
    ├── www/                                  ← (gitignore) copy Kokoro_Nihongo.html + audio, sync thủ công trước khi build
    ├── android/                              ← Project Android native (Gradle) — mở bằng Android Studio được
    └── Kokoro_Nihongo.apk                     ← (gitignore) APK build sẵn mới nhất, ~73MB
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

Luồng đầy đủ:
```
home() → IT専門 → homeDashboard() → [Flashcard/Quiz/Nghe/Nói/⭐Yêu thích] → mode screen
home() → IT業務編 → gyoumuDashboard() → gyoumuTrackList() → gyoumuTrackDetail() → gyoumuReadingMode()
home() → Luyện đọc → readingLibrary() → readingMode(deckList, deckIdx)
home() → Kaiwa → kaiwaLibrary() → kaiwaMode(deckList, deckIdx)
```

### 4.3. Hệ thống "Bộ học" (deck) — quan trọng, ảnh hưởng nhiều logic

Với 596 từ, IT専門 chia thành các **"bộ"** ~20-30 từ (`splitDecks(pool(), 25)` — chia đều số dư, không dồn vào bộ cuối). UI: lưới 4 thẻ/trang (`deckGridHTML()` — component dùng chung cho IT専門/Luyện đọc/Kaiwa), phân trang bằng `‹`/`›`.

- `curDeck` (global, 'ALL' hoặc index string) — khi chọn 1 bộ cụ thể, 4 mode Flashcard/Quiz/Nghe/Nói dùng **TRỌN VẸN** danh sách bộ đó (không random-sample như khi chọn "Tất cả") → hoàn thành 1 phiên = hoàn thành cả bộ.
- **Hoàn thành bộ** lưu ở `store.deckDone[category][deckIndex][mode] = true`, đánh dấu tập trung trong `finish()` (điểm chung của cả 4 mode). Thẻ bộ hiện icon nhỏ (🗂️✍️🎧🎤) cho mode đã hoàn thành, và **chuyển màu xanh lá** khi đủ cả 4 mode.
- ⚠️ **Đổi category → reset `curDeck='ALL'`** (ranh giới bộ phụ thuộc category đang lọc).
- Reading/Kaiwa dùng namespace riêng `store.deckDone['_reading']`/`['_kaiwa']` (chỉ 1 "mode" mỗi cái), không đụng tracking của IT専門.

### 4.4. Yêu thích & Đã nhớ (mới, trên màn Flashcard)

`store.favorites = {id:true}`, `store.cards[id].mastered = true/false` — **CỜ RIÊNG, không dùng chung với `box` SRS tự nhiên** (tránh từ tự nhiên đạt box cao qua chấm điểm bị loại ngoài ý muốn). Helper: `toggleFavorite/isFavorite/toggleMastered/isMastered`.

- Màn Flashcard có 4 nút: **Xem chi tiết/Ẩn chi tiết** (toggle 2 chiều, đồng bộ với chạm thẻ), **Yêu thích**, **Đã nhớ**, **Từ tiếp theo** (không auto-advance khi yêu thích/đã nhớ — user tự bấm next).
- Từ "Đã nhớ" bị lọc khỏi **CẢ 4 mode** (Flashcard/Quiz/Nghe/Nói) ngay tại bước build `queue` trong từng hàm mode — **KHÔNG lọc ở `pool()`** (nếu lọc ở đó, ranh giới "Bộ N (x-y)" sẽ dịch chuyển liên tục, phá vỡ `deckDone` tracking đang khóa theo index cố định).
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

Cả 4 nơi dùng mic (`speakMode`, `setupReadingMic` IT専門 Reading, `setupPracticeMic` Kaiwa, `setupMic` IT業務編 Reading) đều gọi qua lớp này — **toàn bộ logic chấm điểm (`similarity()`, ngưỡng 80/55, `reviewCard()`) giữ nguyên, chỉ khác cách lấy `alts`**.

⚠️ **Bug đã gặp & fix:** `await ensureMicReady()` PHẢI nằm trong try/catch cùng với `recognizeOnce()` — nếu để ngoài, exception từ native plugin (unhandled promise rejection) làm nút mic "chết" im lặng không phản hồi, không có thông báo lỗi. Đã fix cả 4 nơi.

**Plugin native dùng:** `@capgo/capacitor-speech-recognition@8.1.10` (gọi thẳng Android `SpeechRecognizer`), cần quyền `RECORD_AUDIO` trong `AndroidManifest.xml` (đã thêm). Permission flow của web (`micPermission`/`requestMicPermission()`) VẪN giữ nguyên cho trường hợp chạy trên browser thường (desktop/Android Chrome) — `speakModeInit()` bỏ qua banner xin quyền khi `isNativeApp()===true` (để plugin tự hiện dialog quyền native đúng lúc bấm mic).

### 4.6. Module IT業務編 (audio hội thoại công việc IT)

Dữ liệu: 38 track mp3 + transcript xlsx (2 chương, 15 unit, xem `02_IT_Gyoumuhen/`). `build_app.py`'s `extract_gyoumu()` parse transcript (tách lời thoại theo `\r\n` + regex `^([^：:]+)[：:]\s*(.*)$` tách tên nhân vật/nội dung — làm ngay lúc build, không phải runtime). Track 9 và 21 thiếu transcript (`hasTranscript=false`, xác định qua nội dung placeholder trong xlsx — không hardcode số track) — vẫn nghe được nhưng bị loại khỏi Luyện đọc.

Player nghe dùng **1 thẻ `<audio>` thật** trong DOM (không sửa `playAudioUrl()` cũ — hàm đó dành riêng cho TTS, sửa sẽ rủi ro). Progress bar bằng `<input type=range>`. `stopSpeech()` (điểm dừng-audio chung) đã mở rộng để pause luôn audio local này khi back ra khỏi màn.

### 4.7. Speech API & lỗi thường gặp (giữ từ bản cũ, vẫn đúng)

- TTS: Google Translate endpoint (`translate_tts?client=gtx`) → fallback `speechSynthesis` khi lỗi/offline.
- Chấm điểm: `normJa()` bỏ dấu câu → `similarity()` LCS ratio → % (≥80 tuyệt, ≥55 khá).
- **Verify sau mỗi build:** `node --check` trên phần `<script>` tách ra; `json.loads` JSON vocab/gyoumu đủ số lượng; không còn placeholder `__GEN_DATE__`/`__COUNT__`.

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
Máy chạy Claude **không có thiết bị/emulator Android kết nối** — không thể tự cài & bấm thử trên máy thật. Mọi lần build chỉ verify được: build thành công (`gradlew assembleDebug` exit 0), cấu trúc APK đúng (`aapt dump badging`/`unzip -l` kiểm tra permission, assets, plugin registration), và test logic JS bằng cách **mock `window.Capacitor`** trong Chrome preview (giả lập plugin trả kết quả, xác nhận luồng gọi/xử lý lỗi đúng) — KHÔNG thay thế được test thật trên điện thoại (đặc biệt phần mic native).

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

Folder `01_Build_App/_feature_requests/`: `TEMPLATE.md` để copy, đặt tên `FR_<số>_<tên>.md`. Lịch sử: FR_002 (đổi màu + fix Kaiwa + mic reading), FR_003 (multi-theme + IT業務編 — Part 1+2 UI/menu đã có sẵn từ trước, Part 3 audio làm ở FR_004), FR_004 (IT業務編 Luyện nghe/Luyện đọc, đã hoàn thành) — tất cả **đã xong**. Không cần viết file FR nếu không muốn — mô tả trong chat theo cấu trúc (làm gì → hành vi cụ thể → ràng buộc) là đủ.

---

## 9. Backlog / ý tưởng nâng cấp tiếp

- Bump version APK lên "0.1" chính thức (chờ người dùng xác nhận test ổn trên điện thoại thật).
- Quiz nội dung + trích từ vựng riêng cho IT業務編 (đã note rõ ngoài phạm vi FR_004, để FR riêng).
- Đồng bộ tiến độ đa thiết bị (cần backend nhẹ / export-import JSON).
- Chế độ viết kanji, ghép câu, nghe chép chính tả.
- Export tiến độ ra file để backup (tránh mất khi xóa cache trình duyệt/gỡ app).
- Bản release APK đã ký (hiện chỉ có debug build).
- Đổi tên GitHub repo cho khớp tên dự án (hiện đang dùng tạm `Lading_page-VS`).
