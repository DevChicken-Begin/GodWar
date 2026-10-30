# Tách nền cảnh nhiều màu và logo

Dùng quy trình này khi GIF có nền cảnh, chữ hoặc hạt còn sót quanh nhân vật. Chọn phương pháp theo nguồn; màu nhân vật và VFX có thể giống nền. Giữ GIF gốc, lưu bản atlas trước mỗi lần sửa, hash nguồn/mẫu, tham số, frame tham chiếu và script để đối chiếu hoặc tái tạo.

## Đợt đầu: mẫu màu và logo

1. Xem nhiều frame gốc; xác định vùng chữ, nền, thân, VFX và các đoạn nền lộ ra. Nếu người dùng cung cấp mẫu pixel nền, trích màu thực tế từ mẫu, không coi toàn ảnh mẫu là nền; so với màu của nhân vật và hiệu ứng.
2. Tạo bản thử dựa trên mẫu màu và mặt nạ logo theo vị trí, màu và độ ổn định theo thời gian. Dùng ngưỡng bảo thủ và ghi lại ngưỡng; không áp dụng một màu duy nhất cho cả cảnh nhiều màu. Lưu bản trước sửa và thống kê pixel đổi alpha theo frame.
3. Xem toàn bộ frame trên nền sáng và tối; phóng lớn quanh đầu, chân, trong thân, hiệu ứng rời và chữ. Kiểm tra cả frame người dùng chỉ ra lẫn frame lân cận, phân biệt số frame hiển thị 1-based với chỉ số dữ liệu 0-based. Nếu còn nền hoặc logo, tiếp tục đợt hai.

## Đợt hai: mẫu cảnh và footprint logo

1. Tìm các frame gốc mà cảnh lộ ra nhiều, nhân vật và VFX ít che khuất; có thể kết hợp nhiều nguồn cùng cảnh, cùng kích thước và căn chỉnh. So trực quan các mẫu trước khi dùng, ghi nguồn, hash và chỉ số frame. Trung vị theo pixel của các mẫu là ước lượng, không phải nền thật: VFX còn trong mẫu và vùng che khuất có thể làm sai kết quả.
2. So từng frame gốc với mẫu cảnh tại cùng tọa độ; thử ngưỡng chênh lệch RGB và kiểm tra vùng thay đổi trước khi xuất. Bảo vệ vùng có VFX tương tự nền; dùng cách xử lý riêng khi không phân biệt được. So với bản trước trên cả hai nền, đặc biệt ở những frame nhân vật biến mất hoặc hiệu ứng lan rộng.
3. Nếu chữ mờ vẫn còn, tạo footprint logo từ mẫu cảnh hoặc logo chung, xác định vùng chứa chữ và nới biên vừa đủ để bắt viền còn sót. Mặt nạ cố định có thể xóa VFX đi ngang logo: kiểm tra các frame chồng lấp, điều chỉnh theo frame hoặc giữ lại vùng chưa phân biệt được. Không mặc định xóa toàn bộ vùng chữ nếu có nguy cơ mất hiệu ứng.
4. Giữ ảnh so trước/sau, phiên bản trước và kết quả hiện hành. Kiểm tra số frame, thời lượng, canvas, nguồn và các pixel còn giữ; kiểm tra này không chứng minh các pixel đã xóa là nền. Xem hoạt ảnh trong viewer trên nền sáng/tối và ghi rõ frame còn nghi ngờ, phần có thể mất và mức duyệt của người dùng. Sau sửa atlas, đồng bộ hoặc đánh dấu clip/export cũ chưa phản ánh bản mới; chạy lại QA liên quan.

## Trường hợp GodWar ngày 30/10/2026

Anh đã xác nhận bản viewer sau đợt hai trông sạch. Tham khảo [báo cáo dự án](../../../../docs/six-gifs-20261030.md) và các script từ gốc repo: `tools/clean_five_logo_blue_20261030.py` (mẫu `pixel_simple.png` và mặt nạ chữ), `tools/clean_five_scene_20261030_v2.py` (mẫu trung vị Moregorn chỉ số 37–40; ngưỡng RGB tối đa 16), `tools/clean_five_logo_mask_20261030.py` (footprint logo chung, nới biên 4 pixel). Các script này gắn với nguồn, kích thước, vùng và trạng thái atlas của lô đó; không chạy nguyên xi cho lô mới hoặc ghi đè bản đã duyệt. Ngưỡng và vùng phải được đo lại. Việc anh duyệt trực quan không chứng minh riêng việc bảo toàn mọi VFX hay hiệu năng thiết bị; xem các giới hạn và kiểm thử trong báo cáo.
