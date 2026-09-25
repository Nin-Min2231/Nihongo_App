# CLAUDE.md — Kokoro Nihongo Project

## Project Overview

App học tiếng Nhật offline, dùng cho PM/BrSE ngành IT làm việc với đối tác Nhật. Có 2 hình thức chạy: file HTML tự chứa (mở trực tiếp bằng trình duyệt) hoặc APK Android thật (đóng gói bằng Capacitor, có mic/TTS native).

```
日本語の辞書.xlsx  →  build_app.py  →  Kokoro_Nihongo.html  →  (Capacitor) →  Kokoro_Nihongo.apk
```

Đọc file này trước khi sửa code. Muốn hiểu sâu lịch sử quyết định/lý do kỹ thuật: đọc `PROJECT_日本語学習アプリ_Handover.md`. Muốn hướng dẫn build/chạy chi tiết từng bước: đọc `README.md`.

> **Gói Phase 2 (FR_008 → FR_012) + FR_006/FR_007 + redesign dashboard (bảng màu "giấy washi" + trang chủ hero) đã code xong và test qua trình duyệt.** Xem mục "Feature Requests" cuối file + mục UI bên dưới. FR_007 code theo **bản rút gọn** (không cắt audio theo lượt thoại — xem ghi chú đầu file `done/FR_007_reading_real_audio_segments.md`). Redesign dashboard: **PM đã duyệt áp dụng cho toàn app** (2026-09-12), gộp từ 1 worktree khác (`japanese-learning-app-handover-e2f2a1`) vào worktree này — 2 việc không đụng chạm cùng chỗ trong code nên gộp bằng `git apply` sạch, không conflict. Đã build APK cho gói này lần đầu (2026-09-12 tối), phát hiện + fix việc `@capacitor/filesystem`/`@capacitor/share` khai trong `package.json` nhưng **chưa từng `npm install` thật** khiến mọi bản APK trước đó thiếu 2 plugin — xem chi tiết ở handover mục 4.12.
>
> **Cập nhật 2026-09-13:** thêm 4 việc theo yêu cầu PM — xem quy tắc #8 (icon Bộ 6→6, tính cả Điền từ/Phản xạ vào "hoàn thành") + mục UI bên dưới (checkbox "Học từ đã nhớ" ở Flashcard, hero trang chủ đổi số chính thành streak, panel Cài đặt sticky header + đổi thứ tự). Đã commit + fast-forward `main` (commit `f95d252`) và **build lại APK debug với các thay đổi này** — `03_Android_App/Kokoro_Nihongo.apk`, vẫn versionCode 1 / versionName "1.0" (chưa bump, theo mục 5.4 handover). Verify: đủ 4 class plugin, đúng 663 từ + 38 track, quyền RECORD_AUDIO có trong manifest. Bản này sau đó **đã được PM cài/test trên điện thoại thật và xác nhận OK** (2026-09-22) — đã bump lên `versionCode 2`/`versionName "0.1"` và build lại APK debug, verify đủ 4 plugin + đúng version, xem chi tiết cách build ở mục 5.2. `main` local đã push lên `origin/main` xong (không còn ahead nữa).
>
> **2026-09-22:** thêm module thứ 3 **シャドウイング** (FR_013) — xem mục "3 Module" + "FR_013" cuối file. PM test bản PC qua 2 vòng góp ý (mục 4.16/4.17: gộp nghe+luyện nói vào 1 accordion/đoạn, UI riêng màn Unit tiếng Nhật, 3 màu tiến độ + điểm mỗi lượt thoại). Đã build APK debug đo dung lượng thật **~125MB** (`versionCode 3`/`versionName "0.1"`) — **CHƯA cài/test trên điện thoại thật**. Dữ liệu nguồn `06_ Shadowing_Jokyu/` theo yêu cầu PM: **không commit**.
>
> **2026-09-23:** PM test APK trên điện thoại thật (ảnh chụp xác nhận app chạy tốt), góp ý tiếp 3 việc — xem mục 4.18. (1) Gọn + Nhật hoá khối hero trang chủ, thêm ô "Đoạn シャドウイング đã nghe" (lưới 2×2). (2) Mọi màn hình tự cuộn về đầu khi chuyển trang (`setHeader()`). (3) **Redesign IT業務編 theo đúng mẫu シャドウイング**: gộp nghe+luyện đọc vào 1 accordion/track, 3 màu tiến độ, điểm mỗi câu (lần ghi gần nhất) — xem mục "3 Module"/"Kiến trúc App". Sau đó PM soát kỹ thêm, yêu cầu Nhật hoá **nốt phần label/nút còn sót tiếng Việt** trong 2 màn IT業務編 (list Unit + chi tiết Unit) — xem mục 4.19: thêm `stripViGloss()` bóc phần chú thích tiếng Việt lẫn trong dữ liệu `t.type`/`t.chars` (giữ lại romaji tên riêng không dấu như "(Taguchi)"), dịch nốt "Chương"→"第N章", "Đã nghe"→"聴取済み", tên 2 tab, các nút/thông báo trong 2 tab nghe/đọc.
>
> **2026-09-25:** build lại APK debug với toàn bộ thay đổi mục 4.18/4.19 (`versionCode 4`/`versionName "0.1"`, giữ nguyên versionName vì chưa phải mốc ổn định mới) — verify đủ 4 plugin, 663 từ + 38 track IT業務編 + 8 Unit shadowing, 62+38 file audio, quyền RECORD_AUDIO. **CHƯA cài/test trên điện thoại thật.**

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
│       └── done/                  ← FR đã hoàn thành (FR_002..FR_013 + _PHASE2_GOI_CAI_MOT_LAN.md) — lịch sử tham khảo
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
├── 04_Image/
│   └── Logo_Tanpopo.png            ← Logo gốc 1024x1024, nguồn cho app icon + favicon
└── 06_ Shadowing_Jokyu/             ← Nguồn dữ liệu module シャドウイング (FR_013, tên thư mục có khoảng trắng)
    ├── Shadowing_Data.json          ← 8 Unit/22 section/62 track/240 đoạn/1.225 lượt thoại — build_app.py đọc thẳng, không parse xlsx
    ├── Shadowing_Transcript.xlsx    ← Bản người đọc (tham khảo), không dùng khi build
    └── AudioMP3/                    ← 62 file mp3 mono 64kbps — NGUỒN AUDIO DUY NHẤT của module này (~46MB)
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
- SRS data lưu `localStorage` key `jp_learn_v1`; IT業務編 progress lưu key riêng `kokoro_gyoumu_v1`; シャドウイング progress lưu key riêng `kokoro_shadow_v1` (FR_013)
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

**Đổi giao diện 2026-09-13 (không đổi logic xuất/nhập):** khối "💾 Tiến độ học" trong `openSettings()` chuyển lên **đầu panel** (trước "Nguồn giọng đọc"), theo yêu cầu PM vì đây là mục hay dùng nhất. Panel cũng tách thành `.settings-head` (title + nút ✕, `position:sticky;top:0` — không cuộn theo nội dung) + `.settings-body` (phần còn lại, cuộn bên trong `.settings-panel`) — trước đó cả panel cuộn chung 1 khối nên tiêu đề/nút đóng bị trôi mất khi cuộn xuống.

### 7. `_id_lock.json` — KHÔNG xóa, KHÔNG sửa tay
Tiến độ học trong `localStorage` khóa theo `id` (`store.cards[id]`, `store.favorites[id]`).

Bản build cũ lấy `id` = STT cột B. Xóa hoặc chèn một dòng giữa file Excel là mọi `id` phía sau dịch theo, và tiến độ của từ A lặng lẽ gắn sang từ B, không báo gì. **Đã xảy ra thật**: so bản APK 2026-07-18 (596 từ) với từ điển 2026-09-11 (667 từ), có **47 trong 596 id trỏ sang từ khác** do 3 dòng bị xóa ở giữa.

`build_app.py` v2 giữ sổ khóa `_id_lock.json` ánh xạ **từ vựng → id cố định**:
- Từ đã có trong sổ → giữ nguyên id đó vĩnh viễn, dù chuyển lên xuống bao nhiêu dòng
- Từ mới → cấp id kế tiếp chưa ai dùng (`next_id`)
- Id của từ đã xóa khỏi Excel → **không bao giờ cấp lại** cho từ khác
- Từ chỉ bị sửa phần chú thích trong ngoặc (ví dụ `（が）見当たらない` → `見当たらない`) được nhận ra là cùng một từ và giữ nguyên id

Hệ quả: **số `#id` hiển thị trên thẻ không còn khớp STT trong Excel** — đây là đánh đổi có chủ ý, giữ tiến độ quan trọng hơn giữ con số hiển thị.

**Lưu ý hay bị hiểu nhầm là bug (đã kiểm tra thật 2026-09-13):** nhãn header "Bộ N (start-end)" (`curDeckRangeLabel()`) hiển thị **vị trí/STT** của từ trong mảng `VOCAB` hiện tại (thứ tự Excel), còn tag "`#id`" trên mỗi từ là **id cố định** theo `_id_lock.json` — 2 con số này KHÔNG bắt buộc trùng nhau, và lệch nhau là bình thường (VD Bộ 9 hiển thị "(201-225)" nhưng có thể chứa từ tag "#228" — đã verify bằng cách đọc thẳng `VOCAB` trong `Kokoro_Nihongo.html`: dữ liệu bên trong 1 Bộ vẫn đúng 100% theo vị trí, chỉ là con số `#id` tự nhiên trôi theo lịch sử sửa từ điển). KHÔNG "sửa" `deckPool()`/`splitDecksStrict()` để cố ép 2 số này khớp nhau — sẽ phá vỡ toàn bộ thiết kế giữ tiến độ ở quy tắc này.

Xóa `_id_lock.json` = mất ánh xạ = build lại sẽ đánh số từ đầu = tiến độ trong app gắn sai hết. File này **phải commit vào git**.

### 8. Lưới chọn Bộ — nay đủ 6 icon, cả 6 đều tính vào "hoàn thành"
`deckGridHTML()` tô thẻ Bộ thành xanh lá khi **tất cả** icon truyền vào đều đã xong. **Đổi 2026-09-13 (theo yêu cầu PM):** trước đây cố tình chỉ truyền 4 icon 🗂️✍️🎧🎤 (`flash`/`quiz`/`listen`/`speak`) dù `cloze`/`reflex` đã ghi cờ vào `deckDone` từ FR_009/FR_010, để tránh làm mất màu xanh của các Bộ đã hoàn thành trước đó. PM đã xác nhận chấp nhận đánh đổi này — nay `homeDashboard()` truyền đủ **6 icon** 🗂️✍️🧩🎧🎤⚡ (`flash`/`quiz`/`cloze`/`listen`/`speak`/`reflex`) vào `deckGridHTML()`, và `autoFocusDeckIndex()` (FR_006) cũng đòi đủ 6 mode mới coi 1 Bộ là xong.

**Hệ quả đã biết (chấp nhận được, không phải bug):** mọi Bộ từng hoàn thành trước bản cập nhật này (kể cả tiến độ thật trên điện thoại PM) sẽ **tạm mất màu xanh** cho tới khi học lại Điền từ + Phản xạ cho từng Bộ đó — dữ liệu `deckDone` cũ không mất, chỉ là điều kiện xét lại nghiêm hơn.

Nếu sau này thêm mode thứ 7 mà muốn tránh lặp lại việc này: theo đúng mẫu cũ — vẫn gọi `markDeckDone()` nhưng không thêm icon vào mảng truyền cho `deckGridHTML()`, và không thêm điều kiện vào `autoFocusDeckIndex()`.

## Kiến trúc App (app_template.html)

### Navigation flow
```
home() → [chọn 1 trong 2 module] → dashboard riêng của module → mode học → back → home
```

IT専門 (`homeDashboard()`) tự động chọn sẵn **Bộ nhỏ nhất chưa hoàn thành đủ 4 mode** mỗi lần vào (FR_006, `autoFocusDeckIndex()`) — xem quy tắc #8 cho định nghĩa "hoàn thành". Chọn thủ công 1 Bộ khác trong phiên vẫn được, nhưng bị tính lại từ đầu khi rời màn hình rồi vào lại.

IT業務編 (`gyoumuDashboard()`) vào thẳng **`gyoumuUnitScreen(chapter,unit)`** (FR_007 gốc, **redesign lại mục 4.18 handover theo đúng mẫu シャドウイング**) — mỗi Track là 1 accordion (`trackListHTML()`), mở ra có đúng 2 tab con `🎧 Luyện nghe`/`🎤 Luyện đọc` lồng chung 1 thẻ (`trackBodyHTML()`), KHÔNG còn tách 2 khối (player nghe phía trên + tab chọn track luyện đọc phía dưới) như bản FR_007 cũ. Track không có transcript (9, 21) vẫn nghe được, tab Luyện đọc chỉ bị khoá (`disabled`). Chỉ 1 track mở + 1 tab hiện + 1 nguồn audio phát tại 1 thời điểm — đổi track/đổi tab đều `stopAllGyoumuAudio()` trước khi vẽ lại (`renderList()`).

シャドウイング (`shadowDashboard()`) vào thẳng **`shadowUnitScreen(unit)`** (FR_013, redesign mục 4.16/4.17) — tab Section phía trên (`sectionTabsHTML()`), dưới là 1 danh sách **Đoạn** dạng accordion (`segListHTML()`, không phải theo track — 1 track có thể chứa nhiều đoạn): mỗi Đoạn mở ra có đúng 2 tab con `🎧 聞き取り`/`🎤 シャドウイング` lồng chung 1 thẻ (`segBodyHTML()`). Tab nghe phát audio bằng cách seek vào đúng khoảng `[seg.start, seg.end]` của file track thật (**không cắt 240 file mp3 rời**, mốc cắt nằm sẵn trong `Shadowing_Data.json`); tab luyện nói chạy từng lượt thoại trong đúng đoạn đang mở (không còn dropdown chọn đoạn riêng — mở đoạn nào luyện đoạn đó). Chỉ 1 đoạn mở + 1 tab hiện + 1 nguồn audio phát tại 1 thời điểm — đổi Section/đổi tab/đổi đoạn đều `stopAllShadowAudio()` trước khi vẽ lại (`renderSectionTabs()`/`renderList()`). Dòng ghi chú tình huống trong transcript (`spk` rỗng, `jp` bắt đầu bằng 【/［/〈) bị loại khỏi hàng đợi luyện mic (`shadowIsNoteLine()`).

> **IT業務編 và シャドウイング dùng chung 1 bộ hạ tầng "màu theo tiến độ + điểm mới nhất theo câu/lượt thoại"** (redesign mục 4.18, đặt tên trung lập không theo module cụ thể): class CSS `.tint-partial`/`.tint-done` (tô `.topic-card`, đặt trước `.gy-track-row` để `.gy-track-row.open` luôn thắng khi trùng), `.unit-iconwrap`/`.unit-progress` (badge "N/M đã nghe" dưới icon ở dashboard), `.compact-row`/`.compact-body` (layout gọn cho màn Unit gộp — không đụng padding gốc của `.topic-card`/`.player-card`/`.sent-card` vì các module/màn khác vẫn dùng chung 3 class đó), và hàm `scoreColorTier(score)` (<60 đỏ/60-90 vàng/>90 xanh — áp dụng cho cả badge "(done/total·TB点)" mỗi Track/Đoạn lẫn badge điểm từng câu/lượt thoại). Model điểm dùng chung: `gyStore.read[track]={lines:{i:{score,attempts}}}` và `sdStore.spoken[segId]={lines:{i:{score,attempts}}}` — **điểm mỗi câu/lượt là điểm LẦN GHI ÂM GẦN NHẤT, không phải cao nhất**. Ngưỡng feedback mic ngay lúc chấm ở 2 màn này (🌟>90/👍60-90/💪<60) cũng đổi theo `scoreColorTier` — **khác** ngưỡng ≥90/≥51 của Quiz/Luyện nói IT専門 (2 chỗ đó không đổi, xem mục "7 Mode học của IT専門").
>
> **UI 2 màn IT業務編 (`gyoumuDashboard()`/`gyoumuUnitScreen()`) cũng đổi sang tiếng Nhật cho label/nút** (mục 4.19, cùng ngoại lệ như シャドウイング — không đổi quy ước UI tiếng Việt chung của app), **trừ** tagline header module + `unitJp`/`unitVi` (tên chủ đề Unit song ngữ, vẫn giữ nguyên vì là nội dung học, không phải chrome). Điểm khó: `t.type`/`t.chars` trong `GYOUMU_DATA` là 1 chuỗi gộp sẵn "tiếng Nhật (chú thích)" ngay từ cột Excel gốc (không tách JP/VI riêng như unitJp/unitVi) — hàm `stripViGloss(s)` bóc phần trong ngoặc/sau dấu "-" **chỉ khi phần đó chứa dấu tiếng Việt** (nhận diện bằng regex ký tự có dấu), **giữ lại** phần romaji không dấu như "(Taguchi)"/"(Li)" vì đó là phiên âm đọc tên riêng chứ không phải bản dịch cần bỏ.

### 3 Module (Menu chính — registry `MENU_MODULES`, thêm module mới chỉ cần thêm 1 phần tử)
| Module | Trạng thái | Dashboard |
|---|---|---|
| IT専門 (từ vựng IT, 663 từ) | ✅ Active | `homeDashboard()` |
| IT業務編 (hội thoại công việc IT, 38 track) | ✅ Active | `gyoumuDashboard()` |
| シャドウイング (Shadowing 中〜上級編, 62 track/240 đoạn, FR_013) | ✅ Active | `shadowDashboard()` |

> **FR_008 đã gỡ bỏ** module Luyện đọc (`readingLibrary()`) và Kaiwa (`kaiwaLibrary()`) — không dùng nữa, PM xác nhận trùng mục đích với Luyện nói / nội dung ghép giả. Dữ liệu `deckDone._reading` / `deckDone._kaiwa` cũ vẫn còn trong `localStorage` của user cũ nhưng không dùng tới nữa.

> **シャドウイング KHÔNG tính vào "hoàn thành Bộ" của IT専門** — không đụng `deckGridHTML()`/`autoFocusDeckIndex()`/`markDeckDone()` (đúng nguyên tắc quy tắc #8: module riêng thì không thêm icon). Tiến độ lưu riêng `localStorage` key `kokoro_shadow_v1`, khóa theo `id` đoạn cố định `<track>-<no>` trong `Shadowing_Data.json`, không đụng `_id_lock.json` của quy tắc #7: `{listened:{segId:timestamp}, spoken:{segId:{lines:{lineIndex:{score,attempts}}}}}` — **điểm mỗi lượt thoại là điểm LẦN GHI ÂM GẦN NHẤT, không phải điểm cao nhất** (đổi theo PM sau khi test bản đầu, mục 4.16 handover), `shadowSegStats()` tính điểm trung bình 1 đoạn = TB của điểm-gần-nhất từng lượt đã ghi. Nghe/luyện nói xong 1 đoạn chỉ gọi `bumpStreak()` (không cộng `stats.studied`), cùng cách IT業務編 đang làm. **Nội dung giáo trình có bản quyền — chỉ dùng nội bộ cá nhân, không phát hành công khai/lên store** (rủi ro R1 của FR_013).
>
> **UI riêng của シャドウイング dùng tiếng Nhật cho nhãn/nút** (khác quy ước chung "UI tiếng Việt" của app — PM yêu cầu riêng cho module luyện nói này, mục 4.16). Màn Unit (`shadowUnitScreen()`) sau khi PM test bản đầu đã **gộp 🎧 nghe + 🎤 luyện nói vào chung 1 accordion mỗi Đoạn** (2 tab con trong cùng 1 thẻ, thay vì 2 khối tách rời như bản đầu) — chỉ 1 đoạn mở + 1 tab hiện + 1 nguồn audio phát tại 1 thời điểm, đổi Section/đổi tab/đổi đoạn đều `stopAllShadowAudio()` trước khi vẽ lại. Card màu theo tiến độ (không thêm biến `:root`, chỉ thêm class `.sd-partial`/`.sd-done` với hex tint pha nhẹ từ `--warn`/`--good`): dashboard tô theo **% đã nghe của Unit**, danh sách Đoạn trong Unit tô theo **% đã luyện nói của Đoạn** (2 chiều dữ liệu khác nhau, xem mục 4.16). Ngưỡng màu điểm riêng cho module này — <60 đỏ/60-90 vàng/>90 xanh (`shadowScoreColor()`) — **khác** ngưỡng chấm mic chung ≥90/≥51 dùng ở IT専門 Luyện nói + IT業務編 Luyện đọc câu (không đổi 2 chỗ đó).

Main menu (`home()`) có 1 khối thống kê tổng hợp đầu trang: Từ đã thuộc (IT専門) / Cần ôn hôm nay (IT専門) / Track đã nghe (IT業務編) / **Đoạn đã nghe (シャドウイング, thêm mục 4.18)** — lưới 2×2 (trước là 1 hàng 3 ô, đổi vì thêm module thứ 4) — **bấm được** (mũi tên `›`), mở màn hình `statsScreen()` (FR_012, xem mục riêng bên dưới — màn này CHƯA có số liệu シャドウイング, chỉ hero mới có, xem mục 4.18). Số liệu chính của hero (số lớn phía trên) là **số ngày học liên tục**, không phải số liệu này — xem mục UI bên dưới. Mọi màn hình đổi trang đều tự cuộn về đầu (`window.scrollTo(0,0)` đặt trong `setHeader()`, gọi từ mọi hàm render màn hình — mục 4.18, fix trang dài như シャドウイング/IT業務編 giữ nguyên vị trí cuộn cũ khi chuyển màn).

### 7 Mode học của IT専門
- **Flashcard + SRS**: Leitner system (box 0-6, intervals [0,1,2,4,7,15,30]). 4 nút: Chi tiết/Yêu thích/Đã nhớ/Tiếp theo — bấm "Đã nhớ" tính 1 lượt SRS mức "Được" (`reviewCard(id,2)`), không còn hàng nút Quên/Khó/Được/Dễ riêng. Checkbox **"Học từ đã nhớ"** phía trên thẻ (`flashIncludeMastered`, biến toàn cục, KHÔNG lưu localStorage — luôn mặc định tắt mỗi lần vào lại) cho học lại cả từ đã đánh dấu "Đã nhớ"; khi bật, nút "Đã nhớ" của từ đã thuộc tự hiện sẵn trạng thái ✅ (tái dùng logic `isMastered()` có sẵn, không phải code mới) — bấm lại để bỏ đánh dấu.
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
- Flashcard 4 nút: Chi tiết (xanh lá) / Yêu thích (vàng) / Đã nhớ (cam) / Tiếp theo, đều có border màu đậm hơn nền — 4 màu này **không** nằm trong phạm vi redesign, giữ nguyên như cũ. `.card` (khung thẻ) giảm `min-height` 230→186px (2026-09-13) để chừa chỗ cho checkbox "Học từ đã nhớ" phía trên mà không đẩy nút xuống quá xa.
- **Trang chủ (`home()`) — hero đổi lại số chính (2026-09-13, theo yêu cầu PM):** số lớn của hero giờ là **số ngày học liên tục** (`store.stats.streak`, không phải số thẻ đến hạn nữa). Nếu có khoảng đứt quãng trước hôm nay (`streakGapDays()` — số ngày giữa `stats.lastDay` và hôm nay, trừ 2 đầu mút), số hiển thị về 0 kèm dòng cảnh báo màu `--warn` "Bạn đã bỏ lỡ N ngày..." thay cho dòng phụ bình thường (không đợi `bumpStreak()` chạy lại mới cập nhật — tính trực tiếp lúc render `home()`). Nút CTA **"Bắt đầu ôn tập ngay →"** không còn phân nhánh theo due>0/=0 nữa — luôn tính `autoFocusDeckIndex()` (Bộ đang học dở/Bộ tiếp theo, dùng chung logic FR_006) rồi vào thẳng `flashMode(deckPool())` của đúng Bộ đó (trước đây vào `flashMode(VOCAB)` học due-toàn-bộ, không theo Bộ cụ thể). Lưới bên dưới hero (FR_012) mở `statsScreen()` qua link "Xem thống kê chi tiết ›" như cũ.
  - **Đổi tiếp mục 4.18 (2026-09-23, theo yêu cầu PM):** toàn bộ text trong `.dash-hero` (nhãn, dòng phụ, cảnh báo đứt mạch, nút CTA, 4 nhãn ô số liệu, link thống kê) chuyển sang **tiếng Nhật** — ngoại lệ riêng cho khối này, giống ngoại lệ đã áp dụng cho màn シャドウイング, không phải đổi quy ước chung "UI tiếng Việt" của cả app. Lưới số liệu đổi từ 1 hàng 3 ô (`grid-template-columns:repeat(3,1fr)`) sang **lưới 2×2** (`repeat(2,1fr)`) để thêm ô thứ 4 (Đoạn シャドウイング đã nghe) mà không dồn chữ trên 1 hàng. Giảm padding/margin/font-size của cả khối hero (`.dash-hero`/`.dash-num`/`.dash-cta`/`.dash-metrics`/`.dash-metric`) để chừa chỗ hiện được thẻ module thứ 3 (シャドウイング) mà không phải cuộn ngay khi vào app — PM báo trên điện thoại thật, thẻ シャドウイング bị khối hero cũ đẩy khuất gần hết.
- Mobile-first, max-width 560px
- App icon + favicon: dùng `04_Image/Logo_Tanpopo.png` (xem `03_Android_App/assets/icon.png` + `npx capacitor-assets generate`)

## Feature Requests

Xem folder `01_Build_App/_feature_requests/`. Format: `FR_<số>_<tên>.md` theo `TEMPLATE.md`. FR đã hoàn thành nằm trong `done/`. **Hiện không có FR nào pending.**

### FR_013 — Module シャドウイング (2026-09-22)

Thêm module thứ 3 `シャドウイング` (Shadowing 中〜上級編, 8 Unit/62 track/240 đoạn) — xem mục "3 Module" và "Kiến trúc App" ở trên. Dữ liệu nguồn (`Shadowing_Data.json`, `Shadowing_Transcript.xlsx`, `AudioMP3/`) do PM chuẩn bị sẵn ngoài phiên code (OCR bản scan + cắt mốc thời gian tự động bằng `ffmpeg silencedetect`), nằm ở `06_ Shadowing_Jokyu/` (thư mục mới, nằm ngoài `01_Build_App/_feature_requests/` — FR gốc cũng nằm ở đó, đã copy 1 bản vào `done/` cho khớp quy ước). `build_app.py` đọc thẳng JSON (không parse xlsx, không tự cắt audio) qua `extract_shadow()`, tự copy `AudioMP3/*.mp3` → `01_Build_App/audio/shadowing/` giống cơ chế IT業務編. ✅ Đã code + build (663 từ + 38 track + 240 đoạn) + `node --check` pass + test qua Browser pane (`python3 -m http.server`, không dùng `file://`): accordion Luyện nghe phát đúng khoảng `[start,end]` trong file track thật rồi tự dừng + đánh dấu đã nghe (verify bằng cách để phát thật ~15s, không seek bằng JS vì môi trường Browser pane seek audio không ổn định), toggle script/nghĩa không làm gián đoạn audio đang mở, đổi Section dừng audio + reset đúng cả 2 phần, Luyện nói chấm điểm + lưu `bestAvg` đúng, export/import có `kokoro_shadow_v1` và bỏ qua an toàn khi file cũ thiếu key này, khổ 375px không tràn ngang, IT専門/IT業務編 không bị ảnh hưởng. **CHƯA build APK** (đúng thói quen — test kỹ trình duyệt trước). Phát hiện bảng thống kê mục 9.5 của `FR_013_shadowing_module.md` bị sai 1 dòng (Unit 6: tổng thực tế 30 đoạn chứ không phải 27 như bảng ghi) — không ảnh hưởng code vì `build_app.py`/`app_template.html` đọc thẳng dữ liệu, không hardcode theo bảng đó.

**Lưu ý dung lượng (chưa quyết, để ngỏ theo đúng đề xuất trong FR):** audio Shadowing +46MB → tổng audio dự kiến APK tăng lên ~115MB. Chưa build APK nên chưa có số đo thật — đo sau khi build lần đầu rồi mới quyết có cần hạ bitrate xuống 48kbps hay không (mục "Rà soát spec" của FR_013).

**Redesign sau khi PM test bản PC đầu tiên (mục 4.16 handover):** gộp 🎧 nghe + 🎤 luyện nói vào chung 1 accordion mỗi Đoạn (2 tab con, thay vì 2 khối tách rời), đổi UI riêng màn Unit sang tiếng Nhật, thêm 3 màu tiến độ (dashboard theo % Unit đã nghe, danh sách Đoạn theo % đã luyện nói), thêm badge "(đã ghi/tổng · điểm TB)" mỗi Đoạn + badge điểm ngay trên từng lượt thoại — đổi hẳn schema `sdStore.spoken` sang lưu **điểm lần ghi gần nhất theo từng lượt thoại** (không còn `bestAvg` gộp cả đoạn). Xem chi tiết đầy đủ ở mục UI phía trên.

**Vòng 2, sau khi PM test tiếp bản PC (mục 4.17 handover):** Nhật hoá nốt phần còn sót (nhãn "Đoạn"→"段落", "Đã nghe"→"聴取済み", ở cả dashboard lẫn màn Unit); gọn layout màn Unit bằng các class riêng `.sd-seg-row`/`.sd-seg-body` (padding/margin nhỏ hơn, KHÔNG đụng `.topic-card`/`.player-card`/`.sent-card` gốc vì IT業務編 vẫn đang dùng chung — chỉ override khi kết hợp thêm class riêng của Shadowing); dời "セリフ N/M" lên cùng hàng với tab (`margin-left:auto`), bỏ hẳn dòng `.counter` riêng. **Đã build APK debug đo dung lượng thật: ~125MB** (từ ~78MB trước khi có Shadowing) — `versionCode 3`/`versionName "0.1"` (giữ nguyên versionName vì đây vẫn là build thử nghiệm module mới, chưa phải mốc ổn định tiếp theo).

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
