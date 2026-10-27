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
