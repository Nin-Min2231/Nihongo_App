# 01_KHAO_SAT_APP.md — Khảo sát app hiện tại

**Dự án khảo sát:** Kokoro Nihongo (ココロ日本語)
**Đường dẫn:** `D:\01_NguyenNC\10_Claude\100_日本語`
**Người thực hiện:** Claude Code (chỉ đọc, không sửa file nguồn nào)
**Ngày:** 2026-09-11
**Yêu cầu gốc:** `YEU_CAU_KHAO_SAT_APP.md` mục 3

---

## ⚠️ 3 điểm cần đọc trước

**1. Tầng đọc Excel hiện đang HỎNG — không chạy được nữa.**
`日本語の辞書.xlsx` được lưu lại ngày 2026-09-11 bằng công cụ khác, và bản mới **không còn `xl/sharedStrings.xml`** (chuyển sang `inlineStr`). `build_app.py` đọc thẳng `xl/sharedStrings.xml` nên ném `KeyError` ngay dòng đầu. Đây là lý do thực tế, có thể tái hiện, để viết lại tầng đọc Excel. Chi tiết ở **mục B.10**.

**2. Số liệu trong yêu cầu khảo sát không khớp với file Excel hiện tại.**

| | Yêu cầu ghi | File thực tế đo được hôm nay |
|---|---|---|
| Số từ | 649 | **667** |
| STT trùng | 16 giá trị (610–625) | **0 — không trùng** |
| STT thiếu | 7 giá trị (551, 556, 605, 629–632) | **0 — không thiếu** |

File hiện tại có STT chạy liền 1→667, không trùng, không hụt, và không ô nào rỗng ở cả 5 cột C/D/E/F/G. Có vẻ anh NguyenNC đã dọn file sau khi Cowork phân tích. **Cảnh báo "app khóa theo STT là lỗi" hiện KHÔNG còn áp dụng** — nhưng xem mục B.9, khóa theo STT vẫn là rủi ro cho việc migrate tiến độ học.

**3. App đang chạy là bản cũ 596 từ.**
Lần build cuối: 2026-07-18. Từ điển sửa: 2026-09-11. Chênh **71 từ** chưa vào app, và không build lại được vì lý do #1.

---

## A. Tổng quan ★

| Mục | Trả lời |
|---|---|
| **Tên app** | Kokoro Nihongo / ココロ日本語 (app id Android: `com.kokoronihongo.app`) |
| **Mục đích ban đầu** | App học tiếng Nhật **offline** cho PM/BrSE ngành IT làm việc với đối tác Nhật. Học từ vựng IT chuyên ngành + nghe hội thoại công việc IT thật. |
| **Ngôn ngữ và framework** | **KHÔNG dùng framework.** Vanilla HTML + CSS + JavaScript ES6, tất cả trong **1 file HTML duy nhất**. Tầng build: **Python 3** (chỉ standard library). Đóng gói Android: **Capacitor 8.4.2** (`@capacitor/android`). |
| **Chạy trên nền nào** | Hai hình thức: (1) **trình duyệt** — mở thẳng `Kokoro_Nihongo.html`, không cần server; (2) **APK Android thật** — `Kokoro_Nihongo.apk`, có TTS + mic native. Không có bản iOS, không có bản desktop đóng gói. |
| **Cách chạy ở chế độ dev** | Không có dev server. Quy trình: `cd 01_Build_App/_app_build && python3 build_app.py` rồi mở `01_Build_App/Kokoro_Nihongo.html` bằng trình duyệt. Sửa tính năng = sửa `app_template.html` rồi build lại. |
| **Cách build ra bản dùng thật** | **Bản web:** `python3 build_app.py` (1 lệnh).<br>**Bản APK:** `cp ../01_Build_App/Kokoro_Nihongo.html www/index.html` → `cp ../01_Build_App/audio/*.mp3 www/audio/` → `npx cap sync android` → `cd android && ./gradlew.bat assembleDebug`. |
| **Dung lượng source thật** | **~0,75 MB.** Chỉ gồm: 2 file `.html` (template 111 KB + output 296 KB), 2 file `.py` (7 KB + 10 KB), 12 file `.md`, 2 file `.xlsx` (78 KB + transcript). Không tính mp3, PDF, APK, node_modules, build, .git, worktree. |
| **2 GB là do đâu** | Tổng thư mục gốc **2.089 MB**. Không phải do source. Xếp hạng:<br>1. `.claude\worktrees` — **1.189 MB** (bản sao worktree Claude Code tự tạo, xóa được)<br>2. `03_Android_App\android` — **303 MB** (output Gradle: `.gradle`, `app\build`)<br>3. `03_Android_App\node_modules` — **148 MB**<br>4. `.git` — **98 MB** (do lịch sử từng chứa mp3)<br>5. Audio mp3 bị **nhân bản 4 lần** cùng 38 track gốc: `02_IT_Gyoumuhen\AudioCD` 68,6 MB + `01_Build_App\audio` 68,6 MB + `03_Android_App\www\audio` 68,6 MB + bản trong APK/build<br>6. `02_IT_Gyoumuhen\reading_segments` — 35,9 MB (213 đoạn cắt nhỏ)<br>**Kết luận: 2 GB gần như toàn bộ là worktree + build artifact + audio trùng lặp.** |
| **Trạng thái hiện tại** | **Đang dùng, nhưng tầng build đang kẹt.** Bằng chứng: từ điển được cập nhật đều (lần cuối 2026-09-11, thêm 71 từ), có 2 Feature Request đã chốt yêu cầu chờ code (FR_006, FR_007), đã sinh sẵn 213 đoạn audio cho FR_007. Nhưng app chưa build lại kể từ 2026-07-18. |

---

## B. Tầng đọc Excel — mô tả hành vi ★

> Code nguyên văn: xem `02_CODE_DOC_EXCEL.md`.

### 1. File nào chịu trách nhiệm đọc Excel?

| Đường dẫn tương đối | Vai trò |
|---|---|
| `01_Build_App/_app_build/build_app.py` | **Duy nhất** đọc `日本語の辞書.xlsx`. Hàm `extract_vocab()`, dòng 24–65. |
| `01_Build_App/_app_build/segment_reading_audio.py` | Chỉ đọc `02_IT_Gyoumuhen/IT_Gyoumuhen_AudioCD_Transcript.xlsx` (openpyxl). **Không đụng từ điển.** |

App HTML **không đọc Excel lúc chạy**. Không có file JS nào chứa SheetJS/ExcelJS.

### 2. Thư viện gì?

**Không dùng thư viện Excel nào cả.** `build_app.py` mở `.xlsx` như một file ZIP bằng `zipfile` (standard library), đọc thẳng 2 file XML bên trong, và **parse bằng regex** (`re.findall`), unescape bằng `html.unescape`.

Đây là quyết định có chủ ý, ghi rõ trong `CLAUDE.md` quy tắc #1: `openpyxl.save()` rewrite styles làm **mất màu, border, theme** của file từ điển gốc — nên dự án tránh openpyxl hoàn toàn ở đường ghi.

`segment_reading_audio.py` thì **có** dùng `openpyxl` (chỉ đọc, `data_only=True`) — nhưng file này không chạm từ điển.

### 3. Đường dẫn Excel hardcode ở đâu?

**Hardcode trong code, nhưng theo kiểu tương đối tự suy — không có file cấu hình.** `build_app.py` dòng 13–21:

```python
HERE    = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(HERE)
BASE    = os.path.dirname(APP_DIR)
DICT    = os.path.join(BASE, '日本語の辞書.xlsx')
```

Người dùng **không** chọn file. **KHÔNG CÓ** `.env`, `config.json`, `settings.ini`. Ưu điểm: chạy được ở bất kỳ máy nào, không cần sửa path. Nhược điểm: tên file và vị trí bị cố định cứng.

### 4. Đọc vào lúc nào?

**Chỉ lúc build, chạy tay từ command line.** Không đọc lúc khởi động app, không đọc theo lịch, không đọc khi bấm nút. Dữ liệu được nướng cứng vào HTML một lần rồi thôi.

### 5. Sheet nào, dòng nào, cột nào?

- **Sheet:** `xl/worksheets/sheet1.xml` — luôn là sheet đầu tiên, đọc theo **vị trí trong ZIP**, không theo tên. File chỉ có 1 sheet tên `日本語の辞書`.
- **Bỏ qua dòng 1–4** (`if int(rn) < 5: continue`). Dòng 4 là tiêu đề, dòng 1–3 là banner/tác giả/ngày cập nhật.
- **Cột:** B=STT, C=Từ vựng, D=読み方, E=Nghĩa tiếng Việt, F=Tiếng Anh, G=Câu hội thoại ≥N3.
- **Điều kiện giữ dòng:** cột C khác rỗng. Dòng nào C rỗng thì bỏ, không báo lỗi.

### 6. Đọc cả file hay một phần?

Đọc **toàn bộ** sheet1 trong một lần, không phân trang, không giới hạn. Cột H trở đi bị bỏ qua hoàn toàn (hiện rỗng).

### 7. Đọc xong thành cấu trúc gì?

`list[dict]` trong Python, rồi `json.dumps` thành mảng JSON nhúng vào HTML. **Không có class, không có dataclass, không có TypeScript interface** — chỉ là dict trần.

```python
{
    "id": int(cell(rxml, 'B') or len(vocab)+1),   # cột B — STT
    "w":  word,                                   # cột C — từ vựng
    "r":  cell(rxml, 'D'),                        # cột D — 読み方
    "vi": cell(rxml, 'E'),                        # cột E — nghĩa tiếng Việt
    "en": cell(rxml, 'F'),                        # cột F — tiếng Anh
    "ex": cell(rxml, 'G'),                        # cột G — câu hội thoại
    "c":  category(word),                         # TỰ SINH, không có trong Excel
}
```

Phía client (`app_template.html` dòng 257): `const VOCAB = /*__VOCAB__*/[];`

Trường `c` được **suy ra từ chính chữ viết** của từ, bằng hàm `category()`:
- toàn Katakana → `外来語`
- có ký tự Hán → `漢字`
- còn lại → `その他`

Trường này **không còn được dùng để phân loại UI** (app đã bỏ lọc theo chủ đề), giờ chỉ còn `pool()` tham chiếu với `curCat` luôn bằng `'ALL'`. → **Có thể bỏ khi gộp.**

Bảng tần suất sử dụng từng trường trong app: xem `02_CODE_DOC_EXCEL.md` mục 3.

### 8. Có cache không?

**KHÔNG CÓ cache theo nghĩa thông thường** (không JSON cache, không SQLite, không IndexedDB, không invalidate logic).

Nhưng về bản chất, **chính file `Kokoro_Nihongo.html` là cache** — nó chứa toàn bộ dữ liệu Excel đã đông cứng. Cách "invalidate" duy nhất là chạy lại `build_app.py` bằng tay. Đây chính là chỗ đang trục trặc: cache đang giữ 596 từ trong khi nguồn có 667 từ, và không refresh được.

### 9. Khóa định danh một từ vựng là gì?

**Cột B (STT).** `"id": int(cell(rxml,'B') or len(vocab)+1)` — nếu STT rỗng thì fallback sang số thứ tự đọc được.

`id` này được dùng làm **key trong localStorage**:
- `store.cards[id]` — trạng thái SRS của từ
- `store.favorites[id]` — đánh dấu yêu thích

**Về cảnh báo trong yêu cầu khảo sát:** đã kiểm tra file hiện tại — **667 từ, STT 1→667, không trùng, không thiếu**. Cảnh báo (16 trùng / 7 thiếu) không còn đúng với file hôm nay.

**Nhưng rủi ro vẫn còn, và cần nói rõ vì nó ảnh hưởng trực tiếp tới việc gộp:**

STT là **số thứ tự dòng**, không phải mã ổn định. Nếu ai đó chèn 1 từ mới vào giữa và đánh số lại, thì `id` của mọi từ phía sau bị dịch — tiến độ học trong localStorage sẽ **gắn nhầm sang từ khác**, im lặng, không báo lỗi. Từ 596 → 667 từ lần này an toàn vì các từ mới được thêm vào cuối (STT 597–667), nhưng đó là may, không phải do thiết kế.

→ **Khuyến nghị cho bản gộp:** dùng cột C (từ vựng) làm khóa tự nhiên, hoặc sinh id ổn định (hash của C), và giữ STT chỉ để hiển thị/sắp xếp. Kèm bước migrate localStorage cũ.

### 10. Xử lý lỗi ra sao?

**Gần như không có xử lý lỗi.** Không có một `try/except` nào trong `extract_vocab()`.

| Tình huống | Hành vi thực tế |
|---|---|
| **File đang mở trong Excel** | Trên Windows, Excel không khóa đọc → `zipfile` vẫn đọc được bản trên đĩa. Nhưng nếu anh đang có **thay đổi chưa lưu**, script đọc bản cũ và **không cảnh báo gì**. |
| **File không tồn tại / sai đường dẫn** | `FileNotFoundError` chưa bắt → traceback thô. *(Riêng transcript IT業務編 thì CÓ kiểm tra `os.path.isfile()` và bỏ qua êm; từ điển thì không.)* |
| **Thiếu cột, ô rỗng** | Hàm `cell()` trả `''`. Dòng C rỗng bị bỏ im lặng. Dòng thiếu D/E/F/G vẫn được nạp với chuỗi rỗng → app hiện thẻ trống, không báo. |
| **Ký tự lạ** | `html.unescape()` xử lý entity. Regex `<t[^>]*>(.*?)</t>` sẽ **hỏng nếu ô chứa rich text** (nhiều `<r><t>` trong một `<si>`) — hiện được nối lại thành 1 chuỗi, tình cờ đúng, nhưng không phải xử lý có chủ đích. |
| **🔴 Đổi định dạng lưu file (đang xảy ra)** | `z.read('xl/sharedStrings.xml')` → **`KeyError: "There is no item named 'xl/sharedStrings.xml' in the archive"`**. Build chết ngay, không có fallback. |

**Chi tiết lỗi đang xảy ra — hai tầng, cả hai đều phải sửa:**

*Tầng 1 — thiếu file:* Bản `日本語の辞書.xlsx` hiện tại không có `xl/sharedStrings.xml`. Các ZIP entry còn lại: `[Content_Types].xml`, `_rels/.rels`, `xl/workbook.xml`, `xl/_rels/workbook.xml.rels`, `xl/worksheets/sheet1.xml`, `xl/styles.xml`, `xl/theme/theme1.xml`, `docProps/core.xml`, `docProps/app.xml`.

*Tầng 2 — sai kiểu ô:* Kể cả nếu vá tầng 1, regex đọc ô vẫn không khớp. Hiện tại:

```python
m = re.search(r'<c r="'+col+r'\d+"([^>]*)><v>(\d+)</v></c>', row_xml)
```

Regex này đòi ô phải có dạng `<v>chữ_số</v>`. Nhưng file mới lưu chuỗi dạng inline:

```xml
<c r="C5" s="12" t="inlineStr"><is><t>承認</t></is></c>
```

Không có `<v>` → không khớp → **kể cả có sharedStrings, mọi ô chữ vẫn trả về rỗng và app sẽ ra 0 từ.**

*Đã kiểm chứng:* gọi trực tiếp `extract_vocab('日本語の辞書.xlsx')` → `KeyError: 'xl/sharedStrings.xml'`. (Chỉ gọi hàm, không chạy `main()`, nên không file nào bị ghi đè.)

*So sánh 2 phiên bản file:*

| | Bản trong git (2026-07-18) | Bản hiện tại (2026-09-11) |
|---|---|---|
| `xl/sharedStrings.xml` | **CÓ** | **KHÔNG** |
| Kiểu ô chuỗi | `t="s"` + `<v>chỉ_số</v>` | `t="inlineStr"` + `<is><t>văn_bản</t></is>` |
| Số dòng sheet | 600 | 671 |
| Số từ | 596 | 667 |

→ **Tầng đọc mới bắt buộc phải hỗ trợ cả 3 kiểu ô:** `t="s"` (sharedStrings), `t="inlineStr"`, và `t="str"`/số. Nếu chỉ vá cho `inlineStr` thì lần sau anh lưu lại bằng Excel thật (Excel luôn dùng sharedStrings) sẽ **hỏng ngược lại**.

### 11. App có ghi ngược trở lại Excel không?

**KHÔNG. Tuyệt đối chỉ đọc.**

- `build_app.py`: mở ZIP ở mode `'r'`, không có `'w'`/`'a'`. Chỉ ghi ra `Kokoro_Nihongo.html`.
- `segment_reading_audio.py`: `openpyxl.load_workbook(..., data_only=True)`, không gọi `.save()`.
- App HTML: không có API nào ghi file.

→ **Rất thuận lợi cho việc gộp.** File Excel là nguồn một chiều, đổi tầng đọc không có rủi ro mất dữ liệu gốc.

*(3 file `lock_check.tmp`, `test_write.tmp`, `test_write2.tmp` ở thư mục gốc là rác từ lần thử nghiệm khả năng ghi, không phải app sinh ra.)*

### 12. Thời gian đọc bao lâu? App có treo không?

- File 78 KB, 667 dòng, 6 cột. Đo thực tế: **dưới 1 giây** cho cả bước đọc + parse + sinh JSON.
- Bước chậm nhất của `build_app.py` là `sync_audio()` — copy 38 file mp3 (68,6 MB) lần đầu; các lần sau bỏ qua nhờ so sánh kích thước.
- **App không bao giờ treo vì đọc Excel** — lúc chạy app không đọc Excel. Chi phí duy nhất là `Kokoro_Nihongo.html` nặng 296 KB, parse tức thì.

---

## C. Các nguồn dữ liệu KHÁC ★

| Nguồn | Có / Không | Dùng làm gì | Nằm ở đâu |
|---|---|---|---|
| **API bên ngoài** | **CÓ — 1 cái duy nhất** | Google Translate TTS (endpoint không chính thức) để đọc tiếng Nhật ở bản **web**. Thử 2 biến thể `client=gtx` rồi `client=tw-ob`, timeout thì rơi về `speechSynthesis`. Bản **APK không dùng** (xem mục H). | `app_template.html` hàm `gTranslateTTSUrl()` |
| **Cơ sở dữ liệu** | **KHÔNG CÓ** | Không SQLite, không Postgres, không server | — |
| **File JSON / CSV khác** | **CÓ 1** | `segments_data.json` — manifest 213 đoạn audio đã cắt (38 track, 8.700 dòng JSON). **Hiện app CHƯA dùng** — thuộc FR_007 đang pending. | `02_IT_Gyoumuhen/reading_segments/segments_data.json` |
| **localStorage / IndexedDB** | **CÓ — localStorage, 3 key** | `jp_learn_v1` (SRS + streak + favorites + deckDone)<br>`kokoro_gyoumu_v1` (track đã nghe/đã đọc)<br>`kokoro_tts_settings` (tốc độ, cao độ, giọng) | Trình duyệt / WebView. Không IndexedDB. |
| **File âm thanh, hình ảnh** | **CÓ** | 38 mp3 AudioCD IT業務編 (68,6 MB) — app phát trực tiếp qua thẻ `<audio src="audio/NN Track N.mp3">`.<br>213 đoạn mp3 cắt nhỏ (35,9 MB) — chưa dùng.<br>Logo `04_Image/Logo_Tanpopo.png` → app icon + favicon (nhúng base64). | `01_Build_App/audio/`, `02_IT_Gyoumuhen/reading_segments/audio/`, `04_Image/` |
| **Từ điển hoặc dataset khác** | **CÓ 1** | `IT_Gyoumuhen_AudioCD_Transcript.xlsx` — transcript 38 track (Excel thứ hai, vẫn dùng sharedStrings nên vẫn đọc được). Sách gốc `IT_Gyoumuhen.pdf` chỉ để tham khảo, code không đọc. | `02_IT_Gyoumuhen/` |
| **Khác** | **CÓ** | Web Audio API sinh tiếng "bíp" phản hồi chấm điểm phát âm (không dùng file âm thanh ngoài) — hàm `beep()` / `playScoreSound()`. | `app_template.html` |

**Lưu ý cho việc gộp:** ràng buộc "chỉ thay tầng đọc Excel, mọi nguồn khác giữ nguyên" là khả thi gọn — tầng đọc Excel nằm tách bạch hoàn toàn trong `build_app.py`, không dính gì tới TTS, audio, hay localStorage.

---

## D. Mô hình dữ liệu và tiến độ học ★

### 1. Có lưu tiến độ học không? Schema?

**Có, toàn bộ trong `localStorage`, không đồng bộ đi đâu.**

**Key `jp_learn_v1`** (module IT専門 + Luyện đọc + Kaiwa):

```javascript
{
  cards: {
    "<id>": {           // id = STT cột B
      box: 0,           // bậc Leitner 0..6
      due: "2026-09-11",// ngày ôn kế tiếp, YYYY-MM-DD
      correct: 0,       // số lần trả lời đúng
      seen: 0,          // số lần đã gặp
      mastered: false   // người học tự bấm "Đã nhớ"
    }
  },
  stats: {
    studied: 0,         // tổng lượt ôn cộng dồn
    streak: 0,          // số ngày học liên tiếp
    lastDay: null       // "YYYY-MM-DD" ngày học gần nhất
  },
  deckDone: {           // Bộ nào đã hoàn thành mode nào
    "<namespace>": {    // "ALL" (IT専門) | "_reading" | "_kaiwa"
      "<deckIdx>": { flash:true, quiz:true, listen:true, speak:true }
    }
  },
  favorites: { "<id>": true }
}
```

**Key `kokoro_gyoumu_v1`** (module IT業務編, cố tình tách riêng):

```javascript
{ listened: { "<trackNumber>": true }, read: { "<trackNumber>": true } }
```

**Key `kokoro_tts_settings`:**

```javascript
{ mode:'google', speed:0.9, pitch:1.0, gender:'female', voiceName:'' }
```

Code có sẵn cơ chế migrate nhẹ cho user cũ (`if(!store.deckDone) store.deckDone={};`).

### 2. Có thuật toán SRS không?

**Có — Leitner đơn giản, tự cài, không phải SM-2 và không phải FSRS.**

- **Bậc khoảng cách:** `INTERVALS = [0, 1, 2, 4, 7, 15, 30]` ngày, box 0→6.
- **Cách chấm:** hàm `reviewCard(id, quality)` nhận 4 mức — `0` lùi 1 box, `1` giữ nguyên, `2` lên 1 box, `3` lên 2 box.
- **Nhưng UI chỉ phơi ra 1 mức duy nhất.** Flashcard hiện có 4 nút: *Chi tiết / Yêu thích / Đã nhớ / Tiếp theo* — bấm "Đã nhớ" gọi `reviewCard(id, 2)`. Hàng nút *Quên/Khó/Được/Dễ* đã bị bỏ ở FR_005.
- Quiz và Luyện nghe chấm tự động: đúng → `reviewCard(id,2)`, sai → `reviewCard(id,0)`.
- Mức `1` và `3` **hiện không có đường nào gọi tới** — code chết.
- `isDue(id)`: từ chưa gặp bao giờ luôn được coi là đến hạn.
- "Đã thuộc" (`learnedCount()`) = `box >= 3` hoặc `mastered === true`.

### 3. Hiện đã học được bao nhiêu từ? Có tiến độ thật cần giữ không?

**KHÔNG XÁC ĐỊNH ĐƯỢC — lý do:** tiến độ nằm trong `localStorage` của trình duyệt và của WebView trên điện thoại anh NguyenNC. Đây là dữ liệu runtime, không nằm trong repo, Claude Code không đọc được từ filesystem.

**Nhưng đây là ràng buộc migrate quan trọng, cần anh xác nhận:**

- Nếu app đã dùng thật → có tiến độ trong **ít nhất 2 nơi tách biệt** (Chrome trên máy tính, và WebView trong APK), **không đồng bộ với nhau**.
- Cả hai đều khóa theo `id` = STT. **Bản gộp muốn giữ tiến độ thì bắt buộc phải giữ nguyên ánh xạ STT → từ vựng của bản 596 từ.** Vì 71 từ mới được thêm vào cuối (STT 597–667), ánh xạ cũ hiện vẫn còn nguyên vẹn — nhưng đây là điều may, cần kiểm chứng lại trước khi migrate.
- Cách anh tự kiểm tra: mở app trong Chrome → F12 → Console → gõ `localStorage.getItem('jp_learn_v1')`. Nếu ra `null` thì chưa có tiến độ nào để giữ.

### 4. Có thống kê, lịch sử, chuỗi ngày học không?

| Có | Không có |
|---|---|
| Streak (số ngày liên tiếp) | **Lịch sử theo ngày** — chỉ lưu `lastDay`, không có mảng ngày |
| Tổng lượt ôn `studied` | **Biểu đồ / heatmap** |
| Số từ đã thuộc `learnedCount()` | **Lịch sử điểm từng buổi** |
| Số track IT業務編 đã nghe | **Màn hình thống kê riêng** — số liệu chỉ hiện ở dải 3 ô đầu trang chủ |
| Đánh dấu Bộ nào đã xong mode nào | **Xuất / sao lưu tiến độ** |

Streak có một lỗi nhỏ: `bumpStudied()` chỉ được gọi từ `reviewCard()`, nên học IT業務編 hoặc Luyện đọc/Kaiwa **không tính vào streak**.

---

## E. Danh sách màn hình hiện có ★

Toàn bộ là SPA render bằng JS trong **một file duy nhất** `app_template.html` (2.048 dòng). Cột "File source" ghi tên hàm + số dòng thay cho tên file.

| # | Tên màn hình | Mục đích | Dùng nhiều hay ít | File source |
|---|---|---|---|---|
| 1 | **Trang chủ / Menu chính** | 3 ô thống kê (Streak, Từ đã thuộc, Track đã nghe) + 4 thẻ chọn module. Có registry `MENU_MODULES` để thêm module mới chỉ bằng 1 phần tử mảng | Cao — cửa vào duy nhất | `home()` :936 |
| 2 | **IT専門 — Dashboard** | Lưới chọn Bộ (4 thẻ/trang, có nút ‹ ›), mỗi thẻ hiện 4 icon tiến độ 🗂️✍️🎧🎤; bên dưới là 5 nút chế độ học | Cao | `homeDashboard()` :1289 |
| 3 | **Flashcard** | Lật thẻ, 4 nút Chi tiết / Yêu thích / Đã nhớ / Tiếp theo | Cao (mode chính) | `flashMode()` :1355 |
| 4 | **Quiz** | Trắc nghiệm 4 đáp án, hai chiều JP↔VI | Cao | `quizMode()` :1515 |
| 5 | **Luyện nghe** | Nghe TTS rồi chọn nghĩa | Trung bình | `listenMode()` :1560 |
| 6 | **Luyện nói** | Đọc theo, nhận giọng, chấm điểm | Trung bình (cần mic) | `speakMode()` :1622 + `speakModeInit()` :1602 |
| 7 | **⭐ Yêu thích** | Ôn lại các từ đã đánh dấu sao | Thấp–trung bình | `favoritesMode()` :1441 |
| 8 | **Danh sách từ đã thuộc** | Xem lại + bỏ đánh dấu "đã nhớ" | Thấp | `masteredListScreen()` :1420 |
| 9 | **IT業務編 — Dashboard** | 3 ô thống kê + danh sách Unit nhóm theo Chương | Trung bình | `gyoumuDashboard()` :1026 |
| 10 | **IT業務編 — Danh sách Track** | Các track trong 1 Unit | Trung bình | `gyoumuTrackList()` :1060 |
| 11 | **IT業務編 — Player** | Phát mp3 thật: play/pause, seek, replay, chỉnh tốc độ, ẩn/hiện transcript. Nghe hết tự đánh dấu đã nghe | Trung bình | `gyoumuTrackDetail()` :1085 |
| 12 | **IT業務編 — Luyện đọc** | Đọc từng dòng thoại của track, chấm phát âm | Thấp (mới) | `gyoumuReadingMode()` :1185 |
| 13 | **Luyện đọc — Chọn bộ** | Lưới chọn bộ câu ví dụ | Trung bình | `readingLibrary()` :971 |
| 14 | **Luyện đọc — Luyện** | Nghe mẫu → đọc to → chấm điểm | Trung bình | `readingMode()` :1684 |
| 15 | **Kaiwa — Chọn bộ** | Lưới chọn bộ hội thoại | Thấp–trung bình | `kaiwaLibrary()` :990 |
| 16 | **Kaiwa — Hội thoại** | Xem hội thoại bong bóng A/B, rồi luyện đóng vai | Thấp–trung bình | `kaiwaMode()` :1786 |
| 17 | **Cài đặt (panel)** | Chế độ TTS, tốc độ, cao độ, giới tính giọng, chọn voice, xin quyền mic | Thấp | `openSettings()` :549 |
| 18 | **Màn hình Hoàn thành** | Điểm buổi học, tổng đã thuộc, streak, nút Học tiếp / Về trang chủ | Cao (sau mỗi buổi) | `finish()` :2017, `finishReading()` :1766, `finishKaiwa()` :1983, `gyoumuReadingFinish()` :1267 |

> Cột "Dùng nhiều hay ít" là **suy đoán từ vị trí trong luồng điều hướng**, không phải số liệu thật — app không có analytics. Nhờ anh NguyenNC chỉnh lại ở mục I.

---

## F. Danh sách bài tập / trò chơi hiện có ★

| # | Tên bài tập | Cơ chế chơi | Dùng cột nào của Excel | Có dùng âm thanh không |
|---|---|---|---|---|
| 1 | **Flashcard + SRS** | Hiện mặt trước (từ + 🔊), chạm để lật ra cách đọc + nghĩa + câu ví dụ. 4 nút: Chi tiết / Yêu thích / Đã nhớ / Tiếp theo. "Đã nhớ" đẩy thẻ lên 1 bậc Leitner và đặt ngày ôn kế tiếp. Bộ đang chọn học hết cả bộ; chọn "Tất cả" thì lấy tối đa 20 thẻ đến hạn | C, D, E, F, G | **Có** — TTS đọc từ (`w`) và câu ví dụ (`ex`) |
| 2 | **Quiz JP↔VI** | 4 đáp án, ngẫu nhiên hỏi chiều Nhật→Việt hoặc Việt→Nhật. 3 đáp án nhiễu bốc ngẫu nhiên trong cùng bộ. Đúng tự động `reviewCard(2)`, sai `reviewCard(0)`. Bộ "Tất cả" giới hạn 15 câu | C, E (F làm gợi ý khi hỏi ngược) | **Có** — tự đọc từ khi hỏi chiều JP→VI |
| 3 | **Luyện nghe** | Không hiện chữ. Bấm 🔊 nghe, chọn 1 trong 4 nghĩa tiếng Việt. **50% khả năng đọc câu ví dụ thay vì đọc từ** (khó hơn hẳn). Đáp án hiện kèm cách đọc | C, D, E, G | **Có** — TTS là toàn bộ đề bài |
| 4 | **Luyện nói (từ)** | Nghe mẫu → bấm mic đọc theo → nhận giọng `ja-JP` → chấm bằng LCS similarity 0–100. ≥90 xuất sắc, 51–89 khá, <51 luyện lại. Kèm tiếng bíp phản hồi theo mức điểm (Web Audio, 3 nốt lên / 1 nốt / 2 nốt trầm) | C, D | **Có** — TTS đọc mẫu + mic + bíp |
| 5 | **Luyện đọc câu** | Lấy các từ **có câu ví dụ** (`ex.length > 4`), chia bộ ~25 câu. Mỗi câu: nghe mẫu (có nút chậm) → đọc to → chấm điểm giống #4 | **G** là chính, kèm C, E | **Có** — TTS + mic + bíp |
| 6 | **Kaiwa (hội thoại ghép)** | Gom **4–6 câu ví dụ ngẫu nhiên** thành một "hội thoại", gán vai A/B xen kẽ, hiện dạng bong bóng chat lần lượt, rồi cho luyện đóng vai từng dòng có chấm điểm. Tối đa 5 hội thoại/bộ | **G** là chính | **Có** — TTS + mic + bíp |
| 7 | **⭐ Ôn từ yêu thích** | Flashcard rút gọn, chỉ chạy trên các từ đã gắn sao | C, D, E, F, G | **Có** — TTS |
| 8 | **IT業務編 — Nghe track** | Phát mp3 thật của giáo trình, chỉnh tốc độ, ẩn/hiện transcript. Nghe hết tự đánh dấu đã nghe | **Không dùng Excel từ điển** — dùng transcript xlsx riêng | **Có** — file mp3 thật |
| 9 | **IT業務編 — Luyện đọc theo thoại** | Đọc từng dòng thoại của track, chấm phát âm giống #4 | Không dùng Excel từ điển | **Có** — TTS + mic + bíp |

**Ghi chú quan trọng về #6 (Kaiwa):** đây không phải hội thoại thật. Các câu ví dụ độc lập được ghép ngẫu nhiên rồi gán vai A/B — nội dung **không liên quan logic với nhau**. Cần anh NguyenNC xác nhận ở mục I xem bài này còn giá trị học không.

---

## G. Đa thiết bị ○

**1. Chạy được trên điện thoại chưa?**
**Rồi — có APK Android thật.** Đóng gói bằng Capacitor 8.4.2, app id `com.kokoronihongo.app`, đã build sẵn `03_Android_App/Kokoro_Nihongo.apk`. Cài trực tiếp (sideload), không lên Play Store. Có app icon riêng từ `Logo_Tanpopo.png`. **Không có bản iOS** (không có thư mục `ios/`).

**2. Tiến độ có đồng bộ giữa máy tính và điện thoại không?**
**KHÔNG. Hoàn toàn không có đồng bộ.** `localStorage` của Chrome trên máy tính và `localStorage` của WebView trong APK là hai kho tách biệt. Không có tài khoản, không có server, không có export/import. Học trên máy tính không thấy trên điện thoại và ngược lại.

**3. Có chạy được khi mất mạng không?**
**Gần như hoàn toàn — với một ngoại lệ đáng chú ý:**

| Chức năng | Offline? |
|---|---|
| Toàn bộ dữ liệu từ vựng, giao diện, SRS | ✅ Nhúng sẵn trong HTML |
| 38 file mp3 IT業務編 | ✅ File cục bộ |
| Icon, logo, favicon | ✅ base64, không tải ngoài |
| Tiếng bíp chấm điểm | ✅ Web Audio API sinh tại chỗ |
| TTS trên **APK Android** | ✅ Engine TextToSpeech hệ thống, không qua mạng |
| **TTS trên trình duyệt** | ⚠️ **CẦN MẠNG** — đường chính là Google Translate TTS. Mất mạng thì rơi về `speechSynthesis`, chất lượng phụ thuộc giọng cài trên máy |
| Nhận giọng nói (mic) | ⚠️ Web Speech Recognition của Chrome gửi lên server Google → **cần mạng**. Bản native dùng plugin, có thể offline nếu máy đã tải gói ngôn ngữ |

→ **Bản APK gần như offline hoàn toàn; bản web thì không, do TTS.** Đúng như thiết kế: mục tiêu "offline" chủ yếu nhắm vào bản APK.

---

## H. Phát âm và nhận giọng nói ○

**1. Có đọc thành tiếng tiếng Nhật không? Dùng gì?**

**Có. Hai đường hoàn toàn tách biệt, chọn theo môi trường qua `isNativeApp()`:**

**Bản APK Android** → plugin native `@capacitor-community/text-to-speech` v8.0.2, gọi thẳng engine TextToSpeech của hệ điều hành. Không qua mạng.

**Bản web/Chrome** → thứ tự thử:
1. Google Translate TTS, endpoint `client=gtx` (`translate.googleapis.com`)
2. Nếu lỗi/timeout → endpoint `client=tw-ob` (`translate.google.com`)
3. Nếu vẫn lỗi → `speechSynthesis` của trình duyệt
4. Nếu tất cả thất bại → **toast báo lỗi kèm mã lỗi**, không im lặng

Text dài được cắt thành chunk ≤200 ký tự (`splitText()`) vì endpoint Google giới hạn độ dài.

**Lý do có hai đường** (ghi trong `CLAUDE.md` quy tắc #4, đã xác nhận lỗi thật trên máy): Android WebView **không implement Web Speech API**, và endpoint Google Translate TTS **cũng không đáng tin cậy** khi gọi từ WebView đóng gói. Đây là kiến thức đã trả giá — bản gộp **không được quay lại dùng Google TTS làm đường chính cho native**.

**Cấu hình cho người dùng:** tốc độ 0,5–1,5 · cao độ 0,5–2,0 · giọng nam/nữ · chọn voice cụ thể. Lưu ở `localStorage['kokoro_tts_settings']`.

**2. Có chấm phát âm không?**

**Có, nhưng là chấm khớp văn bản, không phải chấm âm học.**

Luồng: mic → speech recognition trả về chuỗi tiếng Nhật → chuẩn hóa (`normJa()` bỏ 、。「」（）khoảng trắng ・ー〜) → so với câu gốc bằng **LCS (Longest Common Subsequence) / max(độ dài)** → điểm 0–100.

- ≥ 90: xuất sắc (3 nốt bíp lên)
- 51–89: khá (1 nốt)
- < 51: luyện lại (2 nốt trầm)

**Nhận giọng:** native dùng `@capgo/capacitor-speech-recognition` v8.1.10; web dùng `SpeechRecognition`/`webkitSpeechRecognition` với `lang='ja-JP'`. Có xử lý xin quyền mic riêng cho từng môi trường (`checkMicPermission()`, `requestMicPermission()`, `ensureMicReady()`).

**Hạn chế cần biết:** cách chấm này đo **kết quả nhận dạng đúng bao nhiêu ký tự**, nên không phân biệt được lỗi trọng âm, ngữ điệu, hay trường âm — nếu engine đoán đúng từ dù phát âm lệch thì vẫn 100 điểm.

**3. File âm thanh thu sẵn?**

| Bộ | Số file | Dung lượng | Vị trí | Trạng thái |
|---|---|---|---|---|
| AudioCD IT業務編 gốc | 38 | 68,6 MB | `02_IT_Gyoumuhen/AudioCD/` | **Nguồn gốc duy nhất** |
| Bản copy cho app web | 38 | 68,6 MB | `01_Build_App/audio/` | `build_app.py` tự copy |
| Bản copy cho APK | 38 | 68,6 MB | `03_Android_App/www/audio/` | Copy tay |
| Đoạn cắt nhỏ | 213 (+2 file `_full`) | 35,9 MB | `02_IT_Gyoumuhen/reading_segments/audio/` | **Đã sinh nhưng app CHƯA dùng** (FR_007) |

**Không có** file mp3 thu sẵn cho 667 từ vựng — toàn bộ từ vựng đều đọc bằng TTS.

Chi tiết bộ đoạn cắt: cắt bằng ffmpeg silence-detection, 5–7 đoạn/track tùy độ dài, biên đoạn "nam châm" về khoảng lặng gần nhất, transcript gom theo lượt thoại. Track 9 và 21 không có transcript (thiếu trang PDF gốc) nên giữ nguyên file đầy đủ, gắn cờ `transcriptAvailable: false` — script **cố tình không bịa nội dung**.

---

## I. Đánh giá của chính anh NguyenNC ★

> **Phần này Claude Code KHÔNG TỰ TRẢ LỜI ĐƯỢC** — cần trải nghiệm sử dụng thật, không suy ra được từ code. Đây là phần **giá trị nhất** để quyết định gộp cái gì bỏ cái gì.
>
> **Nhờ anh NguyenNC điền trực tiếp vào bên dưới rồi hãy upload lên Cowork.**

**1. Ba thứ anh thích nhất ở app hiện tại, và vì sao:**

1.
2.
3.

**2. Ba thứ khó chịu nhất, và vì sao:**

1.
2.
3.

**3. Màn hình hoặc bài tập nào anh đã bỏ không dùng nữa? Vì sao?**

*(Gợi ý các ứng viên Claude Code nghi ngờ, anh xác nhận giúp:)*
- [ ] **Kaiwa** — hội thoại ghép ngẫu nhiên từ câu ví dụ rời rạc, nội dung không liên quan logic
- [ ] **Luyện đọc** — có phần trùng mục đích với Luyện nói
- [ ] **IT業務編 Luyện đọc theo thoại** — mới thêm ở FR_004
- [ ] **Danh sách từ đã thuộc**
- [ ] Khác: ______

**4. Bài tập nào anh thấy thật sự giúp nhớ từ?**


**5. Điều gì khiến anh muốn làm lại phần đọc Excel?**

*(Claude Code đã tìm được 1 lý do kỹ thuật xác thực — xem mục B.10: build hiện đang chết vì file Excel đổi định dạng lưu, mất `sharedStrings.xml`. Nhờ anh bổ sung các lý do khác nếu có: chậm, phải thao tác tay, muốn app tự đọc Excel không cần build lại, muốn sửa từ điển ngay trong app…)*


---

## J. Ba câu hỏi anh chưa trả lời ★

### 1. App hiện tại build bằng công nghệ gì?

**Đã trả lời ở mục A. Tóm tắt:**

```
日本語の辞書.xlsx  ──[ build_app.py — Python 3, chỉ stdlib ]──>  Kokoro_Nihongo.html
                                                                       │
                                                            [ Capacitor 8.4.2 ]
                                                                       ▼
                                                            Kokoro_Nihongo.apk
```

- **Frontend:** vanilla HTML/CSS/JS, không framework, 1 file duy nhất, hoạt động offline
- **Build:** Python 3, không cần `pip install` gì cả (chỉ `zipfile` + `re` + `json`)
- **Mobile:** Capacitor 8.4.2 + 2 plugin native (TTS, speech recognition)
- **Lưu trữ:** `localStorage`, không server, không database

### 2. Trong bản gộp, app nào làm nền?

> **Đây là quyết định của anh NguyenNC — Claude Code không tự chọn thay.** Nhờ anh tick 1 ô:

- [ ] App hiện tại làm nền, bổ sung bài tập từ thiết kế mới vào
- [ ] Prototype mới làm nền, bưng điểm hay của app cũ sang
- [ ] Để Claude đề xuất sau khi đọc khảo sát

**Dữ kiện khách quan để anh cân nhắc (không phải khuyến nghị):**

| Điểm mạnh app hiện tại | Điểm yếu app hiện tại |
|---|---|
| Đã chạy thật trên điện thoại (APK), đã giải xong bài toán khó nhất: TTS + mic native trên Android WebView | Tất cả trong 1 file 2.048 dòng, không module, không test |
| 68,6 MB audio thật của giáo trình IT業務編 + transcript 38 track — **tài sản không tái tạo được** | Không có đồng bộ đa thiết bị |
| Offline thật ở bản APK | SRS chỉ phơi ra 1 mức chấm dù code hỗ trợ 4 |
| Kiến thức đã trả giá về giới hạn Android WebView (`CLAUDE.md` quy tắc #4, #5) | Tầng đọc Excel đang hỏng |
| 213 đoạn audio đã cắt sẵn, chờ dùng | Kaiwa ghép câu ngẫu nhiên, chất lượng nội dung thấp |

### 3. Ý số 3 — chỉ sửa tầng đọc Excel, mọi thứ khác giữ nguyên 100% — đúng chưa?

**Về tính khả thi: RẤT KHẢ THI.** Tầng đọc Excel nằm gọn trong **1 hàm, 42 dòng** (`extract_vocab()`, `build_app.py` dòng 24–65), không dính gì tới TTS, audio, localStorage hay UI. Giao diện với phần còn lại chỉ là **một mảng JSON 7 khóa** (`id, w, r, vi, en, ex, c`) — thay ruột hàm, giữ nguyên đầu ra, mọi thứ khác không cần đụng.

**Về "vấn đề cụ thể của phần đọc Excel hiện tại" — CÓ, và đã xác định chính xác:**

| # | Vấn đề | Mức độ | Chi tiết |
|---|---|---|---|
| 1 | **Build chết hoàn toàn** | 🔴 Chặn đứng | `KeyError: 'xl/sharedStrings.xml'`. File Excel được lưu lại 2026-09-11 bằng công cụ chuyển sang `inlineStr`. → **Không build lại app được nữa.** |
| 2 | **Regex chỉ đọc được `<v>số</v>`** | 🔴 Chặn đứng | Kể cả vá lỗi #1, mọi ô chữ vẫn trả rỗng → app ra 0 từ. |
| 3 | Chỉ hỗ trợ 1 trong 3 kiểu ô của chuẩn xlsx | 🟠 Cao | Cần hỗ trợ cả `t="s"`, `t="inlineStr"`, `t="str"`/số — nếu không, mỗi lần đổi công cụ lưu file là hỏng lại. |
| 4 | Không một `try/except` nào | 🟠 Cao | Sai đường dẫn / thiếu cột / ô rỗng đều hỏng thô hoặc lặng lẽ bỏ qua. |
| 5 | Khóa định danh = STT (số thứ tự dòng) | 🟠 Cao | Chèn từ vào giữa và đánh số lại → tiến độ học gắn nhầm sang từ khác, không báo lỗi. |
| 6 | Phải chạy tay, không tự phát hiện Excel đổi | 🟡 Trung bình | Đúng nguyên nhân app đang lệch 596 vs 667 từ suốt gần 2 tháng. |
| 7 | Parse XML bằng regex | 🟡 Trung bình | Sẽ hỏng với ô rich-text (nhiều `<r><t>` trong một `<si>`). |
| 8 | Trường `c` (phân loại) đã thành code chết | 🟢 Thấp | App đã bỏ lọc theo chủ đề, `curCat` luôn `'ALL'`. Có thể bỏ. |

**Nhờ anh xác nhận 3 điểm sau để chốt phạm vi:**

- [ ] "Giữ nguyên 100% mọi thứ khác" có bao gồm **giữ nguyên tên 7 khóa JSON** (`id/w/r/vi/en/ex/c`) không? *(Giữ thì không phải đụng dòng nào của app; đổi thì phải sửa cả template.)*
- [ ] Có muốn nhân dịp này **đổi khóa định danh** từ STT sang khóa ổn định (kèm bước migrate localStorage) không? *(Vấn đề #5 — không sửa bây giờ thì sẽ đau về sau.)*
- [ ] Có muốn app **tự đọc Excel lúc chạy** thay vì phải build lại không? *(Đây không còn là "chỉ sửa tầng đọc Excel" mà là đổi kiến trúc — bản web mở bằng `file://` không fetch được file cạnh nó, sẽ phải dùng ô chọn file hoặc chạy qua server.)*

---

## Phụ lục — Việc dở dang cần biết khi gộp

**Hai Feature Request đã chốt yêu cầu, chưa code:**

| FR | Nội dung | Trạng thái |
|---|---|---|
| **FR_006** | IT専門: tự động focus vào Bộ nhỏ nhất chưa hoàn thành (đã làm đủ 4 mode), `deckPage` tự nhảy sang trang chứa Bộ đó | Đã chốt yêu cầu 2026-07-26, **chưa code** |
| **FR_007** | IT業務編: luyện đọc theo **audio thật** (dùng 213 đoạn đã cắt) + gộp Luyện nghe và Luyện đọc vào 1 màn hình Unit duy nhất | Đã chốt yêu cầu 2026-07-26, **dữ liệu đã sinh xong**, chưa code |

`app_template.html` **không hề tham chiếu** `reading_segments` hay `segments_data.json` → xác nhận FR_007 chưa được nối vào app.

**Thay đổi chưa commit trong git** (`git status`): `.gitignore`, `Kokoro_Nihongo.html`, `app_template.html`, 2 file gradle, `日本語の辞書.xlsx` đều đang ở trạng thái modified; `segment_reading_audio.py`, FR_006, FR_007, `reading_segments/` chưa được add. Repo chỉ có 4 commit.

**File rác nên dọn:** `lock_check.tmp`, `test_write.tmp`, `test_write2.tmp` ở thư mục gốc.

**Hai file không liên quan tới app** nằm ở thư mục gốc: `Ban_dich_Mail_Request_Spec.md`, `Ban_dich_WRS2_System_Concept.md` (tài liệu dịch công việc).
