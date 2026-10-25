# AutoResearch 失敗記錄 - 2026-05-13

## 嘗試執行的時間
- 日期：2026-05-13
- 時間：05:00 (autoresearch-overnight cron)

## 問題
### 根本原因
train.py 是專為 NVIDIA GPU + CUDA 設計的，但這台 Mac (M4 chip) 沒有 CUDA，只有 MPS (Metal Performance Shaders)。

### 具體錯誤
```
AssertionError: Torch not compiled with CUDA enabled
```

### 代碼中的 CUDA 依賴
1. `torch.cuda.get_device_capability()` - 需要 CUDA
2. Flash Attention 3 kernels - 需要 CUDA  
3. `torch.device("cuda")` - 硬編碼為 cuda
4. `torch.cuda.max_memory_allocated()` - CUDA 專用

## 嘗試的修復（失敗）
1. 使用現有 venv 的 torch 2.11.0 - 沒有 CUDA support
2. 檢查 MPS 可用：`torch.backends.mps.is_available()` = True

## 可能的解決方案
1. **修改 train.py 支援 MPS**：大幅修改以用 `torch.device('mps')` 取代 `cuda`
2. **使用 MLX**：Apple 的 ML framework for Apple Silicon
3. **在其他機器運行**：找到有 NVIDIA GPU 的機器

## 結論
本次 AutoResearch session 無法執行。需要先解決 CUDA/MPS 兼容性問題。

## branch
- autoresearch/may13 (已建立)