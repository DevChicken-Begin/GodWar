# Agent Sprite Forge trong GodWar

Nguồn: [Agent Sprite Forge](https://github.com/0x0funky/agent-sprite-forge), commit `5324342fdfab72430f4e9604f3fe427009f8596d`. Bộ skill được cài cho Codex bằng `tools/install_skills.py --apply --host codex` của tác giả; mở phiên Codex mới để nạp skill. Kiểm tra độ khớp bằng `python tools/install_skills.py --check --host codex` từ bản checkout cùng commit. Năm skill: `generate2dsprite`, `video2dsprite`, `generate2dmedia`, `generate2dmap`, `codeart2d`.

Trong môi trường hiện tại, Python và các thư viện của Forge nằm tại `~/.local/share/godwar-sprite-forge/venv/bin/python`. Trên Codespace mới, làm theo README của tác giả: clone repo, cài `requirements.txt` vào môi trường Python riêng, rồi chạy trình cài trên. Cần ffmpeg 5.1+ và ffprobe cho xử lý video; tạo video còn cần provider hoặc CLI tương thích. Kiểm tra khả năng mỗi phiên bằng `forge_doctor.py` trong skill `generate2dmedia`; không đưa API key vào dự án. Các route API có thể phát sinh chi phí.

## Quy trình cho nhân vật

1. Xem GIF và sổ kiểm duyệt trong `Asset/Character/review/`, xác nhận nhân vật, frame tham chiếu, hướng và hành động trước khi phân loại. Các atlas và bản tách nền hiện tại vẫn là nguồn/bản thử, không mặc định đã duyệt.
2. Với hoạt ảnh thiếu, dùng `$generate2dsprite` lập mô tả và chọn một master dựa trên frame tham chiếu đã xem; duyệt bằng mắt trước khi dùng `$video2dsprite` để tạo từng hành động từ master. Ghi rõ hoạt ảnh và skill nào được tạo bổ sung, tối đa một skill cho mỗi nhân vật. Không khẳng định động tác mới có trong GIF nguồn.
3. Lưu đầu vào, prompt, phiên bản công cụ, đường dẫn và hash nguồn, route, kết quả, thông số, báo cáo QC và quyết định duyệt trong thư mục mới riêng cho từng lần thử. Không ghi đè GIF, atlas hay bản thử cũ. Quan sát từng frame, so danh tính, vũ khí, viền alpha trên nền sáng/tối, tỉ lệ, điểm neo, nhịp và vòng lặp; chỉ số QC không thay thế kiểm duyệt trực quan.
4. Xuất Godot 4 khi kết quả được chọn, kiểm tra thực tế trong editor và trạng thái/chuyển tiếp. Giữ gameplay, sát thương và thời điểm va chạm độc lập với hình. Kiểm tra kích thước, bộ nhớ và hiệu năng trên thiết bị trước khi tuyên bố phù hợp mobile. README của Forge ghi nhận bản xuất Godot 0.4 chưa được xác minh bằng editor.

Có thể yêu cầu trong phiên mới: `Dùng $generate2dsprite giúp chuẩn bị master cho [tên], dựa trên các frame nguồn đã kiểm duyệt của GodWar; giữ nguyên nguồn và ghi provenance.` Chỉ chạy tạo hình hoặc video sau khi đã xác định tham chiếu và mục tiêu cụ thể; không có asset mới nào được tạo trong bước cài đặt này.
