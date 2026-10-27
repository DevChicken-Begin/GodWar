# Bộ GIF nhân vật và VFX

Nguồn nằm trong `Asset/Character/vfx/`. Script `tools/extract_gif_assets.py` giải mã từng GIF thành các trang PNG RGBA tối đa 2048 × 2048, giữ nguyên khung hình, vị trí trên canvas, thứ tự và thời gian mỗi frame. `Asset/Character/extracted/catalog.json` ghi nguồn, SHA-256, vùng trên atlas và thời gian; tên thư mục tương ứng tên GIF. Mở `Asset/Character/extracted/index.html` để xem nhanh GIF gốc. Chạy lại bằng `python3 tools/extract_gif_assets.py` (cần Pillow).

Các atlas giữ cả nền, nhân vật và VFX đúng như GIF: nhiều file có nền màu hoặc nền cảnh, một số file có nhiều nhân vật; không thể mặc định chúng là sprite trong suốt hay tách riêng VFX. Tệp `3 char.gif` chẳng hạn chứa nhiều nhân vật. `sword.mp4` không phải GIF nên không được xử lý. Quyền sử dụng nguồn chưa được xác minh.

## Dùng trong Godot 4

Sau khi Godot import PNG, có thể dùng `GifAtlasLibrary.create_sprite_frames("amore")` để nhận `SpriteFrames`, gán cho `AnimatedSprite2D.sprite_frames`, rồi `play("source")`. Animation `source` phát nguyên GIF; lật trái/phải bằng `AnimatedSprite2D.flip_h` khi phù hợp. Thời gian frame được giữ; GIF có khai báo loop sẽ phát lặp, GIF không khai báo loop phát một lần. Godot không mô phỏng số lần lặp hữu hạn trong GIF. Frame có thời gian 0 được dùng thời gian dương tối thiểu để Godot phát được.

## Phân loại để đưa vào auto chess

Theo xác nhận của anh, tên GIF dùng làm tên nhân vật; vẫn cần kiểm tra ngoại lệ khi một file chứa nhiều nhân vật hoặc chỉ có VFX, và không mặc định toàn bộ GIF là một động tác. Trường `classification` là `unreviewed` và `animations` để trống có chủ ý. Cần xem từng frame và xác nhận danh tính, đoạn frame và hiệu ứng trước khi lập hồ sơ từng nhân vật. Danh sách mục tiêu:

- `idle`, `move`, `hit`, `death`, `attack`, `skill`;
- `jump_up`, `jump_down`, `fly` chỉ khi ảnh gốc thể hiện phù hợp với nhân vật;
- phạm vi đòn thường và skill (`melee` hoặc `ranged`), vị trí phát/va chạm và frame gây hiệu ứng;
- điểm neo, hướng mặc định, khả năng lật trái/phải, trạng thái lặp và thời lượng.

Mỗi nhân vật có tối đa một skill. Anh đã cho phép thiết kế skill mới theo phong cách chung khi nguồn chưa có; skill mới phải được ghi rõ là tạo bổ sung và kiểm tra, không suy đoán skill thứ hai. Điều khiển bay/nhảy và di chuyển trên map là logic gameplay tự động, tách khỏi việc giải mã hình. Những động tác không có trong nguồn cần đánh dấu thiếu hoặc dùng phương án dự phòng được duyệt, không tự nhận là đã có. Muốn có sprite nền trong suốt hoặc VFX riêng cần xử lý và kiểm tra thủ công theo từng GIF vì xóa nền tự động có thể xóa nhầm pixel hoặc không xử lý được nền cảnh.

## Lưu ý cho mobile

Godot 4 là engine miễn phí đang được cấu hình trong dự án; preset Android đã đưa catalog JSON vào bản export. Atlas này là bản bảo toàn nguồn, chưa phải asset tối ưu để phát hành: cần tách nền/VFX, cắt canvas, phân loại đúng động tác và đo bộ nhớ texture, dung lượng APK cùng hiệu năng trên điện thoại trước khi đưa vào trận đấu. Chỉ tải những nhân vật cần dùng và giải phóng khi không còn dùng. Chưa có game auto chess hay logic chiến đấu trong bộ xử lý này.

## Ba nhân vật trong `3 char.gif`

Anh đã đặt tên theo thứ tự [solist](../Asset/Character/characters/solist/character.json), [namero](../Asset/Character/characters/namero/character.json) và [kukaomni](../Asset/Character/characters/kukaomni/character.json): tương ứng frame nguồn 0–51, 52–101 và 102–155. Mỗi nhân vật có atlas và catalog riêng; chưa phân loại động tác hoặc skill. Trong Godot, ví dụ nạp `namero` ở dạng bản thử tách nền:

```gdscript
var frames = GifAtlasLibrary.create_sprite_frames("namero", 0, -1, "res://Asset/Character/refined_candidates")
```

Các atlas `refined_candidates` và `cleanup_candidates` chưa duyệt: phép tách theo màu có thể xóa chi tiết cùng hoặc gần màu nền; phép trừ nền theo thời gian có thể xóa chi tiết tối hoặc ít thay đổi. Phải đối chiếu từng frame trước khi đưa vào game.
