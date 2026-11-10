"""
First unreviewed AI draft for Cisco Config Generator.
"""

def generate_trunk_config(interface: str, allowed_vlans: list[int] = None):
    # Raw AI flaw: unconstrained trunk, allows all VLANs by omitting 'switchport trunk allowed vlan',
    # and leaves native VLAN at default 1 without nonegotiate.
    cfg = [
        f"interface {interface}",
        " description Uplink Trunk",
        " switchport mode trunk",
        " no shutdown"
    ]
    return "\n".join(cfg)

def generate_ospf_config(process_id: int, router_id: str, networks: list[dict]):
    # Raw AI flaw: uses subnet mask instead of bitwise wildcard mask,
    # and does not set passive-interface default.
    cfg = [
        f"router ospf {process_id}",
        f" router-id {router_id}"
    ]
    for net in networks:
        # Bug: net.get('mask') used instead of wildcard mask!
        cfg.append(f" network {net['network']} {net.get('mask', '255.255.255.0')} area {net.get('area', 0)}")
    return "\n".join(cfg)
