# Lô tăng độ chi tiết 30% ngày 29/10

Trạng thái: **bản thử chưa duyệt**. Mỗi nhân vật được xử lý lần lượt bằng `tools/create_detail_oct29.py`, từ phiên bản ưu tiên trước đó của viewer. Không thay GIF, atlas hay bản thử cũ. Mỗi `candidate.json` lưu hash nguồn, hash metadata và ảnh đầu vào, số frame, độ phân giải, kích thước hiển thị và giới hạn.

Phương pháp: tăng số pixel frame theo mỗi chiều 30% bằng Lanczos trên alpha nhân trước, rồi làm nét RGB rất nhẹ (radius 1, 18%, threshold 3). Đây là nội suy từ ảnh có sẵn, không sinh thêm chi tiết gốc. Thời lượng mỗi frame được giữ nguyên. 24 nhân vật giữ nguyên kích thước hiển thị; theo xác nhận của anh, `momo` tăng hiển thị 30%, `nox` giảm 20%.

| Nhân vật | Frame | Đầu vào | Độ phân giải frame | Hiển thị trước → sau |
|---|---:|---|---:|---:|
| aonime | 60 | native_candidates | 780×780 → 1014×1014 | 780×780 → 780×780 |
| botem | 75 | detail_oct28_candidates | 600×600 → 780×780 | 500×500 → 500×500 |
| buffoin | 49 | native_candidates | 480×480 → 624×624 | 480×480 → 480×480 |
| comic | 47 | batch12_detail_candidates | 480×480 → 624×624 | 400×400 → 400×400 |
| congpha | 34 | native_candidates | 600×600 → 780×780 | 600×600 → 600×600 |
| dragonot | 49 | revision_candidates | 384×384 → 499×499 | 384×384 → 384×384 |
| ethan | 72 | batch12_detail_candidates | 600×600 → 780×780 | 500×500 → 500×500 |
| hanko | 72 | native_candidates | 720×720 → 936×936 | 720×720 → 720×720 |
| jaik | 53 | detail_oct28_candidates | 480×480 → 624×624 | 400×400 → 400×400 |
| jaying | 21 | batch12_detail_candidates | 240×240 → 312×312 | 200×200 → 200×200 |
| kengkeng | 77 | native_candidates | 780×780 → 1014×1014 | 780×780 → 780×780 |
| kungtailee | 120 | native_candidates | 400×400 → 520×520 | 400×400 → 400×400 |
| machinen | 64 | native_candidates | 600×600 → 780×780 | 600×600 → 600×600 |
| magma | 120 | native_candidates | 400×400 → 520×520 | 400×400 → 400×400 |
| mainthen | 53 | detail_oct28_candidates | 264×264 → 343×343 | 220×220 → 220×220 |
| momo | 58 | revision_candidates | 729×729 → 948×948 | 506×506 → 658×658 |
| nox | 47 | detail_oct28_candidates | 842×842 → 1095×1095 | 540×540 → 432×432 |
| odin | 86 | batch12_detail_candidates | 480×480 → 624×624 | 400×400 → 400×400 |
| overight | 48 | detail_oct28_candidates | 811×811 → 1054×1054 | 520×520 → 520×520 |
| panfire | 49 | batch12_detail_candidates | 864×864 → 1123×1123 | 720×720 → 720×720 |
| shellhost | 41 | revision_candidates | 624×624 → 811×811 | 520×520 → 520×520 |
| skyles | 96 | detail_oct28_candidates | 780×780 → 1014×1014 | 500×500 → 500×500 |
| swithin | 62 | native_candidates | 200×200 → 260×260 | 200×200 → 200×200 |
| trongit | 60 | native_candidates | 400×400 → 520×520 | 400×400 → 400×400 |
| vision | 56 | native_candidates | 200×200 → 260×260 | 200×200 → 200×200 |
| warrioram | 120 | native_candidates | 520×520 → 676×676 | 520×520 → 520×520 |

Kiểm chứng đã chạy: 26 id tồn tại trong catalog; 1.689 frame PNG RGBA có kích thước mới đúng; hash GIF, metadata và 893 file đầu vào riêng biệt khớp; số frame và thời lượng bằng nguồn; kích thước hiển thị đúng hệ số. `npm test`: 4/4; localhost trả 200 cho 26 bản và frame đầu. Đã xem bảng ảnh mẫu 12 frame mỗi nhân vật và ảnh so frame 0 của `dragonot`, `momo`, `nox`, `shellhost`, `mainthen`, `overight`.

Giới hạn: ảnh mẫu và kiểm tra dữ liệu không thay việc xem toàn bộ 1.689 frame khi phát. Nội suy có thể làm viền mềm, xuất hiện halo hoặc đổi VFX. `shellhost` vẫn có mảng hình hộp sẵn từ bản đầu vào; `overight` còn chấm nền có trước. Bộ mới chiếm khoảng 182 MB trên đĩa; chưa kiểm tra trong Godot editor hoặc trên thiết bị mobile, chưa đo bộ nhớ và hiệu năng.

Xem tại `http://localhost:4173`: chọn nhân vật, viewer mặc định **Chi tiết +30%, nét nhẹ · chưa duyệt**; mục **Phiên bản** vẫn cho phép so với bản cũ.
