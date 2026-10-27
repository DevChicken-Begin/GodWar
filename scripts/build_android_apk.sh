#!/usr/bin/env bash
set -e

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$WORKSPACE_DIR/build"
OUTPUT_APK="$BUILD_DIR/GodWar-debug.apk"

mkdir -p "$BUILD_DIR"

echo "=========================================================="
echo "  📦 ĐANG ĐÓNG GÓI ANDROID APK CHO GODWAR (HEADLESS)"
echo "=========================================================="

"$WORKSPACE_DIR/.bin/godot" --headless --export-debug "Android" "$OUTPUT_APK"

echo ""
echo "=========================================================="
echo "  ✅ ĐÃ XUẤT APK THÀNH CÔNG!"
echo "  📌 File xuất ra: $OUTPUT_APK"
echo "  📊 Dung lượng: $(ls -lh "$OUTPUT_APK" | awk '{print $5}')"
echo "=========================================================="
echo "-> Bạn có thể click chuột phải vào '$OUTPUT_APK' chọn Download,"
echo "   hoặc dùng './scripts/adb_install_phone.sh <IP_điện_thoại>' để nạp qua Wi-Fi!"
