#!/bin/bash
# Monitor embedding server setup

echo "📊 Installation Status"
echo "====================="

# Check pip packages
echo ""
echo "📦 Installed packages:"
pip3 list 2>/dev/null | grep -E "transformers|accelerate|sentencepiece|fastapi|torch" || echo "Not installed yet"

# Check model files
echo ""
echo "📁 Model cache:"
ls -la ~/.cache/huggingface/hub/ 2>/dev/null | grep qwen || echo "Model not downloaded yet"

# Check server
echo ""
echo "🌐 Server status:"
curl -s http://localhost:8000/health 2>/dev/null || echo "Server not running"

echo ""
echo "🖥️ Memory usage:"
free -h | grep Mem
