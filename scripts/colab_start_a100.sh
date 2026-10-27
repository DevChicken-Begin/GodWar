#!/usr/bin/env bash
set -e

SESSION_NAME="godwar-render"

echo "======================================================"
echo "  🚀 KẾT NỐI GOOGLE COLAB GPU A100 (DỰ ÁN GODWAR)"
echo "======================================================"

# Kiểm tra xem session đã tồn tại hay chưa
if colab sessions 2>/dev/null | grep -q "$SESSION_NAME"; then
    echo "-> Phiên '$SESSION_NAME' đã tồn tại và đang chạy!"
else
    echo "-> Đang tạo phiên mới với GPU A100..."
    if ! colab new --gpu A100 -s "$SESSION_NAME"; then
        echo "⚠️ Không thể phân bổ A100 (có thể do hết hạn mức tạm thời), chuyển sang GPU L4..."
        if ! colab new --gpu L4 -s "$SESSION_NAME"; then
            echo "⚠️ Chuyển sang GPU T4..."
            colab new --gpu T4 -s "$SESSION_NAME"
        fi
    fi
fi

echo ""
echo "-> Kiểm tra thông số GPU từ xa..."
echo "!nvidia-smi" | colab exec -s "$SESSION_NAME"

echo ""
echo "======================================================"
echo "  ✅ GPU đã sẵn sàng để render và chạy AI!"
echo "  📌 Tên session: $SESSION_NAME"
echo "  💡 Nhớ chạy 'scripts/colab_stop.sh' khi xong việc để tiết kiệm Compute Units!"
echo "======================================================"
