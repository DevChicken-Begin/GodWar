# GodWar

Dark Fantasy 2D Top-Down Mobile Game developed with Godot 4 & AI Automation Pipeline.

## 🚀 Quick Start (Codespace & Mobile Development)

This repository is designed to be **100% portable across any GitHub Codespace or account**.

### 1. Environment Bootstrap
Whenever opened in a new Codespace, the environment is automatically set up via `.devcontainer/devcontainer.json`.
You can also manually initialize anytime:
```bash
./scripts/bootstrap.sh
```

### 2. Connect GPU (Google Colab)
Leverage remote GPU (A100 / L4 / T4) for AI asset generation and heavy compute:
```bash
./scripts/colab_start_a100.sh   # Connect or start GPU session
./scripts/colab_stop.sh         # Release session to save compute units
```

### 3. Build & Test Android APK
- **Build APK (Headless via Godot CLI):**
  ```bash
  ./scripts/build_android_apk.sh
  ```
  *(Output generated at `build/GodWar-debug.apk`)*

- **Deploy to Android Device over Wi-Fi:**
  ```bash
  ./scripts/adb_install_phone.sh <DEVICE_IP:PORT>
  ```

### 4. VS Code One-Click Tasks
Press **`Ctrl + Shift + B`** (or `Cmd + Shift + B` on macOS) to trigger the primary build action, or open **Terminal > Run Task...** to select from all available automation scripts.

### Kiểm thử GIF và frame nhân vật

**Mốc hiện hành:** các hoạt ảnh anh chốt ngày 29/10/2026 được liệt kê tại [danh sách chốt](docs/approved-animations-20261029.md). Viewer đánh dấu bản đã chốt và các bản tham khảo cũ; các ghi chú bên dưới mô tả lịch sử các bản thử.

Quy trình sử dụng Agent Sprite Forge cho nhân vật được ghi tại [docs/sprite-forge.md](docs/sprite-forge.md).

Trong thư mục dự án, chạy:

```bash
npm run dev
```

Mở `http://localhost:4173` (trong Codespaces, mở cổng 4173 được forward). Dùng ô tìm kiếm để chọn GIF; có thể phát/dừng, xem từng frame, chỉnh tốc độ, phóng to, đổi nền, lật hướng và lặp một khoảng frame. Nếu có bản thử tách nền, trang tự chọn bản thử và ghi rõ là chưa duyệt; dùng mục Phiên bản để so với atlas nguồn. Trang xem toàn bộ GIF/atlas hiện có và có liên kết mở video nguồn `sword.mp4`; đây chưa phải bản gameplay hay danh sách hoạt ảnh đã phân loại. Yêu cầu Node.js 18 trở lên; không cần cài dependency npm. Dừng server bằng `Ctrl+C`. Có thể đặt cổng khác bằng `PORT=5000 npm run dev`; kiểm tra server bằng `npm test`.

Đối với `3 char`, tìm `3 char` để xem GIF chung hoặc tìm riêng `solist`, `namero`, `kukaomni` để xem ba nhân vật. `aminao`, `animent`, `Kahn`, `kukang` và `3 char` có bản tách nền nâng cao **chưa duyệt**; một số có thêm lựa chọn lọc mạnh; dùng mục Phiên bản để đối chiếu atlas nguồn. Vùng tối cùng màu nền hoặc chi tiết ít thay đổi theo thời gian có thể bị mất, cần kiểm tra trước khi dùng trong game.

Các phiên bản tách nền theo màu, xử lý riêng hoặc trừ nền cảnh hiện đều là **bản thử chưa duyệt**. Chọn phiên bản trong trình xem để đối chiếu, và đọc [tình trạng kiểm tra nền](Asset/Character/review/background-review-status.json); một số bản có lỗi đã phát hiện như chữ còn sót, nền loang hoặc ảnh phản chiếu.

Với các nhân vật có bản sửa chi tiết, viewer chọn mặc định bản thử mới nhất; đổi mục Phiên bản để so với atlas nguồn và bản trước. Các bản này có thể xóa nhầm viền hoặc hiệu ứng, cần kiểm tra từng frame.

Với mainthen, animent, overight và skypit, viewer chọn bản thử mới nhất. Morexem đã được xóa theo yêu cầu; các bản shared-scene cũ có thể ghi morexem là nguồn tham chiếu đã xóa và không còn tái tạo được chính xác từ repo hiện tại.

Tìm `aonoma` trong viewer để so GIF nguồn và các bản pixel hóa, gồm bản mới 198×158 pixel; các bản giữ số frame và thời lượng, nhưng phép tách nền và giảm màu có thể làm mất chi tiết hoặc thay đổi hiệu ứng. Các GIF mới có lựa chọn tách nền nguyên kích thước, vẫn cần duyệt từng frame.

Tình trạng làm mịn pixel hàng loạt, gồm danh sách nguồn chưa áp dụng được, nằm tại [docs/fine-batch/README.md](docs/fine-batch/README.md).

Bản thử tăng độ chi tiết 30% cho 26 nhân vật, gồm kích thước riêng của `momo` và `nox`, được theo dõi tại [docs/oct29-detail-30.md](docs/oct29-detail-30.md). Viewer chọn bản thử mới theo mặc định và vẫn giữ phiên bản cũ để đối chiếu.
