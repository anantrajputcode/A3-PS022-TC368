#!/usr/bin/env bash
set -euo pipefail
IFACE="${1:?Usage: sudo ./apply.sh <interface>}"
if nft list table inet ps022_dns >/dev/null 2>&1; then echo 'Table already exists; remove it first.'; exit 1; fi
nft add table inet ps022_dns
nft 'add chain inet ps022_dns input { type filter hook input priority -5; policy accept; }'
nft add rule inet ps022_dns input iifname "$IFACE" udp dport 53 meter dns_per_source '{ ip saddr limit rate over 30/second burst 60 packets }' counter drop
nft add rule inet ps022_dns input iifname "$IFACE" udp dport 53 limit rate over 300/second burst 500 packets counter drop
echo "Applied dedicated lab rules on $IFACE."
