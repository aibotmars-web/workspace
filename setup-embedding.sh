#!/bin/bash
# Qwen3-Embedding-0.6B Setup Script for Docker Container

set -e

echo "🚀 Starting Qwen3-Embedding-0.6B setup..."

# 1. Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install --break-system-packages transformers accelerate sentencepiece fastapi uvicorn

# 2. Create server directory
mkdir -p /root/.openclaw/embedding-server
cd /root/.openclaw/embedding-server

# 3. Create the embedding server
cat > server.py << 'EOF'
#!/usr/bin/env python3
"""
Simple Embedding API Server using HuggingFace Transformers
Runs Qwen3-Embedding-0.6B model
"""

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel

app = FastAPI()

# Load model (CPU only - no GPU in container)
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
print(f"Loading model: {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()
print("✅ Model loaded successfully!")

class EmbedRequest(BaseModel):
    text: str

@app.post("/embed")
async def embed(request: EmbedRequest):
    """Generate embedding for input text"""
    with torch.no_grad():
        inputs = tokenizer(request.text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model(**inputs)
        # Use mean pooling
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return {"embedding": embedding, "dimension": len(embedding)}

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME}

@app.get("/v1/models")
async def models():
    return {
        "data": [{
            "id": MODEL_NAME,
            "object": "model",
            "created": 0,
            "owned_by": "huggingface"
        }]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

chmod +x server.py

# 4. Create startup script
cat > start.sh << 'EOF'
#!/bin/bash
cd /root/.openclaw/embedding-server
nohup python3 server.py > embedding.log 2>&1 &
echo $! > server.pid
echo "Server started with PID: $(cat server.pid)"
sleep 5
curl -s http://localhost:8000/health
EOF

chmod +x start.sh

echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  cd /root/.openclaw/embedding-server && bash start.sh"
echo ""
echo "To test:"
echo "  curl -X POST http://localhost:8000/embed -H 'Content-Type: application/json' -d '{\"text\": \"hello\"}'"
