#!/usr/bin/env bash
set -e

SESSION_NAME="godwar-render"

echo "======================================================"
echo "  📦 CÀI ĐẶT MÔI TRƯỜNG AI / RENDER TRÊN COLAB GPU"
echo "======================================================"

echo "-> Đang cài đặt transformers, datasets, peft, trl, bitsandbytes, accelerate, rembg..."
colab install -s "$SESSION_NAME" transformers datasets peft trl bitsandbytes accelerate rembg diffusers torchvision

echo ""
echo "-> Kiểm tra PyTorch và CUDA trên Colab..."
echo "import torch; print(f'CUDA is available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0)}')" | colab exec -s "$SESSION_NAME"

echo ""
echo "======================================================"
echo "  ✅ Môi trường AI & Render đã sẵn sàng!"
echo "======================================================"
