# Kokoro Nihongo (ココロ日本語) — App học tiếng Nhật cho PM/BrSE ngành IT

App học từ vựng & hội thoại tiếng Nhật, tập trung vào thuật ngữ IT — dùng offline trên điện thoại (1 file HTML) hoặc cài như app Android thật (APK, dùng Capacitor).

## 1. Tổng quan quy trình

```
日本語の辞書.xlsx  (từ điển gốc, 596 từ)
        │  build_app.py
        ▼
Kokoro_Nihongo.html  (app học — mở trực tiếp bằng trình duyệt trên máy tính/điện thoại)
        │  Capacitor (npx cap sync + gradlew)
        ▼
Kokoro_Nihongo.apk  (app Android thật — cài trực tiếp lên điện thoại, có mic native)
```

## 2. Cấu trúc thư mục

```
100_日本語/
├── 日本語の辞書.xlsx                     ← Từ điển gốc (596 từ, KHÔNG mở bằng openpyxl.save())
├── CLAUDE.md                              ← Quy tắc/kiến trúc dự án (đọc trước khi sửa code)
├── PROJECT_日本語学習アプリ_Handover.md   ← Tài liệu handover chi tiết
├── README.md                              ← File này
│
├── 01_Build_App/                          ← App IT専門 (từ vựng) — build từ xlsx
│   ├── Kokoro_Nihongo.html                ← App đã build sẵn, mở được ngay
│   ├── audio/                             ← (KHÔNG commit git) copy từ 02_IT_Gyoumuhen/AudioCD
│   ├── _app_build/
│   │   ├── build_app.py                   ← Script build: xlsx → JSON → inject vào template
│   │   └── app_template.html              ← Toàn bộ CSS + JS của app (sửa file này để thêm tính năng)
│   └── _feature_requests/                 ← TEMPLATE.md (viết FR mới) + done/ (lịch sử FR đã hoàn thành)
│
├── 02_IT_Gyoumuhen/                        ← Nguồn dữ liệu module IT業務編 (hội thoại công việc)
│   ├── IT_Gyoumuhen.pdf                    ← Sách gốc (scan, chỉ để tham khảo)
│   ├── IT_Gyoumuhen_AudioCD_Transcript.xlsx ← Transcript 38 track hội thoại
│   └── AudioCD/                            ← 38 file mp3 gốc (nguồn audio DUY NHẤT, các nơi khác chỉ là bản copy)
│
└── 03_Android_App/                         ← Project Capacitor — đóng gói HTML thành APK Android
    ├── package.json, capacitor.config.json
    ├── www/                                 ← (KHÔNG commit git) copy từ Kokoro_Nihongo.html + audio
    ├── android/                             ← Project Android native (Gradle)
    └── Kokoro_Nihongo.apk                   ← (KHÔNG commit git) APK build sẵn để cài lên điện thoại
```

> **Vì sao vài thư mục không đưa lên GitHub:** `audio/` ở `01_Build_App` và `www/` ở `03_Android_App` chỉ là **bản copy** của `02_IT_Gyoumuhen/AudioCD/` (được script tự copy khi build) — nếu commit cả 3 nơi sẽ tốn dư ~140MB dữ liệu trùng lặp trong repo. Xem chi tiết trong `.gitignore`.

## 3. Cách đọc source code

- **Muốn sửa giao diện/tính năng app học từ vựng, IT業務編, Luyện đọc, Kaiwa:** sửa `01_Build_App/_app_build/app_template.html` — toàn bộ CSS + JS nằm trong 1 file này (không dùng framework/build tool, JavaScript thuần).
- **Muốn sửa cách trích dữ liệu từ xlsx:** sửa `01_Build_App/_app_build/build_app.py`.
- **Muốn hiểu kiến trúc, quy tắc, lịch sử quyết định:** đọc `CLAUDE.md` và `PROJECT_日本語学習アプリ_Handover.md` trước tiên.
- **Muốn sửa phần Android/Capacitor:** vào `03_Android_App/android/` (project Android chuẩn, mở bằng Android Studio cũng được).

## 4. Cách build & chạy debug

### 4.1. Build lại app HTML (sau khi sửa `app_template.html` hoặc thêm từ vào xlsx)

Yêu cầu: Python 3.

```bash
cd 01_Build_App/_app_build
python3 build_app.py
```

Script tự đọc `日本語の辞書.xlsx` + `02_IT_Gyoumuhen/IT_Gyoumuhen_AudioCD_Transcript.xlsx`, tự copy audio, sinh ra `01_Build_App/Kokoro_Nihongo.html`. Đường dẫn trong script tự suy ra từ vị trí file, chạy được ở bất kỳ máy nào, không cần sửa.

### 4.2. Chạy thử / debug app HTML

Chỉ cần mở trực tiếp file `01_Build_App/Kokoro_Nihongo.html` bằng trình duyệt (Chrome/Edge) — không cần server. Mở DevTools (F12) để xem console/debug JS bình thường.

**Lưu ý:** phần ghi âm (mic chấm điểm phát âm) dùng Web Speech API — hoạt động trên Chrome desktop/Android, **không hoạt động trên iOS Safari và không hoạt động trong WebView của APK** (xem mục 4.3).

### 4.3. Build APK Android (để debug mic thật, hoặc cài lên điện thoại)

Yêu cầu: Node.js, JDK 21, Android SDK (build-tools 36.1.0, platform android-36).

> Máy hiện tại (máy đã tạo project này) đã cài sẵn JDK 21 + Android SDK portable tại `D:\Android\jdk21` và `D:\Android\Sdk` (không nằm trong repo, không cần cài lại nếu build trên chính máy này). Nếu build trên máy khác, cần:
> 1. Tự cài JDK 21+ và Android SDK (qua Android Studio hoặc `sdkmanager`).
> 2. Tạo file `03_Android_App/android/local.properties` với nội dung `sdk.dir=<đường dẫn tới Android SDK>`.
> 3. **Sửa/xóa dòng `org.gradle.java.home=D:\\Android\\jdk21` trong `03_Android_App/android/gradle.properties`** — dòng này đang trỏ cứng tới JDK trên máy hiện tại, cần đổi sang đường dẫn JDK 21 trên máy mới (hoặc xóa dòng này nếu máy đã có sẵn JDK 21+ hệ thống, Gradle sẽ tự tìm qua `JAVA_HOME`).
>
> Dòng `android.overridePathCheck=true` trong cùng file thì **giữ nguyên** — dòng này không phải cấu hình riêng máy, mà để né lỗi Android Gradle Plugin chặn đường dẫn project chứa ký tự non-ASCII (thư mục `100_日本語`), cần cho mọi máy build.

```bash
cd 03_Android_App
npm install                          # cài @capacitor/core, @capacitor/android, plugin mic native

# copy bản HTML/audio mới nhất vào www/ trước khi build
cp ../01_Build_App/Kokoro_Nihongo.html www/index.html
cp ../01_Build_App/audio/*.mp3 www/audio/     # nếu chưa có audio, copy từ 02_IT_Gyoumuhen/AudioCD

npx cap sync android                 # đồng bộ www/ + plugin vào project Android

cd android
./gradlew.bat assembleDebug          # Windows — bỏ .bat nếu build trên Mac/Linux
```

APK sinh ra tại `android/app/build/outputs/apk/debug/app-debug.apk`. Cài lên điện thoại Android bằng cách chuyển file qua rồi bấm cài (cần bật "Cài từ nguồn không xác định").

**Debug APK trên điện thoại thật:** mở project `03_Android_App/android/` bằng Android Studio, kết nối điện thoại qua USB (bật chế độ Nhà phát triển + gỡ lỗi USB), bấm Run — Android Studio cho xem log, đặt breakpoint trong code Java/Kotlin của plugin nếu cần, và xem console JS qua `chrome://inspect` trên Chrome desktop (kết nối cùng USB).

## 5. Đẩy lên GitHub

Repo local đã được khởi tạo (`git init` + commit đầu tiên). Để đẩy lên GitHub:

1. Tạo 1 repository mới trên [github.com](https://github.com) (không tick "Initialize with README" vì đã có sẵn).
2. Trong thư mục `100_日本語/`, chạy:
   ```bash
   git remote add origin https://github.com/<tên-tài-khoản>/<tên-repo>.git
   git branch -M main
   git push -u origin main
   ```
3. Nếu muốn chia sẻ APK đã build sẵn mà không muốn nhét vào git (APK ~73MB), có thể tạo 1 "Release" trên GitHub và đính kèm file `Kokoro_Nihongo.apk` vào đó thay vì commit trực tiếp.

## 6. Quy tắc quan trọng cần nhớ

- **KHÔNG dùng `openpyxl.save()`** để sửa `日本語の辞書.xlsx` — sẽ mất màu/border/theme. Luôn sửa raw XML (xem `PROJECT_日本語学習アプリ_Handover.md` mục 3.3).
- **Không sửa tay `Kokoro_Nihongo.html`** — file này luôn bị `build_app.py` ghi đè. Sửa `app_template.html` rồi build lại.
- Module IT業務編 (audio) và phần APK Android **không còn là single-file 100%** — cần giữ đúng cấu trúc thư mục audio khi phân phối (xem mục 2).
- Chi tiết đầy đủ hơn: đọc `CLAUDE.md`.
