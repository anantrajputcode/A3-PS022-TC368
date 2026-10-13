#!/usr/bin/env python3
"""Capped synthetic DNS-shaped workload for authorized private lab networks only."""
import argparse,ipaddress,random,socket,struct,time
MAX_PPS=500;MAX_DURATION=60
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',required=True);p.add_argument('--pattern',choices=('steady','burst','multi-source'),required=True);p.add_argument('--duration',type=int,default=10);p.add_argument('--pps',type=int,default=100);p.add_argument('--confirm-private-lab',action='store_true');a=p.parse_args()
 try:ip=ipaddress.ip_address(a.target)
 except ValueError:p.error('target must be private IPv4')
 if ip.version!=4 or not ip.is_private:p.error('target must be private IPv4')
 if not a.confirm_private_lab:p.error('confirm authorization/isolation with --confirm-private-lab')
 if not 1<=a.pps<=MAX_PPS or not 1<=a.duration<=MAX_DURATION:p.error(f'pps 1..{MAX_PPS}; duration 1..{MAX_DURATION}')
 data=lambda:struct.pack('!HHHHHH',random.randrange(65536),0x0100,1,0,0,0)+b'\x00'+struct.pack('!HH',1,1)
 sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);sent=0;start=time.monotonic();end=start+a.duration
 try:
  while time.monotonic()<end:
   now=time.monotonic()
   if a.pattern=='burst' and (now-start)%1>=.5:time.sleep(min(.01,max(0,end-now)));continue
   sock.sendto(data(),(str(ip),53));sent+=1;time.sleep(1/a.pps)
 except KeyboardInterrupt:print('Interrupted')
 finally:sock.close()
 elapsed=time.monotonic()-start;print(f'Pattern={a.pattern}; attempted={sent}; elapsed={elapsed:.2f}s; average_attempted_pps={sent/max(elapsed,.001):.1f}')
 if a.pattern=='multi-source':print('No source spoofing is used; run from multiple authorized lab hosts for genuine source diversity.')
if __name__=='__main__':main()
