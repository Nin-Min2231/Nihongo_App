# FR_001 — Export/Import tiến độ học

> Đây là file MẪU để tham khảo cách viết. Tên file bắt đầu `_EXAMPLE` nên Claude sẽ bỏ qua khi thực hiện.

---

## 1. Loại thay đổi

- [x] Thêm chức năng mới (new feature)

## 2. Tên chức năng

Export/Import tiến độ học (backup & restore)

## 3. Mô tả ngắn

Cho phép user export toàn bộ tiến độ SRS (box, due, streak) ra file JSON để backup. Và import lại khi đổi thiết bị hoặc xóa cache trình duyệt.

## 4. Hành vi mong muốn (chi tiết)

- Trang chủ thêm icon ⚙️ ở góc phải header → chạm vào mở menu Settings
- Menu có 2 nút:
  - "📤 Export tiến độ" → tạo file `kokoro_backup_2026-07-17.json` và download
  - "📥 Import tiến độ" → mở file picker chọn JSON → confirm "Dữ liệu hiện tại sẽ bị thay thế" → load vào localStorage
- Sau import → quay về home, hiện toast "Đã khôi phục tiến độ: 120 từ đã thuộc"

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — thêm UI settings + logic export/import
- [ ] `build_app.py`
- [ ] `日本語の辞書.xlsx`
- [x] `PROJECT_日本語学習アプリ_Handover.md` — ghi lại chức năng mới

## 6. Ràng buộc kỹ thuật

- Phải hoạt động offline (dùng Blob + download attribute, không cần server)
- Giữ nguyên key localStorage `jp_learn_v1`
- File JSON phải có version field để sau này migrate được

## 7. Ưu tiên

- [ ] Cao
- [x] Trung bình
- [ ] Thấp

## 8. Ghi chú thêm

Đây là item từ backlog mục 8 trong file Handover.
