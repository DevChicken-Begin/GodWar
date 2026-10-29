# Theo dõi chiều cao nhân vật

**Trạng thái mới nhất:** sau đợt 3 đã thêm 11 mục mới và thay nguồn Scorpit, tổng 154 mục tiêu. Chi tiết 12 GIF mới tại `docs/animation-asset-todo.md` và `docs/charnew-qa.md`; mục “Cập nhật kích thước đợt 3” bên dưới ghi lịch sử 143 mục trước đó.

Ảnh tham chiếu `image copy 2.png` là ảnh chụp 884×520 có cả map và nhân vật. Mục tiêu của anh là kích thước hiển thị trong viewport ngang 1920×1080, không thay đổi độ phân giải của atlas. Danh sách 143 nguồn và chiều cao được ghi trong `Asset/Character/characters/height-targets.json`; mọi id đều có trong catalog chính hoặc catalog tách 3 nhân vật. Hash ảnh tham chiếu và từng GIF được ghi trong cùng file, đã đối chiếu 143 mục với GIF nguồn.

Chiều cao phải đo theo thân ở một frame tham chiếu đã xem, không lấy mặc định theo kích thước canvas hay bbox alpha của cả VFX. Nhiều frame đầu chứa vũ khí, lửa, ánh sáng, vật thể rời hoặc hình nền; các giới hạn thân, neo và frame tham chiếu cần được ghi trước khi áp tỷ lệ cố định cho toàn bộ frame. Bảy nguồn `agon`, `amore`, `crapit`, `airpot`, `black`, `bearen`, `blackdog` đã có atlas thử; 136 mục chưa được đo và đóng gói. `amore` đã được áp mốc thử 80 px trong scene hiện tại; frame 0 có bbox alpha 84×94 px và mốc này vẫn cần anh duyệt là đo theo thân như mong muốn.

## Crapit

Đã xem bảng đủ 24 frame: hai hình nằm hai bên, dải x=172–251 trong suốt trên toàn bộ frame. `tools/split_crapit_scale_pilot.py` tạo `Asset/Character/scale_pilots/crapit_v1/`, cắt hai phần không resize, giữ pixel và thời lượng, kèm hash nguồn, thông số và tỉ lệ thử. Frame 0: phần chính bbox alpha cao 176 px, hệ số thử 100/176; phần phụ bbox cao 84 px, hệ số thử 40/84. Bbox alpha có thể gồm hiệu ứng, chưa khẳng định là chiều cao thân; hai hệ số chưa được tích hợp vào scene hoặc duyệt trên thiết bị.

Đã so pixel của cả hai phần với atlas đầu vào trên cả 24 frame và đối chiếu thời lượng: đạt. Chưa phân loại động tác, kiểm tra chất lượng toàn bộ frame ở game size, kiểm tra Godot hoặc APK. Không thay atlas hay GIF gốc.

## Atlas thử có tỷ lệ

`tools/build_measured_atlas_pilots.py` và `tools/build_agon_measured_atlas.py` đã đóng gói atlas riêng cho `agon` (50 frame), `amore` (46 frame), `crapit_main` và `crapit_secondary` (24 frame mỗi bộ) tại `Asset/Character/measured_atlas_pilots/`. Không resize/cắt frame khi đóng gói; sau khi ghi đã đối chiếu RGBA của 144 frame với đầu vào. Metadata lưu hash, thời lượng, canvas, neo và hệ số hiển thị. `crapit` dùng hai phần đã tách theo dải trong suốt nêu trên. `agon` frame 0 đã xem, bbox (125,145)–(295,365), cao 220 px và hệ số thử 90/220.

`GifAtlasLibrary.create_measured_pilot` nạp atlas, timing, neo và hệ số; Godot 4.3 headless trong project tạm đã nạp bốn bộ, kiểm tra texture, 144 thời lượng và phép tính chiều cao 90/80/100/40. Scene Godot thử Amore dùng atlas mới. Mốc `crapit` dựa bbox alpha frame 0 có thể chứa hiệu ứng, anchor là mốc thử; chưa xác nhận bằng mắt khi phát hoặc trên APK. 140 nhân vật khác vẫn chưa được đo và đóng gói.

Viewer hiện nạp `measured_atlas_pilots`: mặc định chọn atlas đã đo cho `agon`, `amore`, và cây chính của `crapit`; mục Phiên bản cho phép chọn thêm quả phụ. Dòng thông tin ghi riêng kích thước canvas gốc và chiều cao tham chiếu đã áp; các nhân vật chưa đo chỉ ghi chiều cao mục tiêu và “chưa áp dụng”. Ở mức phóng 1×, viewer áp hệ số lên toàn canvas, không cắt VFX. `npm test` 6/6, gồm chuyển hai phần `crapit` và xem `agon` 90 px; bốn metadata/atlas trả HTTP 200. Chưa xác minh trực tiếp bằng browser trên thiết bị.

`tools/build_height_batch_review1.py` thêm `airpot` 75 px (67 frame), `black` 70 px (27), `bearen` 90 px (29), `blackdog` 65 px (57). Frame 0 đã xem trên bảng mẫu; số đo dùng vùng alpha và neo ước lượng, cần anh duyệt vì có thể gồm VFX hoặc vật thể. Bộ đóng gói kiểm tra pixel toàn bộ 180 frame; Godot 4.3 headless đã kiểm tra texture, nhịp và tính tỷ lệ. Scene `/amore-scene.html` nạp atlas đã đo và cho chọn từng bộ; sáu hình cùng lúc vẫn là bản sao của một nhân vật, chưa phải chọn sáu nhân vật khác nhau hay collision toàn map.

## Bản thử phủ toàn bộ danh sách

`tools/build_height_bulk_preview.py` đã tạo **136 bản tự động** cho các nguồn còn thiếu; kết hợp bảy nguồn đã có, toàn bộ 143 mục trong danh sách có bản thử, riêng crapit có hai atlas. Với bản tự động, chiều cao tham chiếu lấy từ bbox alpha của frame đầu, neo là giữa đáy bbox; đây **không phải đo thân đã kiểm duyệt**. Vũ khí, VFX, nền hoặc các hình thể khác trong bbox có thể làm kích thước thân thật sai. Viewer và scene ghi rõ “ước lượng alpha, cần duyệt thân”; metadata từng bản ghi vùng đo, nguồn, hash, frame và cảnh báo. `skyles` có bbox chạm mép, `hades` có bbox chiếm hơn 80% canvas và cần kiểm tra kỹ.

Khi có `detail_oct29_candidates`, bản thử đóng gói nguyên các frame chi tiết đó; các nguồn còn lại sao chép hoặc đóng gói atlas tách nền hiện có. Không thay nguồn hay giảm độ phân giải đầu vào. `tools/verify_height_bulk_preview.py` đã kiểm tra 136 bản, **7.848 frame**, hash đầu vào, pixel được đóng gói, số frame và thời lượng; đạt. Bộ `moxie_repaired` riêng giữ canvas đã mở rộng và phần vật thể phục dựng từ bản trước; `moxie` cũng có lựa chọn theo GIF gốc. `conden` giữ mặc định timeline đang xem trước đó và bản tỷ lệ tự động được chọn trong Phiên bản.

Scene `/amore-scene.html` cho chọn từng bản và thay atlas khi đang xem; 6 hình vẫn là 6 bản sao của một lựa chọn. Scene chỉ thử nền và bệ giữa, chưa có đặt 6 nhân vật khác nhau, collision map đầy đủ, đo FPS hay APK thật. `npm test` 6/6. Các bản alpha tự động chưa nên coi là 136 nhân vật đạt chính xác chiều cao thân trước khi được duyệt.

## Chốt mục tiêu và cập nhật 37 nhân vật

Theo danh sách thay thế của anh, đã cập nhật đủ 37 mục tiêu; `comgha` được anh xác nhận là `congpha`, đặt 80 px. 106 mục còn lại được ghi `user_approved_unchanged`, không yêu cầu duyệt lại. Các trạng thái này phản ánh quyết định về **mục tiêu kích thước**, không phải bằng chứng rằng mặt nạ thân hay chất lượng atlas đã đúng.

Metadata của từng atlas được đổi `target_height_px` và `display_scale` theo giá trị mới, không thay pixel hoặc cắt frame. Đã chỉnh 29 mốc tham chiếu của 37 mục: 26 mốc dùng thành phần alpha liên thông đã xem ảnh mẫu để tránh hạt rời; `aminao`, `changlie`, `costmic` dùng khung thân ước lượng bằng mắt để tránh hiệu ứng/vũ khí lớn. Tọa độ cũ và phương pháp được lưu trong ba file lịch sử `height-update-20261029.json`, `height-component-refinement-20261029.json`, `height-manual-refinement-20261029.json` tại `Asset/Character/characters/`. Số đo theo ảnh vẫn là ước lượng: hiệu ứng dính liền, chi tiết rời hoặc phần hình nền trong atlas có thể làm chiều cao thân thực tế sai; ví dụ `shellhost` vẫn chứa hình hộp ở đầu vào.

Hai màn hình đọc cùng `display_scale` từ metadata: chọn **phóng 1×** trong viewer và **zoom cảnh 70%** để đối chiếu cùng đơn vị viewport 1920×1080. “Vừa khung” hay zoom khác thay đổi tỷ lệ trên màn hình; ngay cả khi cùng chiều cao tham chiếu, tư thế, độ rộng, canvas và VFX có thể khác. `conden_tuned` giữ đủ 61 frame và thời lượng timeline đã có, đồng thời áp mục tiêu 65 px; `moxie_repaired` tiếp tục giữ canvas phục dựng.

Kiểm tra: đối chiếu 37 thay đổi, 106 mục không đổi, 143 profile và các atlas thay thế; test viewer/scene so cùng hệ số `airpot` 80 px; `npm test` 6/6. `tools/verify_height_bulk_preview.py` đối chiếu 136 bộ, 7.848 frame và hash đầu vào: đạt. Godot 4.3 headless nạp `airpot` mới 80 px, `black` mới 65 px và `conden_tuned` 61 frame/65 px, kiểm tra thời lượng và texture trong project tạm. Chưa đo thực tế trên APK hoặc kiểm chứng bằng mắt mọi frame/thiết bị.

## Chốt kích thước đợt 2

Đã thay trực tiếp 24 mục tiêu theo danh sách anh cung cấp; 119 mục còn lại được ghi nhận đã chốt và giữ nguyên chiều cao. Cấu hình hiện hành ở `Asset/Character/characters/height-targets.json`; bằng chứng hash ở `Asset/Character/characters/height-update-round2.json`. Mốc thân, điểm neo, thời lượng, vùng frame và ảnh atlas không thay đổi trong đợt này; chỉ đổi mục tiêu và hệ số hiển thị. Bằng chứng không khẳng định mọi tư thế có cùng chiều cao vì pose, VFX và vùng alpha thay đổi theo frame.

`python tools/verify_height_round2.py` đạt: 24 mục thay thế, 119 mục giữ nguyên, 143 profile; đối chiếu hash timeline của 1.570 frame và 137 file atlas trong nhóm sửa. Kiểm thử hai màn dùng cùng metadata và cùng tỷ lệ với `aminao` 70 px: `npm test` 6/6. Cả 24 profile mới được localhost trả về. Godot 4.3 headless trong project tạm chạy `tools/check_height_round2.gd`, nạp `aminao` 82 frame/70 px và `dragonot` 49 frame/90 px, kiểm tra texture, thời lượng và tỷ lệ. Chưa đo chất lượng hình ảnh, FPS hoặc kích thước vật lý trên APK/điện thoại thật.

Theo phản hồi mới, đã bỏ lựa chọn kích thước cũ, xóa các giá trị chiều cao/hệ số đã thay thế khỏi dữ liệu lịch sử đợt 2 và các mục lịch sử liên quan; giữ hash frame/atlas làm bằng chứng. `height-targets.json` là nguồn chiều cao hiện hành duy nhất: viewer, scene và `GifAtlasLibrary.create_measured_pilot` tính hệ số từ mục tiêu này và chiều cao tham chiếu trong metadata atlas. Với 24 nhân vật đã sửa, viewer chỉ hiện atlas kích thước hiện hành và atlas nguồn để tham chiếu, không chọn các phiên bản kích thước cũ. Hai màn hình có nút **Cập nhật kích thước**, hiện thông báo thành công/lỗi riêng; khi chọn nhân vật hoặc tab nhận focus cũng tải lại cấu hình.

`npm test` 7/7 gồm thử trường hợp metadata atlas có số cũ nhưng cấu hình hiện hành có số mới, cập nhật khi trang mở và xác nhận nút phản hồi; `python tools/verify_height_round2.py` đối chiếu 143 profile, 1.570 frame và 137 atlas: đạt. Godot 4.3 headless trong project tạm vẫn trả `aminao` 70 px khi cố ý đặt giá trị khác trong metadata atlas tạm. Đây là kiểm tra dữ liệu và hành vi mô phỏng; chưa xác định nguyên nhân trên trình duyệt của anh hay đo trực tiếp trên điện thoại.

## Cập nhật kích thước đợt 3

Đã thay trực tiếp 20 mục: Kahn 87, choptian 90, comic 85, congpha 85, corepion 65, costmic 75, dracian 95, dragonight 100, dragonot 100, firemen 70, hades 110, iternal 90, jaik 85, kengkeng 90, kumen 80, kungchang 85, midnight 80, momo 85, nox 87 và omra 80 px. 123 mục còn lại không đổi. `height-targets.json` là nguồn chiều cao hiện hành; các giá trị đã bị thay thế của 20 nhân vật được bỏ khỏi bản lưu lịch sử liên quan, còn hash được giữ làm bằng chứng. Viewer chỉ cho chọn bản hiện hành và nguồn tham chiếu đối với các nhân vật đã chỉnh, không chọn các phiên bản kích thước đã thay thế.

Chỉ đổi metadata chiều cao và hệ số hiển thị, không resize atlas, cắt frame hoặc đổi timing. `python tools/verify_height_round3.py` đạt 20 mục, 123 mục không đổi, 143 profile, hash timeline của 1.271 frame và 164 file atlas không đổi. `python tools/verify_height_round2.py` tiếp tục kiểm tra 24 bằng chứng frame lịch sử và 143 profile hiện hành. `npm test` đạt 7/7; thử viewer và scene vẽ Kahn 87 px và momo 85 px theo mốc tham chiếu, kiểm tra cập nhật dữ liệu khi trang đang mở. Godot 4.3 headless trong project tạm nạp Kahn 111 frame/87 px, dragonot 49 frame/100 px, momo 58 frame/85 px và đối chiếu từng texture cùng thời lượng. HTTP local trả dữ liệu hiện hành.

Kích thước là chiều cao tại mốc tham chiếu đã có, không đảm bảo chiều cao thân ở mọi tư thế; một số mốc vẫn là ước lượng alpha có thể gồm VFX. Chưa kiểm tra trực quan toàn bộ 20 nhân vật trong trình duyệt của anh hay trên APK/thiết bị thật; các kiểm tra này không chứng minh đạt 60 FPS hoặc chất lượng phát hành.
