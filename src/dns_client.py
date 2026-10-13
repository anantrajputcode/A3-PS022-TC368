#!/usr/bin/env python3
"""Low-rate legitimate DNS client for private lab targets; writes per-query CSV."""
import argparse,csv,ipaddress,random,socket,struct,time
def encode_name(name):
 out=bytearray()
 for label in name.rstrip('.').split('.'):
  if not label or len(label)>63: raise ValueError('invalid DNS label')
  out.append(len(label));out.extend(label.encode('ascii'))
 out.append(0);return bytes(out)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',required=True);p.add_argument('--name',default='lab.example');p.add_argument('--count',type=int,default=100);p.add_argument('--interval',type=float,default=.1);p.add_argument('--timeout',type=float,default=1);p.add_argument('--output',default='results.csv');a=p.parse_args()
 try:ip=ipaddress.ip_address(a.target)
 except ValueError:p.error('target must be private IPv4')
 if ip.version!=4 or not ip.is_private:p.error('target must be private IPv4')
 if not 1<=a.count<=10000 or a.interval<.01 or a.timeout<=0:p.error('count 1..10000, interval >= .01, timeout > 0 required')
 rows=[]
 with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
  s.settimeout(a.timeout)
  for i in range(a.count):
   ident=random.randrange(65536);packet=struct.pack('!HHHHHH',ident,0x0100,1,0,0,0)+encode_name(a.name)+struct.pack('!HH',1,1);start=time.perf_counter();status='timeout';latency=''
   try:
    s.sendto(packet,(str(ip),53));reply,_=s.recvfrom(4096);latency=round((time.perf_counter()-start)*1000,3);status='response' if len(reply)>=12 and reply[:2]==packet[:2] else 'unexpected_response'
   except socket.timeout:pass
   rows.append((i+1,status,latency));time.sleep(a.interval)
 with open(a.output,'w',newline='') as f:w=csv.writer(f);w.writerow(('sequence','status','latency_ms'));w.writerows(rows)
 ok=sum(r[1]=='response' for r in rows);print(f'{ok}/{len(rows)} responses ({100*ok/len(rows):.1f}%). Saved {a.output}')
if __name__=='__main__':main()
