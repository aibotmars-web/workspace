#!/bin/bash
# 安裝依賴
pip3 install google-api-python-client

# 執行同步
cd "$(dirname "$0")"
python3 sync_with_api.py
