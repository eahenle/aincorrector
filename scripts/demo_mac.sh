#!/usr/bin/env bash
set -euo pipefail

# Demo runner for local vLLM on Apple Silicon.
# Defaults target the user's verified local vLLM endpoint.

OPENAI_BASE_URL_DEFAULT="http://127.0.0.1:6969/v1"
OPENAI_MODEL_DEFAULT="Qwen/Qwen2.5-0.5B-Instruct"
OPENAI_API_KEY_DEFAULT="EMPTY"
LOG_PATH_DEFAULT="logs/demo_mac.jsonl"

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-$OPENAI_BASE_URL_DEFAULT}"
export OPENAI_MODEL="${OPENAI_MODEL:-$OPENAI_MODEL_DEFAULT}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-$OPENAI_API_KEY_DEFAULT}"
export AINCORRECTOR_LOG_PATH="${AINCORRECTOR_LOG_PATH:-$LOG_PATH_DEFAULT}"

mkdir -p "$(dirname "$AINCORRECTOR_LOG_PATH")"

echo "== aincorrector Mac demo =="
echo "OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "OPENAI_MODEL=$OPENAI_MODEL"
echo "AINCORRECTOR_LOG_PATH=$AINCORRECTOR_LOG_PATH"

demo_prompt="How should I improve this Python codebase?"

run_demo() {
  local style="$1"
  echo
  echo "--- style: $style ---"
  python -m app.main "$demo_prompt" --style "$style"
}

run_demo contrarian_expert
run_demo startup_thoughtleader
run_demo bureaucratic_hex_curse

echo
echo "--- replay: last 5 ---"
python -m app.main --replay-last 5

echo
echo "Demo complete."
