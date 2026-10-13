# PS-022 Lab Report

## Environment
- Date/time:
- Generator and target OS/kernel:
- Interface/driver and XDP mode:
- DNS server and lab record:
- Isolation method:

## Method
Keep target, DNS service, duration, legitimate query rate, and offered load consistent. Repeat each condition at least three times.

## Results
| Filter | Scenario | Offered pps | Target CPU % | Filter drops | Legitimate success % | Median latency ms | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|
| No filter | Steady | | | | | | |
| nftables | Steady | | | | | | |
| XDP | Steady | | | | | | |
| No filter | Burst | | | | | | |
| nftables | Burst | | | | | | |
| XDP | Burst | | | | | | |
| No filter | Multi-source | | | | | | |
| nftables | Multi-source | | | | | | |
| XDP | Multi-source | | | | | | |

## Analysis
- CPU change compared with baselines:
- Drops and legitimate-query impact:
- Repeatability and limitations:
- Did you use multiple real source hosts?

## Safety and limitations
Document bounded IPv4 parsing, absence of full DNS semantic parsing, low-rate synthetic workload, and why this prototype cannot eliminate all DNS reflection/amplification attacks.
