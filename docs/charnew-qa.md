# QA 12 GIF mới — bản thử chưa duyệt

Nguồn: `13 charnew/*.gif`, art_source `existing`. Kết quả Forge nằm tại `Asset/Character/forge_pilots/charnew/<id>/clips/animation-clips.json`; mỗi gói có một clip `reference_unclassified`, không khẳng định đó là một động tác hay skill. Các ô dưới là kết quả `qa.checks` của từng file; không có ngưỡng cho `tick_grid` hoặc `loop_seam`. Forge kiểm tra byte copy PNG và timeline WebP, nhưng không thay thế duyệt chuyển động và alpha bằng mắt.

| Nguồn | tick_grid WARN (ms) | near_duplicate_holds WARN (ngưỡng 0) | loop_seam cần duyệt (tỷ lệ) |
|---|---:|---:|---:|
| buffao | 6.667 | — | 1.253544 |
| scosrian | 6.667 | — | 0.595329 |
| dump | — | — | 2.023753 |
| hemsiss | — | 8 | 1.341468 |
| scorpit | 6.667 | — | 0.749647 |
| Domrico | 6.667 | 1 | 2.450969 |
| hecfaom | — | — | 1.101419 |
| Impector | 6.667 | — | 0.338704 |
| Actem | 6.667 | — | 0.861582 |
| Hatomin | 6.667 | — | 0.933595 |
| Trainxoan | 6.667 | — | 1.536363 |
| urguro | 6.667 | — | 0.758020 |

Dấu — nghĩa là kiểm tra đó không WARN; không có nghĩa chuyển động đã được duyệt. `tick_grid` là sai lệch lưới thời gian, không tự chứng minh khựng. `near_duplicate_holds` đánh dấu tư thế gần giống, có thể là giữ chủ ý. Phần nối vòng chỉ là bản xem thử, cần so nguồn trước khi kết luận phải sửa.

Tất cả 12 clip đã được build, song còn cần duyệt nền và chiều cao thân theo frame tham chiếu, cũng như phát 1×/0,5× trên trình duyệt của anh và đo thiết bị. Phân loại clip, animation mới, APK và 60 FPS chưa được xác nhận. Một số frame có phần alpha chạm mép canvas nguồn (buffao 13, scosrian 2, dump 9, hemsiss 5, scorpit 4, Domrico 1, hecfaom 5, Impector 10, urguro 1); đây không phải bằng chứng có thể khôi phục phần hình nằm ngoài GIF.

Ngày 2026-10-29, theo phản hồi: Actem đổi mục tiêu 80 → 85 px theo mốc alpha frame 0 chưa duyệt; atlas được nội suy Lanczos premultiplied 120% và làm nét nhẹ như Hatomin, giữ 66 frame và thời lượng. Nội suy không phục hồi chi tiết không có trong nguồn. Fireknight trong `measured_atlas_pilots` được đóng gói lại từ `fire_deep_candidates`, giữ 91 frame và thời lượng; đây là bản lọc sâu đã có, không chứng minh đã sạch mọi chấm hoặc giữ đủ hạt VFX. Bản atlas trước được lưu tại `Asset/Character/archive/revision_oct29`; quy trình tạo được ghi trong `tools/revise_actem_fire_oct29.py`; script từ chối chạy lại khi bản lưu đã tồn tại, không thay GIF nguồn. Đã kiểm tra hash nguồn, vùng atlas, số frame và thời lượng; cần duyệt trực quan hoạt ảnh và đo thiết bị.

Sau phản hồi làm rõ, Hemsiss bị viền nền tương tự Buffao; không yêu cầu xóa khối đỏ tím. Đã xử lý atlas hiển thị của Buffao (68 frame) và Hemsiss (49 frame) theo tám màu trong `image copy 4.png`, sai lệch tối đa 6 trên mỗi kênh, chỉ xóa các cụm màu tiếp giáp trong suốt. Đã xóa bóng đen RGB (0,0,0) từ hàng 162 trở xuống trên cả hai atlas Moxie (97 frame mỗi bản), giữ phần vật thể phục dựng. Bản trước ở `Asset/Character/archive/cleanup_buffao_moxie_oct29` và `Asset/Character/archive/blue_fringe_oct29`; script là `tools/clean_buffao_moxie_oct29.py` và `tools/clean_blue_fringe_oct29.py`, từ chối chạy đè khi archive đã tồn tại.

`python tools/verify_cleanup_oct29.py` kiểm tra 311 frame: hash nguồn và atlas đầu vào, timeline, pixel bị xóa theo mặt nạ và pixel giữ nguyên đều đạt; `npm test` đạt 7/7. Đã xem bảng thu nhỏ mọi frame Buffao/Hemsiss và 12 frame đối chiếu trước/sau Moxie tại `Asset/Character/review/cleanup-oct29`. Tách theo màu có thể xóa nhầm chi tiết xanh cùng màu hoặc còn sót màu khác; điểm tiếp xúc bóng/chân có thể bị ảnh hưởng. Chưa duyệt phát liên tục trên nhiều nền hay kiểm tra thiết bị; không khẳng định sạch tuyệt đối.

Ngày 2026-10-29: theo yêu cầu đã xóa Hemsiss khỏi repo, gồm GIF nguồn mang tên Hemsiss, atlas, bản lưu xử lý, gói Forge, ảnh review và các catalog. Các số liệu Hemsiss ở trên là lịch sử trước khi xóa; không còn là asset hiện hành. Ảnh phản hồi do người dùng cung cấp được giữ lại.
