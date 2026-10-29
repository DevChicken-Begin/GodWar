# Mốc hoạt ảnh đã chốt ngày 29/10/2026

Anh đã chốt các hoạt ảnh đang hiển thị tại thời điểm này. Danh sách chuẩn là `Asset/Character/characters/approved-animations-20261029.json`: 153 mục trong viewer, 154 bộ atlas (Crapit có thêm phần phụ), gồm `moxie_repaired` đã phục dựng đầu đạn. Mỗi mục ghi profile mặc định, chiều cao, số frame và SHA-256 của metadata và atlas; GIF nguồn cũng được đối chiếu theo hash trong metadata.

Viewer chọn profile mặc định theo danh sách này, gắn nhãn **Đã chốt**; các bản khác ghi **Tham khảo cũ**. Cảnh thử chỉ liệt kê các profile đã chốt. Trong Godot, dùng `GifAtlasLibrary.create_approved_animation(id)` để lấy profile mặc định; `create_measured_pilot` vẫn tồn tại để công cụ có thể nạp một profile cụ thể. Với Crapit, profile phụ `crapit_secondary` được ghi riêng trong danh sách.

Chạy `python tools/verify_approved_animations.py` để phát hiện catalog, kích thước, metadata, nguồn hoặc atlas đã khác mốc này. Khi có yêu cầu thay đổi về sau, cần cập nhật mốc/danh sách chốt một cách có chủ đích sau khi sửa và kiểm chứng; không chạy lại script tạo mốc đè lên bản hiện tại. `tools/freeze_current_animations.py` từ chối ghi đè mốc đã có. Các bản cũ và nguồn vẫn lưu để đối chiếu.

Việc anh chốt xác định phiên bản làm chuẩn; không phải bằng chứng đã đo hiệu năng, kiểm tra từng frame trên thiết bị hay phân loại các chuỗi thành động tác/skill. Các hạn chế kỹ thuật đã ghi trong metadata và tài liệu lịch sử vẫn áp dụng.

Sau mốc này, năm nhân vật mới được bổ sung riêng ở `provisional-animations-five-20261029.json`; viewer và cảnh thử hiển thị chúng với nhãn **mới, chưa chốt**, không nhập vào mốc 153 mục đã duyệt. Xem `docs/five-char-20261029.md`.

## Phiên bản 2

Ngày 2026-10-29, anh chốt thêm năm nhân vật: Mythos 80 px, Tracker 85 px, Epicti 80 px, Nemotront 80 px, Kanhosst 90 px. Mốc hiện hành là `Asset/Character/characters/approved-animations-20261029-v2.json`: 158 mục, 159 profile, gồm 153 mục của mốc trước giữ nguyên và năm mục mới. Viewer, cảnh thử và `GifAtlasLibrary.create_approved_animation` dùng mốc v2; file mốc cũ và hash của nó được giữ để đối chiếu. Việc chốt ghi nhận lựa chọn của anh, không thay thế kiểm tra chất lượng, đo thiết bị hoặc phân loại clip; các cảnh báo ở `docs/five-char-20261029.md` vẫn áp dụng.

Kiểm chứng v2: `python tools/verify_approved_animations.py` đạt 158 mục, 159 profile, 9.453 frame và 1.020 trang atlas; `python tools/verify_five_oct29.py` đạt 600 frame mới; `npm test` đạt 7/7. Godot 4.3 headless nạp 5 nhân vật qua `create_approved_animation` trong project tạm, kiểm tra 120 frame và mục tiêu của từng nhân vật: đạt. Chưa đo trên thiết bị thật.
