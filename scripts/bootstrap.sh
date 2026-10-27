#!/usr/bin/env bash
set -e

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$WORKSPACE_DIR/.bin"

echo "=========================================================="
echo "  🚀 GODWAR: TỰ ĐỘNG KHỞI TẠO PIPELINE ANDROID & GODOT 4"
echo "=========================================================="

mkdir -p "$BIN_DIR" "$HOME/.local/bin"

# 1. Cài đặt Godot 4.3 Headless nếu chưa có
if [ ! -f "$BIN_DIR/godot" ]; then
    echo "-> [1/5] Đang tải Godot 4.3 Headless cho Linux..."
    curl -sL -o "$BIN_DIR/godot.zip" https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_linux.x86_64.zip
    unzip -q "$BIN_DIR/godot.zip" -d "$BIN_DIR/"
    mv "$BIN_DIR/Godot_v4.3-stable_linux.x86_64" "$BIN_DIR/godot"
    chmod +x "$BIN_DIR/godot"
    rm -f "$BIN_DIR/godot.zip"
fi
ln -sf "$BIN_DIR/godot" "$HOME/.local/bin/godot"
echo "   ✅ Godot 4.3 Headless: $(godot --headless --version 2>/dev/null)"

# 2. Cài đặt Android Platform-Tools (adb) nếu chưa có
if [ ! -f "$BIN_DIR/platform-tools/adb" ]; then
    echo "-> [2/5] Đang tải Android Platform Tools (adb)..."
    curl -sL -o "$BIN_DIR/platform-tools.zip" https://dl.google.com/android/repository/platform-tools-latest-linux.zip
    unzip -q "$BIN_DIR/platform-tools.zip" -d "$BIN_DIR/"
    rm -f "$BIN_DIR/platform-tools.zip"
fi
ln -sf "$BIN_DIR/platform-tools/adb" "$HOME/.local/bin/adb"
echo "   ✅ ADB Command-Line: $(adb --version | head -n 1)"

# 3. Tạo Android Debug Keystore nếu chưa có
if [ ! -f "$BIN_DIR/debug.keystore" ]; then
    echo "-> [3/5] Khởi tạo Android Debug Keystore..."
    keytool -keyalg RSA -genkeypair -alias androiddebugkey -keypass android -keystore "$BIN_DIR/debug.keystore" -storepass android -dname "CN=Android Debug,O=Android,C=US" -validity 9999 -deststoretype pkcs12
fi
mkdir -p "$HOME/.local/share/godot/keystores"
cp -f "$BIN_DIR/debug.keystore" "$HOME/.local/share/godot/keystores/debug.keystore"

# 4. Cài đặt Android SDK Build-Tools tối thiểu nếu chưa có
if [ ! -d "$BIN_DIR/android-sdk/build-tools/34.0.0" ]; then
    echo "-> [4/5] Thiết lập Android SDK Build-Tools..."
    mkdir -p "$BIN_DIR/android-sdk/cmdline-tools"
    curl -sL -o "$BIN_DIR/cmdline-tools.zip" https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
    unzip -q "$BIN_DIR/cmdline-tools.zip" -d "$BIN_DIR/android-sdk/cmdline-tools/"
    rm -f "$BIN_DIR/cmdline-tools.zip"
    mv "$BIN_DIR/android-sdk/cmdline-tools/cmdline-tools" "$BIN_DIR/android-sdk/cmdline-tools/latest"
    ln -sf "$BIN_DIR/platform-tools" "$BIN_DIR/android-sdk/platform-tools"
    yes | "$BIN_DIR/android-sdk/cmdline-tools/latest/bin/sdkmanager" --sdk_root="$BIN_DIR/android-sdk" "platforms;android-34" "build-tools;34.0.0" >/dev/null 2>&1
fi

# Cấu hình Godot Editor Settings
mkdir -p "$HOME/.config/godot"
if [ -f "$HOME/.config/godot/editor_settings-4.3.tres" ]; then
    sed -i "s|export/android/android_sdk_path = \".*\"|export/android/android_sdk_path = \"$BIN_DIR/android-sdk\"|g" "$HOME/.config/godot/editor_settings-4.3.tres"
fi

# 5. Cài đặt Export Templates cho Godot nếu chưa có
if [ ! -f "$HOME/.local/share/godot/export_templates/4.3.stable/android_debug.apk" ]; then
    echo "-> [5/5] Cài đặt Android Export Templates cho Godot..."
    mkdir -p "$HOME/.local/share/godot/export_templates/4.3.stable"
    curl -sL -o /tmp/templates.tpz https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_export_templates.tpz
    unzip -q /tmp/templates.tpz -d /tmp/templates/
    mv /tmp/templates/templates/* "$HOME/.local/share/godot/export_templates/4.3.stable/"
    rm -rf /tmp/templates.tpz /tmp/templates
fi

# 6. Cài đặt thư viện Python Colab & đồ họa
pip install --quiet google-colab-cli Pillow numpy opencv-python-headless

echo ""
echo "=========================================================="
echo "  🎉 PIPELINE ANDROID & GODOT 4 ĐÃ SẴN SÀNG 100%!"
echo "  • Lệnh build APK: ./scripts/build_android_apk.sh"
echo "  • Lệnh nạp Wi-Fi: ./scripts/adb_install_phone.sh <IP:PORT>"
echo "=========================================================="
