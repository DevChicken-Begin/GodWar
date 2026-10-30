# Chốt hoạt ảnh và dọn dữ liệu — 30/10/2026

## Mốc hiện hành

Anh chốt toàn bộ lựa chọn và kích thước đang hiển thị. Danh sách 177 mục / 178 profile: `docs/approved-animations-20261030.md`. Manifest hiện hành: `Asset/Character/characters/approved-animations-20261030-v8.json`; viewer và Godot dùng mốc này. V8 gồm sửa Kikontai frame 34, Hecpoirt frame 1/46 và Maxoi vùng mặt. Một số hoạt ảnh vẫn là chuỗi tham chiếu chưa phân loại động tác; sự chốt không chứng minh chất lượng phát hành hoặc hiệu năng mobile.

Mốc v8 đã đối chiếu 1.354 file metadata/atlas, 178 profile, hash GIF nguồn và chiều cao hiện hành; đều khớp. Kích thước hiện hành do `height-targets.json` cung cấp cho viewer/Godot. Dữ liệu cũ trong metadata candidate của một số nhân vật đã chốt được giữ để bảo toàn hash gốc, không thay cho chiều cao hiện hành.

## Xử lý điểm theo phản hồi

- Kikontai: `tools/clean_kikontai_frame34_20261030.py`, frame hiển thị 34 có 36 pixel chuyển trong suốt; ảnh trước/sau tại `Asset/Character/review/twenty-import-20261030/kikontai/frame34-before-after.png`.
- Hecpoirt: `tools/clean_hecpoirt_frame1_46_20261030.py`, frame hiển thị 1 và 46 lần lượt có 15 và 32 pixel chuyển trong suốt; ảnh trước/sau tại `Asset/Character/review/twenty-import-20261030/hecpoirt/frame1-46-before-after.png`.
- Maxoi: `tools/clean_maxoi_face_20261030.py`, loại 627 pixel ở vùng gần mặt trong các frame hiển thị 33–51 theo màu xanh mẫu; ảnh trước/sau tại `Asset/Character/review/twenty-import-20261030/maxoi/face-before-after.jpg`. Có rủi ro xóa nhầm VFX trùng màu; chưa duyệt toàn bộ khi phát.

Ba GIF gốc, atlas trước sửa và clip mới được giữ. Đối chiếu đủ 45, 54 và 51 frame tương ứng: thời lượng, RGB còn giữ và nguồn khớp; alpha chỉ chuyển sang 0. Godot 4.3 headless nạp ba profile đã chốt, đúng số frame và chiều cao. `npm test` 7/7; chưa kiểm tra trên thiết bị.

## Dọn dữ liệu và khả năng truy vết

- Đã xóa 30 GIF trùng ở thư mục gốc theo xác nhận của anh; mỗi file được so SHA-256 với bản giữ tại `Asset/Character/vfx/`. Danh sách và hash: `docs/cleanup-20261030-root-gifs.json`.
- Đã xóa 4.331 file Forge thuộc các lần thử cũ (597.156.511 byte) sau khi kiểm tra từng file, đối chiếu 2.354 file đầu vào/đầu ra của clip hiện hành và giữ GIF nguồn, atlas, frame đầu vào ban đầu và clip hiện hành. Danh sách, hash, lý do và clip hiện hành theo từng file: `docs/cleanup-20261030-forge-plan.json` và `docs/cleanup-20261030-after-maxoi-plan.json`. Các link tới clip thử cũ trong báo cáo lịch sử không còn hoạt động; không dùng chúng làm nguồn hiện hành.
- Đã đổi đường dẫn tham chiếu GIF gốc ở metadata hiện hành sang `Asset/Character/vfx/` và lưu metadata cũ cùng mapping/hash tại `Asset/Character/archive/root_gif_provenance_metadata_20261030/`. Vì thay đổi đường dẫn, hash candidate của một số mốc cũ không còn khớp tại đường dẫn hiện hành; bản metadata cũ khớp hash được lưu trong archive đó. Với Kikontai, Hecpoirt và Maxoi, atlas/candidate trước sửa được lưu lần lượt trong `Asset/Character/archive/kikontai_before_frame34_cleanup/`, `hecpoirt_before_frame1_46_cleanup/` và `maxoi_before_face_cleanup/`. Mốc v8 là mốc dùng hiện tại.
- Một số metadata lịch sử của năm nhân vật còn nhắc `Also.gif` là một nguồn mẫu đã xóa theo yêu cầu trước; không thể tái tạo nguyên vẹn mẫu cũ đó. GIF hiện hành của năm nhân vật vẫn được giữ và hash xác minh được.
- Giữ các archive và các bản Forge cũ của năm nhân vật trước vì chưa chứng minh có thể xóa mà không mất khả năng đối chiếu/tái tạo; clip Forge của năm nhân vật này vẫn chưa đồng bộ với atlas đã chốt. Không xóa bừa các candidate, nguồn GIF, cache Git hoặc toolchain.

Dung lượng thư mục dự án trước bước dọn khoảng 4,1 GiB; sau bước dọn đo khoảng 3,6 GiB (có thể thay đổi khi Git tạo object). Các thay đổi chưa commit có sẵn, gồm 11 GIF trong `13 charnew/` đã bị xóa trước phiên này, vẫn nằm trong working tree và được giữ theo yêu cầu push toàn bộ.

Sau commit và push, đo lại toàn workspace khoảng 4,4 GiB, trong đó `.git` khoảng 1,7 GiB (`size-pack` 1,64 GiB) và `Asset/Character/forge_pilots` 619 MiB. Phần Git tăng do lưu object của commit và lịch sử; xóa file khỏi working tree không tự xóa chúng khỏi lịch sử Git. Không rewrite lịch sử hoặc dọn Git objects trong đợt này.
