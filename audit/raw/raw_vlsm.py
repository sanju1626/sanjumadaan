# audit/raw/raw_vlsm.py
# Raw AI generated code before adversarial audit
import math

def calculate_vlsm(root_cidr, subnets_req):
    # Missing 32-bit bitwise mask & 0xFFFFFFFF
    # Causes ~mask in Python to return negative integers!
    sorted_req = sorted(subnets_req, key=lambda s: s["hosts"], reverse=True)
    for s in sorted_req:
        need = s["hosts"] + 2
        prefix = 32 - math.ceil(math.log2(need))
        mask = 0xFFFFFFFF << (32 - prefix)
        wildcard = ~mask # Negative integer bug in Python!
