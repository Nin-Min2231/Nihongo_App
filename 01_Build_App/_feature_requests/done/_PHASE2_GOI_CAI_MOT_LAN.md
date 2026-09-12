# Phase 2 — Gói cài APK MỘT LẦN

> Lập ngày 2026-09-11 · gồm 5 Feature Request.
> **2026-09-12: Đã code xong cả 5 FR (FR_008→FR_012), đã test qua trình duyệt desktop.** Chưa build APK — còn phải tự chạy lại đủ 6 bước nghiệm thu bên dưới trên thiết bị/khổ máy thật trước khi build, theo đúng tinh thần "đừng build APK khi chưa test kỹ" của tài liệu này.

---

## ⚠️ Hai điều bắt buộc phải biết trước

### 1. PM đang có RẤT NHIỀU tiến độ học trên APK, và chưa có bản sao lưu nào

Tiến độ nằm trong `localStorage` của WebView trong APK trên điện thoại PM. Không có nút xuất, không có bản sao ở đâu cả. Mất là mất vĩnh viễn.

→ **Khi cài APK mới: CÀI ĐÈ lên bản cũ. Tuyệt đối không gỡ app ra cài lại.**
Android giữ nguyên dữ liệu app khi cài đè cùng tên app và cùng khóa ký. Gỡ app là xóa sạch.
Nếu lúc cài báo lỗi `App not installed` thì **dừng lại hỏi PM**, đừng gỡ app cho bằng được.

### 2. Vì vậy cả 5 FR gộp thành MỘT lần cài

Mỗi lần cài APK là một lần chịu rủi ro. Làm xong hết 5 FR, test kỹ trong trình duyệt, rồi mới build APK một lần duy nhất.

**Ngay sau khi cài xong, việc đầu tiên là mở app bấm Xuất tiến độ** (FR_011) và lưu chuỗi JSON lại. Từ lúc đó tiến độ mới thực sự an toàn.

---

## Thứ tự thực hiện

| # | FR | Nội dung | Vì sao thứ tự này |
|---|---|---|---|
| 1 | **FR_008** | Bỏ Kaiwa và Luyện đọc câu | Làm trước cho code gọn lại, bớt khoảng 250–300 dòng, rồi mới thêm mode mới |
| 2 | **FR_011** | Xuất / Nhập tiến độ, cỡ chữ, thời gian phản xạ | Ưu tiên cao nhất. Tạo `uiSettings` mà FR_010 cần đọc |
| 3 | **FR_009** | Điền từ vào câu (穴埋め) | Mode mới, dùng khuôn `quizMode()` |
| 4 | **FR_010** | Phản xạ 3 giây (瞬間作文) | Mode mới, đọc `uiSettings.reflexSec` từ FR_011 |
| 5 | **FR_012** | Màn hình Thống kê | Làm cuối, sửa luôn lỗi streak |

**Không nằm trong gói này:** FR_006 (tự focus Bộ nhỏ nhất) và FR_007 (luyện đọc bằng 213 đoạn audio thật). PM quyết để lại đợt sau.

---

## Ba ràng buộc xuyên suốt cả gói

### A. Không đụng `build_app.py` và không đổi hợp đồng dữ liệu

Tầng đọc Excel vừa được viết lại ở Phase 1 và đã khép lại. Dữ liệu từ vựng vẫn là mảng JSON 7 khóa `{id, w, r, vi, en, ex, c}`.

**Không FR nào trong gói được thêm trường mới vào JSON.** Bài Điền từ vào câu tính vị trí ô trống ngay trong JS lúc chạy, không tính sẵn ở bước build.

### B. Giữ đúng 4 icon trong lưới chọn Bộ

`deckGridHTML()` tô thẻ Bộ thành xanh lá khi **tất cả** icon truyền vào đều đã xong. Hiện có 4 icon 🗂️✍️🎧🎤.

Thêm icon thứ 5 hay thứ 6 cho 2 mode mới sẽ làm **mọi Bộ PM đã hoàn thành lập tức mất màu xanh**, nhìn như mất tiến độ.

→ **Giữ nguyên đúng 4 icon.** Hai mode mới vẫn ghi cờ vào `deckDone` để dành sau này, nhưng không hiển thị icon và không tính vào điều kiện Bộ đã xong. Điều kiện "hoàn thành 1 Bộ" của FR_006 cũng giữ nguyên 4 mode cũ.

### C. Không thêm thư viện, không thêm plugin

App phải giữ nguyên nguyên tắc: 1 file HTML tự chứa, chạy offline, không fetch gì từ ngoài.

- Vòng đếm ngược của FR_010: SVG viết tay.
- Lịch nhiệt và biểu đồ cột của FR_012: CSS grid và div, không dùng thư viện biểu đồ.
- Xuất tiến độ của FR_011: textarea cộng clipboard, **không thêm plugin Capacitor nào**.

Viết code mới bằng ES5 (`var`, `function`) cho đồng nhất với 2.000 dòng code đang có.

---

## Nghiệm thu trước khi build APK

Chạy đủ 6 bước, thiếu bước nào cũng không được báo xong:

1. `cd 01_Build_App/_app_build && python3 build_app.py` — chạy sạch, ra đúng **667 từ + 38 track**.
2. Kiểm tra cú pháp JS:
   ```bash
   python3 -c "import re; html=open('../Kokoro_Nihongo.html',encoding='utf-8').read(); m=re.search(r'<script>(.*?)</script>',html,re.DOTALL); open('_verify.js','w',encoding='utf-8').write(m.group(1))" && node --check _verify.js && rm _verify.js
   ```
3. Mở `Kokoro_Nihongo.html` bằng Chrome, mở DevTools tab Console — **không được có lỗi đỏ nào**.
4. Đi hết luồng: Trang chủ → IT専門 → chọn 1 Bộ → chạy thử **cả 7 mode** → mỗi mode phải tới được màn Hoàn thành → Back về trang chủ được.
5. Kiểm tra riêng 2 điểm dễ hỏng:
   - Lưới chọn Bộ vẫn đúng **4 icon**, các Bộ đã xong vẫn **xanh lá**.
   - Xuất tiến độ ra chuỗi JSON, nhập lại chính chuỗi đó — số liệu phải y nguyên.
6. Thu hẹp cửa sổ trình duyệt xuống khổ điện thoại (khoảng 400px) — không màn nào tràn ngang.

Xong 6 bước mới copy sang `03_Android_App/www/` và build APK.

**Sau khi build APK, trước khi cài: nhắc PM đọc lại mục ⚠️ ở đầu file này.**

---

## Ghi chú về `_id_lock.json`

Phase 1 đã thêm file `01_Build_App/_app_build/_id_lock.json` — sổ khóa giữ mỗi từ vựng đúng một `id` suốt đời, để tiến độ học không bị gắn nhầm khi PM xóa hay chèn dòng trong Excel.

- **Không xóa file này.** Xóa là mất ánh xạ, build lại sẽ đánh số lại từ đầu và tiến độ trong app gắn sai hết.
- **Không sửa tay.**
- Nên thêm vào `.gitignore` hay không: **KHÔNG** — nên commit vào git, vì nó là dữ liệu cần giữ lâu dài chứ không phải file tạm.
- File `_last_build_report.txt` sinh cùng chỗ thì ngược lại, nên cho vào `.gitignore`.
