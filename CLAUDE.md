# CLAUDE.md — Kokoro Nihongo Project

## Project Overview

App học tiếng Nhật offline, dùng cho PM/BrSE ngành IT làm việc với đối tác Nhật. Có 2 hình thức chạy: file HTML tự chứa (mở trực tiếp bằng trình duyệt) hoặc APK Android thật (đóng gói bằng Capacitor, có mic/TTS native).

```
日本語の辞書.xlsx  →  build_app.py  →  Kokoro_Nihongo.html  →  (Capacitor) →  Kokoro_Nihongo.apk
```

Đọc file này trước khi sửa code. Muốn hiểu sâu lịch sử quyết định/lý do kỹ thuật: đọc `PROJECT_日本語学習アプリ_Handover.md`. Muốn hướng dẫn build/chạy chi tiết từng bước: đọc `README.md`.

## Cấu trúc thư mục

```
100_日本語/
├── 日本語の辞書.xlsx              ← Từ điển gốc (596 từ, KHÔNG dùng openpyxl.save())
├── CLAUDE.md                      ← File này
├── PROJECT_日本語学習アプリ_Handover.md  ← Tài liệu handover chi tiết (lịch sử, kiến trúc sâu)
├── README.md                      ← Hướng dẫn build/chạy từng bước
├── 01_Build_App/
│   ├── Kokoro_Nihongo.html        ← App output (build từ template + vocab JSON, KHÔNG sửa tay)
│   ├── audio/                     ← (gitignore) copy từ 02_IT_Gyoumuhen/AudioCD, build_app.py tự sync
│   ├── _app_build/
│   │   ├── app_template.html      ← Template chính (CSS + JS, ~2000 dòng) — SỬA FILE NÀY để thêm tính năng
│   │   └── build_app.py           ← Script build: đọc xlsx + transcript → inject JSON → output HTML
│   └── _feature_requests/
│       ├── TEMPLATE.md            ← Copy file này ra để viết yêu cầu tính năng mới
│       └── done/                  ← FR đã hoàn thành (FR_002 .. FR_005) — lịch sử tham khảo
├── 02_IT_Gyoumuhen/                ← Nguồn dữ liệu module IT業務編 (hội thoại công việc IT)
│   ├── IT_Gyoumuhen.pdf                    ← Sách scan, chỉ tham khảo
│   ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx ← Transcript 38 track
│   └── AudioCD/                             ← 38 file mp3 — NGUỒN AUDIO DUY NHẤT của cả dự án
├── 03_Android_App/                 ← Project Capacitor — đóng gói HTML thành APK Android
│   ├── package.json, capacitor.config.json
│   ├── assets/icon.png            ← Nguồn app icon (copy từ 04_Image/Logo_Tanpopo.png)
│   ├── www/                        ← (gitignore) copy Kokoro_Nihongo.html + audio trước khi build
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

Build script (path tự suy từ vị trí file, chạy được ở bất kỳ máy nào):
1. Đọc `日本語の辞書.xlsx` + `02_IT_Gyoumuhen/IT_Gyoumuhen_AudioCD_Transcript.xlsx` (parse ZIP/XML trực tiếp, KHÔNG dùng openpyxl)
2. Trích vocab → JSON array `[{id, w, r, vi, en, ex, c}, ...]` (c = category tự động: 外来語/漢字/その他), trích 38 track IT業務編 → JSON `GYOUMU_DATA`
3. Replace placeholder trong `app_template.html`: `/*__VOCAB__*/[]`, `/*__GYOUMU__*/[]`, `__GEN_DATE__`, `__COUNT__`
4. Tự copy audio từ `02_IT_Gyoumuhen/AudioCD/` → `01_Build_App/audio/`
5. Output → `Kokoro_Nihongo.html`

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

## Quy tắc QUAN TRỌNG

### 1. xlsx = ZIP — KHÔNG dùng openpyxl.save()
File `.xlsx` là archive ZIP chứa XML. `openpyxl.save()` rewrite styles → **MẤT màu, border, theme**.
Chỉ sửa raw string trên `xl/worksheets/sheet1.xml` và `xl/sharedStrings.xml`, giữ nguyên byte tất cả file khác.
Chi tiết code pattern: xem `PROJECT_日本語学習アプリ_Handover.md` mục 3.2.

### 2. App template — single file, offline
- Toàn bộ CSS + JS trong 1 file HTML (`app_template.html`), không dùng framework
- Không fetch thư viện ngoài (kể cả icon/favicon đều nhúng base64)
- Vocab data nhúng dạng JSON (`/*__VOCAB__*/[]`), gyoumu data (`/*__GYOUMU__*/[]`)
- SRS data lưu `localStorage` key `jp_learn_v1`; IT業務編 progress lưu key riêng `kokoro_gyoumu_v1`
- TTS settings lưu `localStorage` key `kokoro_tts_settings`

### 3. Sửa app = sửa `app_template.html`, KHÔNG sửa `Kokoro_Nihongo.html`
`Kokoro_Nihongo.html` luôn bị `build_app.py` ghi đè mỗi lần build. Muốn thêm/sửa tính năng: sửa `app_template.html` rồi `python3 build_app.py` lại.

### 4. TTS trên Android APK dùng plugin native, KHÔNG dùng Google TTS
Android WebView (nơi Capacitor chạy) **không hề implement Web Speech API**, và endpoint Google Translate TTS (không chính thức) **cũng không đáng tin cậy** khi gọi từ WebView đóng gói (đã xác nhận lỗi thật trên máy — xem `PROJECT_...Handover.md` mục 4.7). App dùng `isNativeApp()` để phát hiện môi trường: native → gọi thẳng plugin `@capacitor-community/text-to-speech` (engine TextToSpeech hệ thống, không qua mạng); web/Chrome → vẫn dùng Google TTS + `speechSynthesis` fallback như cũ. **Đừng quay lại dùng Google TTS làm đường chính cho native** — đã thử và không hoạt động.

### 5. Mic cũng dùng plugin native tương tự
`@capgo/capacitor-speech-recognition` cho native (Android WebView không có Web Speech Recognition API), fallback `SpeechRecognition`/`webkitSpeechRecognition` cho web. Xem `isNativeApp()`/`nativeSR()`/`nativeTTS()` trong `app_template.html`.

## Kiến trúc App (app_template.html)

### Navigation flow
```
home() → [chọn 1 trong 4 module] → dashboard riêng của module → mode học → back → home
```

### 4 Module (Menu chính — registry `MENU_MODULES`, thêm module mới chỉ cần thêm 1 phần tử)
| Module | Trạng thái | Dashboard |
|---|---|---|
| IT専門 (từ vựng IT, 596 từ) | ✅ Active | `homeDashboard()` |
| IT業務編 (hội thoại công việc IT, 38 track) | ✅ Active | `gyoumuDashboard()` |
| Luyện đọc (đọc câu ví dụ + mic) | ✅ Active | `readingLibrary()` |
| Kaiwa (hội thoại ngắn từ câu ví dụ) | ✅ Active | `kaiwaLibrary()` |

Main menu (`home()`) có 1 khối thống kê tổng hợp đầu trang: Streak / Từ đã thuộc (IT専門) / Track đã nghe (IT業務編).

### 5 Mode học của IT専門
- **Flashcard + SRS**: Leitner system (box 0-6, intervals [0,1,2,4,7,15,30]). 4 nút: Chi tiết/Yêu thích/Đã nhớ/Tiếp theo — bấm "Đã nhớ" tính 1 lượt SRS mức "Được" (`reviewCard(id,2)`), không còn hàng nút Quên/Khó/Được/Dễ riêng.
- **Quiz**: Trắc nghiệm JP↔VI
- **Luyện nghe**: Nghe TTS → chọn nghĩa
- **Luyện nói**: Đọc theo → nhận diện giọng → chấm điểm (LCS ratio, ngưỡng ≥90 xuất sắc/≥51 khá/<51 luyện lại) + âm thanh phản hồi (`playScoreSound()`)
- **⭐ Yêu thích**: xem lại từ đã đánh dấu yêu thích

IT専門 chia thành các **Bộ cố định đúng 25 từ, bắt đầu từ #1** (596 từ = 23 Bộ×25 + 1 Bộ 21 từ cuối, hàm `splitDecksStrict()`), không còn lọc theo "Chủ đề" (漢字/外来語/その他).

### TTS System
- **Native (Android APK)**: `@capacitor-community/text-to-speech` — engine TextToSpeech hệ thống, không qua mạng (xem quy tắc #4).
- **Web/browser**: Google Translate TTS (thử 2 endpoint `client=gtx`/`client=tw-ob`) → fallback `speechSynthesis` khi lỗi.
- Cả 2 nhánh: nếu thất bại hoàn toàn → toast báo lỗi (không im lặng).
- Settings: speed (0.5-1.5), pitch (0.5-2.0), gender (male/female), voice picker.

### UI
- Color scheme: Blue (`--brand:#2563eb`, header gradient `#1e40af→#3b82f6`)
- Bộ đang chọn: nền xanh dương nhạt (`#dbeafe`) để phân biệt với Bộ chưa chọn
- Flashcard 4 nút: Chi tiết (xanh lá) / Yêu thích (vàng) / Đã nhớ (cam) / Tiếp theo (xanh dương đậm), đều có border màu đậm hơn nền
- Mobile-first, max-width 560px
- App icon + favicon: dùng `04_Image/Logo_Tanpopo.png` (xem `03_Android_App/assets/icon.png` + `npx capacitor-assets generate`)

## Feature Requests

Xem folder `01_Build_App/_feature_requests/`. Format: `FR_<số>_<tên>.md` theo `TEMPLATE.md`. FR đã hoàn thành nằm trong `done/`. **Hiện không có FR nào đang pending** — sẵn sàng cho yêu cầu Phase 2 mới.

## Ngôn ngữ & Convention

- Comment code: tiếng Anh hoặc tiếng Việt
- UI text: tiếng Việt (cho user) + tiếng Nhật (cho nội dung học)
- Tài liệu: tiếng Việt, thuật ngữ Nhật/Anh giữ nguyên
- Biến/hàm JS: camelCase, tiếng Anh
