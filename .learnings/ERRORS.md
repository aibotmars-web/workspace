# ERRORS.md - 錯誤記錄

## 2026-04-23
### memory_store tool not found
- **狀況**：嘗試呼叫 `memory_store` 但工具不存在
- **複查**：TOOLS.md 裡沒有 memory_store；正確的工具應該是 `memory_recall`（搜尋）和直接寫入檔案
- **預防**：不要呼叫不存在的工具，先查 TOOLS.md 確認
## 2026-04-30 - torch.mps.current_device AttributeError on Mac Mini M4

### 錯誤
訓練完成後 evaluate_bpb 階段崩潰：
```
AttributeError: module 'torch.mps' has no attribute 'current_device'
```
发生在 `prepare.py:251, get_token_bytes(device="cuda")` 调用时。

### 原因
- Mac Mini M4 没有 NVIDIA GPU，只有 Apple MPS (Metal Performance Shaders)
- prepare.py 中的 `get_token_bytes(device="cuda")` 在 MPS 机器上触发 torch.load，torch 内部调用 `torch.mps.current_device()` 但 PyTorch 的 MPS backend 没有实现这个方法

### 修復（已套用）
1. `train.py` 第 19 行後加入：
```python
if hasattr(torch.mps, 'current_device'):
    torch.mps.current_device = lambda: 0
```

2. `prepare.py` 第 27 行後加入：
```python
import torch.mps
torch.mps.current_device = lambda: 0
```

### 預防
prepare.py 的 `get_token_bytes` 硬編碼 device="cuda"，建議改為從 train.py 的 USE_MPS 變數繼承 device 選擇，或將 device 引數改為可選（MPS fallback）。

## Errors

### 2026-05-02 AutoResearch MPS Slowness
- Issue: Training gets killed after ~30 steps (time limit)
- Cause: MPS is much slower than CUDA - each step takes 10-16s
- Solution: Reduce batch size or use pre-trained model
