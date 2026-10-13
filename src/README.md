# PS-022 — eBPF/XDP DNS Rate Limiting Lab

Defensive lab prototype for comparing XDP, nftables, and no-filter baselines for UDP DNS traffic, based on the supplied PS-022 brief.

**Safety:** Use only an isolated private lab network and systems you own or are authorized to test. The synthetic sender is capped at 500 packets/s and 60 seconds, and accepts only private IPv4 targets. It is not a flood tool.

## Files
- `xdp_dns_limiter.c` — bounded Ethernet/IPv4/UDP/DNS-header parsing and per-source/global token buckets.
- `load_xdp.py` — BCC loader; generic XDP by default.
- `dns_client.py` — low-rate legitimate DNS queries with CSV results.
- `traffic_gen.py` — capped steady, burst, and multi-source-pattern workload.
- `measure.py` — summarizes query success/latency and optional local CPU sample.
- `nftables/` — dedicated-table baseline scripts.
- `scripts/check_environment.sh` — dependency checks.
- `report_template.md` — report and comparison table.

## Environment
Use two Linux hosts/VMs on an isolated private network. The target needs Linux BPF support, BCC Python bindings, matching kernel headers, clang/LLVM, iproute2, nftables, and a DNS service listening on UDP/53. Package names vary by distribution.

```bash
bash scripts/check_environment.sh
ip -br link
ip -br addr
```

## Run XDP on target
From this `src/` directory, replace `enp0s8` with the lab-facing interface:

```bash
sudo python3 load_xdp.py --interface enp0s8 --mode generic --per-source-rate 30 --per-source-burst 60 --global-rate 300 --global-burst 500
```
Press Ctrl+C to detach. Native mode requires driver support.

## Compare baselines
Run each condition separately using the same duration, DNS service, legitimate workload, and offered load:
1. **No filter:** detach XDP and remove the lab nftables table.
2. **nftables:** `sudo ./nftables/apply.sh enp0s8`; remove with `sudo ./nftables/remove.sh`.
3. **XDP:** use the command above.

The nftables scripts manage only the dedicated `inet ps022_dns` table; they do not flush the whole ruleset.

## Legitimate query test (generator host)
Use a private target IP and a DNS record configured on the target:
```bash
python3 dns_client.py --target 192.168.56.10 --name lab.example --count 100 --interval 0.1 --output results.csv
python3 measure.py --csv results.csv
```

## Synthetic scenarios (generator host)
```bash
python3 traffic_gen.py --target 192.168.56.10 --pattern steady --duration 10 --pps 100 --confirm-private-lab
python3 traffic_gen.py --target 192.168.56.10 --pattern burst --duration 10 --pps 100 --confirm-private-lab
python3 traffic_gen.py --target 192.168.56.10 --pattern multi-source --duration 10 --pps 100 --confirm-private-lab
```
The generator reports attempted packets, not confirmed arrivals. It does not spoof source IPs; genuine source diversity requires multiple authorized lab hosts.

## Metrics
Record offered pps, target CPU, filter drop counters, legitimate-query success, median/p95 latency, and interface counters. Use `mpstat -P ALL 1` or `pidstat` on the target. Repeat each case at least three times and report medians.

## Limitations
IPv4 UDP only; no IPv6, TCP DNS, fragment reassembly, or full DNS semantic parsing. XDP and nftables must be tested in separate runs. This is a lab prototype, not production DDoS mitigation, and does not eliminate DNS reflection/amplification attacks.

References: https://docs.kernel.org/bpf/ · https://github.com/iovisor/bcc · https://wiki.nftables.org/
