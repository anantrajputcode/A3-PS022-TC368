#include <uapi/linux/bpf.h>
#include <uapi/linux/if_ether.h>
#include <uapi/linux/ip.h>
#include <uapi/linux/udp.h>
#include <linux/in.h>
#include <linux/types.h>
#define DNS_PORT 53
#define DNS_HEADER_LEN 12
#define NS_PER_SEC 1000000000ULL
struct dns_header { __u16 id, flags, qdcount, ancount, nscount, arcount; };
struct bucket { __u64 last_ns, tokens; };
struct config { __u64 rate, burst; };
BPF_HASH(per_source, __u32, struct bucket, 65536);
BPF_ARRAY(global_bucket, struct bucket, 1);
BPF_ARRAY(config_map, struct config, 2);
BPF_ARRAY(stats, __u64, 4); /* candidate, pass, rate-drop, malformed */
static __always_inline void count_stat(__u32 i) { __u64 *v=stats.lookup(&i); if(v) __sync_fetch_and_add(v,1); }
static __always_inline int allow_bucket(struct bucket *b, __u64 now, __u64 rate, __u64 burst) {
 if(!b->last_ns){ b->last_ns=now; b->tokens=burst; }
 else { __u64 refill=((now-b->last_ns)*rate)/NS_PER_SEC; if(refill){ b->tokens+=refill; if(b->tokens>burst)b->tokens=burst; b->last_ns=now; } }
 if(!b->tokens)return 0; b->tokens--; return 1;
}
int xdp_dns_limiter(struct xdp_md *ctx) {
 void *data=(void *)(long)ctx->data, *end=(void *)(long)ctx->data_end;
 struct ethhdr *eth=data; if((void *)(eth+1)>end)return XDP_PASS;
 if(eth->h_proto!=__constant_htons(ETH_P_IP))return XDP_PASS;
 struct iphdr *ip=(void *)(eth+1); if((void *)(ip+1)>end)return XDP_PASS;
 if(ip->version!=4||ip->ihl<5||ip->protocol!=IPPROTO_UDP)return XDP_PASS;
 if((void *)ip+ip->ihl*4>end)return XDP_PASS;
 if(ip->frag_off & __constant_htons(0x3fff))return XDP_PASS;
 struct udphdr *udp=(void *)ip+ip->ihl*4; if((void *)(udp+1)>end)return XDP_PASS;
 if(udp->dest!=__constant_htons(DNS_PORT))return XDP_PASS;
 __u16 len=__builtin_bswap16(udp->len); if(len<sizeof(*udp)+DNS_HEADER_LEN){count_stat(3);return XDP_PASS;}
 struct dns_header *dns=(void *)(udp+1); if((void *)(dns+1)>end){count_stat(3);return XDP_PASS;}
 count_stat(0); __u32 src=ip->saddr, zero=0, pi=0, gi=1;
 struct config *pc=config_map.lookup(&pi), *gc=config_map.lookup(&gi); if(!pc||!gc)return XDP_PASS;
 __u64 now=bpf_ktime_get_ns(); struct bucket init={.last_ns=now,.tokens=pc->burst};
 struct bucket *per=per_source.lookup_or_try_init(&src,&init); if(!per)return XDP_PASS;
 struct bucket *global=global_bucket.lookup(&zero);
 if(!global){struct bucket g={.last_ns=now,.tokens=gc->burst};global_bucket.update(&zero,&g);global=global_bucket.lookup(&zero);if(!global)return XDP_PASS;}
 if(!allow_bucket(per,now,pc->rate,pc->burst)||!allow_bucket(global,now,gc->rate,gc->burst)){count_stat(2);return XDP_DROP;}
 count_stat(1); return XDP_PASS;
}
