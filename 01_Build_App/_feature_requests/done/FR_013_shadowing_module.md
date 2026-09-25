# FR_013 — Module シャドウイング (Shadowing 中〜上級編)

> Dữ liệu đã chuẩn bị sẵn, KHÔNG cần OCR/cắt audio lại. Đọc kỹ mục 9 (dữ liệu có sẵn) trước khi code.

---

## 1. Loại thay đổi

- [x] Thêm chức năng mới (new feature)

## 2. Tên chức năng

**シャドウイング** — module thứ 3 của menu chính, ngang hàng với `IT専門` và `IT業務編`.

## 3. Mô tả ngắn

Thêm module luyện shadowing từ giáo trình *シャドウイング 日本語を話そう 中〜上級編* (8 Unit / 15 Section / 62 track / 240 đoạn hội thoại / 1.225 lượt thoại, song ngữ Nhật–Việt, có audio thật).
Người học chọn Unit → Section → nghe từng **đoạn hội thoại** (cắt sẵn theo mốc thời gian trong file mp3 của track) → luyện nói từng lượt thoại và được chấm điểm bằng mic, giống luồng `IT業務編`.

## 4. Hành vi mong muốn (chi tiết)

### 4.1 Menu chính (`home()`)

- Thêm 1 phần tử vào registry `MENU_MODULES`:
  ```js
  {id:'shadowing', icon:'🗣️', title:'シャドウイング',
   sub:function(){return 'Shadowing hội thoại đời sống · '+SHADOW_SEGCOUNT+' đoạn';},
   open:shadowDashboard},
  ```
- Ô thống kê thứ 3 của hero (`Track đã nghe`) giữ nguyên cho IT業務編. Không đổi hero.

### 4.2 `shadowDashboard()` — chọn Unit

- Header: `シャドウイング` / `Shadowing 中〜上級編 · 8 Unit · 62 track`.
- Khối `.stats` 3 ô: **8 Unit** · **240 Đoạn** · **N Đã nghe** (`Object.keys(sdStore.listened).length`).
- Danh sách 8 thẻ `.topic-card`, mỗi thẻ 1 Unit:
  - Title: `Unit N · <titleJp>`
  - Sub: `<titleVi> · <số track> track · <số đoạn> đoạn`
  - Badge tiến độ: `x/y đoạn đã nghe`.
- Chạm 1 Unit → `shadowUnitScreen(unit)`.

### 4.3 `shadowUnitScreen(unit)` — 1 màn hình gộp (theo đúng mẫu `gyoumuUnitScreen`)

Header: `Unit N · <titleJp>` / `<titleVi>`.

**Tab chọn Section** (Unit 1–7 có 2 section 中級/上級; Unit 8 có 8 section đều 上級):
`Section 1 (中級)` · `Section 2 (上級)` — tab đang chọn tô `var(--soft)`.

**Phần A — 🎧 Luyện nghe** (accordion, mở đúng 1 đoạn tại 1 thời điểm)

- Liệt kê từng **đoạn** của section đang chọn (mỗi đoạn là 1 dòng accordion):
  `Đoạn <no> · <thời lượng> · Track <track>` + dấu ✓ nếu đã nghe.
- Mở 1 đoạn → hiện:
  - Nút ▶/⏸, thanh progress, thời gian `mm:ss / mm:ss` (dùng lại `gyoumuFmtTime`).
  - Nút **🔁 Lặp lại đoạn** (bật/tắt; bật thì hết đoạn tự phát lại từ `start`).
  - Nút **👁 Hiện/Ẩn script** — mặc định **ẨN** (đúng tinh thần shadowing: nghe trước, nhìn sau).
  - Khi hiện script: danh sách lượt thoại `spk：jp` + dòng `vi` nhỏ bên dưới (có nút **🇻🇳 Ẩn/Hiện nghĩa** riêng, mặc định ẩn nghĩa).
- **Phát theo khoảng thời gian, KHÔNG có file mp3 riêng cho từng đoạn**:
  ```js
  audioEl.src = shadowTrackAudioSrc(track);   // 'audio/shadowing/sd_1-02.mp3'
  audioEl.currentTime = seg.start;
  audioEl.play();
  // trong 'timeupdate': if(audioEl.currentTime >= seg.end){ loop? seek(seg.start) : pause(); }
  ```
  Lưu ý: gán `currentTime` **sau** sự kiện `loadedmetadata` nếu `readyState < 1`, nếu không Safari/WebView bỏ qua.
- Nghe xong 1 đoạn (chạm tới `seg.end`) → `sdStore.listened[seg.id] = Date.now()`, `saveShadow()`, `bumpStreak(); save();`
  (giống IT業務編: **không** cộng vào `stats.studied`).

**Phần B — 🎤 Luyện nói (shadowing) + chấm điểm**

- Dropdown/tab chọn đoạn trong section đang chọn.
- Luyện **từng lượt thoại** của đoạn đó, y hệt phần "Luyện đọc câu" của `gyoumuUnitScreen`:
  - Hiện `spk：jp` (to) + `vi` (nhỏ, có nút ẩn/hiện).
  - Nút **🔊 Nghe mẫu (TTS)** + nút **🐢 Chậm** (`speak(jp, slow?0.65:0.9)`).
  - Nút **🎧 Nghe audio thật của đoạn** → phát khoảng `[seg.start, seg.end]` của track.
  - Nút **🎤 Luyện đọc** → `recognizeOnce('ja-JP')` → `similarity(alts[i], line.jp)` → lấy max → `playScoreSound(best)` → hiện điểm theo đúng 3 ngưỡng hiện có (≥90 🌟 / ≥51 👍 / <51 💪).
  - Nút **Tiếp theo →**; hết đoạn thì tính trung bình và lưu:
    ```js
    sdStore.spoken[seg.id] = {bestAvg: Math.max(prev, avg), attempts: prev.attempts+1};
    saveShadow(); bumpStreak(); save();
    ```
- 2 phần A và B **render/bind độc lập** (`renderSdListen()` / `renderSdSpeak()`), không dùng chung 1 hàm render — giữ đúng ràng buộc của FR_007 để audio bên này không bị gián đoạn khi thao tác bên kia.
- Trước khi phát nguồn mới luôn gọi `stopAllShadowAudio()` (dừng audio đoạn + `stopSpeech()`), đảm bảo **chỉ 1 nguồn phát tại 1 thời điểm**.

### 4.4 Unit 8 (hội thoại dài / bài phát biểu)

- Mỗi track Unit 8 chỉ có **1 đoạn** dài 2–2,5 phút, có `title`/`titleVi` (ví dụ `クレーム` / `Khiếu nại`).
- Hiện title ở đầu đoạn. Ở phần Luyện nói, số lượt thoại nhiều (5–24) nên **thêm thanh tiến độ `i/N`**.
- Không cần xử lý gì khác biệt về dữ liệu.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — thêm module (CSS dùng lại 100% class có sẵn, KHÔNG thêm biến `:root` mới)
- [x] `build_app.py` — đọc `Shadowing_Data.json`, inject placeholder, sync audio
- [x] `PROJECT_日本語学習アプリ_Handover.md` + `CLAUDE.md` — cập nhật tài liệu (mục "2 Module" → "3 Module")
- [ ] `日本語の辞書.xlsx` — KHÔNG đụng tới

### 5.1 `build_app.py` — 4 thay đổi

1. Hằng số mới:
   ```python
   SHADOW_JSON  = os.path.join(BASE, '06_ Shadowing_Jokyu', 'Shadowing_Data.json')
   SHADOW_AUDIO_SRC = os.path.join(BASE, '06_ Shadowing_Jokyu', 'AudioMP3')
   SHADOW_AUDIO_DST = os.path.join(AUDIO_DST, 'shadowing')
   ```
2. Hàm `extract_shadow()`: đọc thẳng file JSON (đã đúng schema, **không cần parse xlsx**), trả về `data['units']`. Nếu thiếu file → in cảnh báo và build tiếp với mảng rỗng (giống cách xử lý `extract_gyoumu`).
3. Thêm placeholder `/*__SHADOW__*/[]` vào danh sách kiểm tra + replace (đúng pattern của `/*__GYOUMU__*/[]`).
4. `sync_audio()`: copy thêm `06_ Shadowing_Jokyu/AudioMP3/*.mp3` → `01_Build_App/audio/shadowing/` (so sánh size để bỏ qua file đã copy, y như phần audio IT業務編).
5. Dòng tổng kết cuối: `✓ Built app with %d words + %d IT業務編 tracks + %d shadowing segments`.

### 5.2 `app_template.html` — các điểm chèn

| Vị trí | Nội dung |
|---|---|
| Cạnh `/*__GYOUMU__*/[]` | `const SHADOW = /*__SHADOW__*/[];` + `const SHADOW_SEGCOUNT = …` (tính bằng reduce) |
| Cạnh `GY_LS_KEY` | `const SD_LS_KEY="kokoro_shadow_v1";` + `loadShadow()/saveShadow()/defaultShadowStore()` → `{listened:{}, spoken:{}}` |
| Cạnh `MENU_MODULES` | thêm phần tử `shadowing` |
| Sau block IT業務編 | `shadowDashboard()`, `shadowUnitScreen()`, `shadowTrackAudioSrc()`, `stopAllShadowAudio()` |
| `exportProgress()` / `importProgress()` (FR_011) | **thêm key `kokoro_shadow_v1`** vào cả 2 chiều — nếu quên, tiến độ shadowing không được sao lưu |
| Nút "Xoá toàn bộ dữ liệu" trong Cài đặt | thêm `'kokoro_shadow_v1'` vào mảng 4 key hiện có |

## 6. Ràng buộc kỹ thuật

1. **Offline hoàn toàn** — không fetch gì ngoài file cục bộ.
2. **ES5** (`var`, `function`) cho đồng nhất với code hiện có.
3. **Không thêm thư viện ngoài**, không thêm biến CSS `:root` mới — dùng lại `var(--brand)`, `var(--soft)`, `var(--good)`, `var(--warn)`, `var(--bad)`.
4. **localStorage key mới `kokoro_shadow_v1`**, tách hẳn khỏi `jp_learn_v1` và `kokoro_gyoumu_v1` — tuyệt đối không ghi đè.
5. **Không đụng vào `_id_lock.json`** (quy tắc #7 của CLAUDE.md) — module này không dùng `id` từ vựng.
6. **Không thêm icon thứ 7 vào `deckGridHTML()`/`autoFocusDeckIndex()`** — shadowing là module riêng, không tính vào "hoàn thành Bộ" của IT専門 (xem quy tắc #8).
7. **TTS/mic**: dùng lại `speak()`, `recognizeOnce()`, `similarity()`, `playScoreSound()`, `hasSR()`, `ensureMicReady()` đang có. Không viết logic mới.
8. **Audio đoạn phát theo khoảng thời gian**, không tạo 240 file mp3 rời — giữ APK nhẹ và sửa mốc cắt chỉ cần sửa JSON, không phải cắt lại file.
9. **Dung lượng**: audio shadowing +46 MB (`01_Build_App/audio/shadowing/`), dữ liệu nhúng +≈370 KB vào HTML (338 KB → ≈710 KB). APK sẽ tăng từ ~69 MB audio lên ~115 MB audio — cân nhắc trước khi build APK, nếu quá nặng thì hạ bitrate xuống 48 kbps (giảm còn ~34 MB) trước khi code.

## 7. Ưu tiên

- [x] Trung bình — nên có

## 8. Nghiệm thu (test trong trình duyệt trước, KHÔNG build APK ngay)

1. `python3 build_app.py` chạy sạch, báo đủ `667 words + 38 tracks + 240 shadowing segments`.
2. Verify JS syntax bằng `node --check` (đúng quy trình trong CLAUDE.md).
3. Menu chính hiện đủ **3 thẻ**; chạm シャドウイング vào đúng dashboard.
4. Unit 1 → Section 1 → đoạn 1: audio phát đúng từ `0.0s`, tự dừng ở `14.79s`; bật Lặp lại thì quay về đầu đoạn.
5. Chuyển sang Section 2 khi đang phát → audio phải dừng, không phát chồng.
6. Luyện nói 1 đoạn đủ 4 lượt → hiện điểm trung bình, `kokoro_shadow_v1` có `spoken['1-02-1']`.
7. Nghe 1 đoạn xong → streak tăng đúng 1 lần/ngày, `stats.studied` **không** đổi.
8. Xuất tiến độ → chuỗi JSON có chứa `kokoro_shadow_v1`; nhập lại vào tab trắng → tiến độ shadowing khôi phục đúng.
9. Kiểm khổ máy thật: script tiếng Nhật không tràn ngang ở màn 360px.

---

## 9. Dữ liệu đã chuẩn bị sẵn (KHÔNG phải làm lại)

### 9.1 File

| File | Vị trí | Nội dung |
|---|---|---|
| `Shadowing_Data.json` | `06_ Shadowing_Jokyu/` | 375 KB — toàn bộ dữ liệu, đúng schema mục 9.2 |
| `Shadowing_Transcript.xlsx` | `06_ Shadowing_Jokyu/` | Bản người đọc: sheet `Transcript` (1.225 dòng), `DanhSachTrack` (62 dòng), `QC_Doan` (240 dòng) |
| `AudioMP3/sd_<disk>-<track>.mp3` | `06_ Shadowing_Jokyu/AudioMP3/` | 62 file mp3 mono 64 kbps, tổng 46 MB (convert từ m4a 256 kbps stereo) |

Thư mục `06_ Shadowing_Jokyu/_ocr_tmp/` là file tạm của quá trình OCR (ảnh trang scan, log silencedetect) — **có thể xoá**, không phải dữ liệu nguồn.

### 9.2 Schema `Shadowing_Data.json`

```jsonc
{
  "meta": { "source": "...", "tracks": 62, "segments": 240,
            "audioDir": "audio/shadowing", "audioFormat": "mp3 mono 64kbps", "note": "..." },
  "units": [{
    "unit": 1,
    "titleJp": "家族・夫婦・恋人との会話",
    "titleVi": "Hội thoại với gia đình, vợ chồng, người yêu",
    "sections": [{
      "section": 1,
      "level": "中級",                      // hoặc "上級"
      "tracks": [{
        "track": "1-02",                     // <disk>-<track number> in trên sách
        "disk": 1, "no": 2,
        "audio": "sd_1-02.mp3",              // tên file trong audio/shadowing/
        "dur": 79.12,                        // giây
        "pages": [20],                       // trang sách gốc (tham chiếu)
        "level": "中級", "section": 1,
        "segments": [{
          "id": "1-02-1",                    // KHOÁ TIẾN ĐỘ — duy nhất toàn bộ dữ liệu
          "no": 1,                           // số đoạn in trong ô vuông đỏ của sách
          "page": 20,
          "start": 0.0, "end": 14.79, "dur": 14.79,   // giây, trong file mp3 của track
          "title": "", "titleVi": "",        // chỉ Unit 8 mới có
          "lines": [
            {"spk": "A", "jp": "早くかたづけなさい。", "vi": "Mau dọn dẹp đi!"}
          ]
        }]
      }]
    }]
  }]
}
```

Ghi chú khi code:
- `spk` có thể là `"A"`, `"B"`, tên riêng (Unit 8: `司会`, `中村`…) hoặc **chuỗi rỗng**. Rỗng nghĩa là: dòng ghi chú tình huống (`【2、3分後】`, `〈就職面接〉`) **hoặc** đoạn văn tiếp theo của cùng người nói phía trên. Render: nếu `spk` rỗng và `jp` bắt đầu bằng `【`/`［`/`〈` thì hiện dạng chú thích in nghiêng, không cho luyện mic; còn lại thì hiện thụt lề tiếp nối lượt trên.
- Track `2-23` trải trên 2 trang sách (144 và 146) nên có 5 đoạn — code chỉ cần duyệt theo `segments`, không phụ thuộc `page`.
- `id` đoạn là khoá tiến độ duy nhất, **không đổi công thức** (`<track>-<no>`), nếu đổi thì tiến độ user gắn sai.

### 9.3 Cách dữ liệu được tạo (để biết mà kiểm tra lại khi nghi ngờ)

- **Transcript**: PDF gốc là bản scan 300 dpi **không có text layer** → đọc ảnh từng trang (63 trang tiếng Nhật + 63 trang bản dịch). Đã bỏ furigana và ký hiệu 解説 (bóng đèn đỏ). Đã đối chiếu **số đoạn và số lượt thoại giữa bản Nhật và bản Việt khớp 100%** trên cả 240 đoạn.
- **Mốc cắt đoạn**: `ffmpeg silencedetect (noise=-38dB, d=0.5)` lấy các khoảng lặng, mốc kỳ vọng tính theo **tỉ lệ số ký tự tiếng Nhật** của từng đoạn, rồi dùng quy hoạch động chọn khoảng lặng gần nhất theo thứ tự tăng dần; cắt ở **giữa khoảng lặng**, đệm **0,3 s** mỗi đầu.
- **Kiểm tra chất lượng cắt**: sheet `QC_Doan` trong xlsx có cột `Ký tự/giây`. Giá trị bình thường 4,0–8,0. Chỉ **1/240 đoạn** ra ngoài khoảng (`2-30-1` = nguyên bài phát biểu đám cưới, cả track là 1 đoạn nên không có rủi ro cắt sai). Dù vậy mốc cắt vẫn là **tự động** — nếu nghe thấy đoạn nào bị hụt/dư đầu-cuối, chỉ cần sửa `start`/`end` trong `Shadowing_Data.json` rồi build lại, không phải đụng file audio.

### 9.4 Lưu ý về tên file m4a gốc (đã xử lý, ghi lại để khỏi nhầm sau này)

Tên file m4a trong 2 thư mục CD ghi **sai** Unit/Section từ track `2-11` trở đi (ví dụ `2-11` đề "Unit 6 Section 1" nhưng sách in là **Unit 5 Section 2**). Dữ liệu đã dựng theo **số DISK–track in trên sách** (đúng), không theo tên file. Đừng "sửa lại" theo tên file.

### 9.5 Thống kê

| Unit | Chủ đề | Section | Track | Đoạn |
|---|---|---|---|---|
| 1 | 家族・夫婦・恋人との会話 | 1 (中級) / 2 (上級) | 3 / 5 | 13 / 25 |
| 2 | 親しい友人との会話 | 1 (中級) / 2 (上級) | 4 / 5 | 16 / 23 |
| 3 | 知人や近所の人などとの会話 | 1 (中級) / 2 (上級) | 3 / 6 | 14 / 25 |
| 4 | 医者や店員などとの会話 | 1 (中級) / 2 (上級) | 2 / 4 | 10 / 13 |
| 5 | 同僚との会話 | 1 (中級) / 2 (上級) | 4 / 6 | 16 / 26 |
| 6 | 上司や部下との会話 | 1 (中級) / 2 (上級) | 3 / 4 | 11 / 16 |
| 7 | 社外の人や面接官などとの会話 | 1 (中級) / 2 (上級) | 2 / 3 | 6 / 15 |
| 8 | 長い会話・スピーチなど | 1–8 (上級) | 8 | 8 |
| **Tổng** | | **15 section** | **62** | **240** |

---

## 10. Rà soát spec — điểm mơ hồ / edge case / rủi ro

### Điểm mơ hồ cần PM quyết trước khi code

| # | Vấn đề | Impact | Đề xuất |
|---|---|---|---|
| 1 | Dung lượng APK: +46 MB audio → tổng audio ~115 MB, APK có thể vượt 150 MB | **Cao** | Giữ 64 kbps cho bản web/desktop; nếu APK quá nặng thì build riêng bản 48 kbps (~34 MB) hoặc cho tải audio shadowing sau khi cài |
| 2 | "Nghe xong 1 đoạn" tính là đã học — chạm `seg.end` hay nghe đủ 80% thời lượng? | Trung bình | Dùng mốc chạm `seg.end` (đơn giản, khớp cách IT業務編 đang làm) |
| 3 | Có cần chế độ "Prosody shadowing" (phát audio + mic ghi đồng thời) không? | Trung bình | **Không** ở bản này — Web Speech API không nhận diện tốt khi có audio phát cùng lúc. Bản này = nghe trước, nói sau |
| 4 | Unit 8 đoạn dài 2–2,5 phút, luyện nói 24 lượt liên tục có thể gây nản | Thấp | Thêm thanh tiến độ `i/N` + cho phép thoát giữa chừng vẫn lưu điểm các lượt đã đọc |

### Edge case chưa xử lý trong spec

| # | Edge case | Xử lý đề xuất |
|---|---|---|
| E1 | `spk` rỗng (dòng ghi chú 【…】 / đoạn văn tiếp nối) | Render riêng, **bỏ qua khi luyện mic** — nếu không user sẽ phải đọc "【2、3分後】" |
| E2 | Đang phát đoạn thì user bấm nút Back của app/thiết bị | `onBack` phải gọi `stopAllShadowAudio()` trước khi rời màn hình, nếu không audio phát tiếp ở màn khác |
| E3 | `audioEl.currentTime` gán trước khi metadata sẵn sàng | Gán trong `loadedmetadata` nếu `readyState < 1` (Safari/Android WebView bỏ qua nếu gán sớm) |
| E4 | Đoạn cuối track: `seg.end` == `dur` → sự kiện `ended` bắn trước `timeupdate` | Xử lý cả 2 sự kiện `ended` và `timeupdate` |
| E5 | Máy không có mic / user từ chối quyền | Ẩn hẳn phần Luyện nói, chỉ hiện Luyện nghe (dùng lại `micSupport` của `gyoumuUnitScreen`) |
| E6 | User cũ nhập file tiến độ cũ (không có `kokoro_shadow_v1`) | `importProgress()` phải bỏ qua key thiếu, không throw |
| E7 | Mốc cắt tự động lệch → đoạn bị hụt câu đầu/cuối | Đã đệm 0,3 s; thêm nút "Nghe nguyên track" để user tự đối chiếu khi nghi ngờ |

### Rủi ro

| # | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| R1 | Bản quyền giáo trình — nhúng nguyên transcript + audio vào app | **Cao** | Chỉ dùng nội bộ cá nhân, không phát hành công khai / không lên store |
| R2 | HTML tăng 338 KB → ~710 KB, thời gian parse JS trên máy yếu tăng | Trung bình | Nếu chậm rõ rệt, chuyển `SHADOW` sang lazy-parse (`JSON.parse` 1 chuỗi thay vì object literal) |
| R3 | Mốc cắt sai ở vài đoạn mà chưa phát hiện | Trung bình | Sheet `QC_Doan` để soát; sửa JSON là đủ, không phải cắt lại audio |
| R4 | Đọc OCR từ bản scan có thể còn sai sót lẻ tẻ chưa phát hiện | Thấp–TB | Đã kiểm chéo 100% số đoạn/số lượt Nhật–Việt; sai sót còn lại (nếu có) ở mức từ, sửa trực tiếp trong JSON |
| R5 | Thêm module thứ 3 làm `home()` dài ra trên máy màn nhỏ | Thấp | Menu đã dùng `.topics` cuộn được, không cần đổi |
