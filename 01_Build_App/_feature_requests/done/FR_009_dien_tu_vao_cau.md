# FR_009 — Chế độ học mới: Điền từ vào câu (穴埋め)

> Trạng thái: **Đã code xong, đã test qua trình duyệt desktop (2026-09-12). Chưa build APK cho gói Phase 2.**
> Thuộc gói Phase 2. Làm SAU FR_008.

---

## 0. 変更履歴

| Ngày | Nội dung | Người tạo |
|---|---|---|
| 2026-09-11 | Tạo FR_009. PM chọn bài này làm bài bổ sung số 1 cho mục tiêu nhớ lâu từ chuyên ngành. Thuật toán dò ô trống đã được kiểm chứng trên đủ 667 từ: phủ 629 từ, đạt 94,3%. | NguyenNC (qua Claude Cowork) |

## 1. Loại thay đổi

- [x] Thêm chức năng mới — chế độ học thứ 6 của module IT専門

## 2. Tên chức năng

**Điền từ vào câu** (穴埋め) — mode id `cloze`

## 3. Mô tả ngắn

Lấy câu ví dụ ở cột G của từ đang học, che đúng từ đó thành ô trống, người học chọn lại từ đúng trong 4 phương án. Khác Quiz ở chỗ từ được đặt trong ngữ cảnh nghiệp vụ thật chứ không đứng rời, nên nhớ bền hơn nhiều.

## 4. Hành vi mong muốn (chi tiết)

### 4.1 Vào bài

- Thêm nút thứ 6 vào lưới `.modes` trong `homeDashboard()`, đặt **ngay sau Quiz**:

```
'<button class="mode" data-mode="cloze">'+
  '<span class="ico">🧩</span><div class="mt">Điền từ</div><div class="md">Điền vào câu ví dụ</div></button>'+
```

- Thêm nhánh vào `startMode()`: `else if(m==='cloze') clozeMode(list);`
- Hàm `clozeMode(list)` đặt ngay sau `quizMode()`, viết theo đúng khuôn của `quizMode` cho dễ đối chiếu.

### 4.2 Lọc từ dùng được

- Bỏ các từ đã đánh dấu đã nhớ: `list.filter(function(v){return !isMastered(v.id);})`
- Chỉ giữ từ **dò được ô trống** (`findCloze(v) !== null`).
- Nếu số từ còn lại **nhỏ hơn 4** → hiện thông báo và không vào bài:
  `'<div class="note">Bộ này không đủ 4 từ có câu ví dụ dùng được để tạo bài Điền từ. Hãy thử Quiz hoặc Flashcard nhé!</div>'`
  Nhớ gọi `setHeader('Điền từ','',true)` **trước** mọi lệnh `return` sớm — lỗi này đã gặp ở `listenMode`.
- Số câu: giống Quiz — `curDeck==='ALL'` thì lấy 15 câu, học theo Bộ thì lấy hết.

### 4.3 Thuật toán dò ô trống

Dán nguyên 2 hàm dưới đây vào `app_template.html`, đặt cạnh `allWithEx()`. Đã kiểm chứng trên đủ 667 từ, **không sửa lại logic**:

```javascript
/* Sinh các dạng chữ có thể xuất hiện trong câu ví dụ, dài trước ngắn sau */
function clozeCandidates(w){
  var base = w.replace(/[（(][^）)]*[)）]/g,'').replace(/　/g,' ').trim();
  var seeds = {}; seeds[base]=1; seeds[w.trim()]=1;
  base.split(/[\/／=＝]/).forEach(function(p){ p=p.trim(); if(p) seeds[p]=1; });
  var out = {};
  Object.keys(seeds).forEach(function(t){
    t = t.replace(/^[〜～]+/,'').trim(); if(!t) return;
    out[t]=1;
    ['する','です','ます','な','い'].forEach(function(suf){
      if(t.length>suf.length && t.slice(-suf.length)===suf) out[t.slice(0,-suf.length)]=1;
    });
    var m = t.match(/^[一-鿿]{1,6}/); if(m) out[m[0]]=1;
  });
  return Object.keys(out).filter(function(t){return t.length>0 && t.indexOf('✙')<0;})
                         .sort(function(a,b){return b.length-a.length;});
}

/* Trả về [vị trí, độ dài] đoạn cần che trong v.ex, hoặc null nếu không dò được */
function findCloze(v){
  var ex = v.ex||''; if(!ex) return null;
  var cands = clozeCandidates(v.w);
  for(var i=0;i<cands.length;i++){
    var t=cands[i], p=ex.indexOf(t);
    if(p<0) continue;
    if(t.length===1 && !/[一-鿿]/.test(t)) continue;   // 1 ký tự kana thì bỏ, quá dễ nhầm
    return [p,t.length];
  }
  var y=(v.r||'').replace(/[（(][^）)]*[)）]/g,'').trim();
  var ys=[y].concat(y.split(/[\/／・]/)).map(function(s){return s.trim();})
            .filter(function(s){return s.length>=2;})
            .sort(function(a,b){return b.length-a.length;});
  for(var j=0;j<ys.length;j++){ var q=ex.indexOf(ys[j]); if(q>=0) return [q,ys[j].length]; }
  return null;
}
```

Vì sao cần dò theo gốc từ: 114 trong 667 câu ví dụ không chứa nguyên văn từ, phần lớn do động từ bị chia. Ví dụ `入力する` xuất hiện thành `入力して`, `揃う` thành `揃った`. Dò theo gốc kéo tỉ lệ phủ từ 82,9% lên 94,3%.

### 4.4 Màn hình câu hỏi

- Đầu màn: `'<div class="counter">Điền từ còn thiếu vào câu</div>'`
- Câu ví dụ hiển thị với đoạn đã dò thay bằng **`＿＿＿`** (3 ký tự gạch dưới toàn rộng), không phải gạch dài theo đúng số ký tự. Lý do: một số trường hợp chỉ che được phần gốc Hán tự (ví dụ `切り分ける` che thành `【切】り分けて`), nếu vẽ gạch theo đúng độ dài thì lộ manh mối và trông lệch.
- Cỡ chữ câu ví dụ phải **đủ lớn để đọc thoải mái**, tối thiểu 18px, dòng thưa (`line-height` khoảng 2).
- 4 phương án là **`v.w` nguyên văn** của 4 từ: đáp án đúng cộng 3 từ nhiễu lấy bằng `sample(list,3,v)` — giống hệt cách Quiz lấy nhiễu.
- Có nút **Gợi ý** dưới câu, bấm lần lượt mở 3 bậc, mỗi bậc hiện thêm một dòng, không thu lại được:
  1. Bậc 1 — nghĩa tiếng Việt: `v.vi`
  2. Bậc 2 — ký tự đầu của đáp án: ký tự đầu tiên của `v.w` cộng `…`
  3. Bậc 3 — cách đọc: `v.r`
  Sau bậc 3 thì ẩn nút Gợi ý đi.

### 4.5 Sau khi trả lời

- Tô màu phương án giống hệt Quiz: đúng thì `.correct`, chọn sai thì `.wrong` và tô `.correct` cho đáp án đúng, còn lại `.dim`.
- Chấm điểm: đúng → `reviewCard(v.id,2)` và `score++`; sai → `reviewCard(v.id,0)`.
- **Hiện lại câu ví dụ đầy đủ**, đoạn vừa che được tô nền vàng nhạt để mắt bắt được ngay.
- Có **nút loa đọc cả câu**: `speak(v.ex)`. Nếu câu không chứa ký tự tiếng Nhật thì **ẩn nút loa** — kiểm tra bằng `/[぀-ヿ一-鿿]/.test(v.ex)`. Hiện có đúng 1 câu như vậy (dòng 611, từ `数量`, câu viết hoàn toàn bằng tiếng Việt).
- Chuyển câu sau: đúng thì 750ms, sai thì 1600ms — giống Quiz.

### 4.6 Kết thúc

- Gọi `finish('cloze', queue.length, score);`
- `finish()` sẽ tự gọi `markDeckDone(curCat, curDeck, 'cloze')` — không cần sửa gì thêm.
- Nút "Học tiếp" trong `finish()` gọi `startMode('cloze')`, chạy được nhờ nhánh đã thêm ở 4.1.

### 4.7 KHÔNG thêm icon vào lưới chọn Bộ

**Đây là điểm quan trọng nhất, làm sai sẽ phá tiến độ đang hiển thị.**

Lưới chọn Bộ hiện có 4 icon 🗂️✍️🎧🎤, và `deckGridHTML()` tô thẻ Bộ thành xanh lá khi **tất cả** icon đều xong. Nếu thêm icon thứ 5 cho mode `cloze`, mọi Bộ PM đã hoàn thành sẽ lập tức mất màu xanh, nhìn như bị mất tiến độ.

→ **Giữ nguyên đúng 4 icon.** Mode `cloze` vẫn ghi cờ vào `deckDone` để dành cho sau này, nhưng **không hiển thị icon và không tính vào điều kiện thẻ Bộ đã xong**.

Cũng vì vậy, điều kiện "hoàn thành 1 Bộ" của FR_006 giữ nguyên đúng 4 mode `flash`, `quiz`, `listen`, `speak` — không thêm `cloze` vào.

## 5. Ảnh hưởng đến file nào

- [x] `app_template.html` — thêm `clozeCandidates()`, `findCloze()`, `clozeMode()`; thêm 1 nút mode; thêm 1 nhánh `startMode()`
- [ ] `build_app.py` — không ảnh hưởng, dùng đúng dữ liệu `w`, `r`, `vi`, `ex` đã có
- [ ] `日本語の辞書.xlsx` — không ảnh hưởng
- [x] `CLAUDE.md` — cập nhật danh sách mode của IT専門 từ 5 thành 6
- [x] `PROJECT_日本語学習アプリ_Handover.md` — cập nhật sau khi xong

## 6. Ràng buộc kỹ thuật

- **Tính ô trống ngay trong JS lúc chạy**, không thêm trường mới vào JSON từ vựng. Hợp đồng dữ liệu 7 khóa `{id,w,r,vi,en,ex,c}` giữ nguyên tuyệt đối — `build_app.py` không phải sửa gì.
- Không thêm thư viện ngoài. App vẫn chạy offline.
- Không đổi cấu trúc `localStorage`.
- Không phá `deckGridHTML()` — xem mục 4.7.
- Dùng ES5 như phần còn lại của file (`var`, `function`), không dùng `let`/arrow function trong code mới để đồng nhất với code cũ.

## 7. Ưu tiên

- [x] Cao — đây là bài tập hiệu quả nhất cho mục tiêu nhớ lâu

## 8. Ghi chú thêm

- Số liệu đã đo trên đúng file từ điển 667 từ ngày 2026-09-11:

| | |
|---|---|
| Tạo được ô trống | **629 từ (94,3%)** |
| Không tạo được | 38 từ |

- 38 từ không dùng được đều có lý do rõ: câu ví dụ dùng từ đồng nghĩa thay vì chính từ đó (`要求` nhưng câu dùng `リクエスト`, `鍵` nhưng câu dùng `キー`), hoặc câu lệch hẳn chủ đề. Các từ này app tự bỏ qua, người học không thấy gì bất thường.
- Vì sao bài này mạnh: nó gộp cùng lúc ba yếu tố — bắt buộc tự nhớ ra, đặt trong ngữ cảnh nghiệp vụ quen thuộc, và độ khó vừa đủ. Với người đã có sẵn khung nghiệp vụ IT trong đầu thì học từ trong câu thật hiệu quả hơn hẳn học cặp từ và nghĩa rời rạc.

## 9. Rà soát: Điểm mơ hồ / Edge case / Rủi ro

| # | Nội dung | Mức | Quyết định |
|---|---|---|---|
| 1 | Thêm icon thứ 5 vào lưới Bộ sẽ làm mọi Bộ đã hoàn thành mất màu xanh, nhìn như mất tiến độ. | **Cao** | **Giữ đúng 4 icon.** Mode `cloze` ghi `deckDone` nhưng không hiển thị và không tính vào điều kiện Bộ đã xong. Xem 4.7. |
| 2 | 38 từ không dò được ô trống. | Trung bình | Lọc bỏ khỏi danh sách bài. Nếu bộ còn dưới 4 từ thì báo và mời sang Quiz. |
| 3 | Có trường hợp chỉ che được phần gốc Hán tự, ví dụ `切り分ける` thành `＿＿＿り分けて`, phần đuôi còn lộ. | Trung bình | **Chấp nhận.** Người học vẫn phải nhớ ra mặt chữ Hán, phần khó nhất vẫn còn. Dùng `＿＿＿` cố định 3 ký tự nên không lộ độ dài. |
| 4 | Từ nhiễu có thể trùng nghĩa với đáp án, gây tranh cãi đúng sai. | Thấp | Dùng đúng `sample(list,3,v)` như Quiz. Xác suất thấp, và Quiz đã chạy như vậy lâu nay không sao. |
| 5 | Dòng 611 từ `数量` có câu ví dụ viết hoàn toàn bằng tiếng Việt → bộ đọc tiếng Nhật sẽ đọc sai. | Thấp | Ẩn nút loa khi câu không chứa ký tự tiếng Nhật. Đồng thời PM nên sửa câu này trong Excel. |
| 6 | Câu ví dụ dài trên 60 ký tự (19 câu) hiển thị trên điện thoại sẽ tràn nhiều dòng. | Thấp | Cho xuống dòng tự nhiên, không cắt. Khung `max-width:560px` đã có sẵn, đọc vẫn được. |
| 7 | Người học bấm Gợi ý cả 3 bậc rồi mới chọn đúng — có nên tính là đúng không? | Thấp | **Vẫn tính đúng**, không trừ điểm. Giữ đơn giản. Nếu sau này thấy dễ quá thì mở FR mới. |
