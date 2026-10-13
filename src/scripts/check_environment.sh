#!/usr/bin/env bash
set -u
echo "Kernel: $(uname -r)"
for cmd in ip nft clang python3; do command -v "$cmd" >/dev/null 2>&1 && echo "[OK] $cmd" || echo "[MISSING] $cmd"; done
[ -d "/lib/modules/$(uname -r)/build" ] && echo '[OK] kernel headers' || echo '[WARN] matching kernel headers missing'
python3 -c 'import bcc; print("[OK] BCC Python import")' 2>/dev/null || echo '[MISSING] BCC Python bindings'
