#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script: đọc 日本語の辞書.xlsx → sinh app học tiếng Nhật (1 file HTML offline).
Chạy lại mỗi khi từ điển có từ mới để cập nhật app.

Usage:
    python3 build_app.py            # đọc từ điển, kiểm tra, build ra HTML
    python3 build_app.py --check    # chỉ đọc và kiểm tra, KHÔNG ghi file nào
    python3 build_app.py --force    # bỏ qua cảnh báo, vẫn build
    python3 build_app.py --seed-lock <file.html>
                                    # tạo sổ khóa id từ một bản app đã build trước đó
                                    # (dùng 1 lần, để giữ đúng tiến độ học đang có)

────────────────────────────────────────────────────────────────────────────
TẦNG ĐỌC EXCEL (v2 — 2026-09-11)
────────────────────────────────────────────────────────────────────────────
Bản v1 chỉ đọc được file xlsx lưu theo kiểu sharedStrings + <v>số</v>.
Từ 2026-09-11 từ điển được lưu bằng công cụ khác, chuyển sang inlineStr và
bỏ hẳn xl/sharedStrings.xml → build chết với KeyError. Bản v2 sửa tận gốc:

  1. Đọc được CẢ 3 kiểu ô của chuẩn OOXML:
        t="s"          → chỉ số trỏ vào xl/sharedStrings.xml
        t="inlineStr"  → <is><t>văn bản</t></is>
        t="str" / số   → <v>giá trị</v>
     Kèm rich text (nhiều <r><t> trong một ô) và ô tự đóng <c .../>.
  2. Tìm cột theo TÊN TIÊU ĐỀ thay vì hardcode B/C/D/E/F/G
     → chèn thêm cột vào giữa file không làm app đọc nhầm dữ liệu.
  3. Có try/except và thông báo lỗi nói rõ phải làm gì.
  4. Kiểm tra chất lượng dữ liệu và in báo cáo trước khi ghi file.
  5. KHÓA ID THEO TỪ VỰNG (sổ khóa _id_lock.json).
     Tiến độ học trong localStorage khóa theo id. Bản v1 lấy id = STT cột B,
     nên xóa hay chèn một dòng giữa file là mọi id phía sau dịch theo, và tiến
     độ của từ A lặng lẽ gắn sang từ B. Đã xảy ra thật: so bản APK 2026-07-18
     với từ điển hôm nay, 47 trong 596 id trỏ sang từ khác.
     v2 giữ sổ khóa từ vựng → id. Từ nào đã có id thì giữ nguyên id đó vĩnh viễn,
     dù nó chuyển lên hay xuống bao nhiêu dòng trong Excel. Từ mới nhận id kế tiếp
     chưa ai dùng. Id của từ đã xóa không bao giờ được cấp lại cho từ khác.

ĐẦU RA KHÔNG ĐỔI: vẫn là mảng JSON 7 khóa {id, w, r, vi, en, ex, c}.
app_template.html không cần sửa một dòng nào.
"""
import zipfile, re, html, json, os, sys, datetime, shutil

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
SHADOW_JSON      = os.path.join(BASE, '06_ Shadowing_Jokyu', 'Shadowing_Data.json')
SHADOW_AUDIO_SRC = os.path.join(BASE, '06_ Shadowing_Jokyu', 'AudioMP3')
SHADOW_AUDIO_DST = os.path.join(AUDIO_DST, 'shadowing')
ID_LOCK     = os.path.join(HERE,    '_id_lock.json')          # sổ khóa: từ vựng → id cố định
REPORT      = os.path.join(HERE,    '_last_build_report.txt')


# ═══════════════════════════════════════════════════════════════════════════
#  In ra console an toàn — console Windows không phải lúc nào cũng nuốt được
#  tiếng Nhật; không để build chết chỉ vì một dòng log.
# ═══════════════════════════════════════════════════════════════════════════
_LOG = []


def say(msg=''):
    _LOG.append(msg)
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or 'ascii'
        print(msg.encode(enc, 'replace').decode(enc, 'replace'))


# ═══════════════════════════════════════════════════════════════════════════
#  Tầng đọc xlsx — dùng chung cho cả từ điển và transcript IT業務編
# ═══════════════════════════════════════════════════════════════════════════
_CELL_RE = re.compile(r'<c\b([^>]*?)(?:/>|>(.*?)</c>)', re.DOTALL)
_ROW_RE  = re.compile(r'<row\b([^>]*)>(.*?)</row>', re.DOTALL)
_REF_RE  = re.compile(r'\br="([A-Z]+)(\d+)"')
_T_RE    = re.compile(r'<t[^>]*>(.*?)</t>', re.DOTALL)
_V_RE    = re.compile(r'<v[^>]*>(.*?)</v>', re.DOTALL)


def _texts(xml_fragment):
    """Nối mọi <t> trong đoạn XML — xử lý luôn rich text (nhiều <r><t>)."""
    return html.unescape(''.join(_T_RE.findall(xml_fragment)))


def _load_shared_strings(z):
    """Đọc bảng chuỗi dùng chung. File lưu kiểu inlineStr KHÔNG có file này."""
    if 'xl/sharedStrings.xml' not in z.namelist():
        return []
    raw = z.read('xl/sharedStrings.xml').decode('utf-8')
    return [_texts(si) for si in re.findall(r'<si>.*?</si>', raw, re.DOTALL)]


def _first_sheet_path(z):
    """Lấy đúng file sheet đầu tiên thay vì đoán cứng là sheet1.xml."""
    names = [n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', n)]
    if not names:
        raise ValueError('File xlsx không có worksheet nào.')
    names.sort(key=lambda n: int(re.search(r'(\d+)\.xml$', n).group(1)))
    return names[0]


def read_sheet_rows(xlsx_path):
    """
    Đọc sheet đầu tiên của file xlsx.
    Trả về list [(số_dòng, {'A': 'text', ...}), ...]; ô rỗng không có trong dict.
    Hỗ trợ t="s" / t="inlineStr" / t="str" / số / t="b", rich text và ô tự đóng.
    """
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        shared = _load_shared_strings(z)
        sheet_xml = z.read(_first_sheet_path(z)).decode('utf-8')

    out = []
    for row_attrs, row_body in _ROW_RE.findall(sheet_xml):
        m = re.search(r'\br="(\d+)"', row_attrs)
        row_no = int(m.group(1)) if m else len(out) + 1
        cells = {}
        for attrs, body in _CELL_RE.findall(row_body):
            ref = _REF_RE.search(attrs)
            if not ref:
                continue
            col = ref.group(1)
            tm = re.search(r'\bt="([^"]+)"', attrs)
            t = tm.group(1) if tm else 'n'
            body = body or ''

            if t == 'inlineStr':
                val = _texts(body)
            elif t == 's':
                v = _V_RE.search(body)
                if not v:
                    continue
                try:
                    idx = int(v.group(1).strip())
                except ValueError:
                    continue
                val = shared[idx] if 0 <= idx < len(shared) else ''
            else:  # 'str' (kết quả công thức), 'n' (số), 'b' (luận lý), 'e' (lỗi)
                v = _V_RE.search(body)
                # vài công cụ ghi chuỗi vào <is> mà không khai t="inlineStr"
                val = html.unescape(v.group(1)) if v else _texts(body)

            val = val.strip()
            if val != '':
                cells[col] = val
        out.append((row_no, cells))
    out.sort(key=lambda x: x[0])
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  Tìm cột theo tên tiêu đề
# ═══════════════════════════════════════════════════════════════════════════
# Mỗi trường: danh sách từ khóa, khớp không phân biệt hoa thường, chỉ cần chứa.
HEADER_HINTS = {
    'id': ['stt', 'no.', 'số thứ tự'],
    'w':  ['từ vựng', '単語', 'tu vung'],
    'r':  ['読み方', 'cách đọc', 'cach doc', 'yomi', 'furigana'],
    'vi': ['nghĩa tiếng việt', 'tiếng việt', 'nghĩa', 'nghia'],
    'en': ['tiếng anh', 'english', 'tieng anh'],
    'ex': ['câu hội thoại', 'câu ví dụ', '例文', '会話', 'câu'],
}
LEGACY_COLS = {'id': 'B', 'w': 'C', 'r': 'D', 'vi': 'E', 'en': 'F', 'ex': 'G'}


def find_header(rows, max_scan=12):
    """
    Dò dòng tiêu đề trong 12 dòng đầu. Trả về (số_dòng_tiêu_đề, {trường: cột}).
    Không tìm thấy thì trả (None, None) để hàm gọi rơi về ánh xạ cột cũ.
    """
    best = None
    for row_no, cells in rows:
        if row_no > max_scan:
            break
        mapping, used = {}, set()
        for field, hints in HEADER_HINTS.items():
            for col, text in sorted(cells.items()):
                if col in used:
                    continue
                low = text.lower()
                if any(h in low for h in hints):
                    mapping[field] = col
                    used.add(col)
                    break
        # Cần tối thiểu 4 trường, trong đó phải có cột từ vựng và cột câu ví dụ
        if len(mapping) >= 4 and 'w' in mapping and 'ex' in mapping:
            if best is None or len(mapping) > len(best[1]):
                best = (row_no, mapping)
    return best if best else (None, None)


# ═══════════════════════════════════════════════════════════════════════════
#  Phân loại chữ viết (giữ nguyên hành vi bản cũ — app dùng làm tag hiển thị)
# ═══════════════════════════════════════════════════════════════════════════
def category(w):
    core = re.sub(r'[（）\(\)Ｖ\d\s、。/／・~〜]', '', w)
    if core and all(('ァ' <= c <= 'ヿ') or c == 'ー' for c in core):
        return "外来語"
    if any('一' <= c <= '鿿' for c in core):
        return "漢字"
    return "その他"


# ═══════════════════════════════════════════════════════════════════════════
#  Trích từ vựng
# ═══════════════════════════════════════════════════════════════════════════
JP_CHARS = re.compile(r'[぀-ヿ一-龥]')


def extract_vocab(dict_path):
    """Đọc từ điển → (vocab, issues, header_row, cols). vocab giữ nguyên 7 khóa."""
    if not os.path.isfile(dict_path):
        raise FileNotFoundError(
            "Không tìm thấy từ điển:\n    %s\n"
            "Tên file phải đúng là 日本語の辞書.xlsx và nằm ngay trong %s"
            % (dict_path, BASE))
    try:
        rows = read_sheet_rows(dict_path)
    except zipfile.BadZipFile:
        raise ValueError(
            "File không đọc được như một file Excel:\n    %s\n"
            "Nhiều khả năng file đang hỏng hoặc Excel chưa lưu xong. Đóng Excel rồi chạy lại."
            % dict_path)

    header_row, cols = find_header(rows)
    if cols is None:
        cols = dict(LEGACY_COLS)
        header_row = 4
        say("⚠ Không nhận ra dòng tiêu đề — dùng ánh xạ cột cũ B/C/D/E/F/G, đọc từ dòng 5.")
        say("  Nếu dữ liệu ra sai, kiểm tra lại 6 tiêu đề ở dòng 4 của file Excel.")
    else:
        missing = [f for f in ('id', 'w', 'r', 'vi', 'en', 'ex') if f not in cols]
        for f in missing:
            cols[f] = LEGACY_COLS[f]
        if missing:
            say("⚠ Không dò được tiêu đề cho: %s — tạm dùng cột mặc định %s."
                % (', '.join(missing), ', '.join(LEGACY_COLS[f] for f in missing)))

    vocab = []
    issues = {
        'empty': {k: [] for k in ('r', 'vi', 'en', 'ex')},
        'dup_word': [], 'dup_id': [], 'bad_id': [],
        'ex_no_jp': [], 'ex_missing_word': [], 'skipped_rows': 0,
    }
    seen_word, seen_id = {}, {}

    for row_no, cells in rows:
        if row_no <= header_row:
            continue
        word = cells.get(cols['w'], '')
        if not word:
            if cells:
                issues['skipped_rows'] += 1
            continue

        raw_id = cells.get(cols['id'], '')
        try:
            vid = int(float(raw_id))
        except (ValueError, TypeError):
            vid = len(vocab) + 1
            if raw_id:
                issues['bad_id'].append((row_no, word, raw_id))

        rec = {
            "id": vid,
            "w":  word,
            "r":  cells.get(cols['r'], ''),
            "vi": cells.get(cols['vi'], ''),
            "en": cells.get(cols['en'], ''),
            "ex": cells.get(cols['ex'], ''),
            "c":  category(word),
        }

        for k in ('r', 'vi', 'en', 'ex'):
            if not rec[k]:
                issues['empty'][k].append((row_no, word))
        if word in seen_word:
            issues['dup_word'].append((word, seen_word[word], row_no))
        else:
            seen_word[word] = row_no
        if vid in seen_id:
            issues['dup_id'].append((vid, seen_id[vid], row_no, word))
        else:
            seen_id[vid] = row_no
        if rec['ex'] and not JP_CHARS.search(rec['ex']):
            issues['ex_no_jp'].append((row_no, word, rec['ex']))
        if rec['ex'] and word not in rec['ex']:
            issues['ex_missing_word'].append((row_no, word))

        vocab.append(rec)

    if not vocab:
        raise ValueError(
            "Đọc được file nhưng KHÔNG có từ nào.\n"
            "  Dòng tiêu đề nhận ra: %s\n  Cột đang dùng: %s\n"
            "Kiểm tra xem cột từ vựng có đúng chỗ không." % (header_row, cols))
    return vocab, issues, header_row, cols


# ═══════════════════════════════════════════════════════════════════════════
#  Báo cáo chất lượng dữ liệu
# ═══════════════════════════════════════════════════════════════════════════
def report_issues(vocab, issues, header_row, cols):
    n = len(vocab)
    say("")
    say("─── Kiểm tra dữ liệu từ điển ───────────────────────────────────")
    say("  Dòng tiêu đề: %s   ·   Cột: %s"
        % (header_row, ", ".join("%s=%s" % kv for kv in cols.items())))
    say("  Đọc được: %d từ" % n)

    blockers = []
    if issues['dup_word']:
        blockers.append("%d từ bị trùng ở cột từ vựng" % len(issues['dup_word']))
        say("  ❌ Từ trùng: %d" % len(issues['dup_word']))
        for w, r1, r2 in issues['dup_word'][:5]:
            say("       %s  — dòng %d và dòng %d" % (w, r1, r2))
    if issues['dup_id']:
        blockers.append("%d STT bị trùng" % len(issues['dup_id']))
        say("  ❌ STT trùng: %d  (hai từ sẽ dùng chung một tiến độ học)" % len(issues['dup_id']))
        for vid, r1, r2, w in issues['dup_id'][:5]:
            say("       STT %s — dòng %d và dòng %d (%s)" % (vid, r1, r2, w))
    if issues['bad_id']:
        say("  ⚠ STT không phải số: %d — đã tự đánh số thay" % len(issues['bad_id']))
        for r, w, raw in issues['bad_id'][:3]:
            say("       dòng %d: %s → STT ghi '%s'" % (r, w, raw))

    for k, label in (('r', '読み方'), ('vi', 'nghĩa tiếng Việt'),
                     ('en', 'tiếng Anh'), ('ex', 'câu ví dụ')):
        lst = issues['empty'][k]
        if lst:
            say("  ⚠ Thiếu %s: %d dòng  (ví dụ: %s)"
                % (label, len(lst), ", ".join("dòng %d %s" % (r, w) for r, w in lst[:3])))

    if issues['ex_no_jp']:
        say("  ⚠ Câu ví dụ không có ký tự tiếng Nhật: %d  (bài nghe sẽ đọc sai)"
            % len(issues['ex_no_jp']))
        for r, w, ex in issues['ex_no_jp'][:3]:
            say("       dòng %d: %s → %s" % (r, w, ex[:40]))
    if issues['ex_missing_word']:
        say("  ℹ Câu ví dụ không chứa nguyên vẹn từ: %d (%.1f%%) — bình thường khi động từ bị chia"
            % (len(issues['ex_missing_word']), len(issues['ex_missing_word']) / n * 100))
    if issues['skipped_rows']:
        say("  ℹ Bỏ qua %d dòng có dữ liệu nhưng trống ô từ vựng" % issues['skipped_rows'])

    ids = [v['id'] for v in vocab]
    gaps = sorted(set(range(min(ids), max(ids) + 1)) - set(ids)) if ids else []
    if gaps:
        say("  ℹ STT bị hụt %d số: %s%s"
            % (len(gaps), ", ".join(map(str, gaps[:10])), "…" if len(gaps) > 10 else ""))

    clean = (not blockers and not any(issues['empty'].values()) and not issues['ex_no_jp'])
    if clean:
        say("  ✓ Không phát hiện vấn đề nào.")
    say("────────────────────────────────────────────────────────────────")
    return blockers


# ═══════════════════════════════════════════════════════════════════════════
#  SỔ KHÓA ID  —  từ vựng → id cố định
#
#  Tiến độ học trong localStorage khóa theo id (store.cards[id], favorites[id]).
#  Nếu id đổi thì tiến độ của từ A lặng lẽ gắn sang từ B. Bản v1 lấy id = STT,
#  nên chỉ cần xóa một dòng giữa file là mọi id phía sau dịch theo.
#  Sổ khóa giải quyết tận gốc: mỗi từ giữ đúng một id suốt đời, bất kể nó nằm
#  ở dòng nào trong Excel.
# ═══════════════════════════════════════════════════════════════════════════
_PAREN_RE = re.compile(r'[（(][^）)]*[)）]')


def _norm_word(w):
    """Chuẩn hóa để nhận ra từ chỉ bị sửa phần chú thích trong ngoặc."""
    return _PAREN_RE.sub('', w).replace('　', '').replace(' ', '').strip()


def load_lock():
    if not os.path.isfile(ID_LOCK):
        return None
    try:
        with open(ID_LOCK, 'r', encoding='utf-8') as f:
            d = json.load(f)
        if isinstance(d.get('map'), dict) and d['map']:
            return d
    except Exception:
        pass
    return None


def save_lock(lock):
    with open(ID_LOCK, 'w', encoding='utf-8') as f:
        json.dump({'saved': datetime.datetime.now().isoformat(timespec='seconds'),
                   'next_id': lock['next_id'], 'count': len(lock['map']), 'map': lock['map']},
                  f, ensure_ascii=False, indent=0)


def vocab_from_html(html_path):
    """Đọc mảng VOCAB nhúng trong một bản app đã build — dùng cho --seed-lock."""
    with open(html_path, 'r', encoding='utf-8') as f:
        h = f.read()
    i = h.find('/*__VOCAB__*/')
    if i < 0:
        raise ValueError('File này không phải bản app đã build (không thấy /*__VOCAB__*/).')
    s = h.index('[', i)
    depth = 0
    for k in range(s, len(h)):
        if h[k] == '[':
            depth += 1
        elif h[k] == ']':
            depth -= 1
            if depth == 0:
                return json.loads(h[s:k + 1])
    raise ValueError('Mảng VOCAB trong file bị cắt dở.')


def seed_lock_from_html(html_path):
    v = vocab_from_html(html_path)
    m = {}
    for x in v:
        w, i = x.get('w'), x.get('id')
        if w and isinstance(i, int):
            m[w] = i
    if not m:
        raise ValueError('Không lấy được từ vựng nào từ file.')
    lock = {'map': m, 'next_id': max(m.values()) + 1}
    save_lock(lock)
    say('✓ Đã tạo sổ khóa id từ: %s' % html_path)
    say('  %d từ, id cao nhất %d, id kế tiếp sẽ cấp là %d' % (len(m), max(m.values()), lock['next_id']))
    say('  Lưu tại: %s' % ID_LOCK)
    return lock


def apply_id_lock(vocab):
    """Gán id theo sổ khóa. Ghi đè trường id vốn lấy từ STT. Trả về (lock, stats)."""
    lock = load_lock()
    stats = {'reused': 0, 'renamed': [], 'new': [], 'orphan': [], 'first_time': False}

    if lock is None:
        # Lần đầu: chốt sổ khóa theo đúng STT hiện tại của file.
        m = {}
        for v in vocab:
            m[v['w']] = v['id']
        lock = {'map': m, 'next_id': (max(m.values()) + 1) if m else 1}
        stats['first_time'] = True
        return lock, stats

    m = lock['map']
    next_id = int(lock.get('next_id') or (max(m.values()) + 1))

    # Khớp chính xác trước
    unmatched = []
    for v in vocab:
        if v['w'] in m:
            v['id'] = m[v['w']]
            stats['reused'] += 1
        else:
            unmatched.append(v)

    # Khớp vòng hai: từ chỉ bị sửa phần chú thích trong ngoặc.
    # Chỉ nhận khi cả hai phía đều duy nhất, tránh ghép nhầm.
    present = set(v['w'] for v in vocab)
    free_old = [w for w in m if w not in present]
    on, nn = {}, {}
    for w in free_old:
        on.setdefault(_norm_word(w), []).append(w)
    for v in unmatched:
        nn.setdefault(_norm_word(v['w']), []).append(v)
    for key, olds in on.items():
        news = nn.get(key)
        if len(olds) == 1 and news and len(news) == 1 and key:
            old_w, v = olds[0], news[0]
            v['id'] = m[old_w]
            m[v['w']] = m[old_w]
            del m[old_w]
            stats['renamed'].append((old_w, v['w'], v['id']))

    # Còn lại là từ thật sự mới → cấp id chưa ai dùng bao giờ
    for v in vocab:
        if v['w'] not in m:
            v['id'] = next_id
            m[v['w']] = next_id
            stats['new'].append((v['w'], next_id))
            next_id += 1

    present = set(v['w'] for v in vocab)
    stats['orphan'] = [(w, m[w]) for w in m if w not in present]

    # Bất biến: id không được trùng nhau
    ids = [v['id'] for v in vocab]
    if len(ids) != len(set(ids)):
        dup = [i for i, c in __import__('collections').Counter(ids).items() if c > 1]
        raise ValueError('Lỗi nội bộ: sổ khóa cấp trùng id %s. Xóa %s rồi chạy lại.' % (dup[:5], ID_LOCK))

    lock['next_id'] = next_id
    return lock, stats


def report_lock(stats, vocab):
    say('')
    say('─── Sổ khóa id ────────────────────────────────────────────────')
    if stats['first_time']:
        say('  ℹ Chưa có sổ khóa. Lần này chốt theo đúng STT hiện tại của file.')
        say('    Từ lần sau, mỗi từ giữ nguyên id dù đổi vị trí dòng trong Excel.')
        say('    LƯU Ý: nếu anh đã có tiến độ học trong app, hãy tạo sổ khóa từ')
        say('    chính bản app đang dùng trước đã:')
        say('        python3 build_app.py --seed-lock ../../03_Android_App/www/index.html')
    else:
        say('  Giữ nguyên id: %d từ   ·   Cấp id mới: %d từ   ·   Nhận ra đổi tên: %d'
            % (stats['reused'], len(stats['new']), len(stats['renamed'])))
        for old_w, new_w, i in stats['renamed'][:5]:
            say('     đổi tên, giữ id %d:  %s  →  %s' % (i, old_w, new_w))
        if stats['new']:
            ids = [i for _, i in stats['new']]
            say('     id mới cấp: %d đến %d' % (min(ids), max(ids)))
        if stats['orphan']:
            say('  ⚠ %d từ có trong sổ khóa nhưng không còn trong Excel:' % len(stats['orphan']))
            for w, i in stats['orphan'][:6]:
                say('       id %d  %s' % (i, w))
            say('    Tiến độ học của các từ này nằm lại trong localStorage nhưng không dùng tới.')
            say('    Id của chúng KHÔNG bao giờ được cấp lại cho từ khác.')
        say('  ✓ Mọi từ đã học giữ đúng id — tiến độ trong app không bị gắn nhầm.')
    say('────────────────────────────────────────────────────────────────')



# ═══════════════════════════════════════════════════════════════════════════
#  Trích transcript IT業務編 (đọc, KHÔNG ghi lại file xlsx)
#  Dùng chung tầng đọc mới nên file này lưu kiểu nào cũng đọc được.
# ═══════════════════════════════════════════════════════════════════════════
_LINE_RE = re.compile(r'^([^：:]+)[：:]\s*(.*)$')


def _split_lines(text):
    lines = []
    for raw in re.split(r'\r\n|\r|\n', text):
        raw = raw.strip()
        if not raw:
            continue
        m = _LINE_RE.match(raw)
        if m:
            lines.append({"spk": m.group(1).strip(), "t": m.group(2).strip()})
        else:
            lines.append({"spk": "", "t": raw})
    return lines


def extract_gyoumu(xlsx_path):
    rows = read_sheet_rows(xlsx_path)
    tracks = []
    for row_no, cells in rows:
        if row_no < 4:
            continue
        track_str = cells.get('A', '')
        if not track_str:
            continue
        try:
            track_no = int(float(track_str))
        except ValueError:
            continue
        dialogue = cells.get('H', '')
        has_transcript = bool(dialogue) and not dialogue.strip().startswith('(Không có nội dung')
        chapter_m = re.search(r'(\d+)', cells.get('B', ''))
        unit_m    = re.search(r'(\d+)', cells.get('C', ''))
        tracks.append({
            "track":   track_no,
            "chapter": int(chapter_m.group(1)) if chapter_m else 0,
            "unit":    int(unit_m.group(1)) if unit_m else 0,
            "unitJp":  cells.get('D', ''),
            "unitVi":  cells.get('E', ''),
            "type":    cells.get('F', ''),
            "chars":   cells.get('G', ''),
            "hasTranscript": has_transcript,
            "lines":   _split_lines(dialogue) if has_transcript else [],
            "note":    cells.get('I', ''),
        })
    tracks.sort(key=lambda t: t['track'])
    return tracks


# ═══════════════════════════════════════════════════════════════════════════
#  Trích dữ liệu Shadowing (FR_013) — đọc thẳng JSON đã đúng schema, không parse xlsx
# ═══════════════════════════════════════════════════════════════════════════
def extract_shadow():
    if not os.path.isfile(SHADOW_JSON):
        say("⚠ Không tìm thấy dữ liệu Shadowing: %s — build tiếp với 0 đoạn." % SHADOW_JSON)
        return []
    try:
        with open(SHADOW_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('units', [])
    except Exception as e:
        say("⚠ Không đọc được dữ liệu Shadowing (%s) — build tiếp với 0 đoạn." % e)
        return []


# ─── Copy audio (AudioCD/, AudioMP3/ → audio/ cạnh HTML output) ────────
def _copy_audio_dir(src, dst, label):
    if not os.path.isdir(src):
        say("⚠ %s audio source folder not found: %s — bỏ qua copy audio." % (label, src))
        return 0
    os.makedirs(dst, exist_ok=True)
    copied = 0
    for fname in os.listdir(src):
        if not fname.lower().endswith('.mp3'):
            continue
        s = os.path.join(src, fname)
        d = os.path.join(dst, fname)
        if os.path.exists(d) and os.path.getsize(d) == os.path.getsize(s):
            continue
        shutil.copy2(s, d)
        copied += 1
    return copied


def sync_audio():
    n1 = _copy_audio_dir(AUDIO_SRC, AUDIO_DST, "IT業務編")
    say("✓ Audio synced: %d file(s) copied to %s" % (n1, AUDIO_DST))
    n2 = _copy_audio_dir(SHADOW_AUDIO_SRC, SHADOW_AUDIO_DST, "Shadowing")
    say("✓ Shadowing audio synced: %d file(s) copied to %s" % (n2, SHADOW_AUDIO_DST))


# ═══════════════════════════════════════════════════════════════════════════
#  Build
# ═══════════════════════════════════════════════════════════════════════════
def _write_report():
    try:
        with open(REPORT, 'w', encoding='utf-8') as f:
            f.write("Build report — %s\n" % datetime.datetime.now().isoformat(timespec='seconds'))
            f.write("\n".join(_LOG) + "\n")
    except Exception:
        pass


def main():
    argv = sys.argv[1:]
    args = set(argv)
    force = '--force' in args
    check_only = '--check' in args

    # ── Chế độ tạo sổ khóa id từ một bản app đã build (chạy 1 lần) ──
    if '--seed-lock' in argv:
        i = argv.index('--seed-lock')
        if i + 1 >= len(argv):
            say("❌ Thiếu đường dẫn. Ví dụ:")
            say("   python3 build_app.py --seed-lock ../../03_Android_App/www/index.html")
            sys.exit(1)
        src = argv[i + 1]
        if not os.path.isfile(src):
            say("❌ Không tìm thấy file: %s" % src)
            sys.exit(1)
        if os.path.isfile(ID_LOCK) and not force:
            say("❌ Sổ khóa đã tồn tại: %s" % ID_LOCK)
            say("   Ghi đè sẽ làm lệch tiến độ học. Nếu chắc chắn, thêm --force.")
            sys.exit(1)
        try:
            seed_lock_from_html(src)
        except Exception as e:
            say("❌ %s" % e)
            _write_report()
            sys.exit(1)
        _write_report()
        return

    say("Từ điển: %s" % DICT)
    try:
        vocab, issues, header_row, cols = extract_vocab(DICT)
    except Exception as e:
        say("")
        say("❌ KHÔNG ĐỌC ĐƯỢC TỪ ĐIỂN")
        say(str(e))
        _write_report()
        sys.exit(1)

    blockers = report_issues(vocab, issues, header_row, cols)
    try:
        lock, lock_stats = apply_id_lock(vocab)
    except Exception as e:
        say("")
        say("❌ %s" % e)
        _write_report()
        sys.exit(1)
    report_lock(lock_stats, vocab)

    if blockers and not force:
        say("")
        say("❌ DỪNG BUILD — dữ liệu có lỗi chặn: " + "; ".join(blockers))
        say("   Sửa trong Excel rồi chạy lại, hoặc dùng --force để bỏ qua.")
        _write_report()
        sys.exit(1)

    if check_only:
        say("")
        say("✓ Chế độ --check: dữ liệu đọc được, KHÔNG ghi file nào.")
        _write_report()
        return

    try:
        gyoumu = extract_gyoumu(GYOUMU_XLSX) if os.path.isfile(GYOUMU_XLSX) else []
    except Exception as e:
        say("⚠ Không đọc được transcript IT業務編 (%s) — build tiếp với 0 track." % e)
        gyoumu = []

    shadow = extract_shadow()
    shadow_segcount = sum(len(t['segments']) for u in shadow for s in u['sections'] for t in s['tracks'])

    sync_audio()

    if not os.path.isfile(TEMPLATE):
        say("❌ Không tìm thấy template: %s" % TEMPLATE)
        _write_report()
        sys.exit(1)

    gen_date  = datetime.date.today().isoformat()
    data_js   = json.dumps(vocab,  ensure_ascii=False)
    gyoumu_js = json.dumps(gyoumu, ensure_ascii=False)
    shadow_js = json.dumps(shadow, ensure_ascii=False)

    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        tpl = f.read()

    for ph in ('/*__VOCAB__*/[]', '/*__GYOUMU__*/[]', '/*__SHADOW__*/[]', '__GEN_DATE__', '__COUNT__'):
        if ph not in tpl:
            say("❌ Template thiếu placeholder %s — app_template.html có bị sửa nhầm không?" % ph)
            _write_report()
            sys.exit(1)

    out = tpl.replace('/*__VOCAB__*/[]',  '/*__VOCAB__*/'  + data_js)
    out = out.replace('/*__GYOUMU__*/[]', '/*__GYOUMU__*/' + gyoumu_js)
    out = out.replace('/*__SHADOW__*/[]', '/*__SHADOW__*/' + shadow_js)
    out = out.replace('__GEN_DATE__', gen_date)
    out = out.replace('__COUNT__', str(len(vocab)))

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(out)

    save_lock(lock)
    say("")
    say("✓ Built app with %d words + %d IT業務編 tracks + %d shadowing segments → %s"
        % (len(vocab), len(gyoumu), shadow_segcount, OUT))
    _write_report()


if __name__ == '__main__':
    main()
