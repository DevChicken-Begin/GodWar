# Theo dõi làm mịn pixel hàng loạt

Các bản là **bản thử chưa duyệt**, không thay thế GIF hay các bản xử lý trước. Các source vốn chưa được phân loại có thể chứa cả nhân vật, hiệu ứng hoặc nền.

- Đã tạo: 93 nguồn, 5035 frame; lưới pixel được kiểm tra trên mọi frame trước khi tạo.
- Không xử lý lại theo yêu cầu: agon, airpot, amore, aoda.
- Chưa tạo bản thử vì lưới không đồng nhất hoặc không tìm thấy lưới nguyên (cần phương án riêng): aminao, animent, aonoma, artemis, aument, auranient, authen, bearen, biden, black, blackdog, botem, corepion, dracian, dragonight, dragonmout, fireknight, jaik, knigblack, lois, mainthen, maono, midnight, mortafi, moxie, nox, overight, powerdame, samurai, scorpit, skyles, skypit, snowpie, tigerknight, vemou, wuchen.
- Mọi bản dùng bảng RGBA của phiên bản đầu vào, không tự tạo thêm màu; phép nội suy có thể thay đổi hình dạng biên hoặc VFX và không khôi phục chi tiết bị mất. Tỷ lệ hiển thị lại có thể không nguyên.
- Dữ liệu đầu vào có thể vốn là bản tách nền chưa duyệt: các lỗi nền, chữ hoặc mất chi tiết cũ vẫn có thể tồn tại. Chưa kiểm tra toàn bộ khi phát hoặc trên thiết bị.
- `python tools/verify_fine_batch.py` đã kiểm tra 93 bản / 5.035 frame về hash, timing, lưới, palette, phép Scale2x và atlas. Godot 4.3 nạp được bốn mẫu `anomen`, `azou`, `changlie`, `solist` trong dự án tạm; không phải kiểm thử mọi atlas hay hiệu năng mobile.

Chi tiết từng nguồn: `audit.json`, `build.json` và `verification.json`. Ảnh so mẫu: `sample-comparisons.png`.
