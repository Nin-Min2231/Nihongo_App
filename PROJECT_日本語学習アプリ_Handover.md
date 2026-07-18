# PROJECT — App học tiếng Nhật (日本語学習アプリ) · Tài liệu handover

> **Mục đích tài liệu:** Ghi lại toàn bộ bản chất vấn đề & quy trình, từ khâu **tạo/dịch từ vựng** → **ghi vào từ điển Excel** → **build ra app học trên điện thoại**. Đọc file này là một chat Claude mới hiểu ngay context, không cần giải thích lại.
> **Đối tượng đọc:** Claude (chat mới) hoặc chính người dùng.
> **Người dùng:** NguyenNC — PM/BrSE ngành IT (cầu nối VN ⇄ Nhật).

---

## 1. Tổng quan mục tiêu (Big picture)

Người dùng tích lũy từ vựng tiếng Nhật (chủ yếu thuật ngữ IT/PM) trong quá trình làm việc. Luồng mong muốn:

```
Từ tiếng Nhật mới (dịch/upload)
        │  ①  DỊCH  (skill translator-ja-vi-en)
        ▼
日本語の辞書.xlsx   ← từ điển cá nhân (giữ nguyên format/màu)
        │  ②  BUILD  (build_app.py + app_template.html)
        ▼
Kokoro_Nihongo.html  ← app học chạy trên điện thoại (offline)
```

Output chính:
1. **`日本語の辞書.xlsx`** — từ điển (nguồn dữ liệu gốc), nằm ở connected folder `D:\01_NguyenNC\10_Claude\100_日本語\`.
2. **`Kokoro_Nihongo.html`** — app học (tên hiện tại), sinh ra từ từ điển, nằm ở `100_日本語\01_Build_App\`.

Bộ script build: `100_日本語\01_Build_App\_app_build\` (gồm `build_app.py` + `app_template.html`). Yêu cầu nâng cấp: `100_日本語\01_Build_App\_feature_requests\`.

> **Ghi chú lịch sử tên:** app ban đầu tên `日本語学習アプリ.html` ở thư mục gốc, sau được đổi tên thành **`Kokoro_Nihongo.html`** và chuyển vào `01_Build_App/`. Nếu thấy tài liệu cũ nhắc `日本語学習アプリ.html` thì hiểu là cùng một app.

---

## 2. Đường dẫn & quy ước path (RẤT QUAN TRỌNG)

Cowork map path Windows ↔ Linux sandbox khác nhau. Path Linux (`/sessions/.../mnt/`) **thay đổi theo từng session** (phần tên như `fervent-brave-mendel`). Mỗi session mới phải kiểm tra lại prefix mount bằng `ls /sessions/*/mnt/`.

| Vai trò | Path Windows (người dùng thấy) | Path Bash (Linux sandbox) |
|---|---|---|
| Connected folder | `D:\01_NguyenNC\10_Claude\100_日本語\` | `/sessions/<session>/mnt/100_日本語/` |
| Từ điển | `...\100_日本語\日本語の辞書.xlsx` | `/sessions/<session>/mnt/100_日本語/日本語の辞書.xlsx` |
| App | `...\100_日本語\01_Build_App\Kokoro_Nihongo.html` | `/sessions/<session>/mnt/100_日本語/01_Build_App/Kokoro_Nihongo.html` |
| Build tools | `...\01_Build_App\_app_build\` | `/sessions/<session>/mnt/100_日本語/01_Build_App/_app_build/` |
| Feature requests | `...\01_Build_App\_feature_requests\` | `/sessions/<session>/mnt/100_日本語/01_Build_App/_feature_requests/` |

> **Nguyên tắc ghi file:** luôn ghi ra `/tmp/` trước → `shutil.copy2()` đè lại connected folder (tránh lock file trên Windows). Từ điển **luôn ghi đè** file gốc, không lưu ra tên khác.

---

## 3. GIAI ĐOẠN ① — Dịch từ mới & ghi vào từ điển

### 3.1. Cấu trúc file `日本語の辞書.xlsx`

- Sheet name: `日本語の辞書`
- **Row 2:** title/header (B2:C2 merged = "日本語の辞書", D2="作成者:", E2="NguyenNC", F2="最終更新日:", G2=ngày)
- **Row 3:** trống (separator)
- **Row 4:** header cột (B4:G4)
- **Row 5 trở đi:** dữ liệu từ vựng

Mapping cột:

| Cột | Nội dung | Style trong XML |
|---|---|---|
| B | STT (số, tự tăng) | `s="18"` (numeric) |
| C | Từ vựng (tiếng Nhật) | `s="19" t="s"` (shared string) |
| D | 読み方 (cách đọc) | `s="19" t="s"` |
| E | Nghĩa tiếng Việt | `s="19" t="s"` |
| F | Tiếng Anh tương ứng | `s="19" t="s"` |
| G | Câu hội thoại ví dụ (>= N3) | `s="19" t="s"` |

Font gốc: **Noto Sans JP 12pt** (KHÔNG hardcode font — để nguyên style của file).

### 3.2. Bản chất kỹ thuật: xlsx = ZIP (điểm mấu chốt nhất)

> File `.xlsx` thực chất là **một archive ZIP** chứa nhiều file XML. Nếu dùng `openpyxl.save()` để lưu lại, nó **rewrite `styles.xml` và `theme/theme1.xml`** → **MẤT toàn bộ màu nền, border, theme color**. Đây là lỗi đã gặp nhiều lần.

**Giải pháp (BẮT BUỘC):** Chỉ sửa **raw string** trên đúng 2 file XML, giữ nguyên byte tất cả file còn lại:

```
xlsx (ZIP)
├── xl/worksheets/sheet1.xml   ← CHỈ sửa (thêm <row> mới)
├── xl/sharedStrings.xml       ← CHỈ sửa (thêm <si> mới)
├── xl/styles.xml              ← KHÔNG CHẠM (chứa style/màu)
├── xl/theme/theme1.xml        ← KHÔNG CHẠM (theme color)
└── [các file khác]            ← KHÔNG CHẠM (giữ binary)
```

**Lưu ý phụ:**
- KHÔNG dùng lxml để parse/serialize lại (làm hỏng namespace → Excel báo "We found a problem").
- Chỉ dùng `str.replace()` / `re` trên chuỗi thô.
- Lấy `s=` và `t=` attribute từ **row cuối cùng đang có** để copy đúng style — KHÔNG hardcode.
- Cập nhật `count`/`uniqueCount` trong thẻ `<sst>` của sharedStrings.

### 3.3. Code chuẩn ghi từ mới vào từ điển (giữ nguyên format)

```python
import zipfile, shutil, re, html

DICT = '/sessions/<session>/mnt/100_日本語/日本語の辞書.xlsx'
TMP  = '/tmp/jisho_tmp.xlsx'

# đọc toàn bộ file trong ZIP
with zipfile.ZipFile(DICT, 'r') as z:
    all_files  = {n: z.read(n) for n in z.namelist()}
sheet_raw  = all_files['xl/worksheets/sheet1.xml'].decode('utf-8')
shared_raw = all_files['xl/sharedStrings.xml'].decode('utf-8')

def get_si_text(si_xml):
    return html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si_xml, re.DOTALL)))
def xml_escape(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

# từ đã có (tránh trùng) — quét toàn bộ shared strings
existing = set(get_si_text(s) for s in re.findall(r'<si>.*?</si>', shared_raw, re.DOTALL))

# style + số liệu của row cuối
rows_found     = re.findall(r'(<row[^>]*r="(\d+)"[^>]*>.*?</row>)', sheet_raw, re.DOTALL)
last_row_xml   = rows_found[-1][0]
last_row_num   = int(rows_found[-1][1])
cells_attr     = re.findall(r'<c r="[A-Z]\d+"([^>]*)>', last_row_xml)   # -> [' s="18"', ' s="19" t="s"', ...]
row_attrs_base = re.search(r'<row([^>]*)>', last_row_xml).group(1)
last_stt       = int(re.search(r'<c r="B\d+"[^>]*><v>(\d+)</v>', last_row_xml).group(1))

# to_add = list các tuple (vocab, reading, nghia_vi, eng, example)
for i, (vocab, reading, vi, en, ex) in enumerate(to_add):
    si  = shared_raw.count('<si>')          # index shared string mới
    stt = last_stt + 1 + i
    nr  = last_row_num + 1 + i
    new_si = ''.join(f'<si><t xml:space="preserve">{xml_escape(v)}</t></si>'
                     for v in [vocab, reading, vi, en, ex])
    shared_raw = shared_raw.replace('</sst>', new_si + '</sst>')
    row_attrs = re.sub(r'r="\d+"', f'r="{nr}"', row_attrs_base)
    cells = (
        f'<c r="B{nr}"{cells_attr[0]}><v>{stt}</v></c>'
        f'<c r="C{nr}"{cells_attr[1]}><v>{si}</v></c>'
        f'<c r="D{nr}"{cells_attr[2]}><v>{si+1}</v></c>'
        f'<c r="E{nr}"{cells_attr[3]}><v>{si+2}</v></c>'
        f'<c r="F{nr}"{cells_attr[4]}><v>{si+3}</v></c>'
        f'<c r="G{nr}"{cells_attr[5]}><v>{si+4}</v></c>'
    )
    sheet_raw = sheet_raw.replace('</sheetData>', f'<row{row_attrs}>{cells}</row></sheetData>')

# cập nhật count/uniqueCount
total_si = shared_raw.count('<si>')
shared_raw = re.sub(
    r'(<sst[^>]+count=")\d+("[^>]+uniqueCount=")\d+(")',
    lambda m: f'{m.group(1)}{total_si+1}{m.group(2)}{total_si}{m.group(3)}',
    shared_raw)

# ghi: chỉ replace 2 XML, giữ nguyên phần còn lại
with zipfile.ZipFile(TMP, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in all_files.items():
        if   name == 'xl/worksheets/sheet1.xml': zout.writestr(name, sheet_raw.encode('utf-8'))
        elif name == 'xl/sharedStrings.xml':     zout.writestr(name, shared_raw.encode('utf-8'))
        else:                                     zout.writestr(name, data)
shutil.copy2(TMP, DICT)   # ghi đè file gốc
```

### 3.4. Quy tắc dịch (skill `translator-ja-vi-en`)

- Dịch nghĩa, không dịch từng chữ; ưu tiên Hán-Việt khi phù hợp.
- Mỗi từ điền đủ: 読み方 (cách đọc) + nghĩa Việt + tiếng Anh + câu ví dụ >= N3.
- Katakana → cột tiếng Anh ghi từ gốc (セキュリティ → Security).
- Giữ nguyên mã số, tên riêng, thuật ngữ IT.
- Câu ví dụ: nếu file nguồn có 例文 hợp lệ (thuần tiếng Nhật, đúng ngữ pháp) thì ưu tiên dùng; nếu sai/thiếu/lẫn tiếng Việt-Anh thì sửa lại đúng hoặc tự tạo câu N3 phù hợp ngữ cảnh.
- Chỉ thêm từ **chưa có** trong từ điển (kiểm tra cột C / shared strings).

### 3.5. Khi nhập từ từ file Excel upload (VD: `Untitled spreadsheet.xlsx`)

Cách parse đã dùng (an toàn với ô rich-text, entity `&amp;`, ô numeric):

```python
def si_text(si_xml):  # xử lý cả <t> và <r><t> (rich text)
    return html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si_xml, re.DOTALL)))

def get_cell(rx, col, str_list):
    cells = re.findall(r'<c r="'+col+r'\d+"([^>]*)>(.*?)</c>', rx, re.DOTALL)
    if not cells: return ''
    attrs, content = cells[0]
    v = re.search(r'<v>(.*?)</v>', content)
    if not v: return ''
    raw = v.group(1).strip()
    if 't="s"' in attrs:                    # shared string → tra index
        i = int(raw); return str_list[i] if 0 <= i < len(str_list) else ''
    return raw                              # numeric → giá trị trực tiếp
```

- Cột A = 日本語 (từ để dịch), cột B = 例文 (câu ví dụ).
- Làm sạch 例文: bỏ dòng lẫn tiếng Việt (regex dấu thanh) / tiếng Anh, chỉ giữ dòng thuần Nhật.
- Từ có nhiều dạng ngăn bằng xuống dòng (VD `貼付\n貼り付ける`) → chuẩn hóa `\n` → `/`.

---

## 4. GIAI ĐOẠN ② — Build app từ từ điển

### 4.1. Kiến trúc

App = **1 file HTML tự chứa (self-contained), offline, không phụ thuộc thư viện ngoài** — hợp lý nhất cho điện thoại (mở bằng Chrome → Add to Home Screen như PWA). Không chọn native app vì cần môi trường dev phức tạp, không giao ngay được.

Dữ liệu từ vựng được **nhúng cứng dưới dạng JSON** vào file HTML lúc build (không fetch runtime — tránh lỗi CORS file:// trên điện thoại).

Bộ build 2 file:
- **`build_app.py`** — đọc `日本語の辞書.xlsx`, trích toàn bộ từ (row 5+), tự phân loại (category), inject JSON + ngày build vào template.
- **`app_template.html`** — khung app (CSS + JS), chứa 3 placeholder được thay lúc build:
  - `/*__VOCAB__*/[]` → mảng JSON từ vựng
  - `__GEN_DATE__` → ngày build (YYYY-MM-DD)
  - `__COUNT__` → tổng số từ

Cấu trúc mỗi record JSON: `{id, w(từ), r(読み方), vi, en, ex(ví dụ), c(category)}`.
Category tự động: `外来語` (toàn katakana) / `漢字` (có kanji) / `その他`.

### 4.2. build_app.py — điểm cốt lõi

```python
# đọc xlsx bằng raw ZIP/XML (giống mục 3.3), lấy row >= 5
# category(w): toàn katakana → "外来語"; có kanji → "漢字"; còn lại → "その他"
# vocab = [{id, w, r, vi, en, ex, c}, ...]
data_js = json.dumps(vocab, ensure_ascii=False)
out = tpl.replace('/*__VOCAB__*/[]', '/*__VOCAB__*/' + data_js)
out = out.replace('__GEN_DATE__', gen_date).replace('__COUNT__', str(len(vocab)))
open(OUT, 'w', encoding='utf-8').write(out)
```

Lệnh build: `cd 01_Build_App/_app_build && python3 build_app.py` → sinh `Kokoro_Nihongo.html`.

> **Path tự động (đã fix 2026/07/17):** `build_app.py` nay **tự suy ra đường dẫn từ vị trí của chính nó** (`os.path.abspath(__file__)` → lên 2 cấp là `100_日本語`), KHÔNG còn hardcode tên session. Nhờ vậy chạy ở bất kỳ session nào, hoặc khi đổi tên/di chuyển thư mục, đều đúng — không cần sửa tay. (Trước đây từng hardcode `/sessions/<tên>/...` nên mỗi chat mới phải sửa; nay đã bỏ.)

### 4.3. Các chế độ học (4 modes)

| Mode | Mô tả | Công nghệ |
|---|---|---|
| 🗂️ **Flashcard + SRS** | Lật thẻ, lặp lại ngắt quãng (Leitner). Ưu tiên thẻ đến hạn (due). Session tối đa 20 thẻ. Nút 🔊 đọc từ. | `speechSynthesis` (TTS) |
| ✍️ **Quiz** | Trắc nghiệm ngẫu nhiên JP→VI hoặc VI→JP, 4 lựa chọn, 15 câu/session. | — |
| 🎧 **Luyện nghe** | Nghe từ hoặc câu ví dụ (TTS ja-JP) → chọn nghĩa đúng, 15 câu. | `speechSynthesis` |
| 🎤 **Luyện nói** | Nghe mẫu → đọc theo → nhận diện giọng chấm điểm phát âm, 12 từ. | `SpeechRecognition` (webkit) |

### 4.4. Thuật toán SRS (Leitner)

- Mỗi thẻ có `box` (0..6) → khoảng ngày ôn lại `INTERVALS = [0,1,2,4,7,15,30]`.
- Đánh giá 4 mức: `again(0)` lùi 1 box · `hard(1)` giữ nguyên · `good(2)` +1 box · `easy(3)` +2 box.
- `due` = hôm nay + INTERVALS[box]. Thẻ "đã thuộc" = box >= 3.
- Lưu tiến độ trong **localStorage** (key `jp_learn_v1`): `{cards:{id:{box,due,correct,seen}}, stats:{studied,streak,lastDay}}`.

### 4.5. Speech API — lưu ý theo thiết bị

- **TTS (`speechSynthesis`)**: chọn voice `ja-JP`. Cần giọng tiếng Nhật cài sẵn trên máy (đa số Android có).
- **Nhận diện giọng (`SpeechRecognition`/`webkitSpeechRecognition`)**: lang `ja-JP`.
  - ✅ **Android Chrome**: hoạt động tốt → chấm điểm phát âm tự động.
  - ⚠️ **iOS Safari**: hỗ trợ kém/không ổn định → app tự phát hiện, ẩn tính năng chấm điểm, chỉ cho nghe mẫu + đọc theo (shadowing).
- **Chấm điểm phát âm**: chuẩn hóa (`normJa` bỏ dấu câu) → tính similarity bằng **LCS ratio** giữa câu nhận diện và từ/読み方 → % điểm (>=80 tuyệt, >=55 khá).

### 4.6. Lỗi thường gặp khi build & cách verify

- **Template literal lồng nhau thiếu backtick đóng** → JS syntax error. Đã gặp ở `speakMode` (thiếu `` ` `` đóng template ngoài). **Luôn verify:** đếm số backtick trong `<script>` phải **chẵn**; chạy `node --check` trên phần JS đã tách ra.
- **Verify bắt buộc sau mỗi build:**
  1. Trích JSON `/*__VOCAB__*/[...]` → `json.loads` OK, đủ số từ, không record thiếu `w/vi/r`.
  2. Không còn placeholder `__GEN_DATE__` / `__COUNT__`.
  3. `node --check` phần JS pass.
  4. (Nên) test hàm `similarity` + logic SRS box bằng Node.

---

## 5. Cách CẬP NHẬT app khi có từ mới (auto-update)

App là file tĩnh nên không tự đọc Excel trên PC. "Tự động cập nhật" = **re-run build** mỗi khi từ điển đổi:

```bash
# 1. Xác định lại session mount (đổi theo session)
ls /sessions/*/mnt/
# 2. (nếu path trong build_app.py khác session) cập nhật biến DICT/OUT cho đúng
# 3. Build lại (path tự động, không cần sửa gì)
cd /sessions/<session>/mnt/100_日本語/01_Build_App/_app_build && python3 build_app.py
```

Quy trình mong muốn: sau khi skill dịch thêm từ vào từ điển → chạy luôn `build_app.py` để app có từ mới. Người dùng chỉ cần nói **"cập nhật app"**.

> **Cần làm khi mở lại project (chat mới):** đọc file này trước; kiểm tra `_app_build/` còn `build_app.py` + `app_template.html` không; sửa path theo session hiện tại; build & verify.

---

## 6. Trạng thái hiện tại (cập nhật 2026/07/17)

- Từ điển: **594 từ** (STT 1–594). Category: 漢字 498 · 外来語 75 · その他 21.
- App `Kokoro_Nihongo.html`: đã verify JS OK, nhúng đủ 594 từ. Template hiện tại (`app_template.html` ~58 KB) đã được nâng cấp so với bản gốc: đổi color scheme (tông xanh dương), fix nút "Hiển thị tất cả" ở Kaiwa, thêm mic luyện đọc cả câu (xem `_feature_requests/FR_002_ui_kaiwa_reading_fix.md`).
- Bộ build ở `01_Build_App/_app_build/`.
- **Deliverable dịch thuật khác đã tạo:** `メール申請機能_要件整理案_VI.md` — bản dịch VI đầy đủ 20 mục của spec chức năng "メール申請" (đăng ký email/ML trên Portal nội bộ, Blazor). Từ vựng của tài liệu này đã được nạp vào từ điển (35 từ, STT 560–594), câu ví dụ N3 lấy trực tiếp từ chính spec đó.

---

## 7. Checklist cho chat mới tiếp tục project

- [ ] Đọc file handover này để nắm context.
- [ ] `ls /sessions/*/mnt/` xác định path session.
- [ ] Kiểm tra `日本語の辞書.xlsx` (số từ, format) + `01_Build_App/_app_build/`.
- [ ] Thêm từ mới: dùng skill `translator-ja-vi-en` → ghi bằng raw ZIP/XML (mục 3.3), KHÔNG openpyxl.save.
- [ ] Nếu từ điển đang mở trong Excel → sẽ bị `PermissionError` khi ghi đè; nhờ người dùng đóng file rồi copy lại (bản tạm lưu ở outputs/`/tmp/`).
- [ ] Build app: `python3 build_app.py` (path tự động, không cần sửa) → verify (mục 4.6). Output là `Kokoro_Nihongo.html`.
- [ ] Ghi đè file ở connected folder, `present_files` cho người dùng.
- [ ] Muốn nâng cấp app: sửa `app_template.html` (KHÔNG sửa `Kokoro_Nihongo.html` đã sinh — sẽ bị build đè). Ưu tiên đọc file trong `_feature_requests/` nếu người dùng đã viết yêu cầu.

---

## 8. Feature Request — cách yêu cầu thêm/sửa chức năng

Folder `01_Build_App/_feature_requests/` chứa template và các yêu cầu thay đổi:

- **`TEMPLATE.md`** — copy ra file mới, điền vào, bảo Claude thực hiện.
- Đặt tên file: `FR_<số>_<tên_ngắn>.md` (VD: `FR_002_dark_mode.md`).
- File bắt đầu `_EXAMPLE` là mẫu tham khảo, Claude sẽ bỏ qua.

**Cách nhanh nhất:** Nếu không muốn viết file, chỉ cần nói trong chat theo cấu trúc:
1. Làm gì (thêm/sửa/fix)
2. Mô tả hành vi cụ thể (user làm X → app phản hồi Y)
3. Ràng buộc nếu có (offline, tương thích iOS, v.v.)

Claude sẽ đọc file hoặc chat, tự xác định file cần sửa, build & verify.

---

## 9. Ý tưởng nâng cấp tiếp (backlog gợi ý)

- Đồng bộ tiến độ đa thiết bị (cần backend nhẹ / export-import JSON tiến độ).
- Chế độ "viết chữ" (viết kanji), ghép câu, nghe chép chính tả.
- Nút export tiến độ ra file để backup (tránh mất khi xóa cache trình duyệt).
- Phân nhóm chủ đề sâu hơn (động từ, kính ngữ, DB, môi trường...) thay vì chỉ 3 category tự động.
- Đóng gói PWA thật (manifest.json + service worker) để cài như app & chạy offline hoàn toàn.
```
