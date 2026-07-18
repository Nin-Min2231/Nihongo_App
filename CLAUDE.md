# CLAUDE.md — Kokoro_Nihongo Project

## Project Overview

App học tiếng Nhật offline (single HTML file), dùng cho PM/BrSE ngành IT làm việc với đối tác Nhật.

```
日本語の辞書.xlsx  →  build_app.py  →  Kokoro_Nihongo.html (chạy trên điện thoại)
```

## Cấu trúc thư mục

```
100_日本語/
├── 日本語の辞書.xlsx              ← Từ điển gốc (559+ từ, KHÔNG dùng openpyxl.save())
├── PROJECT_日本語学習アプリ_Handover.md  ← Tài liệu handover chi tiết
├── CLAUDE.md                      ← File này
├── 01_Build_App/
│   ├── Kokoro_Nihongo.html        ← App output (build từ template + vocab JSON)
│   ├── _app_build/
│   │   ├── app_template.html      ← Template chính (CSS + JS, ~1300 dòng)
│   │   └── build_app.py           ← Script build: đọc xlsx → inject JSON → output HTML
│   └── _feature_requests/
│       ├── TEMPLATE.md            ← Template viết feature request
│       ├── FR_002_*.md            ← FR đã hoàn thành
│       └── FR_003_*.md            ← FR multi-theme (pending)
└── 02_IT_Gyoumuhen/
    ├── IT_Gyoumuhen.pdf           ← Sách scan 104 trang
    ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx  ← Transcript hội thoại
    └── AudioCD/                   ← 38 file mp3 (~69MB)
```

## Quy trình Build

```bash
cd 100_日本語/01_Build_App/_app_build
python3 build_app.py
```

Build script:
1. Đọc `日本語の辞書.xlsx` (parse ZIP/XML trực tiếp, KHÔNG dùng openpyxl)
2. Trích vocab → JSON array `[{id, w, r, vi, en, ex, c}, ...]`
3. Replace 3 placeholder trong `app_template.html`: `/*__VOCAB__*/[]`, `__GEN_DATE__`, `__COUNT__`
4. Output → `Kokoro_Nihongo.html`

**Verify sau build:**
```bash
# Check JS syntax
python3 -c "import re; html=open('Kokoro_Nihongo.html').read(); m=re.search(r'<script>(.*?)</script>',html,re.DOTALL); open('/tmp/c.js','w').write(m.group(1))" && node --check /tmp/c.js

# Check vocab count
python3 -c "
import json
html=open('Kokoro_Nihongo.html').read()
idx=html.find('/*__VOCAB__*/')
s=html.index('[',idx); d=0
for i in range(s,len(html)):
    if html[i]=='[': d+=1
    elif html[i]==']': d-=1
    if d==0: print('OK:',len(json.loads(html[s:i+1])),'words'); break
"
```

## Quy tắc QUAN TRỌNG

### 1. xlsx = ZIP — KHÔNG dùng openpyxl.save()
File `.xlsx` là archive ZIP chứa XML. `openpyxl.save()` rewrite styles → **MẤT màu, border, theme**.
Chỉ sửa raw string trên `xl/worksheets/sheet1.xml` và `xl/sharedStrings.xml`, giữ nguyên byte tất cả file khác.
Chi tiết code pattern: xem `PROJECT_日本語学習アプリ_Handover.md` mục 3.3.

### 2. App template — single file, offline
- Toàn bộ CSS + JS trong 1 file HTML
- Không fetch thư viện ngoài
- Vocab data nhúng dạng JSON (placeholder `/*__VOCAB__*/[]`)
- SRS data lưu `localStorage` key `jp_learn_v1`
- TTS settings lưu `localStorage` key `kokoro_tts_settings`

### 3. Build script path
`build_app.py` dùng path tương đối. Nếu chạy Claude Code, chỉ cần `cd` vào `_app_build/` rồi `python3 build_app.py`.

Build script đã dùng path tương đối (tự suy từ `__file__`), hoạt động ở mọi môi trường.

## Kiến trúc App (app_template.html)

### Navigation flow
```
home() → [Chọn chủ đề] → homeDashboard() → [6 mode học] → back → homeDashboard → back → home
```

### 5 Chủ đề (Topic Selection)
| Chủ đề | Trạng thái |
|---|---|
| IT専門 (từ vựng IT) | ✅ Active — hệ thống chính |
| IT業務編 (công việc IT) | 🔜 Coming soon |
| 日常生活 | 🔜 Coming soon |
| N2 | 🔜 Coming soon |
| 面接 | 🔜 Coming soon |

### 6 Mode học (IT専門)
- **Flashcard + SRS**: Leitner system (box 0-6, intervals [0,1,2,4,7,15,30])
- **Quiz**: Trắc nghiệm JP↔VI
- **Listening**: Nghe TTS → chọn nghĩa
- **Speaking**: Đọc theo → SpeechRecognition → chấm điểm (LCS ratio)
- **Reading**: Đọc câu ví dụ + mic
- **Kaiwa**: Hội thoại ngắn từ câu ví dụ

### TTS System
- **Online**: Google Translate TTS (`translate.googleapis.com/translate_tts?client=gtx`)
- **Offline fallback**: Web Speech API (`speechSynthesis`)
- Settings: speed (0.5-1.5), pitch (0.5-2.0), gender (male/female), voice picker
- Auto fallback: online failed → device voice

### UI
- Color scheme: Blue (`--brand:#2563eb`, `--grad:linear-gradient(135deg,#1e40af,#3b82f6)`)
- Button Settings: bg `#d6e1fa`, color `#1e40af`, text "⚙️ 設定"
- Button Back: bg `#d6e1fa`, color `#1e40af`
- Mobile-first, max-width 560px

## Feature Requests

Xem folder `_feature_requests/`. Format: `FR_<số>_<tên>.md` theo `TEMPLATE.md`.
FR pending: FR_003 (multi-theme + IT業務編 integration).

## Ngôn ngữ & Convention

- Comment code: tiếng Anh hoặc tiếng Việt
- UI text: tiếng Việt (cho user) + tiếng Nhật (cho nội dung học)
- Tài liệu: tiếng Việt, thuật ngữ Nhật/Anh giữ nguyên
- Biến/hàm JS: camelCase, tiếng Anh
