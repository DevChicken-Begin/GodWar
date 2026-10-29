# Mốc hoạt ảnh đã chốt ngày 29/10/2026

Anh đã chốt các hoạt ảnh đang hiển thị tại thời điểm này. Danh sách chuẩn là `Asset/Character/characters/approved-animations-20261029.json`: 153 mục trong viewer, 154 bộ atlas (Crapit có thêm phần phụ), gồm `moxie_repaired` đã phục dựng đầu đạn. Mỗi mục ghi profile mặc định, chiều cao, số frame và SHA-256 của metadata và atlas; GIF nguồn cũng được đối chiếu theo hash trong metadata.

Viewer chọn profile mặc định theo danh sách này, gắn nhãn **Đã chốt**; các bản khác ghi **Tham khảo cũ**. Cảnh thử chỉ liệt kê các profile đã chốt. Trong Godot, dùng `GifAtlasLibrary.create_approved_animation(id)` để lấy profile mặc định; `create_measured_pilot` vẫn tồn tại để công cụ có thể nạp một profile cụ thể. Với Crapit, profile phụ `crapit_secondary` được ghi riêng trong danh sách.

Chạy `python tools/verify_approved_animations.py` để phát hiện catalog, kích thước, metadata, nguồn hoặc atlas đã khác mốc này. Khi có yêu cầu thay đổi về sau, cần cập nhật mốc/danh sách chốt một cách có chủ đích sau khi sửa và kiểm chứng; không chạy lại script tạo mốc đè lên bản hiện tại. `tools/freeze_current_animations.py` từ chối ghi đè mốc đã có. Các bản cũ và nguồn vẫn lưu để đối chiếu.

Việc anh chốt xác định phiên bản làm chuẩn; không phải bằng chứng đã đo hiệu năng, kiểm tra từng frame trên thiết bị hay phân loại các chuỗi thành động tác/skill. Các hạn chế kỹ thuật đã ghi trong metadata và tài liệu lịch sử vẫn áp dụng.
