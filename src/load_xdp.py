#!/usr/bin/env python3
"""Attach the BCC XDP DNS limiter; Ctrl+C detaches it."""
import argparse, ctypes, time
from bcc import BPF

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--interface',required=True); p.add_argument('--mode',choices=('generic','native'),default='generic')
 p.add_argument('--per-source-rate',type=int,default=30); p.add_argument('--per-source-burst',type=int,default=60); p.add_argument('--global-rate',type=int,default=300); p.add_argument('--global-burst',type=int,default=500); a=p.parse_args()
 if min(a.per_source_rate,a.per_source_burst,a.global_rate,a.global_burst)<=0:p.error('rates and burst sizes must be positive')
 flags=2 if a.mode=='generic' else 0; b=BPF(src_file='xdp_dns_limiter.c'); fn=b.load_func('xdp_dns_limiter',BPF.XDP); b.attach_xdp(a.interface,fn,flags)
 class Config(ctypes.Structure): _fields_=[('rate',ctypes.c_ulonglong),('burst',ctypes.c_ulonglong)]
 cfg=b['config_map']; cfg[ctypes.c_int(0)]=Config(a.per_source_rate,a.per_source_burst); cfg[ctypes.c_int(1)]=Config(a.global_rate,a.global_burst)
 print(f'Attached {a.mode} XDP to {a.interface}; Ctrl+C detaches. Counters: candidate, pass, rate-drop, malformed')
 try:
  while True:
   time.sleep(1); s=b['stats']; print(', '.join(f'{k}={s[ctypes.c_int(i)].value}' for i,k in enumerate(('candidate','pass','rate_drop','malformed'))))
 except KeyboardInterrupt: pass
 finally: b.remove_xdp(a.interface,flags); print('XDP detached.')
if __name__=='__main__': main()
