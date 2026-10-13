#!/usr/bin/env bash
set -euo pipefail
nft delete table inet ps022_dns 2>/dev/null || true
echo 'Removed dedicated lab table if present.'
