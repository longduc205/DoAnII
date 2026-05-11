#!/bin/bash
curl -s -X POST 'https://api.blackbox.ai/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-4Qk5OHr9GYuUGAuuMxcNiQ' \
  -d '{"messages":[{"role":"user","content":"hello"}],"model":"blackboxai/x-ai/grok-code-fast-1:free","max_tokens":50,"stream":false}'
echo ""
