# PROJECT — Kokoro Nihongo (ココロ日本語) · Tài liệu handover

> **Mục đích tài liệu:** Ghi lại toàn bộ bản chất vấn đề & quy trình — từ **từ điển Excel** → **build app HTML** → **đóng gói APK Android** → **push GitHub**. Đọc file này là 1 chat Claude mới hiểu ngay context, không cần giải thích lại.
> **Đối tượng đọc:** Claude (chat mới) hoặc chính người dùng.
> **Người dùng:** NguyenNC — PM/BrSE ngành IT (cầu nối VN ⇄ Nhật).
> **Cập nhật lần cuối:** 2026-09-25 — **App giờ có đủ 3 module (IT専門/IT業務編/シャドウイング), tất cả đã code + test qua Browser pane + PM tự test trên máy thật, PUSH LÊN GITHUB XONG.**
>
> **Tóm tắt nhanh cho 1 phiên chat mới:** Module thứ 3 **シャドウイング** (Shadowing 中〜上級編, FR_013, mục 4.15) được thêm 2026-09-22, sau đó trải qua nhiều vòng PM test bản PC + góp ý UI (mục 4.16→4.19): gộp 🎧 nghe + 🎤 luyện nói vào **1 accordion mỗi Đoạn/Track** (2 tab con trong cùng 1 thẻ), 3 màu nền theo tiến độ (`.tint-partial`/`.tint-done`), điểm mỗi câu/lượt thoại = **điểm lần ghi âm gần nhất** (không phải cao nhất), UI riêng 2 màn nghe/luyện nói chuyển sang **tiếng Nhật** (ngoại lệ so với quy ước UI tiếng Việt chung của app). Cùng đợt, **IT業務編 được redesign lại theo đúng mẫu シャドウイング** (mục 4.18/4.19) — dùng chung hạ tầng màu/điểm/layout gọn (`scoreColorTier()`, `.compact-row`/`.compact-body`), và trang chủ (`home()`) được gọn lại + Nhật hoá + thêm ô số liệu シャドウイング (mục 4.18). **PM đã cài bản APK `versionCode 4`/`versionName "0.1"` lên điện thoại thật và xác nhận OK (2026-09-25).** Toàn bộ (trừ dữ liệu シャドウイング) đã commit + push — `main` tại `origin/main` giờ ở commit `6fe8245` (push thẳng từ worktree bằng `git push origin <branch>:main`, không qua thư mục project chính — xem mục 6). Đọc chi tiết đầy đủ ở mục 4.15 → 4.20 theo đúng thứ tự thời gian.
>
> **Lưu ý quan trọng còn tồn đọng:** dữ liệu `06_ Shadowing_Jokyu/` (JSON + xlsx + 46MB audio) — **PM yêu cầu KHÔNG commit** (nội dung giáo trình có bản quyền, chỉ dùng nội bộ) — vẫn nằm ở thư mục project chính, KHÔNG có trong git. Bất kỳ ai checkout lại repo từ đầu (máy khác, hoặc xóa sạch thư mục cũ) sẽ build ra app **thiếu hẳn module シャドウイング** (`build_app.py` tự động bỏ qua nếu không thấy file, in cảnh báo, không lỗi) cho tới khi copy lại thư mục này từ nơi lưu trữ riêng của PM. Quyết định bitrate audio (giữ 64kbps hay hạ 48kbps, mục 4.15/4.17) vẫn để ngỏ, không còn cấp thiết vì PM đã test OK ở 64kbps.
>
> Lịch sử trước đó (Phase 2, mục 4.14 trở về trước): đủ Phase 2 (FR_008→FR_012) + FR_006/FR_007 + redesign dashboard "giấy washi" + 4 việc mục 4.14 (checkbox "Học từ đã nhớ", lưới Bộ 6 icon, hero streak, Cài đặt sticky header) — bản APK đầu tiên của gói này (`versionCode 1`/`"1.0"`) được PM xác nhận test ổn 2026-09-22, từ đó bump lên `versionCode 2`/`versionName "0.1"` làm mốc ổn định đầu tiên (mục 5.4). Trước đó nữa, dự án đã trải qua "Phase 1" (2026-09-11): viết lại tầng đọc `build_app.py` (v2, hỗ trợ cả 3 kiểu ô OOXML) sau khi từ điển đổi cách lưu làm build chết, thêm sổ khóa `_id_lock.json`. Đọc kỹ mục 4.9 và `CLAUDE.md` quy tắc #6 nếu thấy nhắc `_id_lock.json`.

---

## 1. Tổng quan mục tiêu (Big picture)

```
日本語の辞書.xlsx  (từ điển gốc, 663 từ)
        │  build_app.py
        ▼
Kokoro_Nihongo.html  ← app học, mở trực tiếp bằng trình duyệt (máy tính/điện thoại), KHÔNG cần cài đặt
        │  npx cap sync + gradlew (project Capacitor ở 03_Android_App/)
        ▼
Kokoro_Nihongo.apk  ← app Android thật, cài trực tiếp lên điện thoại — mic chấm điểm phát âm hoạt động thật
```

**Môi trường làm việc hiện tại:** Windows, chạy trực tiếp qua Bash/PowerShell (KHÔNG phải Cowork sandbox kiểu `/sessions/<tên>/mnt/` như tài liệu handover bản cũ từng mô tả — nếu thấy nhắc tới path đó, đó là thông tin CŨ, bỏ qua). Path project cố định: `D:\01_NguyenNC\10_Claude\100_日本語\`.

**Repo GitHub:** https://github.com/Nin-Min2231/Nihongo_App (đổi tên 2026-09-12 từ `Lading_page-VS` cũ — khớp đúng tên dự án, xem mục 4.12; URL cũ vẫn redirect được). Nhánh `main`, commit gốc `70e1fab`, local mới nhất `f95d252` (mục 4.14) — **CHƯA push**, `origin/main` trên GitHub vẫn đang dừng ở `71b266d`.

---

## 2. Cấu trúc thư mục

```
100_日本語/
├── 日本語の辞書.xlsx                      ← Từ điển gốc (663 từ, PM dọn lại 2026-09-12 — mục 4.11) — KHÔNG dùng openpyxl.save()
├── CLAUDE.md                               ← Quy tắc/kiến trúc dự án
├── PROJECT_日本語学習アプリ_Handover.md    ← File này
├── README.md                               ← Hướng dẫn build/chạy/push GitHub (tiếng Việt, ngắn gọn hơn file này)
├── .gitignore                              ← Loại trừ node_modules/, audio trùng lặp, APK, build artifacts, 05_json/
├── _KHAO_SAT/                               ← Khảo sát hiện trạng + kế hoạch gộp app (2026-09-11), tài liệu tham khảo — đã commit (mục 4.11)
├── 05_json/                                 ← (gitignore) Bản xuất tiến độ (FR_011) PM lưu thủ công ra máy — dữ liệu cá nhân, không phải source
├── Ban_dich_*.md                             ← 2 file dịch KHÔNG liên quan tới Kokoro, nằm lạc chỗ — không đụng, không commit
│
├── 01_Build_App/                           ← App IT専門 (từ vựng) — build từ xlsx
│   ├── Kokoro_Nihongo.html                 ← App đã build (commit vào git, mở trực tiếp được)
│   ├── audio/                              ← (gitignore) copy từ 02_IT_Gyoumuhen/AudioCD, build_app.py tự sync
│   ├── _app_build/
│   │   ├── build_app.py                    ← Script build v2: xlsx + transcript → JSON → inject template + copy audio
│   │   ├── app_template.html                ← TOÀN BỘ CSS+JS của app (~2400+ dòng, sửa file này để thêm tính năng)
│   │   ├── _id_lock.json                    ← ⚠ Sổ khóa từ vựng → id cố định (Phase 1). KHÔNG xóa/sửa tay, PHẢI commit.
│   │   └── segment_reading_audio.py          ← Script cắt audio theo lượt thoại (FR_007 bản gốc) — có dữ liệu (mục 4.10/4.11) nhưng CHƯA nối vào app, giữ cho lần sau
│   └── _feature_requests/                  ← TEMPLATE.md (viết FR mới) + done/ (FR_002..FR_012, tất cả đã xong — không còn FR nào pending)
│
├── 02_IT_Gyoumuhen/                         ← Nguồn dữ liệu module IT業務編 (hội thoại công việc IT)
│   ├── IT_Gyoumuhen.pdf                     ← Sách gốc scan, chỉ tham khảo
│   ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx ← Transcript 38 track (Track|Chương|Unit|...|Nội dung hội thoại|Ghi chú)
│   ├── AudioCD/                              ← 38 file mp3 — NGUỒN AUDIO DUY NHẤT của cả dự án
│   └── reading_segments/                     ← segments_data.json (commit) + audio/ (gitignore, ~37MB) — dữ liệu FR_007 bản gốc, xem mục 4.10
│
├── 04_Image/                                 ← Logo/asset nguồn (không phải code)
│   └── Logo_Tanpopo.png                      ← Logo gốc 1024x1024, dùng làm app icon + favicon
│
├── 06_ Shadowing_Jokyu/                      ← Nguồn dữ liệu module thứ 3 シャドウイング (FR_013, mục 4.15) — tên có khoảng trắng
│   ├── Shadowing_Data.json                   ← 8 Unit/22 section/62 track/240 đoạn/1.225 lượt thoại — build_app.py đọc thẳng
│   ├── Shadowing_Transcript.xlsx             ← Bản người đọc, tham khảo — KHÔNG dùng khi build
│   ├── AudioMP3/                             ← 62 file mp3 mono 64kbps, ~46MB — NGUỒN AUDIO DUY NHẤT của module này
│   ├── FR_013_shadowing_module.md            ← Bản gốc FR (đã copy 1 bản vào 01_Build_App/_feature_requests/done/ cho khớp quy ước)
│   ├── 01_document/, 02_Claude outputs/       ← Tài liệu/output làm việc khi chuẩn bị dữ liệu (OCR, cắt audio) — không cần cho build
│   └── _ocr_tmp/                              ← (nếu còn) file tạm của quá trình OCR — an toàn để xóa, không phải dữ liệu nguồn
│
└── 03_Android_App/                          ← Project Capacitor — đóng gói HTML thành APK Android
    ├── package.json, capacitor.config.json  ← appId com.kokoronihongo.app, appName "Kokoro Nihongo"
    ├── assets/icon.png                       ← Copy của Logo_Tanpopo.png, nguồn cho `npx capacitor-assets generate`
    ├── www/                                  ← (gitignore) copy Kokoro_Nihongo.html + audio, sync thủ công trước khi build
    ├── android/                              ← Project Android native (Gradle) — mở bằng Android Studio được
    └── Kokoro_Nihongo.apk                     ← (gitignore) APK build sẵn mới nhất, ~78MB, xem mục 4.12
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

Hiện tại: **663 từ** (596 → 667 sau Phase 1, 2026-09-11 — xem mục 4.9 về `_id_lock.json`; PM dọn lại còn 663 ngày 2026-09-12 — mục 4.11). `id` mỗi từ **không còn khớp STT cột B** kể từ Phase 1 — xem `CLAUDE.md` quy tắc #7.

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

`home()` render từ **1 registry `MENU_MODULES`** (không hard-code từng card — điểm mở rộng chính, thêm chủ đề mới chỉ cần thêm 1 phần tử vào mảng):

```js
const MENU_MODULES = [
  {id:'it_senmon', icon:'💻', title:'IT専門', ..., open:homeDashboard},
  {id:'it_gyoumu', icon:'🏢', title:'IT業務編', ..., open:gyoumuDashboard},
];
```

**FR_008 (Phase 2, 2026-09-12) đã gỡ hẳn 2 phần tử `reading_lib`/`kaiwa_lib`** cùng toàn bộ hàm `readingLibrary()`/`readingMode()`/`finishReading()`/`kaiwaLibrary()`/`kaiwaMode()`/`finishKaiwa()`/`buildConversations()` — PM xác nhận không dùng 2 module này nữa (Kaiwa ghép câu ví dụ rời rạc thành hội thoại giả không liên quan logic; Luyện đọc câu trùng mục đích với Luyện nói). Dữ liệu `deckDone._reading`/`deckDone._kaiwa` của user cũ vẫn còn nguyên trong `localStorage` (không dọn, không migrate xóa) nhưng không còn đường nào đọc tới. Hàm `allWithEx()` và `splitDecks()` (san đều số dư, khác `splitDecksStrict()`) **được giữ lại có chủ đích** dù mất người dùng cũ — `allWithEx()` nay phục vụ thuật toán dò ô trống của mode Điền từ (mục 4.8).

Luồng đầy đủ hiện tại:
```
home() → IT専門 → homeDashboard() → [Flashcard/Quiz/Điền từ/Nghe/Nói/⚡Phản xạ/⭐Yêu thích] → mode screen
home() → IT業務編 → gyoumuDashboard() → gyoumuUnitScreen(chapter,unit) → [🎧 Luyện nghe / 🎤 Luyện đọc câu, cùng 1 màn hình — FR_007, mục 4.10]
home() → (khối thống kê, bấm được) → statsScreen()
```

**Đã thêm ở FR_005, còn nguyên tới nay:** `home()` hiện 1 khối thống kê tổng hợp toàn hệ thống ngay trên đầu (tái dùng CSS `.stats`/`.stat`): **Streak**, **Từ đã thuộc** (IT専門), **Track đã nghe** (IT業務編). **FR_012 (Phase 2) làm khối này bấm được** (mũi tên `›`, class `.stats-block`) → mở `statsScreen()`, xem mục 4.8.

### 4.3. Hệ thống "Bộ học" (deck) — quan trọng, ảnh hưởng nhiều logic

**Đã đổi ở FR_005 (2026-07-18):** IT専門 **không còn chip lọc "Chủ đề"** (漢字/外来語/その他 đã bỏ khỏi UI — biến `curCat` vẫn còn trong code nhưng luôn cố định `'ALL'`, chỉ dùng làm namespace key cho `deckDone`, không có UI đổi nữa). Toàn bộ từ vựng (663 từ — 667 sau Phase 1, PM dọn lại còn 663 ngày 2026-09-12, xem mục 4.11) được chia **CỐ ĐỊNH đúng 25 từ/bộ, bắt đầu từ #1** bằng hàm riêng `splitDecksStrict(arr, target)` (bộ cuối = phần dư, KHÔNG san đều số dư như trước) → 663 từ = 26 bộ×25 + 1 bộ 13 từ cuối (27 bộ). Hàm `splitDecks()` cũ (san đều số dư) trước kia dùng riêng cho Luyện đọc/Kaiwa — **2 module đó đã bị gỡ ở FR_008 (Phase 2)**, nên `splitDecks()` hiện là hàm không còn ai gọi, giữ lại có chủ đích (xem mục 4.2).

UI: lưới 4 thẻ/trang (`deckGridHTML()` — component dùng chung cho IT専門/Luyện đọc/Kaiwa), phân trang bằng `‹`/`›`. Bộ đang chọn (`.deck-card.on`) đổi nền **xanh dương nhạt** (`#dbeafe`) để phân biệt rõ với bộ chưa chọn (xanh dương đậm mặc định).

- `curDeck` (global, 'ALL' hoặc index string) — khi chọn 1 bộ cụ thể, 4 mode Flashcard/Quiz/Nghe/Nói dùng **TRỌN VẸN** danh sách bộ đó (không random-sample như khi chọn "Tất cả") → hoàn thành 1 phiên = hoàn thành cả bộ.
- **Hoàn thành bộ** lưu ở `store.deckDone[category][deckIndex][mode] = true`, đánh dấu tập trung trong `finish()` (điểm chung của cả 4 mode). Thẻ bộ hiện icon nhỏ (🗂️✍️🎧🎤) cho mode đã hoàn thành, và **chuyển màu xanh lá** khi đủ cả 4 mode (màu selected `.on` ưu tiên hiển thị trước màu `.done` nếu cả 2 cùng áp dụng).
- (Trước FR_008) Reading/Kaiwa dùng namespace riêng `store.deckDone['_reading']`/`['_kaiwa']` — 2 module đã gỡ, nhưng dữ liệu cũ này vẫn còn nguyên trong `localStorage` của user cũ, không bị migrate xóa.
- **FR_009/FR_010 (Phase 2) thêm mode `cloze`/`reflex` vào cùng object `deckDone[curCat][deckIdx]`** nhưng **`deckGridHTML()` chỉ nhận đúng 4 icon cũ** (🗂️✍️🎧🎤) — xem `CLAUDE.md` quy tắc #8. Thêm icon thứ 5/6 sẽ làm mọi Bộ đã hoàn thành (theo 4 mode cũ) lập tức mất màu xanh.
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

⚠️ **Mục này mô tả kiến trúc GỐC (FR_004).** FR_007 (mục 4.10) đã thay hẳn luồng điều hướng List→Detail bằng 1 màn hình gộp `gyoumuUnitScreen()` — thuật toán tách transcript/Track 9,21 vẫn y nguyên, chỉ đổi cách render (accordion + tab thay vì 2 trang riêng).

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
- Chấm điểm phát âm: `normJa()` bỏ dấu câu → `similarity()` LCS ratio → %. **Ngưỡng đã đổi ở FR_005: ≥90 xuất sắc · ≥51 khá · <51 luyện lại** (trước là ≥80/≥55) — áp dụng đồng bộ ở các nơi chấm điểm bằng mic còn lại (`speakMode` IT専門, `setupMic` IT業務編 — `setupReadingMic`/`setupPracticeMic` của Reading/Kaiwa đã mất theo FR_008). Mỗi lần chấm điểm giờ có thêm **âm thanh phản hồi** qua Web Audio API thuần (`playScoreSound(score)`, hàm `beep()` tự tạo tần số, không cần file âm thanh — 3 mức tương ứng 3 ngưỡng điểm).
- **Verify sau mỗi build:** `node --check` trên phần `<script>` tách ra; `json.loads` JSON vocab/gyoumu đủ số lượng; không còn placeholder `__GEN_DATE__`/`__COUNT__`.
- **Verify riêng cho plugin TTS native (không có device thật):** kiểm tra `TextToSpeechPlugin` có compile vào bytecode APK (`unzip classes*.dex` rồi tìm chuỗi `TextToSpeechPlugin`/`community/tts`) + `npx cap sync` log phải liệt kê đủ 2 plugin (`@capacitor-community/text-to-speech` và `@capgo/capacitor-speech-recognition`) — KHÔNG thay thế test thật, nhưng đủ để verify plugin thực sự được đóng gói.

### 4.8. Gói Phase 2 (FR_008 → FR_012, 2026-09-12) — 3 mode mới + xuất/nhập tiến độ + thống kê

Cả gói làm theo đúng thứ tự FR_008 → FR_011 → FR_009 → FR_010 → FR_012 (xem `01_Build_App/_feature_requests/done/_PHASE2_GOI_CAI_MOT_LAN.md` để biết vì sao đúng thứ tự này và các ràng buộc xuyên suốt: không đổi hợp đồng dữ liệu 7 khóa, giữ đúng 4 icon lưới Bộ, không thêm thư viện ngoài).

- **FR_008** — gỡ Kaiwa/Luyện đọc, xem mục 4.2.
- **FR_011 — `uiSettings` (`kokoro_ui_settings`)**: `{fontScale, reflexSec}`, áp `--fs-scale` lên `<html>` ngay lúc script chạy (trước `home()`) để không nháy cỡ chữ. Thêm mục "💾 Tiến độ học" trong `openSettings()`, xuất/nhập **nguyên văn chuỗi** 4 key localStorage (không parse-rồi-dựng-lại, để bản backup cũ vẫn nhập được dù schema đổi sau này), nhập **bắt buộc** hiện bảng so sánh Máy này/File nhập vào + cảnh báo đỏ trước khi ghi đè. **Đường xuất/nhập cho native đã đổi lại ngày 2026-09-12** sau khi PM cài bản APK đầu và thấy copy/dán thủ công tốn công — xem `CLAUDE.md` quy tắc #6 và FR_011 mục 0/4.1/4.2 để biết chi tiết (ghi file thật bằng `@capacitor/filesystem` + mở share sheet bằng `@capacitor/share`, nhập bằng `<input type="file">` cho cả 2 nền tảng, textarea+clipboard chỉ còn là đường lùi).
- **FR_009 — mode `cloze` (Điền từ vào câu, 🧩)**: `findCloze(v)`/`clozeCandidates(w)` (đặt cạnh `allWithEx()`) dò vị trí che trong `v.ex` bằng cách thử nhiều biến thể của `v.w` (bỏ chú thích ngoặc, tách `/`, bỏ đuôi chia động từ する/です/ます/な/い, lấy gốc Hán tự) rồi rơi về so khớp theo `v.r`. **Đo được trên 667 từ (lúc code FR_009): phủ 629 từ (94,3%)** — đã verify lại bằng script Node độc lập khớp đúng số liệu FR nêu. **Đo lại sau khi từ điển còn 663 từ (mục 4.11, 2026-09-12): phủ 627/663 (94,6%)** — logic `findCloze`/`clozeCandidates` không đổi, tỉ lệ chỉ xê dịch nhẹ theo nội dung từ điển mới. Ô trống hiển thị cố định `＿＿＿` (không theo đúng độ dài thật, tránh lộ manh mối). Gợi ý 3 bậc không thu lại được. Tính vào `deckDone` nhưng **không thêm icon** (quy tắc #8).
- **FR_010 — mode `reflex` (Phản xạ Ns, ⚡)**: hiện `v.vi`, vòng đếm ngược vẽ bằng SVG tay (`stroke-dasharray`/`stroke-dashoffset`, cập nhật `setInterval` 60ms), hết giờ hoặc bấm "Xem đáp án ngay" thì sang pha 2 hiện `v.w`/`v.r` để **người học tự chấm** 2 mức (không dùng mic — nhận giọng mất 1-2s khởi động sẽ phá phép đo phản xạ). Đọc `uiSettings.reflexSec` (mặc định 3, chỉnh 3/5/8s ở FR_011). `clearInterval` ở mọi lối thoát, mỗi nhịp tự kiểm tra phần tử SVG còn trong DOM không (tự dọn khi user bấm Back giữa chừng). Tính vào `deckDone` nhưng **không thêm icon**.
- **FR_012 — `statsScreen()`**: thêm `store.stats.history` (`{"YYYY-MM-DD":số_lượt}`, migrate an toàn cho user cũ, **không dựng lại lịch sử quá khứ**). Tách `bumpStudied()` (streak + history + `stats.studied`, gọi từ `reviewCard()`) khỏi `bumpStreak()` (chỉ streak + history) — IT業務編 (nghe xong 1 track lần đầu / hoàn thành 1 lượt luyện đọc theo thoại) chỉ gọi `bumpStreak()`, **fix đúng bug streak không tính khi học IT業務編**. Màn hình gồm 4 khối: streak, lịch nhiệt 12 tuần (CSS grid, không thư viện), phân bố trạng thái (Đã thuộc/Đang học/Từ khó/Chưa học — mỗi từ tính đúng 1 nhóm, tổng = `VOCAB.length`), dự báo tải ôn 7 ngày (`store.cards[*].due`, quá hạn gộp vào "Hôm nay"). Mở từ khối thống kê ở `home()` (mục 4.2).

**Đã test qua trình duyệt desktop (Chrome headless)**: cả 7 mode chạy được, lưới Bộ vẫn đúng 4 icon + chuyển xanh lá khi đủ 4 mode cũ, xuất/nhập tiến độ round-trip đúng số liệu, khổ màn ~390px không tràn ngang, không lỗi console. **Bản APK đầu tiên của gói này đã build, cài lên máy PM thành công (2026-09-12) và PM đã lấy được 1 bản xuất tiến độ thật** (516 lượt ôn, 85 từ đã thuộc, 246 thẻ theo dõi — xác nhận app + SRS + `_id_lock.json` hoạt động đúng ngoài đời thật). Ngay sau đó đổi đường xuất/nhập sang ghi file thật (mục trên) — **bản APK có thay đổi này CHƯA được PM cài/test trên điện thoại**, đặc biệt luồng `Filesystem.writeFile`+`Share.share()` và `<input type="file">` phía nhập trên native (chỉ verify được bằng mock `window.Capacitor` trong Chrome — xem mục 5.5).

### 4.9. "Phase 1" (2026-09-11) — viết lại tầng đọc Excel, `_id_lock.json`

Không thuộc phiên làm Phase 2, nhưng ảnh hưởng trực tiếp tới `build_app.py`/`app_template.html` nên ghi lại để không nhầm lẫn nguồn gốc thay đổi:

- Từ điển đổi cách lưu (chuyển hẳn sang `t="inlineStr"`, bỏ `xl/sharedStrings.xml`) làm `build_app.py` bản v1 (chỉ đọc được `t="s"` + `<v>`) chết với `KeyError`. `build_app.py` v2 đọc được **cả 3 kiểu ô** OOXML (`t="s"`/`t="inlineStr"`/`t="str"` hoặc số), kèm rich text và ô tự đóng; tìm cột theo **tên tiêu đề** dòng 4 thay vì hardcode B/C/D/E/F/G.
- Từ điển tăng từ 596 → **667 từ**.
- Thêm sổ khóa `01_Build_App/_app_build/_id_lock.json`: ánh xạ **từ vựng → id cố định vĩnh viễn**, không theo STT cột B nữa. Lý do: bản v1 dùng `id = STT`, nên xóa/chèn 1 dòng giữa Excel làm mọi id phía sau dịch theo — tiến độ học của từ A lặng lẽ gắn sang từ B. **Đã xảy ra thật**: so bản APK 2026-07-18 (596 từ) với từ điển 2026-09-11 (667 từ), 47/596 id trỏ sang từ khác. Chi tiết đầy đủ: `CLAUDE.md` quy tắc #7. File này **phải commit vào git**, không bao giờ xóa/sửa tay.
- Cờ CLI mới: `--check` (chỉ đọc + báo cáo, không ghi file), `--force` (bỏ qua cảnh báo chặn), `--seed-lock <file.html>` (khởi tạo sổ khóa từ 1 bản app đã build, dùng 1 lần).

### 4.10. FR_006 + FR_007 + Redesign dashboard (2026-09-12, cuối ngày)

**FR_006 — IT専門 auto-focus Bộ nhỏ nhất chưa hoàn thành**: `autoFocusDeckIndex(decks)` duyệt Bộ theo thứ tự tăng dần, trả về Bộ đầu tiên chưa đủ 4 cờ `deckDoneModes` (flash/quiz/listen/speak), hoặc Bộ cuối nếu đã xong hết. `homeDashboard(keepDeck)` gọi hàm này và set `curDeck`/`deckPage` **mỗi lần vào màn hình mà không truyền `keepDeck=true`** — 2 nơi duy nhất truyền `true` là click chọn Bộ thủ công và click nút lật trang lưới Bộ (`deckPrev`/`deckNext`/`.deck-card`), để không tự ghi đè lựa chọn thủ công ngay trong phiên. Test qua Browser pane: đúng cả 5 hành vi mô tả trong `01_Build_App/_feature_requests/done/FR_006_focus_bo_nho_nhat.md`.

**FR_007 — IT業務編 màn hình Unit gộp (bản rút gọn)**: dữ liệu audio cắt sẵn theo FR gốc (`segments_data.json` + 213 mp3 + `segment_reading_audio.py`) **không tồn tại trong repo** (tạo ở 1 session Cowork riêng, chưa từng commit) — hỏi lại PM, PM chọn bỏ hẳn bước cắt audio, dùng nguyên file track thật. `gyoumuTrackList()`/`gyoumuTrackDetail()`/`gyoumuReadingMode()`/`gyoumuReadingFinish()` cũ bị xóa hẳn (không giữ dead code), thay bằng 1 hàm `gyoumuUnitScreen(chapter,unit)`: accordion "🎧 Luyện nghe" (mở đúng 1 track) + tab "🎤 Luyện đọc câu" (mỗi câu vẫn có nút 🔊 TTS mẫu như cũ, cộng thêm nút "🎧 Nghe cả đoạn hội thoại" phát nguyên track qua `gyoumuTrackAudioSrc()`). **Bug thật bắt được lúc test**: bản đầu dùng 1 hàm `renderAll()` chung cho cả 2 phần → bấm "Câu tiếp theo" ở phần đọc vô tình rebuild luôn `<audio>` của Player đang mở ở phần nghe, làm mất vị trí đang phát — vi phạm đúng yêu cầu "2 phần độc lập trạng thái" của FR. Sửa bằng 2 hàm `renderListen()`/`renderRead()` độc lập, mỗi hàm chỉ rebuild `<div>` con của riêng nó (`#gyListenWrap`/`#gyReadWrap`). Đã verify lại qua `python3 -m http.server` cục bộ (không dùng `file://` trần — pane preview mở `file://` dạng snapshot `data:` URL, tắt hẳn `localStorage`, che mất nguyên nhân thật của bug).

**Redesign dashboard — bảng màu "giấy washi" + trang chủ hero**: làm trong 1 worktree khác (`japanese-learning-app-handover-e2f2a1`, cùng nhánh gốc `claude/fr-008-012-phase2-7244b9`) theo yêu cầu PM "đối ứng như demo khảo sát" (1 artifact Claude Design riêng PM từng xem lúc khảo sát Phase 2, kiến trúc dữ liệu khác hẳn Kokoro — chỉ lấy bảng màu/bố cục "hero", **không** lấy Google Fonts vì vi phạm nguyên tắc offline). Đổi toàn bộ biến `:root` sang tông ấm (`--brand:#1F5673` thay `#2563eb`, xem đủ ở `CLAUDE.md` mục UI) + viết lại `home()` thành 1 "hero card" hiện số thẻ đến hạn ôn hôm nay + CTA "Bắt đầu ôn tập ngay". Ban đầu **chưa PM duyệt** (câu hỏi treo: đổi màu toàn app hay chỉ trang chủ) — PM đã trả lời **toàn app**, nên gộp thẳng bản redesign này (qua `git apply` từ diff của worktree kia — 2 việc không đụng cùng vùng code, áp patch sạch, không conflict) vào cùng worktree đang code FR_006/007, verify lại cả 3 tính năng cùng hoạt động đúng.

**Việc thêm sau khi PM xem thử redesign (cùng ngày)**: PM chỉ ra 4 chỗ bản redesign bỏ sót — `.backbtn`/`.settings-btn` (2 nút xuất hiện ở mọi màn hình), `.mic-banner`, `.tts-ok`+`.tc-badge` — vẫn dùng hex cứng của tông xanh dương cũ do không đi qua biến `:root`. Đã sửa cả 4 sang tái dùng đúng token đã có (`var(--soft)`/`var(--brand)`/`var(--warn)`/`var(--good)`), không bịa hex mới. PM cũng yêu cầu đồng bộ 2 chi tiết ở **mọi mode học IT専門** (trước đây chỉ Flashcard/Yêu thích có): nhãn "Bộ N (start-end) · vị trí/tổng" ở header (`curDeckRangeLabel()`) và tag "category · #id" trên mỗi từ — đã thêm cho Quiz/Cloze/Luyện nghe/Luyện nói/Phản xạ (Phản xạ chỉ hiện tag ở pha hiện đáp án, không hiện ở pha đoán để khỏi lộ gợi ý). Xem đủ ở `CLAUDE.md` mục UI + mục "7 Mode học".

Cả 3 việc trên (FR_006, FR_007, redesign + 2 phần bổ sung) **đã build + verify (`node --check`, đếm 667 từ/38 track) + test tay qua Browser pane, sau đó đã commit + push + build APK** — xem mục 4.11/4.12.

### 4.11. Rà soát thư mục project chính + cập nhật từ điển 663 từ (2026-09-12, khuya)

Trước khi merge nhánh worktree vào `main`, kiểm tra `git status` tại chính thư mục project (`100_日本語/`, không phải worktree) thì phát hiện **nó KHÔNG sạch** — có việc dở dang từ nhiều tuần trước, chưa từng commit bởi bất kỳ phiên nào:

- Bản sửa nhỏ, cũ của `app_template.html`/`CLAUDE.md`/`.gitignore`/2 file gradle — đã kiểm tra kỹ (`git diff` so với nhánh worktree `a6711ad`), xác nhận **hoàn toàn trùng hoặc cũ hơn**, an toàn để bỏ (`git checkout --`).
- Nhiều file/thư mục **có giá trị thật, chưa ai lưu lại**: `02_IT_Gyoumuhen/reading_segments/` (217 mp3 + `segments_data.json` — **chính là dữ liệu audio cắt sẵn của FR_007** mà trước đó tưởng "không có trong repo"! Hóa ra nó nằm sẵn ở đây, chỉ chưa commit nên không worktree nào thấy được), `01_Build_App/_app_build/segment_reading_audio.py` (script tạo ra dữ liệu trên), `_KHAO_SAT/` (tài liệu khảo sát + kế hoạch gộp app, 2026-09-11), `05_json/` (2 bản xuất tiến độ thật của PM sáng cùng ngày). Cộng thêm 3 file `.tmp` rác cũ (tháng 7) và các file FR trùng lặp ở gốc `_feature_requests/` (đã có bản chính thức trong `done/`) — dọn bỏ.

**Quan trọng nhất: `日本語の辞書.xlsx` trong thư mục chính có 1 chỉnh sửa thật, rất gần đây của PM** — phát hiện nhờ thấy file khóa tạm `~$日本語の辞書.xlsx` (đang mở trong Excel). Đợi PM lưu file, đọc lại 2 lần vì số từ đổi liên tục (666 → 663) tới khi PM xác nhận lưu xong. Nội dung sửa: xóa 1 mục nháp (`N✙用`) + gọn chú thích ngoặc của 4 từ (VD `（に）書き込む`→`書き込む`, `紐づく（紐づける）`→`紐づく`). Đã sao lưu file này ra ngoài **trước khi** đụng vào bất cứ thứ gì khác trong thư mục chính — nguyên tắc chung: không bao giờ ghi đè/loại bỏ 1 file đang có sửa đổi thật của PM mà chưa sao lưu trước.

Trình tự xử lý an toàn: sao lưu xlsx thật → bỏ các bản sửa cũ/trùng đã xác nhận dư thừa → fast-forward `main` lên đúng bản đầy đủ (`a6711ad`) → đưa xlsx thật trở lại → `build_app.py` chạy lại, đọc kỹ báo cáo sổ khóa: **659 từ giữ nguyên id, 3 từ đổi tên được nhận diện đúng giữ nguyên id, 1 từ** (`（お）気軽（な）`→`お気軽`, xóa cả 2 ngoặc cùng lúc nên thuật toán nhận-diện-đổi-tên không khớp được) **nhận id mới, id cũ bị khóa vĩnh viễn** — đúng theo thiết kế an toàn của `_id_lock.json` (`CLAUDE.md` quy tắc #7), không phải lỗi. Verify `node --check` + đếm đúng 663 từ, rồi commit toàn bộ (từ điển, HTML build lại, `_id_lock.json`, dữ liệu FR_007, `_KHAO_SAT/`) — commit `0c2cf0f`. Thêm `05_json/` vào `.gitignore` (dữ liệu cá nhân, không phải source code) thay vì commit.

2 file `Ban_dich_Mail_Request_Spec.md`/`Ban_dich_WRS2_System_Concept.md` ở gốc thư mục **không liên quan tới Kokoro** — để nguyên, không commit, không xóa.

### 4.12. Push GitHub + build APK debug mới (2026-09-12, khuya)

Push `main` lên GitHub thành công — commit `0c2cf0f` rồi `c69b48b`. **Repo đã đổi tên**: `Nin-Min2231/Lading_page-VS` → `Nin-Min2231/Nihongo_App` (khớp đúng backlog cũ "đổi tên repo cho khớp tên dự án" — có vẻ đã đổi từ phía GitHub, không phải phiên này làm). Push vẫn qua được nhờ GitHub tự redirect; chưa cập nhật lại URL remote local (lệnh `git remote set-url` bị hệ thống an toàn của Claude Code chặn, không quan trọng — chỉ là cosmetic).

Chạy đủ 6 bước nghiệm thu trong `done/_PHASE2_GOI_CAI_MOT_LAN.md` qua Browser pane + `python3 -m http.server` cục bộ (không dùng `file://` trần vì tắt `localStorage`, che mất lỗi thật — xem mục 4.10): build sạch 663 từ, `node --check` pass, 0 lỗi console, chạy hết cả 7 mode tới màn Hoàn thành (dùng JS gọi thẳng hàm mode để nhanh, không cần click tay từng bước), lưới Bộ đúng 4 icon + xanh lá khi xong, xuất/nhập tiến độ so sánh khớp số liệu (Từ đã thuộc/Tổng lượt ôn/Streak), khổ 375px không tràn ngang ở 4 màn hình (home/dashboard/quiz/gyoumu-unit).

**Phát hiện + fix 1 lỗi thật lúc build APK**: `03_Android_App/package.json` đã khai `@capacitor/filesystem` + `@capacitor/share` (dùng cho xuất/nhập tiến độ FR_011) từ lâu, nhưng **`npm install` chưa từng chạy lại thật** sau đó — `node_modules/@capacitor/` thiếu hẳn 2 gói này. `npx cap sync` chỉ báo đúng 2/4 plugin, không cảnh báo gì thêm. Nghĩa là **mọi bản APK build trước phiên này đều thiếu tính năng xuất/nhập tiến độ ra file thật**, âm thầm rơi về đường lùi textarea, không có dấu hiệu lỗi nào trong log build. Đã `npm install` lại (thêm 3 gói), sync lại xác nhận đủ 4 plugin, build lại và verify bằng cách quét bytecode `.dex` trong APK: cả 4 class plugin (`FilesystemPlugin`, `SharePlugin`, `TextToSpeechPlugin`, speech-recognition) đều có mặt. Verify thêm: quyền `RECORD_AUDIO` có trong manifest đã merge, 38 file audio IT業務編 đóng gói đủ, `VOCAB` trong `index.html` nhúng đúng 663 từ.

APK copy ra `03_Android_App/Kokoro_Nihongo.apk`, gửi PM. Vẫn `versionCode 1`/`versionName "1.0"` (chưa bump — theo mục 5.4). **Bài học cho lần sau: mỗi khi thêm plugin Capacitor mới vào `package.json`, luôn đối chiếu số lượng plugin `npx cap sync` báo với số dòng dependency Capacitor trong `package.json` — lệch số là phải `npm install` lại trước khi build, `cap sync` không tự cảnh báo thiếu.**

### 4.13. Dọn dẹp git worktree/nhánh thừa (2026-09-12, khuya)

Dự án từng có tới 3 worktree cùng lúc (`read-handover-file-d24408`, `japanese-learning-app-handover-e2f2a1`, `khao-sat-app-request-...`) do nhiều phiên Claude làm việc song song không biết tới nhau — đây chính là nguyên nhân của vài lần hiểu nhầm "code bị mất"/"màn hình không giống" trong ngày 2026-09-12 (xem mục 4.10, 4.11). Sau khi mọi việc đã gộp hết vào `main`, đã xác nhận **từng nhánh/worktree không còn commit riêng nào chưa nằm trong `main`** (dùng `git merge-base --is-ancestor`) rồi mới xóa: 4 nhánh git thừa (`fr-008-012-phase2-7244b9`, `japanese-learning-app-handover-e2f2a1`, `khao-sat-app-request-0bd6bf`, `read-handover-file-d7c3c0` — 2 nhánh cuối trùng y hệt nội dung đã có trong `main`, khác chỉ ở hash commit, verify bằng `git diff` rỗng) và 1 thư mục worktree vật lý (folder kia ban đầu bị khóa bởi 1 phiên Claude khác đang mở — PM đóng phiên đó xong mới xóa được thật). **Còn đúng 1 worktree** (`read-handover-file-d7c3c0`, nơi phiên chat tạo/sửa tài liệu này chạy) — PM tự xóa tay sau khi phiên kết thúc.

**Bài học ghi lại rõ để tránh lặp lại:** trước khi tin bất kỳ mô tả "trạng thái hiện tại" nào (kể cả ảnh chụp màn hình, hay tài liệu handover khác), luôn chạy `git worktree list` — dự án này đã 3 lần trong 1 ngày có việc thật, có giá trị (dữ liệu FR_007, bản redesign PM duyệt, bản sửa từ điển) nằm âm thầm ở 1 nơi không phải chỗ đang được kiểm tra.

### 4.14. 4 yêu cầu mới của PM (2026-09-13) — Flashcard, Điền từ/Phản xạ, trang chủ, Cài đặt

Phiên chat này chạy trong 1 worktree mới (`handover-file-review-9bd2f7`, nhánh `claude/handover-file-review-9bd2f7`), tách biệt với worktree `read-handover-file-d7c3c0` nhắc ở mục 4.13 — 2 worktree khác nhau, đừng nhầm. PM đưa trực tiếp trong chat 4 yêu cầu (không viết file FR), đều sửa trong `app_template.html`:

1. **Flashcard — checkbox "Học từ đã nhớ"**: thêm ngay trên khung thẻ, mặc định tắt. Bật lên thì các từ đã đánh dấu "Đã nhớ" quay lại vào lượt học (nút "Đã nhớ" của chúng tự hiện sẵn trạng thái ✅ — tái dùng `isMastered()` có sẵn, không phải logic mới). Biến `flashIncludeMastered` (module-level, không lưu `localStorage`) — **bug nhỏ bắt được lúc tự kiểm tra lại**: ban đầu quên reset biến này về `false` mỗi khi vào lại Flashcard từ đầu (qua nút mode hoặc CTA trang chủ), nên bật 1 lần là dính luôn suốt phiên trình duyệt dù thoát ra vào lại — đã fix bằng cách reset ở đúng 2 điểm "bắt đầu phiên mới" (`startMode('flash')` và CTA `dashStart` ở `home()`), còn các đường "tiếp tục phiên đang chạy" (tự bật/tắt checkbox, hoặc xem "Từ đã thuộc" rồi quay lại) thì vẫn giữ nguyên trạng thái, không bị reset. `.card` giảm `min-height` 230→186px để chừa chỗ.
2. **Điền từ / Phản xạ — hỏi về việc "dữ liệu sai Bộ"**: PM chỉ ra ví dụ thẻ tag `#228` xuất hiện trong khi header ghi "Bộ 9 (201-225)", nghi ngờ là bug lấy sai dữ liệu theo Bộ. **Đã verify bằng cách đọc thẳng `VOCAB` trong `Kokoro_Nihongo.html`: không phải bug** — dữ liệu bên trong 1 Bộ vẫn đúng 100% theo vị trí/STT, chỉ là nhãn header hiển thị vị trí còn tag hiển thị `#id` cố định theo `_id_lock.json` (2 hệ số khác nhau, xem `CLAUDE.md` quy tắc #7 — đã bổ sung thêm đoạn giải thích đúng ví dụ `#228` này vào đó để không ai hiểu nhầm lại). Không đụng gì vào `deckPool()`/`splitDecksStrict()`.
3. **Điền từ / Phản xạ — thêm icon vào lưới Bộ**: PM xác nhận (qua `AskUserQuestion`, chọn phương án "thêm icon + tính vào hoàn thành") chấp nhận đánh đổi mà `CLAUDE.md` quy tắc #8 (bản cũ) từng cố tình tránh — lưới Bộ giờ đủ **6 icon** 🗂️✍️🧩🎧🎤⚡, và 1 Bộ chỉ xanh lá khi đủ cả 6 mode (trước là 4). `autoFocusDeckIndex()` (FR_006) cũng cập nhật theo. **Hệ quả đã báo trước và PM đồng ý**: mọi Bộ đã hoàn thành trước đây (kể cả tiến độ thật PM có trên điện thoại từ bản APK 2026-09-12) sẽ tạm mất màu xanh cho tới khi học lại Điền từ + Phản xạ cho từng Bộ — dữ liệu `deckDone` cũ không mất, chỉ là điều kiện xét lại nghiêm hơn.
4. **Trang chủ — hero đổi số chính + CTA**: số lớn ở hero chuyển từ "số thẻ đến hạn hôm nay" sang **số ngày học liên tục** (`store.stats.streak`). Thêm hàm `streakGapDays()` — nếu có khoảng đứt quãng trước hôm nay (dựa `stats.lastDay` so với hôm nay), số hiển thị về 0 kèm cảnh báo "Bạn đã bỏ lỡ N ngày..." (tính trực tiếp lúc render, không cần đợi học lại mới cập nhật). Nút CTA "Bắt đầu ôn tập ngay" bỏ nhánh due>0/=0 cũ, giờ luôn tính `autoFocusDeckIndex()` rồi vào thẳng `flashMode(deckPool())` của đúng Bộ đang học dở/tiếp theo (trước đó vào `flashMode(VOCAB)` học due-toàn-bộ không theo Bộ nào). Lưới 3 ô phụ đổi thành Từ đã thuộc/Cần ôn hôm nay/Track đã nghe (bỏ ô Streak trùng với số hero).
5. **Cài đặt — sticky header + đổi thứ tự**: tách `.settings-panel` thành `.settings-head` (title+✕, `position:sticky`) và `.settings-body` (phần còn lại, cuộn bên trong panel) — trước đó cuộn xuống là mất luôn tiêu đề/nút đóng. Khối "💾 Tiến độ học" chuyển lên đầu panel theo yêu cầu PM.

**Verify đã chạy**: `node --check` pass, đếm đúng 663 từ, không lỗi console; test tay qua `python3 -m http.server` + Browser pane cho cả 5 việc trên bằng cách gọi thẳng hàm JS (nhanh hơn click tay) — bao gồm chạy thật cả 6 mode học cho 1 Bộ để xác nhận lưới Bộ chuyển xanh lá đúng lúc đủ 6 icon, và test riêng việc reset checkbox giữa các lần vào Flashcard.

**Đã commit + fast-forward `main`**: commit `f95d252` trong worktree `handover-file-review-9bd2f7`, sau đó `git merge --ff-only` từ chính thư mục project (`main` đang sạch nên fast-forward không conflict). `main` local giờ ở `f95d252`, **chưa push lên GitHub** (`origin/main` vẫn ở `71b266d`).

**Đã build lại APK debug** theo đúng quy trình mục 5.2 (copy HTML mới vào `www/index.html`, audio đã đủ 38 file từ trước không cần copy lại, `npx cap sync android` xác nhận đủ 4 plugin, `gradlew assembleDebug` — BUILD SUCCESSFUL). Verify bằng cách đọc thẳng file trong APK (`zipfile` + `aapt dump permissions`/`badging`): 663 từ, 38 audio, 4 class plugin (`TextToSpeechPlugin`/`FilesystemPlugin`/`SharePlugin`/speech-recognition) có trong `.dex`, quyền `RECORD_AUDIO` có khai báo, `versionCode 1`/`versionName "1.0"` (chưa bump). APK ở `03_Android_App/Kokoro_Nihongo.apk`. **CHƯA cài/test trên điện thoại thật.**

**Dọn worktree tiếp** (nối mục 4.13): PM tự tay xóa được worktree thừa `read-handover-file-d7c3c0` (git đã gỡ đăng ký trước đó trong phiên này, nhưng bản thân folder trên ổ đĩa bị 1 tiến trình khác khóa không xóa được qua Bash/PowerShell — không xác định được tiến trình nào vì máy không có sẵn `handle.exe`; PM đóng cửa sổ liên quan rồi tự xóa được). **Worktree đang hoạt động của phiên này** (`handover-file-review-9bd2f7`) đã fully merge vào `main`, không còn gì rời rạc — PM sẽ tự xóa tay sau khi đóng phiên chat này (không xóa giữa chừng vì đây chính là thư mục làm việc của phiên đang chạy).

### 4.15. PM xác nhận test thật OK → bump version 0.1 + thêm module シャドウイング (FR_013) (2026-09-22)

Phiên chat mới, vẫn chạy trong đúng thư mục worktree `handover-file-review-9bd2f7` (folder PM chưa xóa như dự định ở mục 4.14) nhưng **git đã gán 1 branch khác** cho worktree này: `claude/read-handover-file-b582d2` thay vì `claude/handover-file-review-9bd2f7` cũ. Cả 2 branch cùng trỏ đúng 1 commit `aace5f8` như `main`/`origin/main` (không có gì phân kỳ) — chỉ là tên khác, không phải lỗi. **Bài học lặp lại của mục 4.13/6:** đầu phiên đã chạy `git worktree list`/`git branch -a -v` để xác nhận, và phát hiện thêm 1 điều tài liệu cũ ghi sai: banner + mục 4.14/6 nói `main` "chưa push", nhưng `git log origin/main..main` rỗng thật — **đã push xong từ trước**, chỉ là dòng ghi chú không được cập nhật lại sau khi push.

**Việc 1 — Bump version APK (đã đủ điều kiện theo mục 5.4):** PM báo đã cài và test bản APK gói 2026-09-13 (`aace5f8`, 4 việc mục 4.14) trên điện thoại thật, ổn. Sửa `android/app/build.gradle`: `versionCode 1→2`, `versionName "1.0"→"0.1"` (theo đúng số PM đã chốt trước đó ở mục 5.4/backlog — versionName đi xuống về mặt số nhưng là quy ước cố ý, không phải lỗi đánh máy). Worktree này thiếu sẵn `node_modules/`, `www/`, `android/local.properties` (đều gitignore, chưa từng chạy build ở đây) — chạy `npm install` (416 gói), tạo lại `www/index.html`+`www/audio/` từ `Kokoro_Nihongo.html`/`audio/` hiện có, tạo `local.properties` trỏ `sdk.dir=D:\Android\Sdk`, `npx cap sync android` xác nhận đủ 4 plugin, `gradlew assembleDebug` (JAVA_HOME/GRADLE_USER_HOME trỏ `D:\Android\jdk21`/`D:\Android\gradle-home`) — BUILD SUCCESSFUL. Verify bằng `aapt dump badging` (versionCode='2' versionName='0.1', `RECORD_AUDIO` có) + quét `.dex` (đủ 4 class plugin) + đọc thẳng `VOCAB` trong APK (663 từ) + đếm audio (38 file). APK ở `03_Android_App/Kokoro_Nihongo.apk`. Chỉ `android/app/build.gradle` là thay đổi thật sự (2 dòng version) — chưa commit, hỏi PM trước khi commit theo đúng quy ước mặc định của dự án (mục 7 checklist).

**Việc 2 — FR_013, module thứ 3 シャドウイング:** PM đưa file `06_ Shadowing_Jokyu/FR_013_shadowing_module.md` (spec rất chi tiết, tự PM/1 phiên khác đã chuẩn bị sẵn kèm dữ liệu — xem mục 9 của chính file FR: `Shadowing_Data.json` 8 Unit/22 section/62 track/240 đoạn/1.225 lượt thoại đã OCR + cắt mốc thời gian tự động bằng `ffmpeg silencedetect`, đối chiếu 100% số đoạn/lượt Nhật-Việt). FR tự flag 4 điểm "cần PM quyết trước khi code" (mục 10) — xử lý: điểm dung lượng audio (impact Cao, +46MB → APK ~115MB) **để ngỏ, chưa build APK để đo số thật** thay vì đoán trước; 3 điểm còn lại (mốc "đã nghe" = chạm `seg.end`, không làm mode nghe+nói đồng thời, thêm thanh tiến độ cho Unit 8) làm theo đúng đề xuất có sẵn trong FR vì khớp pattern IT業務編 đã có.

Code theo đúng khuôn mẫu `gyoumuUnitScreen()` (FR_007) — xem mô tả kiến trúc ở `CLAUDE.md` mục "3 Module"/"FR_013". Điểm khác biệt chính so với IT業務編: thêm 1 lớp Section dùng chung cho cả 2 phần (đổi Section = dừng audio + vẽ lại cả 3 khối), và audio phát theo **khoảng thời gian trong file track thật** (`audioEl.currentTime=seg.start` rồi tự dừng ở `seg.end` qua `timeupdate`+`ended`) thay vì file mp3 cắt sẵn — không tạo 240 file audio rời, giữ APK nhẹ hơn và sửa mốc cắt chỉ cần sửa JSON. Toggle "Hiện script"/"Hiện nghĩa" dùng `classList.toggle('hidden', ...)` trực tiếp (không re-render) để không làm mất vị trí audio đang mở — giữ đúng nguyên tắc FR_007 mục 6 nhưng áp dụng thêm cho cả tương tác *bên trong* 1 khối, không chỉ giữa 2 khối.

**Verify đã chạy** (qua Browser pane, `python3 -m http.server`, không dùng `file://`): build sạch 663 từ + 38 track + **240 đoạn shadowing**, `node --check` pass, dashboard hiện đúng 8 Unit với số track/đoạn khớp dữ liệu thật (điểm 9.5 của FR có 1 dòng sai — Unit 6 thực tế 30 đoạn chứ không phải 27 như bảng ghi, không ảnh hưởng code vì đọc thẳng JSON không hardcode); mở Unit 1 đúng cấu trúc Section 1(中級)/2(上級), phát thật ~15s 1 đoạn (không seek bằng JS vì môi trường Browser pane seek `currentTime` không ổn định/bị reset) xác nhận **tự dừng đúng ở `seg.end`** + ghi `sdStore.listened['1-02-1']` + `bumpStreak()` (không cộng `stats.studied`, đúng yêu cầu); đổi Section dừng audio + reset đúng cả 2 phần; toggle script/nghĩa giữ nguyên trạng thái audio đang mở (verify bằng đọc `currentTime` trước/sau không đổi); Luyện nói chạy hết 5 lượt ra màn "Xong đoạn này!" + ghi đúng `sdStore.spoken`; Unit 8 (đoạn dài, có `title`) hiện đúng + thanh tiến độ; export/import có `kokoro_shadow_v1`, import file cũ thiếu key này không xóa dữ liệu shadow đang có (test trực tiếp cả 2 chiều); khổ 375px không tràn ngang (chụp màn hình xác nhận); gọi lại `homeDashboard()`/`gyoumuDashboard()`/`home()` xác nhận 2 module cũ không bị ảnh hưởng; 0 lỗi console suốt quá trình test.

Đã cập nhật `CLAUDE.md` (banner, cấu trúc thư mục, "3 Module", mục FR_013) và file này. Đã copy `06_ Shadowing_Jokyu/FR_013_shadowing_module.md` vào `01_Build_App/_feature_requests/done/` cho khớp quy ước (giữ nguyên bản gốc, không xóa/di chuyển). **Dữ liệu `06_ Shadowing_Jokyu/` (JSON + xlsx + 46MB audio) chưa commit** — cần PM xác nhận trước khi `git add` (tương tự cách `02_IT_Gyoumuhen/AudioCD/` đã được commit làm nguồn audio chính thức, xem mục 6) vì đây là nội dung giáo trình có bản quyền, chỉ dùng nội bộ. Thư mục con `01_document/`/`02_Claude outputs/` trong `06_ Shadowing_Jokyu/` (tài liệu làm việc lúc chuẩn bị dữ liệu, không phải input của `build_app.py`) chưa được copy vào worktree — để PM quyết có cần giữ lại không. **Chưa build APK cho module này** — chờ quyết định về dung lượng audio, và theo đúng thói quen luôn test kỹ trình duyệt trước khi build APK.

### 4.16. PM test bản PC → redesign UI シャドウイング (2026-09-22, cùng ngày)

PM mở thẳng file HTML build ở mục 4.15 bằng trình duyệt riêng (theo đúng cách dùng app ở chế độ web — không qua server), chụp màn hình kèm góp ý cụ thể. 4 điểm chính, đã sửa hết trong `app_template.html`:

1. **Dashboard (`shadowDashboard()`):** badge "N/M đoạn đã nghe" trước đè lên tiêu đề Unit dài (do `.tc-badge` định vị `position:absolute` dùng chung với các màn khác) — chuyển sang badge riêng `.sd-unit-progress` nằm trong luồng bình thường, ngay dưới icon (không đụng `.tc-badge` gốc để không ảnh hưởng màn khác đang dùng nó). Thêm 3 màu nền thẻ Unit theo % đã nghe: trắng (0%) / vàng nhạt `.sd-partial` (một phần) / xanh nhạt `.sd-done` (100%) — hex tint pha từ `--warn`/`--good`, không thêm biến `:root` mới, đặt CSS trước rule `.gy-track-row.open` để trạng thái đang mở luôn ưu tiên hiển thị hơn tint (giống nguyên tắc deck-card `.on` > `.done` đã có).
2. **Màn Unit (`shadowUnitScreen()`) — 4 việc:**
   - Toàn bộ label/nút chuyển sang tiếng Nhật (`🎧 聞き取り`, `🔁 リピート再生`, `👁 スクリプトを表示`, `🇻🇳 訳を表示`, `🐢 ゆっくり`, `🎧 実際の音声を聞く`, `🎤 発音練習`, `次へ →`, thông báo lỗi/feedback mic...) — **khác quy ước chung "UI tiếng Việt"** của cả app, áp dụng riêng cho đúng màn này theo yêu cầu PM. Nhãn cấu trúc "Đoạn N"/"Track N"/"Section N" giữ nguyên (không phải UI hành động).
   - Mỗi "Đoạn N" thêm badge `(đã-ghi/tổng · điểm-TB点)`, và mỗi lượt thoại trong tab luyện nói thêm badge điểm riêng (`#sdLineScoreTag`, cập nhật ngay bằng DOM trực tiếp sau khi chấm — không rebuild cả khối để không mất thông báo 🌟/👍/💪 vừa hiện). **Đổi hẳn schema lưu điểm:** trước là `{bestAvg, attempts}` gộp cả đoạn, giờ `{lines:{lineIndex:{score,attempts}}}` lưu **điểm LẦN GHI ÂM GẦN NHẤT của từng lượt thoại riêng** (PM cho ví dụ rõ: đọc 2 lần 80 rồi 72 → lấy 72, không lấy điểm cao 80) — `shadowSegStats()` tính điểm trung bình đoạn = TB của các điểm-gần-nhất đã có. Ngưỡng màu cho các badge điểm này (`shadowScoreColor()`): <60 đỏ (`--bad`) / 60-90 vàng (`--warn`) / >90 xanh (`--good`) — **số khác** ngưỡng chấm mic chung ≥90/≥51 đang dùng ở IT専門/IT業務編 (không đổi 2 chỗ đó, chỉ đổi phần hiển thị mới trong Shadowing để không tự mâu thuẫn màu ngay trong cùng 1 màn hình).
   - **Gộp hẳn 🎧 Luyện nghe + 🎤 Luyện nói vào 1 accordion mỗi Đoạn**, thay vì 2 khối tách rời (nghe ở trên, nói ở dưới với dropdown chọn đoạn riêng) của bản đầu — theo đúng đề xuất "1 tab trong mỗi đoạn" PM gợi ý, chọn phương án tab (🎧 聞き取り / 🎤 シャドウイング) vì phù hợp màn hẹp điện thoại hơn cách khác (ví dụ 2 cột). Vì giờ chỉ 1 đoạn mở + 1 tab hiện tại 1 thời điểm, không cần 3 khối render độc lập như bản đầu nữa — rút gọn còn 2 (`renderSectionTabs()`/`renderList()`), đổi Section/đổi tab/đổi đoạn đều `stopAllShadowAudio()` trước khi vẽ lại (đơn giản hơn, không mất gì vì giờ không còn 2 khu vực cùng hiển thị song song nữa).
   - Thêm 2 màu nền cho mỗi hàng Đoạn theo % **đã luyện nói** (khác trục dữ liệu với màu Unit ở mục 1, vốn theo % đã nghe): trắng/`.sd-partial`/`.sd-done`, tái dùng đúng 2 class đã thêm ở mục 1.

**Verify lại sau redesign:** `node --check` pass, build vẫn 663 từ + 38 track + 240 đoạn; test qua Browser pane — dashboard 3 màu đúng theo % nghe (đánh dấu tay Unit 1 nghe 1 đoạn/38 → vàng nhạt, Unit 4 nghe đủ 23/23 → xanh nhạt); mở Unit 1 vẫn phát audio thật đúng khoảng `[start,end]` rồi tự dừng + ghi `listened` (chờ thật ~13s, không seek bằng JS — môi trường Browser pane seek `currentTime` không ổn định, đã ghi nhận từ mục 4.15); đổi tab nghe↔nói dừng đúng audio đang phát (`currentShadowAudio.paused===true` sau khi đổi); mô phỏng 2 lần ghi 80 rồi 72 cho cùng 1 lượt → `shadowLineScore()` trả đúng 72 (không phải 80); màn hoàn thành hiện đúng điểm TB theo đúng logic mới; ngưỡng màu đúng cả 5 mốc test (59/60/72/91/95); khổ 375px chụp ảnh xác nhận không tràn ngang, badge/tag đọc rõ; gọi lại `homeDashboard()`/`gyoumuDashboard()`/`home()` không bị ảnh hưởng; 0 lỗi console suốt quá trình.

**Còn lại:** vẫn đúng các điểm mở của mục 4.15 (dữ liệu `06_ Shadowing_Jokyu/` chưa commit theo yêu cầu PM, quyết định bitrate audio để sau khi PM test xong rồi build APK đo số thật). Chưa commit gì của cả redesign này.

### 4.17. PM test tiếp bản PC (vòng 2) → build APK đo dung lượng thật (2026-09-22, cùng ngày)

3 việc PM góp ý tiếp sau khi xem lại: (1) Nhật hoá nốt phần còn sót tiếng Việt ở cả 2 màn (dashboard: "Đoạn"→"段落", "Đã nghe"→"聴取済み"; màn Unit: "Đoạn N"→"段落 N"); (2) gọn layout màn Unit — thêm 2 class riêng `.sd-seg-row`/`.sd-seg-body` (padding/margin nhỏ hơn hẳn `.topic-card`/`.player-card`/`.sent-card` gốc, ghép thêm class chứ không sửa class gốc vì IT業務編 vẫn dùng chung 3 class đó) để 1 màn hình điện thoại thấy được nhiều đoạn hơn; (3) dời dòng đếm "セリフ N/M" từ 1 dòng riêng lên cùng hàng với 2 nút tab (dùng `margin-left:auto` đẩy sang phải), bớt 1 dòng + margin của nó. Verify lại qua Browser pane (375px): xác nhận cả 3 đúng, không lỗi console, 2 module cũ không ảnh hưởng.

Sau đó PM yêu cầu build luôn APK để test trên điện thoại thật (đã test đủ trên PC). Quy trình đúng mục 5.2: copy `index.html` + `audio/shadowing/*.mp3` (62 file) mới vào `www/`, bump `versionCode 2→3` (**giữ nguyên** `versionName "0.1"` — đây là build thử nghiệm module mới thêm vào, chưa phải mốc ổn định tiếp theo cần đổi tên phiên bản), `npx cap sync android` xác nhận đủ 4 plugin, `gradlew assembleDebug` — BUILD SUCCESSFUL. Verify `aapt dump badging` (versionCode='3' versionName='0.1', RECORD_AUDIO có) + quét `.dex` (đủ 4 class plugin) + đọc thẳng APK: 663 từ, 38 track IT業務編, 8 Unit shadowing, 62 audio shadowing + 38 audio IT業務編 đóng gói đủ.

**Số đo dung lượng thật (điểm còn để ngỏ ở mục 4.15/4.16 giờ đã có số):** APK **~125MB** (từ ~78MB trước khi có Shadowing, tức shadowing cộng thêm ~47MB — đúng như ước tính ban đầu +46MB audio). Quyết định giữ 64kbps hay hạ 48kbps vẫn để PM chốt sau khi cài thử trên điện thoại thật — 125MB không có giới hạn kỹ thuật nào chặn (cài trực tiếp, không qua Play Store), chỉ là vấn đề dung lượng máy/thời gian tải nếu chia sẻ file.

APK ở `03_Android_App/Kokoro_Nihongo.apk`. **CHƯA cài/test trên điện thoại thật.** Nhắc lại quy tắc cài đè, không gỡ app cũ (đang có tiến độ học thật) — xem banner đầu file. Toàn bộ code/data của FR_013 (cả 2 vòng redesign) và bump version lần này **vẫn chưa commit** — dữ liệu `06_ Shadowing_Jokyu/` theo đúng yêu cầu PM là không commit.

### 4.18. PM test APK trên điện thoại thật → 3 việc mới: gọn+Nhật hoá hero, scroll-to-top, redesign IT業務編 (2026-09-23)

PM gửi ảnh chụp màn hình APK **chạy thật trên điện thoại** (thanh trạng thái Android thật, không phải giả lập) — xác nhận bản build mục 4.17 hoạt động tốt trên máy thật, kể cả module シャドウイング mới. Góp ý 3 việc:

**1. Khối hero trang chủ (`home()`) che mất thẻ シャドウイング, phải cuộn mới thấy:** ảnh chụp cho thấy khối "今日の学習" cao chiếm gần hết màn hình điện thoại thật, đẩy thẻ module thứ 3 xuống gần hết viewport. Đã: (a) Nhật hoá toàn bộ text còn tiếng Việt trong hero — nhãn "ngày học liên tục"→"日連続学習中", dòng phụ "541 thẻ IT専門 cần ôn hôm nay..."→"IT専門 復習カード 541枚 · 継続を切らさずに", cảnh báo đứt mạch, nút CTA "Bắt đầu ôn tập ngay →"→"今すぐ復習を始める →", 3 nhãn ô số liệu, link "Xem thống kê chi tiết ›"→"詳しい統計を見る ›" — **ngoại lệ riêng cho khối hero này**, không đổi quy ước UI tiếng Việt chung của app; (b) PM yêu cầu rà soát số liệu thống kê có còn đúng hệ thống mới nhất không — phát hiện khối 3 ô số liệu **thiếu hẳn số liệu シャドウイング** (chỉ có Từ đã thuộc/Cần ôn hôm nay của IT専門 + Track đã nghe của IT業務編) dù đã có module thứ 3 từ mục 4.15 — đề xuất + thêm ô thứ 4 "聴取済み段落" (`Object.keys(sdStore.listened).length`), đổi lưới từ 1 hàng 3 ô sang **2×2**; (c) giảm padding/margin/font-size toàn bộ `.dash-hero`/`.dash-num`/`.dash-cta`/`.dash-metrics`/`.dash-metric` (padding hero 22px→16px, font số chính 52px→40px, margin các khối đều giảm ~30-40%) để cả khối hero + đủ 3 thẻ module hiện gọn hơn, đỡ phải cuộn ngay khi mở app.

**2. Vào lại シャドウイング (hay bất kỳ màn nào) không tự cuộn về đầu trang:** do trước đó cuộn sâu xuống rồi chuyển màn (qua Section khác, hoặc quay lại dashboard), vị trí cuộn cũ bị giữ nguyên vì code chỉ thay `main.innerHTML`, không đụng gì tới scroll. Sửa tận gốc, 1 chỗ duy nhất: thêm `window.scrollTo(0,0)` vào cuối `setHeader()` — hàm này được gọi đầu tiên ở **mọi** hàm render màn hình trong app (home/dashboard/mode học...), nên fix 1 chỗ là khỏi màn nào cũng bị, không chỉ riêng シャドウイング (dù PM chỉ báo cáo thấy rõ ở đó, do đây là màn dài/cuộn nhiều nhất).

**3. Redesign IT業務編 theo đúng mẫu シャドウイング (PM yêu cầu áp dụng "màu sắc theo status, layout nghe+đọc, tính điểm" tương tự):** `gyoumuUnitScreen()` viết lại hoàn toàn theo kiến trúc `shadowUnitScreen()` — mỗi **Track** (thay vì Đoạn, vì IT業務編 không có tầng segment) giờ là 1 accordion duy nhất, mở ra có 2 tab con `🎧 Luyện nghe`/`🎤 Luyện đọc` lồng chung 1 thẻ, thay hẳn kiến trúc FR_007 cũ (2 khối tách rời: accordion nghe phía trên + tab chọn track có transcript luyện đọc riêng phía dưới, độc lập trạng thái mở). Track 9/21 (không transcript) tab Luyện đọc bị khoá (`disabled`) nhưng vẫn nghe được bình thường. Đổi schema điểm `gyStore.read[track]` từ `{bestAvg,attempts}` (điểm trung bình cao nhất từng đạt qua 1 lượt đọc hết track) sang `{lines:{lineIndex:{score,attempts}}}` — **điểm mỗi câu là điểm LẦN GHI ÂM GẦN NHẤT**, đúng quy tắc PM chốt ở mục 4.16 cho シャドウイング, giờ áp dụng luôn cho IT業務編. Thêm badge "(đã đọc/tổng · điểm TB点)" mỗi Track trong danh sách + badge điểm ngay trên từng câu đang luyện, tô màu theo `scoreColorTier()` (đổi tên từ `shadowScoreColor()`, dùng chung cho cả 2 module). 3 màu nền: dashboard (`gyoumuDashboard()`) tô theo % Track **đã nghe** trong Unit (thêm badge "N/M đã nghe" dưới icon, y hệt シャドウイング dashboard); danh sách Track trong Unit tô theo % câu **đã luyện đọc**.

**Dọn code đi kèm (không đổi hành vi, chỉ đổi tên cho rõ nghĩa):** đổi tên các class/hàm dùng chung từ tiền tố `sd-`/`shadow` sang tên trung lập vì giờ IT業務編 dùng lại y hệt: `.sd-partial/.sd-done` → `.tint-partial/.tint-done`, `.sd-unit-iconwrap/.sd-unit-progress` → `.unit-iconwrap/.unit-progress`, `.sd-seg-row/.sd-seg-body` → `.compact-row/.compact-body`, `shadowScoreColor()` → `scoreColorTier()`. Đổi bằng `sed` toàn file, verify lại bằng `node --check` + đếm dữ liệu — không sót chỗ nào.

**Verify đã chạy** (Browser pane, 375px, sau khi `localStorage.clear()` để test sạch): hero gọn hẳn, đủ 3 thẻ module gần như không cần cuộn; chuyển màn (home→シャドウイング dashboard, home→シャドウイング Unit 1) xác nhận `scrollY` về đúng 0 dù trước đó đã cuộn sâu; IT業務編 Unit 2 — Track 2 mở đúng 2 tab, nghe thật audio track (currentTime tăng đúng), đổi tab dừng audio đúng (`currentGyoumuAudio.paused===true`), giả lập ghi 2 lần điểm 80 rồi 72 cho cùng 1 câu → lấy đúng 72 (không lấy 80), badge Track hiện đúng "(1/17 · 72点)" màu vàng (60-90), tint hàng đổi đúng `tint-partial`; Track 9 (không transcript) tab Luyện đọc khoá đúng, click không phản ứng, không tint (total=0); khổ 375px không tràn ngang toàn bộ 3 module; gọi lại `homeDashboard()`/`shadowDashboard()`/`shadowUnitScreen()` xác nhận không bị ảnh hưởng; 0 lỗi console suốt quá trình.

Đã cập nhật `CLAUDE.md` (banner, mục "Kiến trúc App" IT業務編/シャドウイング dùng chung hạ tầng, mục UI hero, mục "3 Module") và file này. **Chưa build APK cho vòng này** — chưa được PM yêu cầu, để dành sau khi PM xác nhận bản PC OK (đúng thói quen). Chưa commit gì thêm.

### 4.19. Nhật hoá nốt phần label/nút còn sót trong IT業務編 (2026-09-23, cùng ngày)

PM gửi ảnh chụp màn Unit IT業務編 (Track 1 · Unit "求人ポスター"), khoanh đỏ 4 chỗ vẫn còn tiếng Việt: 2 nút tab "Luyện nghe"/"Luyện đọc", tag "聞き取り練習 (Luyện nghe)" + dòng "DJ (quảng cáo radio)" trong player, nút "↺ Nghe lại", nút "👁 Hiện transcript" — yêu cầu Nhật hoá label/nút ở cả 2 màn "list unit" (`gyoumuDashboard()`) và "chi tiết unit" (`gyoumuUnitScreen()`), ví dụ mẫu thêm: badge "0/1 đã nghe".

**Điểm khó phát hiện khi làm:** `t.type`/`t.chars` trong `GYOUMU_DATA` (trích từ cột F/G của `IT_Gyoumuhen_AudioCD_Transcript.xlsx`) là **1 chuỗi gộp sẵn** kiểu "聞き取り練習 (Luyện nghe)" hoặc "受付 (Lễ tân) / リー (Li) / 田口 (Taguchi)" ngay từ nguồn — khác với `unitJp`/`unitVi` vốn đã được tách 2 cột riêng. Nếu chỉ strip trắng mọi cụm trong ngoặc sẽ xóa nhầm romaji tên riêng như "(Taguchi)"/"(Li)" (phiên âm đọc tên nhân vật, không phải bản dịch, không phải "tiếng Việt" theo đúng nghĩa yêu cầu). Giải quyết bằng cách nhận diện tiếng Việt qua **dấu tiếng Việt** (regex ký tự có dấu: `àáảã...đ`): viết hàm `stripViGloss(s)` — bóc cụm trong ngoặc `(...)`/`（...）` HOẶC đuôi sau dấu "-" chỉ khi cụm đó chứa ít nhất 1 ký tự có dấu tiếng Việt, giữ nguyên nếu là romaji thuần (không dấu). Test qua 3 trường hợp thật trong data: `"聞き取り練習 (Luyện nghe)"` → `"聞き取り練習"`; `"受付 (Lễ tân) / リー (Li) / 田口 (Taguchi)"` → `"受付 / リー (Li) / 田口 (Taguchi)"` (chỉ bỏ đúng "(Lễ tân)", giữ nguyên 2 tên romaji); `"リー (Li) - độc thoại"` (không có ngoặc ở đuôi, tiếng Việt nằm sau dấu "-") → `"リー (Li)"`. Cả 3 đều đúng.

Danh sách đã dịch: `gyoumuDashboard()` — "Đã nghe"→"聴取済み" (nhãn thống kê + badge "N/M đã nghe"→"N/M 聴取済み"), "Chương N"→"第N章". `gyoumuUnitScreen()` — tab "🎧 Luyện nghe"→"🎧 聞き取り", "🎤 Luyện đọc"→"🎤 音読練習"; `t.type`/`t.chars` qua `stripViGloss()`; "⚠ Không có transcript"→"⚠ スクリプトなし"; nút "↺ Nghe lại"→"↺ もう一度再生"; nút + toggle "👁 Hiện/Ẩn transcript"→"👁 スクリプトを表示/隠す"; toàn bộ text trong tab luyện đọc (thông báo không có transcript/không có câu, màn hoàn thành "Xong buổi đọc!"→"終了！", nút "Đọc lại"→"もう一度練習", "🐢 Chậm"→"🐢 ゆっくり", "🎧 Nghe cả đoạn hội thoại"→"🎧 会話全体を聞く", nút mic "Luyện đọc"→"発音練習", hint/feedback mic, thông báo lỗi audio) — dịch y hệt bộ từ đã dùng cho シャドウイング (mục 4.16) để 2 module nhất quán ngôn ngữ. **Giữ nguyên** (nội dung song ngữ có chủ đích, không phải chrome): tagline header `setHeader('IT業務編','Hội thoại công việc IT · N track',...)`, và `unitJp`/`unitVi` (tên chủ đề Unit) ở cả 2 màn.

**Verify đã chạy**: build sạch 663/38/240, `node --check` pass; test `stripViGloss()` trực tiếp bằng 3 case trên đúng cả 3; mở Unit 1→Track 1 xác nhận tag còn đúng "聞き取り練習"/"DJ" (đã sạch tiếng Việt), 2 tab + toàn bộ nút trong màn nghe đều tiếng Nhật (chụp ảnh 375px đối chiếu lại đúng như ảnh PM khoanh đỏ); mở Unit 2→Track 2 xác nhận chars nhiều tên giữ đúng romaji, chỉ bỏ đúng phần dịch; gọi lại `homeDashboard()`/`shadowDashboard()`/`home()` không ảnh hưởng; 0 lỗi console.

Đã cập nhật `CLAUDE.md` (mục "Kiến trúc App", thêm đoạn giải thích `stripViGloss()`) và file này.

### 4.20. Build APK debug với toàn bộ thay đổi mục 4.18/4.19 (2026-09-25)

PM yêu cầu build APK để test trên điện thoại thật. Quy trình đúng mục 5.2: rebuild HTML sạch (663 từ + 38 track + 240 đoạn shadowing, `node --check` pass) → copy `index.html` mới vào `www/` (audio 2 module không đổi từ mục 4.17, không cần copy lại) → bump `versionCode 3→4` (**giữ nguyên** `versionName "0.1"` — vẫn là build thử nghiệm các thay đổi UI mục 4.18/4.19, chưa phải mốc ổn định mới) → `npx cap sync android` xác nhận đủ 4 plugin → `gradlew assembleDebug` — BUILD SUCCESSFUL (1m44s). Verify: `aapt dump badging` (versionCode='4' versionName='0.1', RECORD_AUDIO có), quét `.dex` (đủ 4 class plugin), đọc thẳng APK (663 từ VOCAB, 38 track GYOUMU, 8 Unit SHADOW, 62 audio shadowing + 38 audio IT業務編 đóng gói đủ).

APK ở `03_Android_App/Kokoro_Nihongo.apk` (~125MB, tương đương bản trước — không thay đổi audio nên dung lượng không đổi nhiều). **CHƯA cài/test trên điện thoại thật.** Nhắc lại quy tắc cài đè, không gỡ app cũ. Toàn bộ code mục 4.18/4.19 + bump version lần này vẫn **chưa commit**.

### 4.21. PM xác nhận test OK trên điện thoại thật → commit + push GitHub (2026-09-25)

PM cài `versionCode 4`/`versionName "0.1"` (mục 4.20) lên điện thoại thật, xác nhận **test OK**, rồi yêu cầu đẩy code lên Git và cập nhật handover.

**Commit:** gộp toàn bộ việc từ mục 4.15 đến 4.20 (module シャドウイング + redesign IT業務編 + Nhật hoá UI + gọn/Nhật hoá hero trang chủ + scroll-to-top + 3 lần bump version) thành **1 commit** — hợp lý vì đây là 1 mạch công việc liên tục, đã test cùng nhau, tách nhỏ theo mốc thời gian bây giờ không có giá trị tham khảo gì thêm. **Cố ý loại trừ `06_ Shadowing_Jokyu/`** khỏi commit (add từng file cụ thể, không dùng `git add -A`) theo đúng yêu cầu PM đã chốt ở mục 4.15. 8 file thay đổi: `CLAUDE.md`, `PROJECT_..._Handover.md`, `Kokoro_Nihongo.html`, `_id_lock.json`, `app_template.html`, `build_app.py`, `build.gradle`, và file mới `01_Build_App/_feature_requests/done/FR_013_shadowing_module.md`. Commit `6fe8245`.

**Push — khác quy trình các phiên trước:** phiên này chạy trong worktree, và system prompt của chính phiên **cấm `cd` vào thư mục gốc của repo** (khác các phiên trước, vốn được fast-forward local `main` từ thư mục project chính rồi mới push — mục 4.13/4.14). Giải quyết bằng cách push **thẳng từ branch của worktree lên `origin/main`**: `git push origin claude/read-handover-file-b582d2:main` — vì `origin/main` trước đó đang đứng đúng ở commit gốc mà worktree này rẽ nhánh ra (`aace5f8`, đã `git fetch` xác nhận trước khi push), nên đây là 1 fast-forward sạch, không có gì phức tạp. Verify lại bằng `git fetch` + `git log origin/main -1` sau khi push: đúng `6fe8245`. **Hệ quả cần biết:** local `main` (ở thư mục project chính `100_日本語/`, ngoài mọi worktree) **vẫn đứng ở `aace5f8`, chưa được fast-forward theo** — khác các lần trước. Phiên sau hoặc chính PM, khi làm việc trực tiếp ở thư mục project chính, chỉ cần `git pull` 1 lần là đồng bộ, không có gì rủi ro (không có commit nào khác ở local `main` cần giữ).

Đã viết lại banner đầu file này (mục "Cập nhật lần cuối") gộp toàn bộ mục 4.15→4.21 thành 1 bản tóm tắt mạch lạc cho phiên chat mới đọc nhanh, và cập nhật mục 6 (Git & GitHub) cho khớp cách push mới + nhắc lại rõ quy tắc không commit `06_ Shadowing_Jokyu/`.

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
cd ../../03_Android_App
npx cap sync android
# ⚠ BẮT BUỘC đối chiếu: log trên phải liệt kê ĐỦ số plugin bằng số dòng Capacitor
# trong package.json (hiện là 4: text-to-speech, filesystem, share, speech-recognition).
# Thiếu plugin nào = npm install chưa cài nó thật (đã xảy ra thật 2026-09-12, mục 4.12
# — package.json khai đủ nhưng node_modules thiếu, cap sync KHÔNG tự báo lỗi).
# Nếu thiếu: chạy `npm install` rồi `npx cap sync android` lại trước khi build.

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
Đã bump lên bản chính thức đầu tiên **`versionCode=2`/`versionName="0.1"`** trong `android/app/build.gradle` (2026-09-22, mục 4.15) — PM đã xác nhận test ổn trên điện thoại thật với bản trước đó (`versionCode=1`/`"1.0"`), đúng điều kiện đã thỏa thuận. Từ giờ mỗi lần build APK thật (không chỉ test nội bộ) nên tăng tiếp `versionCode` (không nhất thiết đổi `versionName` mỗi lần).

### 5.5. Giới hạn môi trường build hiện tại
Máy chạy Claude **không có thiết bị/emulator Android kết nối** — không thể tự cài & bấm thử trên máy thật. Mọi lần build chỉ verify được: build thành công (`gradlew assembleDebug` exit 0), cấu trúc APK đúng (`aapt dump badging`/`unzip -l` kiểm tra permission, assets, plugin registration), và test logic JS bằng cách **mock `window.Capacitor`** trong Chrome preview (giả lập plugin trả kết quả, xác nhận luồng gọi/xử lý lỗi đúng) — KHÔNG thay thế được test thật trên điện thoại (đặc biệt phần mic/TTS native). **Quy trình thực tế đang dùng:** Claude build + verify tối đa có thể → PM tự cài APK lên điện thoại thật để test → báo lại kết quả (kèm ảnh chụp/toast lỗi cụ thể nếu có) → Claude sửa tiếp dựa trên phản hồi đó. Cách này đã từng cần 2-3 vòng lặp cho 1 bug (VD TTS ở FR_005: vòng 1 chỉ thêm timeout/toast — chưa sửa được gốc; vòng 2 mới thêm plugin native TTS và fix thật, nhờ có mã lỗi cụ thể PM báo lại ở vòng 1).

### 5.6. Công cụ tạo app icon
`@capacitor/assets` (devDependency, `npx capacitor-assets generate --android`) — sinh toàn bộ icon launcher (mọi mật độ, adaptive icon foreground/background) + splash screen sáng/tối từ 1 ảnh nguồn vuông duy nhất `03_Android_App/assets/icon.png` (copy từ `04_Image/Logo_Tanpopo.png`, 1024x1024). Muốn đổi logo: thay file `assets/icon.png` rồi chạy lại lệnh trên, sau đó `npx cap sync android` + build lại APK như quy trình mục 5.2.

---

## 6. GIAI ĐOẠN ④ — Git & GitHub

- Repo local đã `git init` tại `100_日本語/` (không phải trong `03_Android_App/` hay thư mục con nào) — đây là nơi git thật nằm, `.claude/worktrees/<tên>/` chỉ là bản checkout tạm của 1 phiên chat, share chung `.git` với thư mục này.
- Git identity **local-only** (không phải global): `user.name=NguyenNC`, `user.email=nguyennc@vi-mash.com`.
- Remote: `origin` → https://github.com/Nin-Min2231/Nihongo_App.git (đổi tên 2026-09-12, xem mục 4.12 — URL cũ `Lading_page-VS` vẫn redirect được), nhánh `main`. **Đã push xong tới `6fe8245`** (2026-09-25, mục 4.20/4.21 — module シャドウイング + redesign IT業務編 + mọi thay đổi UI liên quan). Local `main` (ở thư mục project chính) **chưa fast-forward theo** — session chạy trong worktree bị cấm `cd` vào thư mục gốc nên **push thẳng bằng `git push origin <branch-của-worktree>:main`**, không qua bước fast-forward local `main` như các phiên trước (mục 4.13/4.14 từng làm). PM hoặc phiên sau, khi đứng đúng ở thư mục project chính, chỉ cần `git pull` (hoặc `git merge --ff-only origin/main`) để đồng bộ.
- `.gitignore` loại trừ: `node_modules/`, audio trùng lặp (chỉ giữ `02_IT_Gyoumuhen/AudioCD/` làm nguồn duy nhất, bỏ 2 bản copy ở `01_Build_App/audio/` và `03_Android_App/www/` — `01_Build_App/audio/shadowing/` của module mới cũng nằm trong diện loại trừ này vì là con của `01_Build_App/audio/`), `02_IT_Gyoumuhen/reading_segments/audio/` (~37MB, giữ `segments_data.json`), `05_json/` (bản xuất tiến độ cá nhân), APK, Gradle/Android build artifacts, `local.properties` (machine-specific), `.claude/settings.local.json`. **`06_ Shadowing_Jokyu/` (nguồn: JSON + xlsx + 46MB audio) KHÔNG nằm trong `.gitignore`, và KHÔNG được commit** — không phải vì kỹ thuật mà vì **PM đã yêu cầu rõ ràng: không commit** (nội dung giáo trình có bản quyền, chỉ dùng nội bộ, xem banner đầu file + mục 4.15/4.20). Mọi lần `git add`, phải loại trừ tay thư mục này (add từng file/thư mục cụ thể, không dùng `git add -A`/`.`) — khác với `02_IT_Gyoumuhen/AudioCD/` (cùng kiểu dữ liệu nhưng ĐÃ được commit làm nguồn chính thức, vì đó là quyết định trước đó cho module IT業務編, không áp dụng ngược lại cho シャドウイング).
- Muốn commit thay đổi mới: **KHÔNG dùng `git add -A`/`git add .`** kể từ khi có `06_ Shadowing_Jokyu/` (không gitignore nhưng PM yêu cầu không commit) — liệt kê rõ từng file/thư mục cần add rồi mới `git commit`. Ngoài điểm đó ra thì như bình thường; vẫn cần kiểm tra `git status` trước khi add để không lỡ commit thứ đã gitignore.
- **Chỉ còn `main` + đúng 1 worktree đang hoạt động** (folder `handover-file-review-9bd2f7`, đã fully merge vào `main` — mục 4.14) — mọi worktree cũ khác đã dọn sạch (mục 4.13, 4.14). **Lưu ý:** git có thể gán **branch khác nhau** cho cùng 1 folder worktree giữa các phiên chat (mục 4.15 gặp `claude/read-handover-file-b582d2` thay vì `claude/handover-file-review-9bd2f7` cũ, dù cùng 1 folder, cùng commit `aace5f8`) — không phải lỗi, chỉ là tên branch trôi theo tên phiên. **Trước khi tin bất kỳ mô tả "trạng thái hiện tại" nào, chạy `git worktree list` và `git branch -a -v`** — dự án này từng có nhiều phiên làm việc song song không biết tới nhau, gây hiểu nhầm thật nhiều lần.

---

## 7. Checklist cho session mới tiếp tục project

- [ ] Đọc file này (đủ context, không cần đọc lại toàn bộ lịch sử chat cũ).
- [ ] Chạy `git worktree list` + `git branch -a -v` trước — xác nhận đang đứng đúng nơi có `main` mới nhất, không phải 1 worktree/nhánh cũ còn sót (mục 4.13, đã xảy ra thật nhiều lần).
- [ ] Xác nhận `git status` sạch (`nothing to commit`) trước khi bắt đầu — nếu có thay đổi dở dang từ trước, hỏi người dùng trước khi động vào (kể cả khi đang đứng ở thư mục project chính, không chỉ worktree — mục 4.11 đã có bài học thật).
- [ ] Muốn sửa app HTML/logic: sửa `01_Build_App/_app_build/app_template.html`, KHÔNG sửa `Kokoro_Nihongo.html` (bị build đè).
- [ ] Muốn thêm từ mới: skill `translator-ja-vi-en` → ghi bằng raw ZIP/XML (mục 3.2), KHÔNG `openpyxl.save()`. Kiểm tra file có đang mở trong Excel không (`~$日本語の辞書.xlsx`) trước khi đọc/sửa.
- [ ] Sau khi sửa: `python3 build_app.py` → verify (`node --check`, đếm JSON) → **test kỹ trong Chrome preview trước khi build APK** (thói quen làm việc người dùng đã yêu cầu rõ — đừng build APK ngay khi chưa được xác nhận).
- [ ] Muốn build APK: theo đúng quy trình mục 5.2 (có bước đối chiếu số plugin `npx cap sync`, xem cảnh báo trong đó), nhớ `export JAVA_HOME`/`GRADLE_USER_HOME` trước khi `gradlew`.
- [ ] Đọc `01_Build_App/_feature_requests/` nếu có FR mới người dùng viết sẵn (hiện không có FR nào pending — FR mới cũng có thể nằm ở thư mục dữ liệu riêng như `06_ Shadowing_Jokyu/`, không nhất thiết trong `_feature_requests/`, xem mục 4.15).
- [ ] Commit + push theo mục 6 nếu người dùng yêu cầu (mặc định KHÔNG tự ý commit/push nếu không được nhắc).

---

## 8. Feature Request — cách yêu cầu thêm/sửa chức năng

Folder `01_Build_App/_feature_requests/`: `TEMPLATE.md` để copy, đặt tên `FR_<số>_<tên>.md`, viết xong đặt ngay tại `_feature_requests/` (khi hoàn thành sẽ chuyển vào `done/`). **Không còn FR nào pending** — tất cả từ FR_002 tới FR_013 đều đã xong, nằm trong `done/`: FR_002 (đổi màu + fix Kaiwa + mic reading), FR_003 (multi-theme + IT業務編 — Part 1+2 UI/menu đã có sẵn từ trước, Part 3 audio làm ở FR_004), FR_004 (IT業務編 Luyện nghe/Luyện đọc), FR_005 (fix TTS Android bằng plugin native — **đã test thật, PM xác nhận nghe được**; redesign Flashcard/IT専門/main menu; thêm app icon), FR_006 (IT専門 auto-focus Bộ, mục 4.10), FR_007 (IT業務編 Unit gộp, bản rút gọn — mục 4.10), FR_008..FR_012 (gói Phase 2, mục 4.8), FR_013 (module thứ 3 シャドウイング, mục 4.15 — **đã code + build + test qua Browser pane, CHƯA build APK**). FR_013 là ví dụ FR không nằm trong `_feature_requests/` (PM đặt cùng dữ liệu ở `06_ Shadowing_Jokyu/`, đã copy 1 bản vào `done/` cho khớp quy ước) — không cần viết file FR nếu không muốn, mô tả trong chat theo cấu trúc (làm gì → hành vi cụ thể → ràng buộc) là đủ.

---

## 9. Backlog / ý tưởng nâng cấp tiếp

- ~~Bump version APK lên "0.1" chính thức~~ — **đã xong** (mục 4.15, 2026-09-22).
- Quyết định dung lượng audio Shadowing trước khi build APK cho FR_013: giữ 64kbps (+46MB, APK ~115MB) hay hạ 48kbps (~34MB) — cần build thử 1 lần để đo số thật rồi mới quyết (mục 4.15, FR_013 mục 10).
- Quyết định có commit `06_ Shadowing_Jokyu/` (46MB, nội dung có bản quyền) vào git hay không (mục 6).
- Quiz nội dung + trích từ vựng riêng cho IT業務編 (đã note rõ ngoài phạm vi FR_004, để FR riêng).
- Đồng bộ tiến độ đa thiết bị **kiểu gộp thông minh** (FR_011 mới làm ghi đè một chiều, chưa gộp theo nguyên tắc "bậc cao hơn thắng" — PM đã đồng ý tạm thời, mở FR mới nếu cần).
- Chế độ viết kanji, ghép câu, nghe chép chính tả.
- Thêm lại nút "Khó" cho SRS (`reviewCard` mức 1/3 hiện là code chết, xem mục "SRS — điểm cần biết" trong `CLAUDE.md`).
- FR_007 bản đầy đủ: nối `02_IT_Gyoumuhen/reading_segments/` (217 mp3 cắt sẵn theo lượt thoại, đã có data — mục 4.10/4.11) vào `gyoumuUnitScreen()` thay cho bản rút gọn hiện dùng nguyên track — PM nói để test bản hiện tại trước, báo lại nếu muốn làm tiếp.
- Bản release APK đã ký (hiện chỉ có debug build).
