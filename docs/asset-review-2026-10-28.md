# Theo dõi các yêu cầu chỉnh asset ngày 2026-10-28

Trạng thái: **đang thực hiện**. Anh đã xác nhận +30% là tăng độ phân giải chi tiết của bản đang xem, giữ kích thước hiển thị. Mỗi bản mới phải lưu riêng, ghi đường về GIF và hash nguồn, giữ các phiên bản trước và chỉ đánh dấu hoàn thành khi đã kiểm tra tương ứng. Frame trong phản hồi của anh có thể là số hiển thị bắt đầu từ 1; khi xử lý phải đối chiếu thêm chỉ số bắt đầu từ 0 và ghi rõ.

## 1. Làm mịn thêm các nhân vật được nêu

Anh yêu cầu tăng thêm 30%. Đây là yêu cầu về mức xử lý, không phải bằng chứng rằng ảnh nguồn có thêm chi tiết. Cần xác định lưới và bản đang dùng của từng nhân vật; không dùng lại một phép chia lưới có thể xóa viền/VFX. Tạo bản thử riêng, ghi lưới/cách nội suy và so với bản đang dùng; kiểm tra thời lượng, số frame, alpha và xem chuyển động. Các ô dưới đây phản ánh trạng thái của **lô Scale2x trước**, chưa phải hoàn thành mức tăng 30% mới.

| Nhân vật | Trạng thái lô trước | Yêu cầu 30% |
|---|---|---|
| artemis | Chưa tạo: lưới mẫu không đồng nhất | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| nox | Chưa tạo: lưới mẫu không đồng nhất | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| overight | Chưa tạo: lưới mẫu không đồng nhất | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| powerdame | Chưa tạo: lưới lệch ở frame khác | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| wuchen | Chưa tạo: lưới mẫu không đồng nhất | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| ziggist | Đã có bản Scale2x chưa duyệt | [ ] Đã tạo bản thử; chờ duyệt chuyển động |
| scorpit | Chưa tạo: lưới mẫu không đồng nhất; có bản sửa chữ | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| skyles | Chưa tạo: lưới lệch ở frame khác | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| snowpie | Chưa tạo: lưới mẫu không đồng nhất | [ ] Đã tạo bản thử; chờ duyệt chuyển động |
| tigerknight | Chưa tạo: lưới mẫu không đồng nhất; còn lỗi nền | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| azza | Đã có bản Scale2x chưa duyệt | [ ] Đã tạo bản thử; chờ duyệt chuyển động |
| dracian | Chưa tạo: lưới mẫu không đồng nhất | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| dragonmout | Chưa tạo trong lô Scale2x; đã có bản thử lọc nét 20% | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |
| mortafi | Chưa tạo: lưới mẫu không đồng nhất | [x] Bản tăng tiếp đã được anh duyệt ở mức tạm ổn |

Chi tiết lô trước: [báo cáo làm mịn](fine-batch/README.md). Lần này cả 14 mục đã có `detail_130_candidates`, nội suy frame trung gian 130% theo mỗi chiều từ bản đang xem, viewer đọc trực tiếp frame trung gian này và giữ kích thước hiển thị như cũ. Đã đóng gói atlas độ phân giải cao riêng trong `detail_130_atlases`; Godot có hàm tải thử và trả tỷ lệ hiển thị. Atlas tương thích cũ được giữ nguyên. `tools/verify_detail130_candidates.py` và `tools/verify_detail130_atlases.py` đối chiếu 669 frame, nhưng không chứng minh tăng chi tiết thật hay chất lượng VFX; vẫn phải duyệt khi phát. Đã rà bảng ảnh thu nhỏ cho toàn bộ 669 frame của 14 nhân vật; [ảnh đối chiếu](../Asset/Character/review/request-20261028/detail130-sheets/) lưu trong repo. Bảng thu nhỏ không đủ xác nhận độ mượt hay mọi pixel sát viền.

## 2. Hoạt ảnh và hiệu ứng

- [ ] **blacktiger:** kiểm tra 26 frame, duration, ranh giới vòng lặp và chuyển động. Thử bổ sung frame chỉ khi có phương án giữ hình dạng/đặc điểm nhân vật; đánh dấu frame tạo mới và so trực quan, không coi tăng số frame tự động là mượt. Đã tạo `motion_v2_candidates/blacktiger` 52 frame (26 frame nguồn + 26 frame nội suy DIS), giữ 2.600 ms. Bản thử đầu chồng hình ở chuyển động nhanh nên bản v2 chỉ biến dạng frame trước; xem mẫu chỉ số 7, 10, 18 cho thấy vẫn có bước chuyển gắt và có thể biến dạng, chưa thể xác nhận mượt.
- [ ] **conden:** xem đoạn anh chỉ ở frame 43–48 và vùng cung; tạo bản thử mũi tên bắn ra theo hướng, tỷ lệ và nhịp quan sát được. Lưu mũi tên/VFX bổ sung riêng, ghi điểm xuất phát, đường bay, frame và nguồn tham chiếu; kiểm tra khi phát, không tự xác nhận là hiệu ứng gốc. Đã thêm 4 frame tổng hợp (48 → 52), dùng hiệu ứng cắt từ chỉ số nguồn 43, kéo dài canvas sang phải 720 → 960; tổng thời gian giữ nguyên. Theo phản hồi chưa thấy mũi tên, đã tạo `repaired_v2_candidates/conden` mặc định ở viewer: các frame nguồn 45–48 có quãng bay, mỗi frame hiển thị 70 ms, tăng vòng lặp 280 ms. Anh phản hồi bản đó chỉ có đầu tên. Đã dựng `repaired_v5_candidates/conden` với thân lấy mẫu từ màu và độ dày của thân nguồn, nối lại vùng bị che; 12 vị trí bay tăng từ 39 lên 55 px/70 ms, tương ứng khoảng 71%–100% mốc 55 px/70 ms (bước giữa hai frame nguồn trong bản v2). Sau đó tên ra khỏi canvas; 56 frame, vòng lặp dài thêm 560 ms. Hai ảnh phản hồi và hash được lưu trong metadata. Kiểm tra tự động khớp mọi atlas và đã tải Godot 4.3; vẫn cần xem chuyển động và duyệt thẩm mỹ.
- [ ] **firer:** kiểm tra toàn bộ 113 frame, duration và sự thay đổi giữa các frame; xác định đoạn gây khựng trước khi thử chỉnh nhịp/nội suy. Đã xác nhận thời lượng nguồn gồm 97 frame 130 ms, 8 frame 150 ms và 8 frame 200 ms; chưa xác định chính xác nguyên nhân khựng. Đã tạo bản `motion_v2_candidates/firer`: 113 → 226 frame, mỗi frame gốc được chia thời lượng giữa ảnh gốc và ảnh nội suy, tổng thời gian không đổi. Ảnh mẫu chỉ số 20, 40, 80 không đủ chứng minh hết giật; cần xem toàn chuyển động.
- [x] **moxie:** xác định frame/đoạn viên đá bị khuất trong [ảnh phản hồi](../Asset/Character/review/request-20261028/moxie.png), phân biệt do giới hạn canvas, mặt nạ nền hay nguồn gốc; sửa bản thử và so trước/sau từng frame liên quan. Đã xem GIF nguồn: ở chỉ số 21 và 25 vật thể chạm và bị cắt bởi cạnh phải canvas 300 × 250; phần ngoài canvas không có trong các frame đó. Đã dùng vùng vật thể trong chỉ số 20 phục dựng ba frame chỉ số 21, 25, 30, mở rộng canvas 300 → 340 pixel sang phải, giữ nguyên nhịp; ảnh mẫu cho thấy vật thể không còn bị cắt. Phần ngoài ảnh nguồn là phục dựng và cần duyệt đường bay.
- [x] **newwomen:** anh xác nhận giữ hiệu ứng gốc, không cần thêm mũi tên; đã xóa bản thử thêm đường bay và giữ GIF, atlas gốc cùng các bản xử lý nền trước.

## 3. Tách nền

- [x] **fireknight:** xác định frame tương ứng [ảnh phản hồi](../Asset/Character/review/request-20261028/fireknight.png); xử lý các chấm nền trên bản riêng, kiểm tra vùng sát nhân vật và VFX trên nền sáng/tối. Ghi số pixel/kiểm thử và nguy cơ mất hiệu ứng. Ảnh tham chiếu tương ứng gần chỉ số 53; bản thử `fire_speck_candidates` xóa 4.468 pixel trên 91 frame, riêng chỉ số 53 xóa 204 pixel. Quan sát so sánh vẫn thấy nhiều đốm, chưa hoàn tất; cùng màu xanh cũng có thể là chi tiết hiệu ứng. Bản thử chỉ hiện trong lựa chọn viewer, không làm mặc định. Đã tạo thêm `fire_orphan_candidates`: xóa điểm xanh đứng lẻ và cụm xám nhỏ cô lập, 19.744 pixel trên 91 frame, riêng chỉ số 53 xóa 2.381 pixel; ảnh đối chiếu frame 53 sạch hơn rõ. Theo phản hồi tiếp theo, `fire_deep_candidates` lọc thêm các cụm xám/xanh rời tối đa 8 pixel, 11.756 pixel trong 91 frame (305 ở chỉ số 53); vẫn cần xem các frame khác và kiểm tra khả năng mất hạt hiệu ứng.
- [x] **tigerknight:** so vùng dưới thân và sau vai tại frame 64/chỉ số lân cận với [ảnh phản hồi](../Asset/Character/review/request-20261028/tigerknight.png) và GIF nguồn; xử lý riêng, tránh xóa chi tiết xanh cùng màu chủ thể. Đã tạo bản `clean_130_frames` trên bản 30%, xử lý chỉ số 63 và 64: loại 858 và 660 pixel chi tiết xanh theo mặt nạ từ bản nền. Ảnh so sánh cho thấy vùng sau vai và dưới thân sạch hơn. Theo phản hồi tiếp theo, đã tạo `clean_all_130_frames` áp dụng mặt nạ màu cho cả 66 frame, bản v2 loại 54.593 pixel ở lưới 130%, kể cả 348 điểm màu xanh còn sau nội suy; so sánh mẫu các chỉ số 3, 10, 30, 32, 34, 40, 54, 59, 63 cho thấy vùng xanh dưới thân giảm. Vẫn cần duyệt chuyển động và tránh mất chi tiết xanh trùng màu.

## 4. Xóa dữ liệu

- [x] **lois:** đã xóa GIF và các thư mục dẫn xuất khỏi repo, cập nhật catalog/roster/kiểm duyệt và danh sách ẩn. Kiểm tra đường dẫn và catalog hiện hành không còn mục này; `npm test` đạt.
- [x] **maono:** đã xóa và kiểm tra tương tự `lois`; không xóa nhân vật khác. Báo cáo lô làm mịn cũ vẫn là nhật ký lịch sử, có thể nhắc tên hai nguồn đã xóa.

## Kiểm chứng chung

- [ ] Mỗi bản mới có metadata về nguồn, phương pháp, frame, thời lượng và giới hạn; GIF nguồn không bị ghi đè trừ hai nguồn được yêu cầu xóa.
- [ ] Kiểm tra dữ liệu tự động, đọc kết quả QA và xem trực quan các đoạn liên quan trong viewer; kiểm thử Godot phù hợp với phần đã tích hợp.
- [ ] Ghi kết quả thực tế và phần chưa kiểm tra, đặc biệt các thay đổi VFX/chuyển động và kiểm thử trên thiết bị. Không tuyên bố hoàn thiện cho mobile khi chưa có số liệu.

Kiểm tra Godot 4.3 trong dự án tạm: hàm `create_detail130_candidate` tải artemis (64 frame) và ziggist (32 frame), tỷ lệ trả về cho canvas hiển thị 300 × 300. Chưa kiểm tra trực quan toàn bộ hoạt ảnh hoặc trên thiết bị.

Ngày 2026-10-28, kiểm tra dữ liệu `python tools/verify_motion_repair_candidates.py`: đủ năm bản thử, tổng thời gian từng frame nguồn khớp và các frame không chỉnh giữ pixel gốc. Godot 4.3 dự án tạm tải blacktiger 52, firer 226, conden 52, bản newwomen cũ 75 (đã loại theo yêu cầu) và moxie 97 frame, với canvas ghi trong metadata; kiểm thử viewer mô phỏng chuyển timeline và trả về nguồn. Các bản hoạt ảnh mới chỉ được xem qua ảnh đối chiếu mẫu, chưa chứng minh mượt và chưa kiểm tra thiết bị.

Rà bảng ảnh toàn bộ fireknight (91) và tigerknight (66): bản lọc mới giảm rõ vùng xanh. Ở fireknight, các điểm rời còn lại trong một số frame phần lớn có màu sáng trùng VFX, chưa đủ bằng chứng để xóa an toàn. Tigerknight v2 xóa thêm 348 pixel màu xanh còn sót sau nội suy, tổng 54.593 pixel; tiêu chí màu vẫn có thể trùng chi tiết chủ thể. Chưa đánh dấu sạch hoàn toàn chỉ dựa vào bảng ảnh.

Khảo sát nhịp nguồn: artemis có 32 frame 70 ms rồi 32 frame 60 ms; aumen có 67 frame 60 ms. Viewer nay có chế độ so sánh thời lượng 60/70/130 ms (chỉ preview); đọc trước tối đa bốn ảnh chi tiết, không bảo đảm loại hết giật. Chưa đo browser hoặc APK thật.

Rà lại todo sau phản hồi thân tên: đã thêm bản v5 cho conden và xem bảng thu nhỏ đủ 14 bộ frame. Chưa có bằng chứng phát liên tục cho 14 bộ; bản nội suy blacktiger vẫn có đoạn chuyển gắt, firer chưa chứng minh hết giật; moxie và hai bản tách nền vẫn cần duyệt chuyển động. Không tự đánh dấu hoàn tất các mục này. Chưa kiểm tra APK hay thiết bị.

## Kiểm tra lại sau khi khôi phục phiên

- Ngày 2026-10-28: chạy lại `python tools/verify_detail130_candidates.py`, `python tools/verify_detail130_atlases.py`, `python tools/verify_motion_repair_candidates.py`, `python tools/verify_conden_arrow_v5.py`, `python tools/verify_deep_cleanup.py`: đều đạt; 14 bộ 130% có 669 frame, các bản chuyển động giữ tổng thời lượng nguồn, bản conden v5 có 56 frame và 12 vị trí đường bay. Đây là kiểm tra dữ liệu, không thay thế duyệt hình ảnh và chuyển động.
- `npm test` đạt 4/4 khi chạy ngoài sandbox có quyền mở cổng; chạy trong sandbox thất bại 2 kiểm thử cần bind cổng. Viewer chạy tại cổng 4173, trang trả HTTP 200 và API motion liệt kê blacktiger, firer.
- Phiên kiểm tra này không có trình duyệt để quan sát phát liên tục, không có ffmpeg/ffprobe hay tuyến tạo video sẵn dùng, và không kiểm tra APK/thiết bị thật. Các mục chờ duyệt và đoạn blacktiger còn chuyển gắt vẫn chưa hoàn tất. Không có asset nào được sửa trong lần rà soát này.

## Yêu cầu tăng độ phân giải bổ sung

- [x] Tạo bản thử riêng từ bản mặc định đang xem cho 26 mục: artemis, aument, bearen, biden, botem, choptian, conden, corepion, dracian, dragonight, dragonmout, ethan, guard, jaik, Kahn, kapicon, knight, mainthen, mortafi, nox, overight, powerdame, scorpit, skyles, tigerknight và wuchen. Tăng 20% theo mỗi chiều, riêng dragonmout tăng 40%, giữ kích thước hiển thị. Tigerknight dùng bản lọc nền toàn bộ. Mỗi bản nằm ở `Asset/Character/detail_oct28_candidates/<id>`; metadata ghi nguồn, hash các đầu vào, số frame, nhịp và kích thước. Tạo lại bằng `python tools/create_detail_oct28.py` trong thư mục đầu ra trống; có thể tạo từng mục bằng cách truyền tên.
- [x] Conden dùng mũi tên có thân đã phục dựng ở bản v5; chín vị trí bay từ frame nguồn chỉ số 44, bước 55, 59, 63, 67, 71, 75, 79, 83 px/70 ms, tức 100% đến khoảng 151% của mốc cũ 55 px/70 ms. Mũi tên ra khỏi canvas; 53 frame. Bản cũ vẫn có thể chọn trong viewer.
- [x] `python tools/verify_detail_oct28.py`: đạt 26 mục, 1.449 frame, hash đầu vào, kích thước, thời lượng và đường bay; `npm test`: 4/4. Viewer liệt kê đủ 26 mục. Đã xem ảnh mẫu artemis, dragonmout, tigerknight và ba frame conden; không thay thế xem chuyển động liên tục.
- [ ] Duyệt từng hoạt ảnh, viền và VFX, nhất là tốc độ và thân tên conden. Nội suy Lanczos có xử lý alpha chỉ tăng mật độ pixel, không khôi phục chi tiết nguồn và không bảo đảm giảm nhòe; ảnh nguồn và các bản trước được giữ. Chưa kiểm tra Godot hoặc thiết bị thật cho các bản mới.

## Phản hồi trải nghiệm và nợ còn lại

- Anh xác nhận moxie đã ổn; tigerknight và fireknight ổn định. Anh chấp nhận 26 bản tăng phân giải ở mức tạm ổn, dù chưa thật nét; đây là duyệt trải nghiệm các bản đó, không xác nhận mọi bản cũ hoặc chất lượng phát hành.
- Firer: tạo `speed_oct28_candidates/firer` dựa trên `fine_candidates` vốn là mặc định trước thay đổi, giữ 113 frame, chia thời lượng cho 5 (130/150/200 ms thành 26/30/40 ms), tổng 15.410 → 3.082 ms. Mặc định viewer là bản mới ở tốc độ 1×; vẫn cần anh duyệt nhịp thực tế.
- Conden: `speed_oct28_candidates/conden` dùng lại chín vị trí tên của bản +20%, thời lượng mỗi vị trí 70 → 0,7 ms (100×), tổng 6,3 ms; các frame nhân vật vẫn có tổng 70 ms mỗi frame nguồn. Điều này nhanh hơn một chu kỳ làm tươi màn hình phổ biến, nên tên có thể không thấy hoặc như dịch chuyển tức thời. Cần anh kiểm tra; có thể cần hiệu ứng vệt hoặc tỷ lệ khác để nhìn rõ.
- `python tools/verify_speed_oct28.py` đạt: hash đầu vào, đường bay, thời lượng và đường dẫn; `npm test` đạt 4/4. Chưa xem phát liên tục hay đo trên thiết bị. Bản nguồn và phiên bản cũ được giữ.
- Còn nợ: blacktiger có chuyển động nội suy còn gắt; các mục ziggist, snowpie, azza trong lô 130% cũ chưa nằm trong danh sách 26 vừa được anh duyệt; các bản tốc độ mới cần duyệt; chưa tích hợp/kiểm tra đầy đủ các bản mới vào gameplay Godot hoặc đo hiệu năng, APK và thiết bị thật. Các kết quả xem ở browser không chứng minh chất lượng mobile. Workspace có nhiều thay đổi chưa commit, bao gồm xóa file và asset mới; cần rà riêng trước khi commit, không tự khôi phục hoặc xóa.

## Chỉnh nhịp 60 FPS và sửa tên biến mất

- Firer: bản `speed_60fps_candidates` dùng 113 frame của bản mặc định trước, đặt thời lượng theo bội số 1/60 giây và làm tròn tích lũy quanh mục tiêu nguồn / 3. Cả vòng 5.133,33 ms so với mục tiêu chính xác 5.136,67 ms. Bản ×5 vẫn có thể chọn.
- Conden: bản 60 FPS thử đầu có frame giữ tư thế không vẽ tên, trong đó frame hiển thị số 50. Bản `conden_60fps_candidates` thay đoạn đó bằng 17 vị trí liên tiếp, mỗi vị trí một nhịp 60 Hz, bước tăng từ 25 đến 40 px/nhịp; frame 50 có tên, vị trí cuối ra khỏi canvas. Tư thế nguồn được căn tích lũy vào nhịp 60 Hz; tổng vòng 3.366,67 ms so với 3.360 ms nguồn. Tổng thời gian đoạn tên là 283,33 ms, dài hơn bản ×100 trước. Các ảnh tên và thân vẫn là phục dựng.
- `python tools/verify_60fps_candidates.py` đối chiếu timing, hash, từng ảnh tên, frame 50 và đường bay; `npm test` đạt 4/4. Đã xem ảnh tĩnh frame 49–52. Chưa xem phát thực tế hay đo trên thiết bị; dữ liệu căn theo 60 Hz không bảo đảm trình duyệt hoặc game đạt 60 FPS. Cần anh duyệt chuyển động và tốc độ mới.

## Điều chỉnh theo phản hồi tiếp theo

- Firer: bản `tune_60fps_candidates/firer` lấy bản gốc đang dùng trước khi đổi tốc độ, đặt mục tiêu 2× và căn tổng thời gian tích lũy vào nhịp 60 Hz. 113 frame, vòng 7.700 ms so với mục tiêu chính xác 7.705 ms. Các bản 3× và 5× được giữ để so sánh.
- Conden: bản `tune_60fps_candidates/conden` giữ 17 vị trí liên tục nhưng dùng bước đều 33 px mỗi nhịp 60 Hz thay cho các bước tăng tốc; không làm thay đổi nhịp nguồn đã được căn trong bản trước. Viewer bắt đầu tải trước ảnh đoạn tên từ frame 39 để giảm nguy cơ giật khi giải mã; chưa đo mức dùng bộ nhớ hay tốc độ trên thiết bị. Nguồn và các bản trước được giữ.
- `python tools/verify_tune_60fps.py` đạt kiểm tra nguồn, ảnh, đường bay, frame 50 và nhịp; `npm test` đạt 4/4. Chưa có bằng chứng phát liên tục thực tế, cần anh duyệt tốc độ và độ mượt hai bản.

Ngày 2026-10-29: theo ảnh phản hồi `image copy 8.png`, đã phục dựng đầu đạn trong atlas mặc định `moxie_repaired`. Frame hiển thị 39 (chỉ số 38) có đầu đạn nguyên; ở frame 40–47 tia chạm cạnh phải 300 px của GIF gốc. Mở rộng canvas từ 340 lên 660 px, nối tia theo cột mép nguồn, dùng đầu đạn từ frame 39 và cho tiến thêm 40 px mỗi frame; đầu đạn được thu nhỏ theo chiều dày tia khi tia thu lại. Tọa độ ngoài GIF và chuyển động là phục dựng, không phải dữ liệu gốc. Giữ 97 frame, thời lượng, neo, tỷ lệ và bản phục dựng trước; bản trước lưu ở `Asset/Character/archive/moxie_repaired_before_beam_oct29`. Tạo bằng `tools/extend_moxie_beam_oct29.py`, ảnh đối chiếu tại `Asset/Character/review/cleanup-oct29/moxie-beam-frames-39-48.png`. `python tools/verify_moxie_beam_oct29.py` kiểm tra hash, timeline, mọi pixel ngoài vùng phục dựng và kết quả tám frame: đạt. Canvas rộng hơn có thể làm nhân vật trông nhỏ hơn trong chế độ vừa khung, nhưng không đổi tỷ lệ 1×. Chưa xác nhận chuyển động khi phát trên thiết bị.
