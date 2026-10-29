# Kế hoạch chuyển GIF tham chiếu thành asset animation

GIF là nguồn tham chiếu. Danh tính, hướng, điểm neo và ranh giới từng động tác cần được kiểm duyệt trước khi đặt tên hay dùng làm skill.

- [x] Ghi yêu cầu, chia bước và giữ nguồn cùng các bản thử cũ.
- [ ] Kiểm kê từng GIF: hash, kích thước, số frame, nhịp, alpha, nội dung và các đoạn cần xác nhận; lập danh sách động tác thực sự quan sát được.
- [ ] Chọn từng nhân vật để duyệt: tách frame, nền, điểm neo chung, kiểm tra từng frame và phân đoạn; ghi nguồn, quyết định và lỗi còn lại. Không tự đặt tên skill hay tạo động tác chưa có trong GIF.
- [ ] Tạo bộ clip theo `generate2dsprite`, giữ thời lượng gốc 1×; xuất SpriteFrames Godot 4, kiểm tra import, neo, nhịp, trạng thái và chuyển tiếp. Tạo hoạt ảnh mới theo master được duyệt khi đã xác định yêu cầu.
- [ ] Đổi trình kiểm thử để đọc cùng bộ asset và timeline dùng trong Godot; có chế độ so GIF tham chiếu, 1× và 0,5×, giữ kích thước hiển thị đo được.
- [ ] Đo thời gian tải/giải mã, bộ nhớ, độ trễ render và số lần bỏ frame ở 1×/0,5×. So với thời lượng và các tư thế nguồn trước khi kết luận nguyên nhân giật. 60 FPS là tần số hiển thị; GIF có thể chứa ít tư thế hơn và giữ một frame nhiều nhịp.
- [ ] Sửa nguyên nhân đã đo, đánh giá tốc độ và sự liền mạch ở 1× và 0,5×; nếu cần thêm frame trung gian thì ghi rõ chúng được tạo mới và kiểm tra biến dạng.
- [ ] Điều tra kích thước thực tế của momo, độ mịn/nét và so ảnh ở cùng kích thước hiển thị; chỉ đưa ra cách sửa sau khi có phép đo và hình đối chiếu.
- [ ] Tạo bản thử Godot/APK, kiểm thử xuyên suốt, animation và hiệu năng trên Android thật; lưu thiết bị, thời gian, FPS, frame time, kết quả và lỗi. Chưa tuyên bố đạt APK hoặc 60 FPS trước khi đo.
- [ ] Gửi từng bộ và bản kiểm thử để anh xem, ghi phản hồi, sửa và duyệt trước khi mở rộng.

## Bước nhỏ đầu tiên

Thử đóng gói `dragonot` từ bản đã lọc hạt vào một clip tham chiếu nguyên vẹn. Tên clip không xác nhận đây là một hành động duy nhất; điểm neo tạm thời và phân đoạn còn chờ duyệt. Kiểm tra bằng Forge và Godot nếu công cụ có sẵn; ghi riêng cảnh báo, kết quả và điều chưa kiểm chứng.

- Đã tạo `Asset/Character/forge_pilots/dragonot_reference_v1/`: đầu vào `revision_candidates/dragonot`, nguồn GIF và hash ghi trong metadata của bản đầu vào; 49 frame × 70 ms = 3.430 ms. Neo tạm [192,192] là tâm canvas, chưa được chọn theo chân nhân vật. Clip `reference_unclassified` chạy lặp chỉ để đối chiếu; chưa phân loại hay xác nhận các đoạn động tác.
- `build_animation_clips.py --no-reviews` báo **WARN** `tick_grid`: 6,667 ms, threshold null, trong `clips/animation-clips.json`; `loop_seam` cần duyệt trực quan, giá trị 0,689473, threshold null. Các frame copy và timeline WebP được Forge đối chiếu; cảnh báo không chứng minh nguyên nhân bị giật.
- `export_engine.py --target godot-spriteframes --max-atlas-size 4096` báo PASS, một atlas tối đa 2.330 px. Godot 4.3 headless đã import trong dự án tạm, nạp `.tscn`, kiểm tra 49 frame, từng frame 70 ms, tổng 3,43 giây và loop. Chưa kiểm tra hình khi phát trong editor, chưa đo 60 FPS hoặc kiểm tra APK và thiết bị.
- Bản mẫu này là một bước đóng gói để kiểm tra, chưa là bộ chuyển động hoàn chỉnh; còn phải duyệt tách nền, mốc neo và ranh giới từng động tác trước khi mở rộng.

Giả thuyết GIF nặng làm khựng là cần đo; hiện chưa có bằng chứng loại trừ nguyên nhân do tải ảnh, render, thời lượng hoặc khoảng cách giữa các tư thế.

## Điều tra viewer theo phản hồi 1×

- Bản `detail_oct29_candidates` đọc từng PNG riêng; sau mỗi lần vẽ viewer giữ ảnh hiện tại và tải trước tối đa bốn ảnh tiếp. Khi decode hoàn tất sau lúc timeline đã chuyển, kết quả vẽ cũ bị bỏ. Đây là cơ chế có thể gây khựng, chưa phải phép đo trên máy của anh.
- Kích thước giải mã RGBA ước tính cho mỗi frame: `momo` 948×948 ≈ 3,43 MiB, `nox` 1095×1095 ≈ 4,57 MiB, `aonime` 1014×1014 ≈ 3,92 MiB. Không tính overhead trình duyệt. Bộ `dragonot` Godot dùng một atlas 2330×2330 ≈ 20,71 MiB giải mã, 1,51 MiB PNG. Đây là so sánh cấu trúc/tải trọng, chưa là đo FPS hay thời gian giải mã.
- Viewer có lựa chọn `Godot · atlas tham chiếu thử` cho `dragonot`. `preview.json` mô tả đúng các ô trong `.tres`; đã so pixel RGBA đủ 49 ô với đầu vào. Có thể tái tạo metadata bằng `tools/build_dragonot_godot_preview.py` khi chưa có file output. Các tùy chọn phiên bản khác được giữ để so sánh.
- Viewer hiện hiển thị số nhịp trình duyệt quá 33 ms, frame timeline vượt qua khi cập nhật, lượt vẽ hoàn tất sau khi chọn frame khác và thời gian từ yêu cầu ảnh đến giải mã dài nhất. Các số là chỉ báo của phiên viewer, không tự xác định nguyên nhân và có thể bao gồm thao tác người dùng. Cần so 1×/0,5× trên thiết bị thật, cùng thời gian đo, sau khi tải ổn định.
- Nguyên nhân thấy được của kích thước `momo` trong viewer: `canvas` bị giới hạn bởi khung cao tối đa 500 px; chế độ vừa khung có thể thu cả hai kích thước về cùng mức. Phóng 1× nay hiển thị theo CSS pixel và cho cuộn; vẫn cần xem trên thiết bị của anh. `npm test` 4/4; chưa có browser trong môi trường để đo hoặc quan sát trực tiếp.
- Chưa thêm frame nội suy: chưa có bằng chứng xác định đoạn nào thiếu tư thế, và chưa đánh giá biến dạng. Chưa hoàn thành bóc tách toàn bộ nhân vật, phân loại động tác, kiểm thử APK hoặc mục tiêu 60 FPS trên thiết bị.

## Thứ tự thực hiện sau phản hồi

1. Đo và xử lý tải/giải mã, phát 1× và 0,5× trên viewer dùng asset đã bóc; kiểm tra đại diện rồi mở rộng toàn bộ. Xác định đoạn thiếu tư thế bằng so sánh nguồn trước khi thử tạo frame trung gian; giữ tổng thời gian 1×.
2. Cùng anh xác nhận từng nhân vật, ranh giới động tác và skill có thực trong mẫu; ghi riêng các hoạt ảnh chưa có và cần tạo mới.
3. Sau khi duyệt điểm neo, tách nền và phân đoạn, đóng gói từng bộ Godot gồm clip nguồn đã duyệt và các clip mới đã xác nhận. Đo lại trong Godot và APK trên thiết bị, rồi anh duyệt chất lượng và hiệu năng.

Ảnh anh gửi cho `dragonot` cho thấy thời gian tải/giải mã dài nhất 2.011 ms, 53 frame timeline bị vượt qua và 29 lượt vẽ hoàn tất muộn; anh nhận xét sau đó không còn cảm giác khựng. Các số được tích lũy trong phiên và không cho biết thời điểm mỗi sự kiện, vì vậy chưa đủ chứng minh toàn bộ 53 frame bị vượt qua trong lúc tải đầu.

Viewer đã được sửa để chờ frame đầu được giải mã và vẽ trước khi khởi động đồng hồ timeline khi đổi nhân vật hoặc phiên bản. `npm test` đạt 5/5, gồm kiểm thử giả lập chậm 2 giây và xác nhận timeline chưa tiến trước khi ảnh sẵn sàng. Việc này xử lý thời điểm bắt đầu; chưa chứng minh hết khựng trong những vòng sau khi tải từng PNG và chưa đo trên thiết bị của anh. Cần làm mới trang rồi so các chỉ số sau khi chọn từng phiên bản.

## Thử tỷ lệ nhân vật trên map

Đã tạo scene `Asset/Scenes/amore_scale_test/scene.tscn` và preview `/amore-scene.html`: viewport 1080×1920, map mẫu phóng đều rồi cắt giữa, `amore` ở frame đầu cao khoảng 240 px, neo thử lên mặt bệ. Phát 46 frame theo 70 ms nguồn; di chuyển chỉ giới hạn vị trí trên bệ, chưa có animation đi được phân loại hoặc vật lý map. Godot 4.3 headless nạp scene; `npm test` đạt 6/6, gồm mô phỏng hoạt ảnh và giới hạn di chuyển. Đang chờ anh xem tỷ lệ; chưa xem trên thiết bị thật hoặc đo FPS. Chi tiết nguồn và thông số tại `Asset/Scenes/amore_scale_test/README.md`.

Theo phản hồi, scene thử đã đổi sang viewport ngang 1920×1080. Chiều cao mẫu vẫn là 240 px; map được phóng đều theo chiều rộng và cắt trên/dưới. `npm test` đạt 6/6, Godot 4.3 headless xác nhận viewport, 46 frame, tỷ lệ và vị trí chân trên bệ. Chưa kiểm tra thiết bị hoặc APK.

Sau phản hồi cảnh quá lớn, thêm zoom 50–100%, mặc định 70% và sáu bản sao Amore làm mốc mật độ; ở 70%, chiều cao mẫu là khoảng 168 px trong viewport 1920×1080. Map được hiển thị trọn với vùng xanh cho phần chưa có map; Godot dùng cùng mức 70%. Đây là giả lập bố cục, chưa xác nhận kích thước, FPS hay chất lượng trên APK thật.

Theo phản hồi tiếp theo, giảm chiều cao hiển thị mẫu xuống khoảng 80 px tại zoom mặc định 70%; giữ atlas `fine_candidates/amore/atlas_000.png` và timing nguồn. Zoom cảnh tiếp tục phóng cả map lẫn nhân vật theo cùng hệ số. Kiểm thử Godot 4.3 headless xác nhận chiều cao mẫu 80 px, 46 frame và neo chân trên bệ; chưa đo trên APK.

Nhận thêm chiều cao mục tiêu cho 64 nguồn và ảnh tham chiếu `image copy 2.png`; đã lưu danh sách tại `Asset/Character/characters/height-targets.json`. `amore` có scene mẫu 80 px; `crapit` đã được tách thành hai bộ frame thử, chưa áp tỷ lệ vào scene. 63 mục ngoài Amore còn cần đo thân, chọn neo, áp kích thước và duyệt; chi tiết xem `docs/character-height-review.md`.

Đã nhận bổ sung 79 nhân vật, tổng cộng 143 mục; bao gồm ba mục tách từ GIF `3 char`. Hash 143 nguồn được đối chiếu. Cần đo và áp 142 mục ngoài Amore; cần xây scene chọn tối đa sáu nhân vật, đặt trên hình học mặt đất được kiểm chứng, kiểm tra không cắt khung VFX và giữ nguyên pixel nguồn. Scene mẫu hiện tại chỉ di chuyển Amore trên một bệ; chưa đáp ứng đặt tùy chọn tất cả nhân vật hay collision map đầy đủ.

Cập nhật kích thước đợt 2: 24 mục thay thế và 119 mục còn lại được anh chốt. `tools/verify_height_round2.py` xác nhận 143 profile, 1.570 frame và 137 atlas của nhóm sửa; viewer và scene dùng cùng hệ số, Godot headless kiểm tra mẫu `aminao` và `dragonot`. Đây là chốt mục tiêu kích thước; các bước đo hiệu năng thực tế, scene có sáu nhân vật khác nhau và collision map vẫn chưa hoàn tất.

Cập nhật chiều cao đợt 3: 20 mục thay trực tiếp, 123 mục không đổi; cấu hình hiện hành và bằng chứng tại `Asset/Character/characters/height-targets.json` và `height-update-round3.json`. `python tools/verify_height_round3.py` kiểm tra 143 profile, 1.271 frame và 164 atlas; `npm test` 7/7; Godot 4.3 headless kiểm tra Kahn, dragonot, momo. Cần anh kiểm tra trực quan trên scene; kiểm tra FPS/APK và scene sáu nhân vật khác nhau vẫn chưa hoàn tất.

## Nhập 12 GIF mới

- [x] Kiểm kê 12 nguồn (anh xác nhận số lượng); lưu hash và 770 frame trong `Asset/Character/characters/charnew-import.json`. Nguồn là art có sẵn (`existing`); không tạo ảnh bằng AI.
- [x] Tách và đóng gói atlas nguyên khung; xử lý nền xanh theo màu biên từng frame, riêng Trainxoan loại thêm màu nền gần biên có hạt. Bản tách là ứng viên chưa duyệt vì màu nền có thể gần màu nhân vật/VFX. Bảng đủ frame trên nền sáng/tối ở `Asset/Character/review/charnew_<id>/`.
- [x] Thay nguồn đang dùng của scorpit bằng `vfx/scorpit_charnew.gif`; nguồn cũ `vfx/scorpit.gif` và atlas cũ được lưu trong `archive/scorpit_before_charnew/`. Mục tiêu vẫn 80 px. Đã xem toàn bộ 40 frame trên bảng sáng ở cỡ thu nhỏ, chưa thấy dòng chữ cũ; cần duyệt chi tiết và nền tối.
- [x] Đặt mục tiêu theo danh sách anh đưa. Mốc tỷ lệ dùng bbox alpha frame 0, không phải đo thân đã duyệt; bbox có thể chứa vũ khí, cánh, hiệu ứng. Cần anh kiểm tra thực tế trên scene trước khi coi chiều cao thân là chính xác.
- [x] Hatomin có frame 480×480 tăng lên 576×576 (120% mỗi chiều) bằng Lanczos alpha nhân sẵn và sharpen nhẹ; không thay chiều cao hiển thị mục tiêu 80 px. Nội suy không phục hồi chi tiết nguồn; chưa chứng minh sắc nét hơn hay mượt trên thiết bị.
- [x] `python tools/verify_charnew.py` đối chiếu SHA nguồn, 770 frame gốc, từng pixel sau xử lý, timing và 12 mục tiêu. `npm test` 7/7; Godot 4.3 headless nạp cả 12 bộ, so 770 texture/timing và tỷ lệ tại mốc tham chiếu. Các dữ liệu đang được server local cung cấp.
- [ ] Kiểm tra trực quan từng frame trên nền sáng/tối và xác nhận không mất chi tiết hoặc còn hạt/chữ; duyệt lại bbox thân/neo cho 12 nhân vật. Một số frame nguồn có phần alpha chạm mép, không thể kết luận phần ngoài canvas có tồn tại hay không.
- [ ] Kiểm tra phát 1×/0,5× sau khi tải ổn định; đo frame time, bỏ frame, chi phí giải mã và so chuyển động GIF. Viewer dùng atlas và tải trước trang kế tiếp, nhưng chưa chứng minh hết khựng. Chưa có phép đo APK hoặc 60 FPS trên thiết bị.
- [x] Sprite Forge đã build 12 clip tham chiếu chưa phân loại; các WARN, giá trị và đường dẫn QA được ghi tại `docs/charnew-qa.md`. Cảnh báo nối vòng cần kiểm tra trực quan, không tự kết luận đã sửa mượt.


## Zoom trong Kiểm thử hoạt ảnh

Đã bỏ vùng xem +20%, trả lại toàn bộ frame và kích thước khung ban đầu. Lăn chuột trên vùng hoạt ảnh để phóng to hoặc thu nhỏ; có thể chọn lại 1× hoặc Vừa khung trong danh sách. Zoom chỉ thay đổi cách xem trong viewer.
