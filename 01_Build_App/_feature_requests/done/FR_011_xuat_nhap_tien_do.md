# FR_011 — Cài đặt: Xuất / Nhập tiến độ học, cỡ chữ, thời gian phản xạ

> Trạng thái: **Đã code xong, đã test qua trình duyệt desktop (2026-09-12). Chưa build APK cho gói Phase 2.**
> Thuộc gói Phase 2. **Đây là FR quan trọng nhất của gói** — xem mục 8.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-09-11 | Tạo FR_011. PM chọn cách đồng bộ bằng file xuất nhập thay vì cloud, để giữ nguyên tính offline của bản APK. | NguyenNC (qua Claude Cowork) |
| 2026-09-12 | **Sửa sau khi PM test bản APK đầu tiên**: bản gốc dùng textarea + nút Sao chép cho native (đúng như mục 4.1 mô tả), nhưng PM thấy copy/dán thủ công tốn công. Đổi sang **ghi file `.json` thật + mở hộp thoại Chia sẻ hệ thống** (thêm 2 plugin `@capacitor/filesystem` + `@capacitor/share` — phá vỡ ràng buộc "không thêm plugin" ở mục 6 bản gốc, đã được PM chấp thuận qua yêu cầu trực tiếp). Nhập tiến độ cũng đổi sang `<input type="file">` cho cả web lẫn native (trước đó chỉ web mới có). Xem mục 4.1/4.2/4.6/9 đã cập nhật bên dưới. | NguyenNC (qua Claude Cowork) |

## 1. Loại thay đổi

- [x] Thêm chức năng mới — xuất và nhập tiến độ học
- [x] Thay đổi UI/UX — thêm 2 ô chỉnh trong màn hình Cài đặt

## 2. Tên chức năng

**Xuất / Nhập tiến độ học** cộng 2 tùy chỉnh: **cỡ chữ** và **thời gian phản xạ**

## 3. Mô tả ngắn

Hiện tiến độ học nằm trong `localStorage` của từng thiết bị, máy tính và điện thoại hoàn toàn tách rời, và **không có cách nào sao lưu**. FR này thêm nút xuất toàn bộ tiến độ ra một chuỗi JSON và nút nhập lại, để chuyển máy được và có bản phòng hờ.

## 4. Hành vi mong muốn (chi tiết)

### 4.1 Xuất tiến độ

- Thêm mục **💾 Tiến độ học** trong `openSettings()`, đặt sau phần cài giọng đọc, ngăn bằng `<hr class="sep">`.
- Nút **📤 Xuất tiến độ**. Bấm vào thì gom đúng 3 key của app:

```javascript
var payload = {
  app: 'kokoro_nihongo',
  version: 1,
  exportedAt: new Date().toISOString(),
  wordCount: VOCAB.length,
  data: {
    jp_learn_v1:        localStorage.getItem('jp_learn_v1'),
    kokoro_gyoumu_v1:   localStorage.getItem('kokoro_gyoumu_v1'),
    kokoro_tts_settings:localStorage.getItem('kokoro_tts_settings'),
    kokoro_ui_settings: localStorage.getItem('kokoro_ui_settings')
  }
};
```

- **Hai đường xuất khác nhau tùy môi trường**, dùng `isNativeApp()` để phân nhánh (đã sửa 2026-09-12 — xem 0. 変更履歴):

| Môi trường | Cách xuất |
|---|---|
| **Web / Chrome** | Tạo `Blob`, gắn vào thẻ `<a download="kokoro_tien_do_YYYY-MM-DD.json">` rồi tự bấm. Tải file bình thường. |
| **APK Android** | `<a download>` **không hoạt động** trong WebView đóng gói. Dùng `@capacitor/filesystem` ghi file vào `Directory.Cache` (không cần xin quyền lưu trữ — scoped storage từ Android 10+ chặn ghi trực tiếp ra thư mục công khai), rồi gọi `@capacitor/share` mở hộp thoại Chia sẻ hệ thống để người học chọn "Lưu vào thiết bị"/Drive/Zalo/Mail. Nếu 2 plugin lỗi hoặc không có sẵn → rơi về `textarea` + nút Sao chép như bản cũ (không bao giờ kẹt cứng). |

- Nút Sao chép (chỉ còn dùng khi rơi vào nhánh dự phòng): thử `navigator.clipboard.writeText()` trước; lỗi thì rơi về `textarea.select()` cộng `document.execCommand('copy')`. Báo bằng toast khi xong.
- Hiện kèm dòng tóm tắt để người học biết mình vừa sao lưu cái gì:
  `Đã xuất: <N> từ có tiến độ · <M> từ đã thuộc · streak <S> ngày`

### 4.2 Nhập tiến độ

- Nút **📥 Nhập tiến độ**. Bấm vào thì mở ô chọn:
  - **`<input type="file" accept=".json">` cho cả web lẫn native** (sửa 2026-09-12 — Capacitor Android hỗ trợ sẵn `<input type="file">` mở trình chọn file gốc của hệ điều hành, không cần plugin riêng, nên không còn lý do giới hạn chỉ web).
  - Vẫn giữ `<textarea>` để dán chuỗi JSON thủ công, phòng khi không mở được file (ví dụ file bị mất/hỏng, hoặc máy không hỗ trợ trình chọn file).
- Sau khi nhận được chuỗi, **kiểm tra trước khi ghi**:
  1. `JSON.parse` được không. Lỗi → báo `Chuỗi không hợp lệ, hãy copy lại đầy đủ từ đầu đến cuối.`
  2. Có đúng `payload.app === 'kokoro_nihongo'` không. Sai → báo `File này không phải bản sao lưu của Kokoro Nihongo.`
  3. Có `payload.data.jp_learn_v1` không. Thiếu → báo thiếu dữ liệu tiến độ.

- **Bắt buộc hiện bảng so sánh trước khi ghi đè**, không được ghi thẳng:

```
                    Máy này        File nhập vào
Từ đã thuộc            120              340
Tổng lượt ôn           450             1890
Streak                   3               27
Ngày xuất                —       2026-09-11
```

- Dưới bảng là cảnh báo rõ ràng:
  `Nhập vào sẽ GHI ĐÈ toàn bộ tiến độ trên máy này. Không khôi phục lại được.`
- 2 nút: **Hủy** và **Ghi đè**. Mặc định con trỏ ở nút Hủy.
- Nếu số liệu máy này **lớn hơn** file nhập vào ở cả 3 dòng, hiện thêm dòng đỏ:
  `Máy này đang có nhiều tiến độ hơn file. Chắc chắn muốn ghi đè?`
- Bấm Ghi đè → ghi cả 4 key, rồi `location.reload()` để app nạp lại state sạch.

### 4.3 Cỡ chữ

- Thanh trượt **90% – 135%**, bước 5%, mặc định 100%.
- Áp dụng bằng biến CSS trên thẻ gốc: `document.documentElement.style.setProperty('--fs-scale', v)`.
  Trong CSS, các cỡ chữ chính nhân với biến này, ví dụ `font-size: calc(16px * var(--fs-scale, 1))`.
  Tối thiểu phải áp cho: chữ thân bài, từ vựng cỡ lớn (`.qword`), câu ví dụ, và các nút đáp án.
- Áp dụng **ngay khi kéo**, để người học thấy kết quả tức thì.
- Lý do có mục này: lão thị khởi phát điển hình ở tuổi 40–45, kanji nhiều nét in nhỏ trên điện thoại rất khó phân biệt.

### 4.4 Thời gian phản xạ

- 3 nút chọn **3 / 5 / 8 giây**, mặc định 3.
- Ghi vào `uiSettings.reflexSec`. FR_010 đọc giá trị này.

### 4.5 Key localStorage mới

Tạo key riêng `kokoro_ui_settings`, **không nhét chung vào `kokoro_tts_settings`**:

```javascript
const UI_KEY = "kokoro_ui_settings";
var uiSettings = loadUI();
function loadUI(){
  try{ return Object.assign({fontScale:1, reflexSec:3}, JSON.parse(localStorage.getItem(UI_KEY))||{}); }
  catch(e){ return {fontScale:1, reflexSec:3}; }
}
function saveUI(){ localStorage.setItem(UI_KEY, JSON.stringify(uiSettings)); }
```

Gọi áp dụng `fontScale` **ngay lúc app khởi động**, trước khi render `home()`, để không bị nháy cỡ chữ.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — mở rộng `openSettings()`, thêm `UI_KEY` / `loadUI()` / `saveUI()` / `exportProgress()` / `importProgress()`, thêm biến CSS `--fs-scale`
- [ ] `build_app.py` — không ảnh hưởng
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [x] `CLAUDE.md` — bổ sung key `kokoro_ui_settings` vào mục quy tắc 2
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật sau khi xong

## 6. Ràng buộc kỹ thuật

- ~~Không thêm plugin Capacitor mới~~ **(đã đổi 2026-09-12)**: PM test bản đầu thấy copy/dán thủ công tốn công, yêu cầu xuất/nhập bằng file thật. Đã thêm `@capacitor/filesystem` + `@capacitor/share` (FileProvider dùng lại cấu hình sẵn có của project, không cần sửa `AndroidManifest.xml`/`file_paths.xml`). Textarea + clipboard giữ lại làm đường lùi khi 2 plugin lỗi/không có sẵn.
- Không server, không tài khoản, không cần mạng. Toàn bộ chạy offline.
- **Không đổi tên hay cấu trúc 3 key localStorage đang có.** Xuất và nhập nguyên văn chuỗi, không parse rồi dựng lại — như vậy về sau schema có đổi thì bản sao lưu cũ vẫn nhập được.
- Nhập phải có bước xác nhận, tuyệt đối không ghi đè im lặng.
- Dùng ES5 cho đồng nhất với code cũ.

## 7. Ưu tiên

- [x] **Cao nhất trong gói Phase 2** — xem mục 8

## 8. Ghi chú thêm — vì sao FR này quan trọng nhất

PM đã học rất nhiều trên bản APK, và **toàn bộ tiến độ đó hiện không có bản sao lưu nào**. Nếu điện thoại hỏng, hoặc lỡ gỡ app ra cài lại, là mất sạch, không lấy lại được.

Vì vậy thứ tự thực hiện gói Phase 2 nên là:

1. **FR_011 trước tiên** (ít nhất là phần Xuất).
2. Các FR còn lại.
3. Build APK **một lần duy nhất** cho cả gói.
4. **Ngay sau khi cài xong, mở app bấm Xuất tiến độ** và lưu chuỗi JSON lại. Từ lúc đó trở đi tiến độ mới thực sự an toàn.

Cũng nhắc PM: khi cài APK mới thì **cài đè lên bản cũ, tuyệt đối không gỡ app ra cài lại**. Android giữ nguyên dữ liệu app khi cài đè cùng tên app và cùng khóa ký. Gỡ app là xóa sạch localStorage.

Ghi chú thêm về bản web: app mở bằng `file://` nên mỗi đường dẫn file là một vùng lưu riêng trong Chrome. Đổi tên file hoặc chuyển thư mục là tiến độ bản web coi như mất. Bản APK không bị vấn đề này.

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro

| # | Nội dung | Mức | Quyết định |
|---|---|---|---|
| 1 | `<a download>` không hoạt động trong WebView của APK — đây chính là môi trường PM dùng chính. | **Cao** | Phân nhánh bằng `isNativeApp()`. Native ghi file bằng `@capacitor/filesystem` rồi mở share sheet bằng `@capacitor/share` (đổi 2026-09-12, xem 0. 変更履歴); textarea+Sao chép chỉ còn là đường lùi. Bắt buộc test thật trên APK — cả luồng ghi file/share sheet lẫn `<input type="file">` phía nhập đều chưa test được trên thiết bị thật (máy dev không có Android thật), chỉ verify được bằng mock `window.Capacitor` trong Chrome. |
| 2 | Nhập nhầm file của thiết bị khác rồi ghi đè mất tiến độ đang có nhiều hơn. | **Cao** | Bắt buộc hiện bảng so sánh, cảnh báo đỏ khi máy này nhiều hơn, mặc định con trỏ ở nút Hủy. |
| 3 | Chuỗi JSON rất dài, dán vào Zalo có thể bị cắt. | Trung bình | Hiện độ dài chuỗi kèm lời nhắc kiểm tra ký tự cuối là `}`. Khi nhập, kiểm tra `JSON.parse` sẽ bắt được nếu bị cắt. |
| 4 | `navigator.clipboard` cần ngữ cảnh bảo mật, có thể lỗi trên `file://`. | Trung bình | Rơi về `execCommand('copy')`. Vẫn lỗi thì để nguyên textarea cho người học tự bôi đen copy tay. |
| 5 | Nhập bản sao lưu cũ khi app đã đổi schema. | Trung bình | Xuất và nhập nguyên văn chuỗi, không dựng lại. Cơ chế migrate sẵn có (`if(!store.deckDone) store.deckDone={};`) sẽ tự bù phần thiếu. |
| 6 | Tiến độ 2 máy đã lệch nhau, nhập một chiều sẽ mất một bên. | Trung bình | Bản này chỉ làm **ghi đè**, chưa làm gộp. PM đã đồng ý. Nếu sau này cần gộp theo nguyên tắc bậc cao hơn thắng thì mở FR mới. |
| 7 | `fontScale` áp muộn gây nháy cỡ chữ lúc mở app. | Thấp | Áp ngay lúc khởi động, trước khi gọi `home()`. |
| 8 | Cỡ chữ 135% có thể làm vỡ layout ở vài màn hình. | Thấp | Test 3 mức 90 / 100 / 135% trên khổ điện thoại hẹp nhất, sửa chỗ nào tràn. |
