#!/usr/bin/env python3
"""Summarize query CSV and optionally sample local CPU busy percentage."""
import argparse,csv,statistics,time
def sample():
 with open('/proc/stat') as f:v=list(map(int,f.readline().split()[1:]))
 return sum(v),v[3]+(v[4] if len(v)>4 else 0)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--csv',required=True);p.add_argument('--cpu-seconds',type=int,default=0);a=p.parse_args()
 with open(a.csv,newline='') as f:rows=list(csv.DictReader(f))
 n=len(rows);ok=sum(r['status']=='response' for r in rows);print(f'Queries: {n}; successful: {ok}; success_rate: {100*ok/n if n else 0:.1f}%')
 lat=sorted(float(r['latency_ms']) for r in rows if r.get('latency_ms'))
 if lat:print(f'Median latency={statistics.median(lat):.3f} ms; p95={lat[min(len(lat)-1,int(.95*len(lat)))]:.3f} ms; samples={len(lat)}')
 if a.cpu_seconds>0:
  t0,i0=sample();time.sleep(a.cpu_seconds);t1,i1=sample();dt=t1-t0;print(f'Local CPU busy: {100*(1-(i1-i0)/dt) if dt else 0:.1f}% over {a.cpu_seconds}s; run on target host')
if __name__=='__main__':main()
