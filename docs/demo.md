# Demo Guide

This project can be demoed against any OpenAI-compatible endpoint. For your current MacBook setup, use the included script.

## Prerequisites

- Python 3.11+
- Project dependencies installed
- A running OpenAI-compatible backend (vLLM verified at `http://127.0.0.1:6969/v1`)
- Served model name available as `Qwen/Qwen2.5-0.5B-Instruct`

## Quick Start (MacBook + local vLLM)

From the repository root:

```bash
chmod +x scripts/demo_mac.sh
./scripts/demo_mac.sh
```

The script will:

1. Set default environment values (overridable by your shell env):
   - `OPENAI_BASE_URL=http://127.0.0.1:6969/v1`
   - `OPENAI_MODEL=Qwen/Qwen2.5-0.5B-Instruct`
   - `OPENAI_API_KEY=EMPTY`
   - `AINCORRECTOR_LOG_PATH=logs/demo_mac.jsonl`
2. Run three demo styles using the same prompt:
   - `contrarian_expert`
   - `startup_thoughtleader`
   - `bureaucratic_hex_curse`
3. Print the last 5 replay records.

## Optional Overrides

You can override defaults by exporting variables before running:

```bash
export OPENAI_BASE_URL="http://127.0.0.1:6969/v1"
export OPENAI_MODEL="Qwen/Qwen2.5-0.5B-Instruct"
export OPENAI_API_KEY="EMPTY"
export AINCORRECTOR_LOG_PATH="logs/my_demo.jsonl"
./scripts/demo_mac.sh
```

## Direct CLI Example

If you prefer manual invocation:

```bash
python -m app.main "How should I improve this Python codebase?" --style contrarian_expert
python -m app.main --replay-last 5
```

## Troubleshooting

- If replay is empty, verify that generations completed and `AINCORRECTOR_LOG_PATH` is writable.
- If completions fail, verify vLLM responds on `/v1/models` and `/v1/chat/completions`.
- For local vLLM CPU/Apple Silicon builds, ensure your environment follows the vLLM Apple CPU build guidance.
