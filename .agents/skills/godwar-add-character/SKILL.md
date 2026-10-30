---
name: godwar-add-character
description: Nhập nhân vật mới vào dự án GodWar khi người dùng nói “Thêm char mới” hoặc yêu cầu thêm GIF/ảnh nhân vật; tách nền, đóng atlas, tích hợp viewer và kiểm chứng theo Sprite Forge.
---

# Thêm nhân vật GodWar

Áp dụng trong repo GodWar khi anh thêm nguồn nhân vật và yêu cầu “Thêm char mới” hoặc nhập asset nhân vật. Dùng skill `generate2dsprite` cho nguồn frame sẵn có; `art_source=existing`. Đọc AGENTS.md và các quy trình, catalog, viewer, mốc đã chốt hiện tại trước khi sửa.

1. Tìm và xem các file nguồn, kiểm tra trùng tên/hash và các thay đổi đang có. Không ghi đè, xóa hoặc đổi nguồn; không suy ra danh tính hay tên động tác từ tên GIF. Ghi lại nhận xét quan sát được và nội dung chưa rõ.
2. Lấy chiều cao mục tiêu pixel của từng nhân vật từ yêu cầu hoặc thông tin đã xác nhận. Nếu thiếu, hỏi anh kích thước từng nhân vật còn thiếu; chờ câu trả lời trước khi build hoặc đặt tỷ lệ cho nhân vật đó, trong lúc đó tiếp tục các phần độc lập. Không tự chọn chiều cao.
3. Xem nhiều frame và màu nền thực tế; tách nền phù hợp từng nguồn, giữ hiệu ứng/chi tiết và cả canvas, ghi thuật toán và nguồn để tái tạo. Không tự nhận tách sạch tuyệt đối; xem alpha trên nền sáng/tối. Giữ số frame và thời lượng nguồn, không tự đặt tên skill hay phân loại clip.
   - Khi nền có nhiều màu, logo hoặc hạt xanh quanh nhân vật, áp dụng quy trình hai đợt và cách đối chiếu trong [tách nền cảnh phức tạp](references/background-cleanup.md); điều chỉnh theo từng nguồn thay vì áp nguyên ngưỡng cho mọi GIF.
   - Với nền nhiều màu hoặc có chữ/logo: tạo mẫu nền độc lập và mặt nạ chữ theo vị trí, màu và sự ổn định qua thời gian; so từng frame với nguồn. Đặc biệt kiểm tra hạt nền nhỏ quanh thân, vùng nền trùng màu nhân vật, các mảng nền nằm trong thân và vùng hiệu ứng chồng chữ. Không chỉ dựa vào ngưỡng màu, median hoặc so hash/pixel để tuyên bố sạch.
   - Tạo bảng xem toàn bộ frame trên nền sáng và tối, phóng lớn các vùng rủi ro và xem hoạt ảnh trong viewer; ghi frame còn lỗi, phần có nguy cơ bị xóa nhầm và kết quả kiểm tra. Nếu còn chữ/nền hoặc chưa xác định được pixel là nền hay VFX, tiếp tục xử lý theo từng nguồn; giữ bản gốc, giữ các phiên bản thử và đánh dấu chưa duyệt, không báo đã tách sạch.
4. Chọn một frame tham chiếu, ước lượng thân (không mặc định lấy toàn bộ VFX), giữ một neo và một hệ số cho cả chuỗi. Lưu tọa độ, chiều cao tham chiếu, chiều cao anh yêu cầu, hệ số, hash nguồn và giới hạn của phép đo. Khi không phân biệt an toàn được thân với VFX, đánh dấu ước lượng cần duyệt hoặc hỏi anh thay vì khẳng định độ chính xác.
5. Đóng atlas Godot tương thích pipeline hiện tại và tạo clip Sprite Forge từ các frame với `reference_unclassified`, `art_source=existing`, thời lượng nguồn. Xem filmstrip và các frame đại diện; ghi nguyên từng WARN/FAIL, giá trị và ngưỡng của QA. Lưu đầu vào và script tái tạo.
6. Tích hợp catalog, roster, chiều cao, inventory, trạng thái kiểm duyệt, viewer và scene thử theo thiết kế đang có. Nhân vật mới là bản chờ duyệt; không sửa hay thay mốc hoạt ảnh đã chốt, không gọi bản mới là đã chốt khi anh chưa yêu cầu. Xác nhận Godot có thể nạp atlas nếu môi trường hỗ trợ.
7. Đối chiếu hash, số lượng, pixel, vùng atlas, thời lượng từng frame và tỷ lệ; chạy kiểm thử viewer/tích hợp thích hợp. Ghi nhật ký dự án và báo rõ nguồn, kết quả, QA WARN/FAIL, những gì chưa duyệt, kiểm thử và giới hạn thiết bị. Không khẳng định đạt chất lượng phát hành hoặc tối ưu mobile nếu chưa đo.
