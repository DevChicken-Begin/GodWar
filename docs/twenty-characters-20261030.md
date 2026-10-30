# Nhập 20 GIF — 30/10/2026

Đang thực hiện. Danh sách nguồn, hash, kích thước, số frame và thời lượng: `Asset/Character/review/twenty-import-20261030/inventory.json`. Giữ nguyên GIF gốc. Tất cả 520×520; `samset` có thời lượng 60 và 70 ms, còn lại chỉ 60 ms. Tên là tên file, chưa phân loại động tác.

Chiều cao thân (px, viewport 1920×1080) do anh cung cấp: samset 80, kikontai 80, hecpoirt 70, uopon 80, isorat 75, ompan 85, combra 90, maxoi 80, osiris 85, thorn 80, onaon 70, cornra 90, ison 90, charmia 80, Kungteng 90, cons 90, isis 80, omega 80, oset 80, pandung 85. Mốc thân ước lượng cần duyệt.

Nguồn mẫu đều dùng cảnh xanh và logo trong ảnh giữa GIF. Phép thử sử dụng mẫu Moregorn frame chỉ số 37–40, mẫu xanh `pixel_simple.png` và footprint logo chung. Màu nền có thể trùng nhân vật/VFX; logo cố định có thể che hiệu ứng. Bắt buộc xem toàn bộ frame và phát thực tế, không xem đối chiếu pixel là bằng chứng tách sạch. Dữ liệu mới chưa được anh duyệt.

Theo yêu cầu, năm atlas hiện hành Aquamen, Diorai, Evenl, Moregorn, Moresword được chốt tại `Asset/Character/characters/approved-animations-20261030-v3.json` với hash và chiều cao; mốc v2 được giữ. Forge clip của năm nhân vật vẫn là phiên bản trước sửa nền, chưa đồng bộ với atlas đã chốt. `npm test` sau chuyển mốc: 7/7; kiểm hash 5 atlas và metadata thành công.

## Bản thử trong viewer

Đã đưa 20 GIF vào catalog, atlas đo và viewer dưới nhãn chưa chốt. Nguồn gốc được giữ; atlas nguồn và bản tách được lưu riêng. Đã đối chiếu 1.147 frame với GIF sau các bước phục hồi: hash nguồn, số frame, thời lượng và màu RGB của pixel còn hiển thị khớp. `samset` giữ cả 60 và 70 ms. API viewer trả đủ 20 catalog và atlas; `npm test` đạt 7/7. Các phép này không chứng minh phần bị xóa đều là nền.

Khi đối chiếu `cons` chỉ số frame 48 (hiển thị 49), phát hiện mask logo làm thủng vòng hiệu ứng thành hình chữ; `tools/repair_cons_logo_overlap_20261030.py` phục hồi 16.990 pixel ở frame đó bằng đối chiếu màu nguồn với mẫu logo và nền, rồi tạo clip Forge mới. Ảnh mẫu sau sửa đã xem. Kiểm tra tự động vùng logo cảnh báo 7 GIF có nguy cơ VFX chồng: combra, hecpoirt, ompan, onaon, osiris, samset, thorn; `tools/repair_twenty_logo_overlaps_20261030.py` phục hồi theo cùng nguyên tắc và tạo clip mới. Dữ liệu trước sửa nằm trong `Asset/Character/archive/twenty_cons_before_logo_repair/` và `Asset/Character/archive/twenty_before_logo_overlap/`; báo cáo frame nghi ngờ tại `Asset/Character/review/twenty-import-20261030/logo-overlap-audit.json`. Phép ước lượng vẫn có thể bỏ sót hiệu ứng hoặc khôi phục logo; chưa xem toàn bộ kết quả mới khi phát. Bảng `contact-light.jpg`/`contact-dark.jpg` của tám GIF có phục hồi được tạo trước sửa, không phải ảnh hiện hành.

QA Forge hiện hành: 19 GIF (trừ samset) `tick_grid` WARN value 6.667, threshold null; `near_duplicate_holds` WARN combra value 1, samset 3, uopon 2, threshold 0. `loop_seam` cần xem trực quan; chi tiết từng GIF, giá trị và ngưỡng tại `Asset/Character/review/twenty-import-20261030/forge-qa.json`, nguồn QA ở đường dẫn ghi trong file. GIF và hoạt ảnh mới chưa được anh duyệt; mốc thân và neo ước lượng, cần duyệt tỷ lệ và chuyển động. Chưa kiểm tra hiệu năng thiết bị mobile.

Godot 4.3 headless: trong dự án tạm đã import atlas hiện hành và chạy `tools/check_twenty_20261030.gd`; đủ 20 nhân vật nạp được, số frame, thời lượng và chiều cao theo mốc ước lượng khớp. Đây chưa kiểm tra playback trực quan hoặc hiệu năng trên thiết bị.

## Rà chấm và cập nhật chiều cao tiếp theo

Anh yêu cầu combra 80, cons 80, cornra 85, omega 75, ompan 75, oset 75, pandung 80, Domrico 90, Actem 90, Aquamen 65, Diorai 70, Kahn 90, Kungteng 85 và Moresword 65 px. `height-targets.json` là nguồn chiều cao hiện hành cho viewer và Godot; metadata atlas của sáu nhân vật đã chốt giữ nguyên để không làm sai hash mốc cũ, còn mốc chốt mới `approved-animations-20261030-v4.json` ghi chiều cao mới. Mốc v3 và atlas đã chốt được giữ.

Một chấm xanh tồn tại cùng tọa độ ở nhiều nhân vật; mẫu cảnh cũ tại vị trí đó lẫn màu hiệu ứng. `tools/refine_twenty_static_residue_20261030.py` tạo mẫu trung vị từ 80 frame thuộc 20 GIF, lấy điểm ổn định khi ít nhất 70% mẫu gần trung vị trong sai khác RGB tối đa 8. Xóa pixel đang hiện nếu khớp màu xanh cảnh ổn định hoặc pixel logo ổn định trong vùng logo, sai khác tối đa 8. Đã giữ atlas trước sửa tại `Asset/Character/archive/twenty_before_static_residue/`, tạo lại clip Forge và ảnh `static-refined-light.jpg`/`static-refined-dark.jpg` của từng GIF. Số pixel chuyển trong suốt: 40.068 trên 1.070 frame. Đây không chứng minh mọi pixel đó là nền: có thể xóa hiệu ứng trùng màu và còn sót màu khác. Đã xem ảnh mẫu frame đầu của cả 20 và bảng nền sáng của combra/cons/cornra; chưa xem hết hoạt ảnh khi phát.

Kiểm thử: so 1.147 frame trước/sau: RGB không đổi, alpha chỉ chuyển về 0, màu pixel còn giữ và thời lượng khớp GIF. API và hàm `resolveHeightProfile` khớp cả 14 kích thước; kiểm hash 6 hồ sơ chốt trong v4 khớp. `npm test` 7/7. Forge QA hiện hành tại `Asset/Character/review/twenty-import-20261030/forge-qa.json`: 19 GIF trừ samset có WARN `tick_grid` value 6.667 threshold null; `near_duplicate_holds` WARN combra 1, samset 3, uopon 2 (threshold 0). Chưa kiểm tra Godot hoặc thiết bị sau lần chỉnh này; clip Forge của 5 nhân vật đã chốt trước đây vẫn cần đồng bộ atlas của họ.

## Sửa các chấm anh chỉ ra

Đã xử lý 15 nguồn: Kungteng, charmia, combra, cornra, isis, omega, ompan, pandung, samset, thorn, uopon, maxoi, cons, osiris, oset. `tools/clean_fifteen_reported_spots_20261030.py` giới hạn lọc nền ở bốn cụm tọa độ nghi ngờ (gồm điểm gần chân và bốn điểm nhìn thấy sau lưng maxoi), so RGB với mẫu cảnh trong sai khác tối đa 25 và yêu cầu màu xanh tối; vùng logo của cons, ompan, osiris, oset, samset, thorn được đối chiếu với frame 0 cùng GIF, xóa pixel khớp trong sai khác tối đa 25. Kết quả vẫn có nguy cơ mất VFX màu tương tự hoặc sót hạt ngoài vùng/ngoài ngưỡng. Không sửa GIF gốc; atlas trước nằm tại `Asset/Character/archive/twenty_before_reported_spots/`. Đã tạo lại clip Forge của 15 nguồn và ảnh `reported-spots-light.jpg`/`reported-spots-dark.jpg` từng nguồn.

Đã xem ảnh trước/sau `reported-spots-comparison.jpg`: ompan frame hiển thị 6, 17, 22, 28; cons frame 1 và 49; maxoi frame 33 và 39; pandung frame 42; thorn frame 40. Các điểm được chọn giảm ở mẫu; chấm tối vùng ompan ở frame 6/17 được loại và cons frame 49 vẫn giữ vòng hiệu ứng nhìn ở ảnh mẫu. Với oset, kiểm tra toàn bộ 49 frame trong vùng logo x=90..434, y=35..149 cho thấy alpha hiện hành bằng 0, nên lần này không xóa thêm pixel ở nguồn đó; chưa chứng minh điểm anh thấy không nằm ngoài vùng này. Chưa kiểm tra phát thực tế toàn bộ chuỗi hay duyệt tất cả frame phóng lớn.

Kiểm tra 857 frame của 15 nguồn: hash GIF, số frame, thời lượng, RGB pixel giữ lại khớp nguồn; so với atlas trước, RGB không đổi và alpha chỉ chuyển 0 tại 35.441 pixel. Kiểm tra này không chứng minh pixel bị xóa là nền. `npm test` 7/7 và API viewer có đủ 15. Forge QA hiện hành tại `Asset/Character/review/twenty-import-20261030/forge-qa.json`: 14 nguồn trừ samset có WARN `tick_grid` value 6.667 threshold null; `near_duplicate_holds` WARN combra 1, samset 3, uopon 2, threshold 0. Chưa kiểm tra Godot hoặc thiết bị sau lần sửa này.

## Mốc chốt và sửa tiếp

Toàn bộ lựa chọn hiện hành được anh chốt tại `Asset/Character/characters/approved-animations-20261030-v8.json`. Các sửa Kikontai frame 34, Hecpoirt frame 1/46 và Maxoi vùng mặt, các kiểm thử cùng những dữ liệu trung gian đã dọn được mô tả tại `docs/cleanup-and-freeze-20261030.md`.
