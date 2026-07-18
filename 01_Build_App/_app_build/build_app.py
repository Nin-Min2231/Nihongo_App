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
