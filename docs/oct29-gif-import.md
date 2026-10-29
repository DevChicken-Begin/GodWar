# Lô 13 GIF ngày 29/10 — bản thử để xem trên localhost

Nguồn là 13 GIF người dùng đặt ở thư mục gốc. `tools/import_oct29_gifs.py` sao chép nguyên byte vào `Asset/Character/vfx/`, tách từng frame vào atlas trong `extracted/`, và tạo atlas alpha nguyên kích thước trong `native_candidates/`. `candidate.json` của từng nguồn ghi SHA-256, thời lượng frame, màu nền đo được và số pixel bị xóa. Ảnh xem nhanh ở `Asset/Character/review/<id>/sample-keyed.jpg`.

Phương pháp: lấy màu viền phổ biến theo từng frame rồi xóa pixel sai khác RGB tối đa 5. `dragonot` có nhiều dải nền phẳng nên còn xóa các màu tối chính xác xuất hiện ở viền và chiếm ít nhất 0,5% frame. Không đổi kích thước, tốc độ hoặc thứ tự frame. `art_source=existing`; không tạo hình mới và không tạo animation bằng AI.

**Tình trạng:** Bản tách nền chưa duyệt. Mẫu đầu/giữa/cuối của từng GIF đã được xem trước khi nhập; atlas alpha cần tiếp tục xem toàn bộ frame trên nền sáng và tối. Màu tối của nhân vật có thể trùng nền; `dragonot` đặc biệt cần kiểm tra các chi tiết tối và mảng nền còn sót. Chưa xác nhận danh tính từ tên file, chưa phân đoạn idle/chạy/đánh/skill, chưa chọn master, chưa xuất SpriteFrames Godot và chưa kiểm thử mobile. `roster.json` để `animations={}` và `skill.status=unreviewed` vì GIF không chứng minh tên động tác.

Xem bản thử: `npm run dev`, mở `http://localhost:4173`, tìm tên GIF và chọn **Tách nền nguyên kích thước · chưa duyệt** hoặc **Atlas nguồn** để so. Dùng thanh frame và đổi nền để kiểm tra. Có thể dùng `PORT=5000 npm run dev` nếu cổng 4173 bận.

Tái tạo trên checkout chưa nhập: `/home/codespace/.local/share/godwar-sprite-forge/venv/bin/python tools/import_oct29_gifs.py`. Script chỉ chạy khi các đích chưa tồn tại để tránh ghi đè asset cũ. `forge_doctor.py` đã chạy ngày 29/10: có Python/Pillow/numpy/scipy trong venv và skill khớp bản cài; thiếu ffmpeg và route tạo video, không ảnh hưởng việc tách GIF có sẵn.

Kiểm tra đã chạy: đối chiếu SHA-256 giữa 13 nguồn và bản sao, số frame và thời lượng từng frame của GIF với catalog, kích thước vùng atlas, và alpha của đủ 943 frame; tất cả đạt. `npm test`: 4/4 bài kiểm tra viewer đạt. API localhost trả 200 cho trang, GIF nguồn và atlas thử; cả 13 id có trong `/api/assets` và `/api/native-candidates`. Chưa kiểm thử trong Godot editor hoặc thiết bị thật.

## Cập nhật theo ảnh kiểm thử của anh

Ảnh `dragonot` trên nền caro cho thấy rất nhiều hạt tối còn sót ở vùng trong suốt. `tools/clean_dragonot_specks.py` tạo bản thử mới trong `revision_candidates/dragonot`, giữ bản `native_candidates` để đối chiếu. Bộ lọc tìm thành phần alpha liên thông 8 hướng, xóa pixel màu nền tối trong các thành phần có tối đa 16 pixel. Kết quả: 49 frame, 22.425 pixel hạt được xóa; frame nhiều nhất 2.783 pixel. Ảnh mẫu trên nền sáng: `Asset/Character/revision_candidates/dragonot/sample-light.jpg`. Đã xem lại frame 0, 17, 31, 48 trên nền caro; không còn các chấm đen rải khắp như ảnh báo lỗi. Viewer chọn bản này mặc định khi tìm `dragonot`; cần kiểm duyệt các hiệu ứng tối tách rời có thể bị mất.

Theo yêu cầu, đã xóa asset của `knigblack`, `monsterdead`, `newwomen`, `firer`, `kapicon` khỏi `Asset/Character`: GIF, atlas, mọi thư mục bản thử mang đúng id, và các mục catalog/roster/inventory/trạng thái đang dùng. `removed.json` cũng chặn hiển thị nếu catalog cũ được nạp. Tài liệu báo cáo cũ và mã công cụ lịch sử vẫn có thể nhắc đến các id đã xóa; chúng không còn là asset có thể xem trong viewer.
