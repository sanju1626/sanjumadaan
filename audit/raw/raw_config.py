# audit/raw/raw_config.py
# Raw AI generated code before adversarial audit
def trunk_template(interface):
    # Unconstrained trunk vulnerability (omits switchport trunk allowed vlan and native vlan 999)
    return f"interface {interface}\n switchport mode trunk"

def ospf_template(network, subnet_mask):
    # Hallucinated wildcard mask using subnet mask directly
    return f"router ospf 1\n network {network} {subnet_mask} area 0"
