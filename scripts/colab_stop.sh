#!/usr/bin/env bash

SESSION_NAME="godwar-render"

echo "======================================================"
echo "  🛑 DỪNG PHIÊN COLAB ĐỂ TIẾT KIỆM COMPUTE UNITS"
echo "======================================================"

if colab sessions 2>/dev/null | grep -q "$SESSION_NAME"; then
    echo "-> Đang giải phóng phiên '$SESSION_NAME'..."
    colab stop -s "$SESSION_NAME"
    echo "-> Đã tắt máy ảo Colab thành công!"
else
    echo "-> Phiên '$SESSION_NAME' hiện không chạy hoặc đã được tắt trước đó."
fi
