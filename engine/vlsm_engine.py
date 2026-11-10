"""
First unreviewed AI draft for VLSM Engine.
"""
import math
from engine.errors import AddressSpaceExhaustedError, InvalidParameterError
from engine.addr import ip_to_int, int_to_ip, parse_cidr

def calculate_vlsm(root_cidr: str, subnets_req: list[dict], allow_rfc3021: bool = False):
    root_ip, root_prefix, _ = parse_cidr(root_cidr)
    root_size = 1 << (32 - root_prefix)
    root_end = root_ip + root_size

    # Sort descending
    sorted_req = sorted(subnets_req, key=lambda s: s["hosts"], reverse=True)
    
    cursor = root_ip
    allocated = []
    
    for item in sorted_req:
        name = item["name"]
        hosts = item["hosts"]
        
        # Raw AI implementation:
        need = hosts + 2
        prefix = 32 - math.ceil(math.log2(need))
        size = 1 << (32 - prefix)
        
        # Align cursor
        start = (cursor + size - 1) & ~(size - 1)
        end = start + size
        
        if end > root_end:
            raise AddressSpaceExhaustedError("Root address space exhausted")
            
        mask = (0xFFFFFFFF << (32 - prefix)) # Raw AI flaw: missing & 0xFFFFFFFF
        wildcard = ~mask # Raw AI flaw: missing & 0xFFFFFFFF yields negative integer in Python!
        
        network_ip = start
        broadcast_ip = end - 1
        first_host = network_ip + 1
        last_host = broadcast_ip - 1 # Raw AI flaw: wrong for /31 or /32
        gateway = first_host
        
        allocated.append({
            "name": name,
            "requested_hosts": hosts,
            "prefix": prefix,
            "network": int_to_ip(network_ip),
            "mask": int_to_ip(mask),
            "wildcard": int_to_ip(wildcard), # Will crash or output negative IP!
            "first_host": int_to_ip(first_host),
            "last_host": int_to_ip(last_host),
            "broadcast": int_to_ip(broadcast_ip),
            "gateway": int_to_ip(gateway)
        })
        
        cursor = end
        
    return allocated
