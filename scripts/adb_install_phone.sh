#!/usr/bin/env bash
set -e

PHONE_IP="$1"
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APK_PATH="$WORKSPACE_DIR/build/GodWar-debug.apk"

if [ -z "$PHONE_IP" ]; then
    echo "=========================================================="
    echo "  📱 NẠP GAME VÀO ĐIỆN THOẠI ANDROID QUA WI-FI"
    echo "=========================================================="
    echo "Cách dùng: ./scripts/adb_install_phone.sh <IP_DIEN_THOAI:PORT>"
    echo "Ví dụ:     ./scripts/adb_install_phone.sh 192.168.1.15:5555"
    echo ""
    echo "Danh sách thiết bị kết nối hiện tại:"
    adb devices
    exit 1
fi

if [ ! -f "$APK_PATH" ]; then
    echo "-> Chưa có file APK, tiến hành build trước..."
    "$WORKSPACE_DIR/scripts/build_android_apk.sh"
fi

echo "-> Đang kết nối tới điện thoại $PHONE_IP qua Wi-Fi..."
adb connect "$PHONE_IP"

echo "-> Đang nạp file APK vào điện thoại..."
adb install -r "$APK_PATH"

echo "-> Tự động khởi chạy game GodWar trên màn hình điện thoại..."
adb shell monkey -p com.godwar.game -c android.intent.category.LAUNCHER 1

echo ""
echo "=========================================================="
echo "  ✅ HOÀN TẤT! Game đã tự động bật sáng trên điện thoại."
echo "  💡 Bạn có thể xem log thời gian thực bằng: adb logcat -s Godot:V"
echo "=========================================================="
