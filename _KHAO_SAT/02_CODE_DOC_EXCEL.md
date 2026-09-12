# 02_CODE_DOC_EXCEL.md — Tầng đọc Excel (DÁN NGUYÊN VĂN)

**Dự án:** Kokoro Nihongo (ココロ日本語) — `D:\01_NguyenNC\10_Claude\100_日本語`
**Sinh ngày:** 2026-09-11
**Không có file nào bị cắt vì lý do dung lượng.** Tổng kích thước file này < 100 KB (giới hạn 300 KB không bị chạm).

---

## Kết quả tìm kiếm từ khóa

Đã grep toàn bộ source (bỏ `node_modules`, `.git`, `dist`, `build`, `out`, `venv`, `__pycache__`, `.gradle`, `.claude\worktrees`) với các từ khóa yêu cầu:

`xlsx` `XLSX` `SheetJS` `ExcelJS` `exceljs` `openpyxl` `pandas` `read_excel` `Workbook` `Worksheet` `OleDb` `EPPlus` `ClosedXML` `NPOI` `辞書` `日本語の辞書` `.xlsx` `sheet_to_json`

**Chỉ có ĐÚNG 2 file source chạm vào Excel:**

| # | File | Vai trò | Số dòng |
|---|---|---|---|
| 1 | `01_Build_App/_app_build/build_app.py` | **Tầng đọc Excel CHÍNH** — đọc `日本語の辞書.xlsx` + transcript IT業務編, sinh app HTML | 168 |
| 2 | `01_Build_App/_app_build/segment_reading_audio.py` | Đọc Excel transcript IT業務編 bằng openpyxl để cắt audio thành đoạn. **Không đụng tới `日本語の辞書.xlsx`** | 253 |

**KHÔNG CÓ** thư viện JS nào đọc Excel (không SheetJS, không ExcelJS). App HTML **không đọc file Excel lúc chạy** — dữ liệu đã được nướng cứng (bake) vào HTML lúc build.

### Checklist bắt buộc của mục 4

| Yêu cầu | Trạng thái |
|---|---|
| File đọc Excel chính — nguyên văn 100% | ✅ mục 1 (`build_app.py`) |
| File định nghĩa kiểu dữ liệu / model của một từ vựng | ✅ mục 3 — **KHÔNG CÓ file riêng.** Model là dict Python trong `build_app.py` + `const VOCAB` trong `app_template.html`. Đã dán nguyên văn cả hai chỗ. |
| File cấu hình chứa đường dẫn Excel | ❌ **KHÔNG CÓ.** Không có `.env`, `config.json`, `settings.ini`. Đường dẫn được **suy ra từ vị trí của chính script** — xem khối `# ─── Paths ───` trong `build_app.py`. |
| Lớp cache hoặc chuyển đổi dữ liệu | **KHÔNG CÓ lớp cache.** Lớp chuyển đổi = `extract_vocab()` + `json.dumps()` + `str.replace()` trong `build_app.py`, đã dán nguyên văn. |
| Worker / thread / tiến trình nền để đọc file | ❌ **KHÔNG CÓ.** Đọc đồng bộ, một luồng, chạy tay từ command line. |
| Code đọc Excel nằm rải rác trong file lớn | Không rải rác. Toàn bộ nằm gọn trong `build_app.py`. |

---

## 1. `01_Build_App/_app_build/build_app.py`

- **Vai trò:** Script build duy nhất — đọc 2 file Excel, sinh ra app HTML tự chứa. Đây là file **sẽ bị viết lại**.
- **Số dòng:** 168
- **Sửa lần cuối:** 2026-07-17 19:23
- **Thư viện:** chỉ standard library (`zipfile`, `re`, `html`, `json`, `os`, `datetime`, `shutil`). Cố ý **không dùng openpyxl** — xem `CLAUDE.md` quy tắc #1 (openpyxl.save() làm mất màu/border/theme của file gốc).

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script: đọc 日本語の辞書.xlsx → sinh app học tiếng Nhật (1 file HTML offline).
Chạy lại mỗi khi từ điển có từ mới để cập nhật app.

Usage: python3 build_app.py
"""
import zipfile, re, html, json, os, datetime, shutil

# ─── Paths (tự suy ra từ vị trí của chính script — KHÔNG hardcode session) ─────
# build_app.py nằm ở: 100_日本語/01_Build_App/_app_build/build_app.py
HERE    = os.path.dirname(os.path.abspath(__file__))   # .../01_Build_App/_app_build
APP_DIR = os.path.dirname(HERE)                         # .../01_Build_App
BASE    = os.path.dirname(APP_DIR)                      # .../100_日本語
DICT     = os.path.join(BASE,    '日本語の辞書.xlsx')
OUT      = os.path.join(APP_DIR, 'Kokoro_Nihongo.html')
TEMPLATE = os.path.join(HERE,    'app_template.html')
GYOUMU_XLSX = os.path.join(BASE, '02_IT_Gyoumuhen', 'IT_Gyoumuhen_AudioCD_Transcript.xlsx')
AUDIO_SRC   = os.path.join(BASE, '02_IT_Gyoumuhen', 'AudioCD')
AUDIO_DST   = os.path.join(APP_DIR, 'audio')

# ─── Extract vocab ─────────────────────────────────────────────────────────────
def extract_vocab(dict_path):
    with zipfile.ZipFile(dict_path, 'r') as z:
        sheet  = z.read('xl/worksheets/sheet1.xml').decode('utf-8')
        shared = z.read('xl/sharedStrings.xml').decode('utf-8')

    def si_text(si_xml):
        return html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si_xml, re.DOTALL)))
    S = [si_text(s) for s in re.findall(r'<si>.*?</si>', shared, re.DOTALL)]

    rows = re.findall(r'(<row[^>]*r="(\d+)"[^>]*>.*?</row>)', sheet, re.DOTALL)
    def cell(row_xml, col):
        m = re.search(r'<c r="'+col+r'\d+"([^>]*)><v>(\d+)</v></c>', row_xml)
        if not m: return ''
        attrs, val = m.group(1), m.group(2)
        if 't="s"' in attrs:
            i = int(val); return S[i] if i < len(S) else ''
        return val

    def category(w):
        core = re.sub(r'[（）\(\)Ｖ\d\s、。/／・~〜]', '', w)
        if core and all(('ァ' <= c <= 'ヿ') or c == 'ー' for c in core):
            return "外来語"
        if any('一' <= c <= '鿿' for c in core):
            return "漢字"
        return "その他"

    vocab = []
    for rxml, rn in rows:
        if int(rn) < 5:
            continue
        word = cell(rxml, 'C')
        if not word:
            continue
        vocab.append({
            "id": int(cell(rxml, 'B') or len(vocab)+1),
            "w":  word,
            "r":  cell(rxml, 'D'),
            "vi": cell(rxml, 'E'),
            "en": cell(rxml, 'F'),
            "ex": cell(rxml, 'G'),
            "c":  category(word),
        })
    return vocab

# ─── Extract IT業務編 transcript (đọc, KHÔNG ghi lại file xlsx) ────────────────
def extract_gyoumu(xlsx_path):
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        sheet  = z.read('xl/worksheets/sheet1.xml').decode('utf-8')
        shared = z.read('xl/sharedStrings.xml').decode('utf-8')

    def si_text(si_xml):
        return html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si_xml, re.DOTALL)))
    S = [si_text(s) for s in re.findall(r'<si>.*?</si>', shared, re.DOTALL)]

    rows = re.findall(r'(<row[^>]*r="(\d+)"[^>]*>.*?</row>)', sheet, re.DOTALL)
    def cell(row_xml, col):
        m = re.search(r'<c r="'+col+r'\d+"([^>]*)><v>(\d+)</v></c>', row_xml)
        if not m: return ''
        attrs, val = m.group(1), m.group(2)
        if 't="s"' in attrs:
            i = int(val); return S[i] if i < len(S) else ''
        return val

    line_re = re.compile(r'^([^：:]+)[：:]\s*(.*)$')

    def split_lines(text):
        lines = []
        for raw in re.split(r'\r\n|\r|\n', text):
            raw = raw.strip()
            if not raw:
                continue
            m = line_re.match(raw)
            if m:
                lines.append({"spk": m.group(1).strip(), "t": m.group(2).strip()})
            else:
                lines.append({"spk": "", "t": raw})
        return lines

    tracks = []
    for rxml, rn in rows:
        if int(rn) < 4:
            continue
        track_str = cell(rxml, 'A')
        if not track_str:
            continue
        dialogue = cell(rxml, 'H')
        has_transcript = not dialogue.strip().startswith('(Không có nội dung')
        chapter_m = re.search(r'(\d+)', cell(rxml, 'B'))
        unit_m    = re.search(r'(\d+)', cell(rxml, 'C'))
        tracks.append({
            "track":   int(track_str),
            "chapter": int(chapter_m.group(1)) if chapter_m else 0,
            "unit":    int(unit_m.group(1)) if unit_m else 0,
            "unitJp":  cell(rxml, 'D'),
            "unitVi":  cell(rxml, 'E'),
            "type":    cell(rxml, 'F'),
            "chars":   cell(rxml, 'G'),
            "hasTranscript": has_transcript,
            "lines":   split_lines(dialogue) if has_transcript else [],
            "note":    cell(rxml, 'I'),
        })
    tracks.sort(key=lambda t: t['track'])
    return tracks

# ─── Copy audio (AudioCD/ ngoài 01_Build_App → audio/ cạnh HTML output) ────────
def sync_audio():
    if not os.path.isdir(AUDIO_SRC):
        print(f"⚠ Audio source folder not found: {AUDIO_SRC} — bỏ qua copy audio.")
        return
    os.makedirs(AUDIO_DST, exist_ok=True)
    copied = 0
    for fname in os.listdir(AUDIO_SRC):
        if not fname.lower().endswith('.mp3'):
            continue
        src = os.path.join(AUDIO_SRC, fname)
        dst = os.path.join(AUDIO_DST, fname)
        if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src):
            continue
        shutil.copy2(src, dst)
        copied += 1
    print(f"✓ Audio synced: {copied} file(s) copied to {AUDIO_DST}")

# ─── Build ─────────────────────────────────────────────────────────────────────
def main():
    vocab = extract_vocab(DICT)
    gyoumu = extract_gyoumu(GYOUMU_XLSX) if os.path.isfile(GYOUMU_XLSX) else []
    sync_audio()
    gen_date = datetime.date.today().isoformat()
    data_js = json.dumps(vocab, ensure_ascii=False)
    gyoumu_js = json.dumps(gyoumu, ensure_ascii=False)

    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        tpl = f.read()

    out = tpl.replace('/*__VOCAB__*/[]', '/*__VOCAB__*/' + data_js)
    out = out.replace('/*__GYOUMU__*/[]', '/*__GYOUMU__*/' + gyoumu_js)
    out = out.replace('__GEN_DATE__', gen_date)
    out = out.replace('__COUNT__', str(len(vocab)))

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f"✓ Built app with {len(vocab)} words + {len(gyoumu)} IT業務編 tracks → {OUT}")

if __name__ == '__main__':
    main()
```

---

## 2. `01_Build_App/_app_build/segment_reading_audio.py`

- **Vai trò:** Đọc Excel transcript IT業務編 bằng **openpyxl** (khác hẳn `build_app.py`), rồi dùng ffmpeg silence-detection cắt 38 track mp3 thành 213 đoạn ngắn + sinh `segments_data.json`. **Không đọc `日本語の辞書.xlsx`.** Kết quả hiện **CHƯA được app dùng** (FR_007 còn pending).
- **Số dòng:** 253
- **Sửa lần cuối:** 2026-07-26 17:39
- **Thư viện:** `openpyxl` (cần `pip install`) + `ffmpeg`/`ffprobe` trong PATH.

```python
"""
segment_reading_audio.py — Cắt audio IT業務編 (AudioCD) thành 5-7 đoạn/track bằng
silence-detection (ffmpeg), gom transcript theo lượt thoại/câu tương ứng.
Dùng cho tính năng "Luyện đọc theo audio thật" (xem FR_006).

Chạy: cd 01_Build_App/_app_build && python3 segment_reading_audio.py
Yêu cầu: ffmpeg/ffprobe trong PATH, `pip install openpyxl`.
Path tự suy từ vị trí file (giống build_app.py) — chạy được ở bất kỳ máy nào.
"""
import openpyxl, subprocess, json, re, os, sys

HERE    = os.path.dirname(os.path.abspath(__file__))   # .../01_Build_App/_app_build
APP_DIR = os.path.dirname(HERE)                         # .../01_Build_App
BASE    = os.path.dirname(APP_DIR)                       # .../100_日本語

SRC = os.path.join(BASE, "02_IT_Gyoumuhen")
AUDIO_DIR = os.path.join(SRC, "AudioCD")
TRANSCRIPT_XLSX = os.path.join(SRC, "IT_Gyoumuhen_AudioCD_Transcript.xlsx")
OUT_ROOT = os.path.join(SRC, "reading_segments")
OUT_AUDIO = os.path.join(OUT_ROOT, "audio")
os.makedirs(OUT_AUDIO, exist_ok=True)

SENT_SPLIT = re.compile(r'(?<=[。！？])')

def get_duration(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                           "-of","default=noprint_wrappers=1:nokey=1", path],
                          capture_output=True, text=True)
    return float(out.stdout.strip())

def get_silence_midpoints(path):
    """Run ffmpeg silencedetect, return list of (start,end) midpoints."""
    proc = subprocess.run(["ffmpeg","-i",path,"-af","silencedetect=noise=-30dB:d=0.25","-f","null","-"],
                          capture_output=True, text=True)
    log = proc.stderr
    starts = [float(x) for x in re.findall(r'silence_start:\s*([\-0-9.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end:\s*([0-9.]+)', log)]
    mids = []
    for s, e in zip(starts, ends):
        if e > s:
            mids.append((s+e)/2.0)
    return sorted(mids)

NO_TRANSCRIPT_MARKERS = ("Không có nội dung", "KHÔNG CÓ")

def has_transcript(text):
    if not text or not text.strip():
        return False
    return not any(marker in text for marker in NO_TRANSCRIPT_MARKERS)

def split_units(text):
    """Return list of (speaker_or_None, unit_text) preserving turn boundaries."""
    turns = [t for t in (text or "").split("\n") if t.strip()]
    units = []
    if len(turns) >= 4:
        for t in turns:
            m = re.match(r'^([^\:\：]{1,20})[：:]\s*(.*)$', t)
            if m:
                units.append((m.group(1).strip(), t.strip()))
            else:
                units.append((None, t.strip()))
    else:
        # monologue: split single (or few) turn(s) by sentence delimiters
        for t in turns:
            m = re.match(r'^([^\:\：]{1,20})[：:]\s*(.*)$', t)
            speaker = m.group(1).strip() if m else None
            content = m.group(2).strip() if m else t.strip()
            sentences = [s.strip() for s in SENT_SPLIT.split(content) if s.strip()]
            for s in sentences:
                units.append((speaker, s))
    return units

def num_segments_for(duration):
    if duration < 65:
        return 5
    elif duration < 95:
        return 6
    else:
        return 7

def balanced_partition(units, k):
    """Partition ordered units into exactly min(k,n) contiguous buckets,
    balanced by cumulative char length (nearest-fraction split, not greedy-drift)."""
    n = len(units)
    k = min(k, n)
    if k <= 1:
        return [units]
    lengths = [len(u[1]) for u in units]
    cum = []
    s = 0
    for l in lengths:
        s += l
        cum.append(s)
    total = cum[-1] if cum[-1] > 0 else n
    splits = []
    prev = -1
    for j in range(1, k):
        target = total * j / k
        lo = prev + 1
        hi = n - 1 - (k - j)  # leave >=1 unit for each remaining bucket
        if hi < lo:
            hi = lo
        best_i = min(range(lo, hi + 1), key=lambda x: abs(cum[x] - target))
        splits.append(best_i)
        prev = best_i
    buckets = []
    start = 0
    for sp in splits:
        buckets.append(units[start:sp + 1])
        start = sp + 1
    buckets.append(units[start:])
    return buckets

def snap_to_silence(ideal_time, silence_mids, tolerance):
    best = None
    best_diff = tolerance
    for m in silence_mids:
        d = abs(m - ideal_time)
        if d <= best_diff:
            best = m
            best_diff = d
    return best if best is not None else ideal_time

def cut_audio(path, start, end, out_path):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",path,
                     "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
                     "-acodec","libmp3lame","-q:a","4", out_path], check=True)

def main():
    wb = openpyxl.load_workbook(TRANSCRIPT_XLSX, data_only=True)
    ws = wb['AudioCD_Transcript']
    rows = list(ws.iter_rows(min_row=4, values_only=True))

    files = sorted(os.listdir(AUDIO_DIR))
    track_file = {}
    for f in files:
        m = re.match(r"(\d+)\s", f)
        if m:
            track_file[int(m.group(1))] = f

    tracks_out = []
    for r in rows:
        track, chapter, unit, unit_ja, unit_vi, ctype, chars, text, note = r
        if track is None:
            continue
        track = int(track)
        audio_path = os.path.join(AUDIO_DIR, track_file[track])
        duration = get_duration(audio_path)

        if not has_transcript(text):
            # Known content gap: source PDF pages missing for this track (see 'note' column).
            # Do not fabricate segments/text. Keep the whole track as a single unsegmented
            # reference file so the app can still play it, but flag transcriptAvailable=false.
            out_dir = os.path.join(OUT_AUDIO, f"track{track:02d}")
            os.makedirs(out_dir, exist_ok=True)
            fname = f"track{track:02d}_full.mp3"
            out_path = os.path.join(out_dir, fname)
            subprocess.run(["ffmpeg","-y","-loglevel","error","-i",audio_path,"-acodec","copy",out_path], check=True)
            tracks_out.append({
                "track": track,
                "chapter": chapter,
                "unit": unit,
                "unitJa": unit_ja,
                "unitVi": unit_vi,
                "contentType": ctype,
                "characters": chars,
                "sourceAudioFile": track_file[track],
                "sourceDurationSec": round(duration,2),
                "transcriptAvailable": False,
                "gapNote": (note or "").strip(),
                "segmentCount": 0,
                "segments": []
            })
            print(f"Track {track:2d}: dur={duration:6.1f}s NO TRANSCRIPT (data gap, see note) -> 0 segments, kept as single file", flush=True)
            continue

        units = split_units(text)
        k = num_segments_for(duration)
        buckets = balanced_partition(units, k)
        k_actual = len(buckets)

        silence_mids = get_silence_midpoints(audio_path)
        total_chars = sum(len(u[1]) for u in units)
        cum = 0
        boundary_times = []
        # compute cumulative char count at each bucket end (except last)
        for bi, bucket in enumerate(buckets[:-1]):
            cum += sum(len(u[1]) for u in bucket)
            ideal_t = duration * (cum / total_chars) if total_chars else duration*(bi+1)/k_actual
            tol = min(6.0, duration*0.15)
            snapped = snap_to_silence(ideal_t, silence_mids, tol)
            boundary_times.append(round(snapped, 2))

        # build segment time ranges
        bounds = [0.0] + boundary_times + [round(duration,2)]
        # ensure strictly increasing
        for i in range(1, len(bounds)):
            if bounds[i] <= bounds[i-1]:
                bounds[i] = bounds[i-1] + 0.5

        seg_records = []
        out_dir = os.path.join(OUT_AUDIO, f"track{track:02d}")
        os.makedirs(out_dir, exist_ok=True)
        for si, bucket in enumerate(buckets, start=1):
            start_t = bounds[si-1]
            end_t = bounds[si]
            fname = f"track{track:02d}_seg{si:02d}.mp3"
            out_path = os.path.join(out_dir, fname)
            cut_audio(audio_path, start_t, end_t, out_path)
            speakers = sorted(set(u[0] for u in bucket if u[0]))
            seg_text = "\n".join(u[1] for u in bucket)
            seg_records.append({
                "id": f"T{track:02d}-S{si:02d}",
                "order": si,
                "startTime": round(start_t,2),
                "endTime": round(end_t,2),
                "durationSec": round(end_t-start_t,2),
                # forward-slash relative path (used as URL by the web app, not an OS path)
                "audioFile": f"track{track:02d}/{fname}",
                "speakers": speakers,
                "text": seg_text
            })

        tracks_out.append({
            "track": track,
            "chapter": chapter,
            "unit": unit,
            "unitJa": unit_ja,
            "unitVi": unit_vi,
            "contentType": ctype,
            "characters": chars,
            "sourceAudioFile": track_file[track],
            "sourceDurationSec": round(duration,2),
            "transcriptAvailable": True,
            "segmentCount": len(seg_records),
            "segments": seg_records
        })
        print(f"Track {track:2d}: dur={duration:6.1f}s units={len(units):2d} -> {len(seg_records)} segments", flush=True)

    manifest = {
        "generatedBy": "segment_reading_audio.py (silence-detection + text-balanced grouping)",
        "sourceTranscript": "IT_Gyoumuhen_AudioCD_Transcript.xlsx",
        "sourceAudioDir": "02_IT_Gyoumuhen/AudioCD",
        "trackCount": len(tracks_out),
        "tracks": tracks_out
    }
    out_json = os.path.join(OUT_ROOT, "segments_data.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("\nDone. Manifest written to", out_json)

if __name__ == "__main__":
    main()
```

---

## 3. `01_Build_App/_app_build/app_template.html` — TRÍCH ĐOẠN (file dài 2.048 dòng > 1.500)

- **Vai trò:** Template chứa toàn bộ CSS + JS của app. Đây là nơi **định nghĩa kiểu dữ liệu của một từ vựng** phía client và nơi tiêu thụ dữ liệu Excel.
- **Số dòng cả file:** 2.048
- **Sửa lần cuối:** 2026-07-18 19:47

> ⚠️ **ĐÃ CẮT** — theo đúng quy ước "file dài hơn 1.500 dòng thì dán phần liên quan + 50 dòng trước/sau":
>
> - **ĐÃ DÁN đoạn A: dòng 205–360** — gồm khai báo `const VOCAB`, `const GYOUMU`, `GEN_DATE`, toàn bộ schema localStorage + SRS, cộng ~50 dòng CSS/HTML phía trước làm ngữ cảnh.
> - **ĐÃ DÁN đoạn B: dòng 798–950** — toàn bộ logic tiêu thụ các trường của từ vựng: `pool()`, `allWithEx()`, `splitDecks()`, `splitDecksStrict()`, `deckPool()`, `curDeckRangeLabel()`, `deckGridHTML()`, `MENU_MODULES`, `home()`.
> - **ĐÃ CẮT BỎ:**
>   - dòng 1–204: `<head>`, favicon base64, ~700 dòng CSS
>   - dòng 361–797: TTS (Google Translate TTS + Capacitor native TTS), mic permission, speech recognition, hàm chấm điểm `similarity()`, âm thanh phản hồi
>   - dòng 951–2048: các màn hình học (gyoumu player, flashcard, quiz, listen, speak, reading, kaiwa, finish)
>
>   Các đoạn bị cắt **không đọc Excel** và **không định nghĩa model từ vựng**.
> - Nếu cần trọn file: `01_Build_App/_app_build/app_template.html` (111 KB).

### Hợp đồng interface mà tầng đọc Excel mới BẮT BUỘC phải giữ

`build_app.py` bơm vào một mảng JSON, mỗi phần tử đúng 7 khóa viết tắt. Số lần từng khóa được dùng trong `app_template.html`:

| Khóa | Từ cột Excel | Kiểu | Số lần dùng | Ghi chú |
|---|---|---|---|---|
| `id` | B (STT) | number | 27 | **Khóa định danh.** Dùng làm key của `store.cards[id]` và `store.favorites[id]` trong localStorage |
| `w`  | C (Từ vựng tiếng Nhật) | string | 19 | Mặt trước flashcard, text đưa vào TTS |
| `r`  | D (読み方) | string | 7 | Furigana |
| `vi` | E (Nghĩa tiếng Việt) | string | 11 | Đáp án Quiz / Luyện nghe |
| `en` | F (Tiếng Anh tương ứng) | string | 4 | Gợi ý trong Quiz |
| `ex` | G (Câu hội thoại ≥ N3) | string | 14 | Nguồn cho module Luyện đọc + Kaiwa (`allWithEx()` lọc `ex.trim().length > 4`) |
| `c`  | *(KHÔNG có trong Excel)* | string | 4 | **Tự sinh** bởi hàm `category()` trong `build_app.py`: `外来語` / `漢字` / `その他` |

Tất cả 8 vị trí tham chiếu `VOCAB` trong template:

```text
257:  const VOCAB = /*__VOCAB__*/[];
848:  function pool(){ return curCat==='ALL'? VOCAB : VOCAB.filter(v=>v.c===curCat); }
850:  function allWithEx(){ return VOCAB.filter(function(v){return v.ex && v.ex.trim().length>4;}); }
930:  {id:'it_senmon', ... sub:function(){return 'Từ vựng IT chuyên ngành · '+VOCAB.length+' từ';} ...}
1291: setHeader('IT専門', 'Từ vựng IT chuyên ngành · '+VOCAB.length+' từ', true);
1443: var favList = VOCAB.filter(function(v){return isFavorite(v.id);});
2032: '...Tổng đã thuộc: '+learned+'/'+VOCAB.length+' từ · Streak '+(store.stats.streak||0)+'...'
2044: if(!VOCAB.length){ main.innerHTML='<div class="note">Chưa có dữ liệu từ vựng. Hãy chạy lại build_app.py.</div>'; }
```

Ngoài ra `build_app.py` còn thay 4 placeholder text trong template: `/*__VOCAB__*/[]`, `/*__GYOUMU__*/[]`, `__GEN_DATE__`, `__COUNT__`.

---

### Đoạn A — `app_template.html` dòng 205–360 (NGUYÊN VĂN)

```html
.sep{border:none;border-top:1px solid var(--line);margin:14px 0}

/* topic selection */
.topics{display:flex;flex-direction:column;gap:12px}
.topic-card{background:var(--card);border:1.5px solid var(--line);border-radius:16px;padding:18px 16px;
  cursor:pointer;box-shadow:var(--shadow);transition:.15s;display:flex;align-items:center;gap:14px;position:relative}
.topic-card:active{transform:scale(.98)}
.topic-card .tc-icon{font-size:32px;min-width:42px;text-align:center}
.topic-card .tc-body{flex:1}
.topic-card .tc-title{font-size:16px;font-weight:700}
.topic-card .tc-sub{font-size:12.5px;color:var(--sub);margin-top:2px}
.topic-card .tc-badge{position:absolute;top:10px;right:12px;font-size:10px;font-weight:700;border-radius:99px;padding:3px 10px}
.topic-card.active .tc-badge{background:#dcfce7;color:#166534}
.topic-card.soon{opacity:.65;cursor:default}
.topic-card.soon:active{transform:none}
.topic-card.soon .tc-badge{background:var(--soft);color:var(--sub)}

/* IT業務編 — audio player + transcript */
.player-card{background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:var(--shadow);
  padding:22px 20px;text-align:center;margin-bottom:14px}
.play-btn{background:var(--brand);border:none;border-radius:50%;width:72px;height:72px;font-size:28px;color:#fff;
  cursor:pointer;box-shadow:0 6px 20px rgba(37,99,235,.3);transition:.12s;margin-top:14px}
.play-btn:active{transform:scale(.93)}
.progress-row{display:flex;align-items:center;gap:8px;margin-top:16px}
.progress-row input[type=range]{flex:1;height:6px}
.progress-row .ptime{font-size:11.5px;color:var(--sub);min-width:34px}
.player-controls{display:flex;justify-content:center;gap:8px;margin-top:14px;flex-wrap:wrap}
.transcript-panel{background:var(--soft);border-radius:12px;padding:14px;margin-top:10px;text-align:left;
  max-height:320px;overflow-y:auto}
.transcript-line{font-size:14.5px;line-height:1.8;margin-bottom:6px}
.transcript-line b{color:var(--brand)}
</style>
</head>
<body>
<div class="app">
  <header>
    <div class="hrow">
      <button class="backbtn hidden" id="backBtn">← 戻る</button>
      <img class="header-logo hidden" id="headerLogo" alt="Kokoro Nihongo">
      <div>
        <h1 id="hTitle">ココロ日本語</h1>
        <div class="sub" id="hSub">Kokoro Nihongo · <span id="hCount">__COUNT__</span> từ</div>
      </div>
      <button class="settings-btn" id="settingsBtn" title="Cài đặt">⚙️ 設定</button>
    </div>
  </header>
  <main id="main"></main>
  <footer>Kokoro Nihongo v2.0 · __GEN_DATE__ · Dữ liệu từ 日本語の辞書.xlsx</footer>
</div>

<script>
/* ═══════════════ DATA ═══════════════ */
const VOCAB = /*__VOCAB__*/[];
const GYOUMU = /*__GYOUMU__*/[];
const GEN_DATE = "__GEN_DATE__";

/* ═══════════════ STORAGE / SRS ═══════════════ */
const LS_KEY = "jp_learn_v1";
const INTERVALS = [0, 1, 2, 4, 7, 15, 30];
let store = load();
if(!store.deckDone) store.deckDone={}; // migrate: user cũ chưa có field này
if(!store.favorites) store.favorites={}; // migrate: user cũ chưa có field này
function load(){
  try{ return JSON.parse(localStorage.getItem(LS_KEY)) || defaultStore(); }
  catch(e){ return defaultStore(); }
}
function defaultStore(){ return {cards:{},stats:{studied:0,streak:0,lastDay:null},deckDone:{},favorites:{}}; }
function save(){ localStorage.setItem(LS_KEY, JSON.stringify(store)); }
function today(){ return new Date().toISOString().slice(0,10); }
function cardState(id){
  if(!store.cards[id]) store.cards[id] = {box:0, due:today(), correct:0, seen:0, mastered:false};
  return store.cards[id];
}
function isMastered(id){ var c=store.cards[id]; return !!(c && c.mastered); }
function toggleMastered(id){ var c=cardState(id); c.mastered=!c.mastered; save(); return c.mastered; }
function isFavorite(id){ return !!store.favorites[id]; }
function toggleFavorite(id){
  if(store.favorites[id]) delete store.favorites[id]; else store.favorites[id]=true;
  save();
  return isFavorite(id);
}
function isDue(id){
  const c = store.cards[id];
  if(!c) return true;
  return c.due <= today();
}
function reviewCard(id, quality){
  const c = cardState(id);
  c.seen++;
  if(quality===0){ c.box=Math.max(0,c.box-1); }
  else if(quality===1){ /* stay */ }
  else if(quality===2){ c.box=Math.min(INTERVALS.length-1,c.box+1); c.correct++; }
  else { c.box=Math.min(INTERVALS.length-1,c.box+2); c.correct++; }
  const d = new Date(); d.setDate(d.getDate()+INTERVALS[c.box]);
  c.due = d.toISOString().slice(0,10);
  bumpStudied();
  save();
}
function bumpStudied(){
  const t=today();
  if(store.stats.lastDay!==t){
    const y=new Date(); y.setDate(y.getDate()-1);
    store.stats.streak = (store.stats.lastDay===y.toISOString().slice(0,10))? store.stats.streak+1 : 1;
    store.stats.lastDay=t;
  }
  store.stats.studied++;
}
function learnedCount(){ return Object.values(store.cards).filter(c=>c.box>=3||c.mastered).length; }
function dueCount(list){ return list.filter(v=>isDue(v.id)).length; }

/* Đánh dấu 1 bộ (deck) đã hoàn thành 1 mode — ns = namespace (category, hoặc '_reading'/'_kaiwa') */
function markDeckDone(ns, deckIdx, mode){
  if(!store.deckDone[ns]) store.deckDone[ns]={};
  if(!store.deckDone[ns][deckIdx]) store.deckDone[ns][deckIdx]={};
  store.deckDone[ns][deckIdx][mode]=true;
  save();
}
function deckDoneModes(ns, deckIdx){
  return (store.deckDone[ns] && store.deckDone[ns][deckIdx]) || {};
}

/* ═══════════════ TTS SETTINGS ═══════════════ */
const TTS_KEY = "kokoro_tts_settings";
let ttsSettings = loadTTS();
function loadTTS(){
  try{
    var s = JSON.parse(localStorage.getItem(TTS_KEY));
    if(s && s.mode) return Object.assign(defaultTTS(), s);
    return defaultTTS();
  } catch(e){ return defaultTTS(); }
}
function defaultTTS(){
  return {mode:'google', speed:0.9, pitch:1.0, gender:'female', voiceName:''};
}
function saveTTS(){ localStorage.setItem(TTS_KEY, JSON.stringify(ttsSettings)); }

/* ═══════════════ IT業務編 STORAGE (riêng biệt, không đụng jp_learn_v1) ═══════════════ */
const GY_LS_KEY = "kokoro_gyoumu_v1";
let gyStore = loadGyoumu();
function loadGyoumu(){
  try{ return JSON.parse(localStorage.getItem(GY_LS_KEY)) || defaultGyoumuStore(); }
  catch(e){ return defaultGyoumuStore(); }
}
function defaultGyoumuStore(){ return {listened:{}, read:{}}; }
function saveGyoumu(){ localStorage.setItem(GY_LS_KEY, JSON.stringify(gyStore)); }

/* ═══════════════ SPEECH (Google Translate TTS + Device fallback) ═══════════════ */
let allJaVoices=[];
let jaVoice=null;
let currentAudio=null;
let currentGyoumuAudio=null;

function loadJaVoices(){
  if(!('speechSynthesis' in window)) return;
  var vs=speechSynthesis.getVoices();
  allJaVoices = vs.filter(function(v){return v.lang==='ja-JP'||v.lang.startsWith('ja');});
```

---

### Đoạn B — `app_template.html` dòng 798–950 (NGUYÊN VĂN)

```html
/* text similarity for pronunciation scoring */
function normJa(s){ return (s||'').replace(/[、。「」『』（）\(\)\s.,!?！？・ー〜~]/g,''); }
function similarity(a,b){
  a=normJa(a); b=normJa(b);
  if(!a||!b) return 0;
  if(a===b) return 100;
  const m=a.length,n=b.length,dp=Array(n+1).fill(0);
  for(let i=1;i<=m;i++){let prev=0;for(let j=1;j<=n;j++){const t=dp[j];dp[j]=a[i-1]===b[j-1]?prev+1:Math.max(dp[j],dp[j-1]);prev=t;}}
  return Math.round(dp[n]/Math.max(m,n)*100);
}

/* ═══════════════ ÂM THANH PHẢN HỒI CHẤM ĐIỂM PHÁT ÂM (Web Audio API — không cần file âm thanh ngoài) ═══════════════ */
let sfxCtx=null;
function getSfxCtx(){
  var AC = window.AudioContext || window.webkitAudioContext;
  if(!AC) return null;
  if(!sfxCtx) sfxCtx = new AC();
  if(sfxCtx.state==='suspended') sfxCtx.resume();
  return sfxCtx;
}
function beep(freq, startTime, duration, gain){
  var ctx=getSfxCtx(); if(!ctx) return;
  var osc=ctx.createOscillator(), g=ctx.createGain();
  osc.type='sine'; osc.frequency.value=freq;
  var t0=ctx.currentTime+startTime;
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime(gain||0.2, t0+0.02);
  g.gain.exponentialRampToValueAtTime(0.0001, t0+duration);
  osc.connect(g); g.connect(ctx.destination);
  osc.start(t0); osc.stop(t0+duration+0.02);
}
/* Âm thanh theo mức điểm phát âm (LCS similarity): <50 nhắc thử lại (2 nốt trầm) · 51-89 khá tốt (1 nốt) · 90-100 xuất sắc (chuỗi 3 nốt lên) */
function playScoreSound(score){
  try{
    if(score>=90){ beep(784,0,0.12,0.22); beep(988,0.1,0.12,0.22); beep(1175,0.2,0.2,0.24); }
    else if(score>=51){ beep(660,0,0.18,0.2); }
    else { beep(311,0,0.16,0.18); beep(233,0.15,0.2,0.18); }
  }catch(e){}
}

/* ═══════════════ HELPERS ═══════════════ */
const $=s=>document.querySelector(s);
const main=$('#main'), backBtn=$('#backBtn'), hTitle=$('#hTitle'), hSub=$('#hSub'), headerLogo=$('#headerLogo');
(function(){ var fav=document.querySelector('link[rel="icon"]'); if(fav && headerLogo) headerLogo.src=fav.href; })();
let curCat='ALL';
let curDeck='ALL';
let deckPage=0;
let readingDeckPage=0;
let kaiwaDeckPage=0;
const DECK_SIZE=25;
function pool(){ return curCat==='ALL'? VOCAB : VOCAB.filter(v=>v.c===curCat); }
/* Luyện đọc/Kaiwa không lọc theo chủ đề — luôn dùng toàn bộ từ có câu ví dụ, không phụ thuộc curCat */
function allWithEx(){ return VOCAB.filter(function(v){return v.ex && v.ex.trim().length>4;}); }
/* Chia đều một mảng thành các "bộ" ~DECK_SIZE phần tử, dồn số dư rải đều thay vì dồn hết bộ cuối */
function splitDecks(arr, target){
  target = target || DECK_SIZE;
  var n = arr.length;
  if(n===0) return [];
  var numDecks = Math.max(1, Math.round(n/target));
  var base = Math.floor(n/numDecks), extra = n % numDecks;
  var decks = [], idx = 0;
  for(var i=0;i<numDecks;i++){
    var size = base + (i<extra?1:0);
    decks.push(arr.slice(idx, idx+size));
    idx += size;
  }
  return decks;
}
/* Chia CỐ ĐỊNH mỗi bộ đúng target từ, bắt đầu từ #1, bộ cuối = phần dư còn lại — dùng cho IT専門
   (đơn giản, dễ đoán vị trí, không dồn/san đều số dư như splitDecks() dùng cho Luyện đọc/Kaiwa) */
function splitDecksStrict(arr, target){
  target = target || DECK_SIZE;
  var decks=[];
  for(var i=0;i<arr.length;i+=target) decks.push(arr.slice(i,i+target));
  return decks;
}
function deckPool(){
  var p = pool();
  if(curDeck==='ALL') return p;
  var decks = splitDecksStrict(p);
  return decks[parseInt(curDeck,10)] || p;
}
/* Nhãn "Bộ N (start-end)" dùng cho header Flashcard khi đang học theo 1 Bộ cụ thể (rỗng nếu học "Tất cả") */
function curDeckRangeLabel(){
  if(curDeck==='ALL') return '';
  var decks = splitDecksStrict(pool());
  var idx = parseInt(curDeck,10);
  var d = decks[idx];
  if(!d) return '';
  var offset=0;
  for(var k=0;k<idx;k++) offset+=decks[k].length;
  return 'Bộ '+(idx+1)+' ('+(offset+1)+'-'+(offset+d.length)+')';
}

const DECK_GRID_PAGE_SIZE=4;
/* Lưới thẻ bộ dùng chung (IT専門 dashboard + Reading/Kaiwa library) — items:[{key,label,icons:[{icon,done}]}]
   Thẻ tự chuyển xanh lá (.done) khi TẤT CẢ icon truyền vào đều đã hoàn thành (IT専門: đủ 4 mode; Reading/Kaiwa: mode duy nhất của nó) */
function deckGridHTML(idPrefix, items, page){
  var totalPages = Math.max(1, Math.ceil(items.length/DECK_GRID_PAGE_SIZE));
  page = Math.max(0, Math.min(page, totalPages-1));
  var pageItems = items.slice(page*DECK_GRID_PAGE_SIZE, page*DECK_GRID_PAGE_SIZE+DECK_GRID_PAGE_SIZE);
  return '<div class="deck-grid-wrap">'+
    '<button class="pager-btn" id="'+idPrefix+'Prev"'+(page<=0?' disabled':'')+'>‹</button>'+
    '<div class="deck-grid">'+
      pageItems.map(function(it){
        var icons = it.icons.filter(function(i){return i.done;}).map(function(i){return '<span>'+i.icon+'</span>';}).join('');
        var allDone = it.icons.every(function(i){return i.done;});
        return '<button class="deck-card'+(allDone?' done':'')+(it.selected?' on':'')+'" data-key="'+it.key+'">'+
          '<div class="deck-icons">'+icons+'</div>'+
          '<div class="deck-label">'+it.label+'</div>'+
        '</button>';
      }).join('')+
    '</div>'+
    '<button class="pager-btn" id="'+idPrefix+'Next"'+(page>=totalPages-1?' disabled':'')+'>›</button>'+
  '</div>';
}
function shuffle(a){ a=a.slice(); for(let i=a.length-1;i>0;i--){const j=Math.random()*(i+1)|0;[a[i],a[j]]=[a[j],a[i]];} return a; }
function sample(arr,n,exclude){ return shuffle(arr.filter(x=>x!==exclude)).slice(0,n); }
function esc(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
let onBack=null;
backBtn.onclick=()=>{ stopSpeech(); if(onBack) onBack(); else home(); };
function setHeader(title,sub,showBack){
  hTitle.textContent=title; if(sub!==null) hSub.innerHTML=sub;
  backBtn.classList.toggle('hidden',!showBack);
  headerLogo.classList.toggle('hidden',showBack);
}

/* ═══════════════ TOPIC SELECTION (màn hình chính) ═══════════════ */
/* ═══════════════ MENU CHÍNH — registry để thêm chủ đề mới không phải sửa home() ═══════════════
   Thêm 1 chủ đề tương lai (kể cả dạng "Coming soon"): chỉ thêm 1 phần tử vào mảng này.
   "soon:true" hiện badge Coming soon + toast, không cần hàm open(). */
const MENU_MODULES = [
  {id:'it_senmon', icon:'💻', title:'IT専門', sub:function(){return 'Từ vựng IT chuyên ngành · '+VOCAB.length+' từ';}, open:homeDashboard},
  {id:'it_gyoumu', icon:'🏢', title:'IT業務編', sub:function(){return 'Hội thoại thực tế công việc IT · '+GYOUMU.length+' track';}, open:gyoumuDashboard},
  {id:'reading_lib', icon:'📖', title:'Luyện đọc', sub:function(){return 'Đọc câu ví dụ, nghe + lặp lại';}, open:readingLibrary},
  {id:'kaiwa_lib', icon:'💬', title:'Kaiwa', sub:function(){return 'Hội thoại ngắn từ câu ví dụ';}, open:kaiwaLibrary},
];

function home(){
  onBack=null;
  setHeader('ココロ日本語', 'Kokoro Nihongo · Chọn chủ đề', false);
  var learned=learnedCount();
  var gyListened=Object.keys(gyStore.listened).length;
  main.innerHTML=
    '<div class="stats">'+
      '<div class="stat"><div class="n">'+(store.stats.streak||0)+'</div><div class="l">Streak</div></div>'+
      '<div class="stat"><div class="n">'+learned+'</div><div class="l">Từ đã thuộc</div></div>'+
      '<div class="stat"><div class="n">'+gyListened+'</div><div class="l">Track đã nghe</div></div>'+
    '</div>'+
    '<div class="sectitle">Chọn chủ đề bạn muốn học</div>'+
    '<div class="topics">'+
      MENU_MODULES.map(function(m){
        return '<div class="topic-card '+(m.soon?'soon':'active')+'" data-topic="'+m.id+'">'+
```

---

## 4. Cấu trúc XML thật của `日本語の辞書.xlsx` (bản hiện tại, 2026-09-11)

Không phải code dự án, nhưng bắt buộc phải biết để viết lại tầng đọc — vì **định dạng file đã đổi so với bản mà app đang đọc được**.

Danh sách entry trong ZIP:

```text
docProps/app.xml                205 bytes
docProps/core.xml               602
xl/theme/theme1.xml           4,026
xl/worksheets/sheet1.xml    455,122
xl/styles.xml                 8,521
_rels/.rels                     531
xl/workbook.xml                 729
xl/_rels/workbook.xml.rels      504
[Content_Types].xml             975
```

→ **KHÔNG CÓ `xl/sharedStrings.xml`.** Đây chính là chỗ `build_app.py` chết.

- Sheet: `<sheet name="日本語の辞書" sheetId="1" state="visible" r:id="rId1"/>` (chỉ 1 sheet)
- Dimension: `<dimension ref="B1:P671"/>` — 671 dòng, dữ liệu từ vựng từ dòng 5 đến dòng 671
- Cột H..P có style nhưng rỗng hoàn toàn

Dòng tiêu đề (dòng 4) và dòng dữ liệu đầu tiên (dòng 5), nguyên văn XML:

```xml
<row r="4" ht="30" customFormat="1" customHeight="1" s="10"><c r="B4" s="16" t="inlineStr"><is><t>STT</t></is></c><c r="C4" s="17" t="inlineStr"><is><t>T&#7915; v&#7921;ng (Ti&#7871;ng Nh&#7853;t)</t></is></c><c r="D4" s="17" t="inlineStr"><is><t>&#35501;&#12415;&#26041; (C&#225;ch &#273;&#7885;c)</t></is></c><c r="E4" s="17" t="inlineStr"><is><t>Ngh&#297;a ti&#7871;ng Vi&#7879;t</t></is></c><c r="F4" s="17" t="inlineStr"><is><t>Ti&#7871;ng Anh t&#432;&#417;ng &#7913;ng</t></is></c><c r="G4" s="17" t="inlineStr"><is><t>C&#226;u h&#7897;i tho&#7841;i c&#7845;p &#273;&#7897; &gt;= N3</t></is></c><c r="I4" s="9" t="n"></c><c r="J4" s="9" t="n"></c><c r="K4" s="9" t="n"></c><c r="L4" s="9" t="n"></c><c r="M4" s="9" t="n"></c><c r="N4" s="9" t="n"></c><c r="O4" s="9" t="n"></c><c r="P4" s="9" t="n"></c></row>

<row r="5" ht="22.2" customHeight="1"><c r="B5" s="13" t="n"><v>1</v></c><c r="C5" s="12" t="inlineStr"><is><t>&#25215;&#35469;</t></is></c><c r="D5" s="12" t="inlineStr"><is><t>&#12375;&#12423;&#12358;&#12395;&#12435;</t></is></c><c r="E5" s="12" t="inlineStr"><is><t>Ph&#234; duy&#7879;t, ch&#7845;p thu&#7853;n</t></is></c><c r="F5" s="12" t="inlineStr"><is><t>Approval</t></is></c><c r="G5" s="12" t="inlineStr"><is><t>&#19978;&#21496;&#12398;&#25215;&#35469;&#12434;&#12418;&#12425;&#12387;&#12390;&#12363;&#12425;&#12289;&#22865;&#32004;&#26360;&#12395;&#12469;&#12452;&#12531;&#12375;&#12390;&#12367;&#12384;&#12373;&#12356;&#12290;</t></is></c></row>
```

So sánh với bản **đang commit trong git (2026-07-18)** — bản mà `build_app.py` đọc được:

| | Bản git (2026-07-18) | Bản hiện tại (2026-09-11) |
|---|---|---|
| `xl/sharedStrings.xml` | **CÓ** | **KHÔNG CÓ** |
| Kiểu ô chuỗi | `t="s"` + `<v>chỉ_số</v>` | `t="inlineStr"` + `<is><t>văn_bản</t></is>` |
| Số dòng sheet | 600 | 671 |
| Số từ vựng | 596 | 667 |

`build_app.py` đọc được bản trái, **chết ở bản phải**. Chi tiết ở `01_KHAO_SAT_APP.md` mục B.

---

## 5. Transcript IT業務編 (nguồn Excel thứ hai) — để tham khảo

`02_IT_Gyoumuhen/IT_Gyoumuhen_AudioCD_Transcript.xlsx`

- 1 sheet tên `AudioCD_Transcript`, 41 dòng, dữ liệu từ dòng 4, 38 track
- **Vẫn dùng `xl/sharedStrings.xml`** (chưa bị đổi định dạng) → nhánh `extract_gyoumu()` của `build_app.py` vẫn chạy được
- Cột: A=Track, B=Chapter, C=Unit, D=Unit tiếng Nhật, E=Unit tiếng Việt, F=Loại nội dung, G=Nhân vật, H=Nội dung hội thoại, I=Ghi chú
- Track 9 và 21 không có transcript (thiếu trang trong PDF gốc) — ô H ghi `(Không có nội dung...)`, code nhận diện bằng chuỗi này
