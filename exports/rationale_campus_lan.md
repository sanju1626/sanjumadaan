# Architectural Decision & Rationale Report: Campus LAN Profile (Single-Site Enterprise)
Generated algorithmically by **NetArchitect Explainable Decision Engine**.

## Executive Summary
This report documents all deterministic design choices, mathematical boundary calculations, and standard protocol justifications applied during automated network synthesis.

---
## Formal Architectural Decision Records (ADRs)

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `Cat6a 10GBASE-T with 10GBASE-T RJ-45`
- **Condition Triggered**: Distance <= 100m (Copper limit)
- **Standard / Mathematical Basis**: *IEEE 802.3an*
- **Engineering Reasoning**: Selected Cat6a 10GBASE-T copper cabling because link distance (30.0 m) is within the 100 m IEEE 802.3an standard channel boundary.
- **Inputs Used**: distance=30 m, link=Link

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OM4 MMF with 10GBASE-SR SFP+ (850 nm VCSEL)`
- **Condition Triggered**: Distance 101-400m (MMF modal dispersion limit)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-SR*
- **Engineering Reasoning**: Selected OM4 Multimode Fiber (MMF 10GBASE-SR) because link distance (180.0 m) exceeds the 100 m Cat6a copper limit but remains within the 400 m OM4 modal dispersion limit at 850 nm.
- **Inputs Used**: distance=180 m, link=Link

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OM4 MMF with 10GBASE-SR SFP+ (850 nm VCSEL)`
- **Condition Triggered**: Distance 101-400m (MMF modal dispersion limit)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-SR*
- **Engineering Reasoning**: Selected OM4 Multimode Fiber (MMF 10GBASE-SR) because link distance (320.0 m) exceeds the 100 m Cat6a copper limit but remains within the 400 m OM4 modal dispersion limit at 850 nm.
- **Inputs Used**: distance=320 m, link=Link

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OM4 MMF with 10GBASE-SR SFP+ (850 nm VCSEL)`
- **Condition Triggered**: Distance 101-400m (MMF modal dispersion limit)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-SR*
- **Engineering Reasoning**: Selected OM4 Multimode Fiber (MMF 10GBASE-SR) because link distance (395.0 m) exceeds the 100 m Cat6a copper limit but remains within the 400 m OM4 modal dispersion limit at 850 nm.
- **Inputs Used**: distance=395 m, link=Link

### Decision: Subnet Prefix Sizing: BLDG-A-Data
- **Selected Solution**: `10.10.0.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-A-Data', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: BLDG-B-Data
- **Selected Solution**: `10.10.2.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-B-Data', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: BLDG-C-Data
- **Selected Solution**: `10.10.4.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(200+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-C-Data', 200 endpoints required. Sizing arithmetic: 200 hosts + 2 = 202 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 78.1%.
- **Inputs Used**: requested_hosts=200, allocated_block_size=256

### Decision: Subnet Prefix Sizing: BLDG-A-WiFi
- **Selected Solution**: `10.10.5.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(180+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-A-WiFi', 180 endpoints required. Sizing arithmetic: 180 hosts + 2 = 182 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 70.3%.
- **Inputs Used**: requested_hosts=180, allocated_block_size=256

### Decision: Subnet Prefix Sizing: BLDG-B-WiFi
- **Selected Solution**: `10.10.6.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(180+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-B-WiFi', 180 endpoints required. Sizing arithmetic: 180 hosts + 2 = 182 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 70.3%.
- **Inputs Used**: requested_hosts=180, allocated_block_size=256

### Decision: Subnet Prefix Sizing: BLDG-A-Voice
- **Selected Solution**: `10.10.7.0/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(120+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-A-Voice', 120 endpoints required. Sizing arithmetic: 120 hosts + 2 = 122 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 93.8%.
- **Inputs Used**: requested_hosts=120, allocated_block_size=128

### Decision: Subnet Prefix Sizing: BLDG-B-Voice
- **Selected Solution**: `10.10.7.128/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(120+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-B-Voice', 120 endpoints required. Sizing arithmetic: 120 hosts + 2 = 122 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 93.8%.
- **Inputs Used**: requested_hosts=120, allocated_block_size=128

### Decision: Subnet Prefix Sizing: BLDG-C-WiFi
- **Selected Solution**: `10.10.8.0/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(120+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-C-WiFi', 120 endpoints required. Sizing arithmetic: 120 hosts + 2 = 122 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 93.8%.
- **Inputs Used**: requested_hosts=120, allocated_block_size=128

### Decision: Subnet Prefix Sizing: BLDG-C-Voice
- **Selected Solution**: `10.10.8.128/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(80+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLDG-C-Voice', 80 endpoints required. Sizing arithmetic: 80 hosts + 2 = 82 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 62.5%.
- **Inputs Used**: requested_hosts=80, allocated_block_size=128

### Decision: Subnet Prefix Sizing: Servers-Farm
- **Selected Solution**: `10.10.9.0/26 (Mask: 255.255.255.192, Wildcard: 0.0.0.63)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(60+2)) = /26
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'Servers-Farm', 60 endpoints required. Sizing arithmetic: 60 hosts + 2 = 62 -> 64 = 2^6 -> /26. Block capacity: 64 addresses (62 usable). Allocation efficiency: 93.8%.
- **Inputs Used**: requested_hosts=60, allocated_block_size=64

### Decision: Subnet Prefix Sizing: HQ-Management
- **Selected Solution**: `10.10.9.64/26 (Mask: 255.255.255.192, Wildcard: 0.0.0.63)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(40+2)) = /26
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'HQ-Management', 40 endpoints required. Sizing arithmetic: 40 hosts + 2 = 42 -> 64 = 2^6 -> /26. Block capacity: 64 addresses (62 usable). Allocation efficiency: 62.5%.
- **Inputs Used**: requested_hosts=40, allocated_block_size=64

### Decision: Subnet Prefix Sizing: P2P-EDGE-CORE
- **Selected Solution**: `10.10.9.128/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-EDGE-CORE', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Layer 2 VLAN Segmentation Structure
- **Selected Solution**: `802.1Q Segregated Broadcast Domains (11 active VLANs)`
- **Condition Triggered**: Multi-department / Multi-functional enterprise campus endpoint segregation
- **Standard / Mathematical Basis**: *IEEE 802.1Q Tagged Frame Architecture*
- **Engineering Reasoning**: Configured discrete 802.1Q VLANs: VLAN 10 (BLDG-A-Data), VLAN 20 (BLDG-B-Data), VLAN 30 (BLDG-C-Data), VLAN 12 (BLDG-A-WiFi), VLAN 22 (BLDG-B-WiFi), VLAN 11 (BLDG-A-Voice), VLAN 21 (BLDG-B-Voice), VLAN 32 (BLDG-C-WiFi), VLAN 31 (BLDG-C-Voice), VLAN 100 (Servers-Farm), VLAN 99 (HQ-Management). Prevents broadcast storms across disparate departments, isolates voice VoIP jitter from data bursts, and enforces strict Layer 3 boundary inspection at the Core SVI.
- **Inputs Used**: vlans=VLAN 10 (BLDG-A-Data), VLAN 20 (BLDG-B-Data), VLAN 30 (BLDG-C-Data), VLAN 12 (BLDG-A-WiFi), VLAN 22 (BLDG-B-WiFi), VLAN 11 (BLDG-A-Voice), VLAN 21 (BLDG-B-Voice), VLAN 32 (BLDG-C-WiFi), VLAN 31 (BLDG-C-Voice), VLAN 100 (Servers-Farm), VLAN 99 (HQ-Management)

### Decision: Topology Architecture Tier
- **Selected Solution**: `Two-Tier Collapsed Core (Core/Distribution combined)`
- **Condition Triggered**: Access Switches <= 4 and Endpoints < 2500 -> Collapsed Core
- **Standard / Mathematical Basis**: *Cisco Enterprise Campus 3.0 Hierarchical Design Principles*
- **Engineering Reasoning**: Selected Two-Tier Collapsed Core architecture. With 3 access switches and 1702 endpoints across 1 building(s), a dedicated distribution layer is unnecessary. Collapsing Core and Distribution into high-throughput L3 switches eliminates an active forwarding hop (saving ~50 us latency), lowers hardware Capex/Opex, and simplifies STP root placement while maintaining access uplink oversubscription at 1.2:1 (well within the <=20:1 enterprise campus best-practice ceiling).
- **Inputs Used**: access_switches=3, total_endpoints=1702, buildings=1, oversubscription_ratio=1.2:1

### Decision: Routing Architecture & Protocol Selection
- **Selected Solution**: `Single-Area OSPFv2 (Area 0)`
- **Condition Triggered**: Single-Site <50 Subnets -> Area 0
- **Standard / Mathematical Basis**: *RFC 2328 (OSPF Version 2)*
- **Engineering Reasoning**: Network scale is single-site (1 site) with 12 subnets (< 50 threshold). A flat single-area design (Backbone Area 0) minimizes SPF CPU overhead, eliminates ABR inter-area route propagation complexity, and provides sub-second Dijkstra SPF convergence without route summarization.
- **Inputs Used**: site_count=1, subnet_count=12, has_cloud_vpc=False, is_multi_as=False

### Decision: Layer 2 Loop Prevention & Spanning-Tree
- **Selected Solution**: `Rapid Per-VLAN Spanning Tree Plus (Rapid-PVST+, Priority 4096)`
- **Condition Triggered**: Layer 2 switched topology requires deterministic root bridge & sub-second port convergence
- **Standard / Mathematical Basis**: *IEEE 802.1w Rapid Spanning Tree Protocol (RSTP)*
- **Engineering Reasoning**: Selected IEEE 802.1w Rapid Spanning Tree via Cisco Rapid-PVST+. Core L3 switch is explicitly pinned as root bridge with 'spanning-tree vlan 1-4094 priority 4096'. Host-facing access ports enable 'spanning-tree portfast' and 'spanning-tree bpduguard enable' to bypass listening/learning delays and shut down errant switch injections immediately.
- **Inputs Used**: protocol=rapid-pvst, core_priority=4096, access_features=portfast + bpduguard

### Decision: Topology Resiliency & Failover Latency
- **Selected Solution**: `Partial / Single-Homed Access or Leaf Topology (0/4 redundant links)`
- **Condition Triggered**: Non-redundant single-homed links detected during N-1 link-removal sweep
- **Standard / Mathematical Basis**: *Graph Theory All-Pairs Shortest Path & N-1 Link Survivability*
- **Engineering Reasoning**: Baseline maximum shortest-path latency is 0.1036 ms. N-1 check: 0 link(s) reconverge cleanly; 3 allowed single-homed leaf link(s) isolate a leaf endpoint; 1 backbone/uplink failure(s) partition the graph (EDGE-R1 <-> CORE-SW). Calculated worst-case latency: 0.10 ms. Note: Design latency targets are computed objectives based on standard 5 us/km optical propagation delay and 50 us/hop switching latency under uncontended bandwidth assumptions — never guaranteed under arbitrary queuing contention or carrier network congestion.
- **Inputs Used**: nodes=5, links=4, baseline_latency_ms=0.1036, n_minus_1_full=False
- **Warnings**: Single-homed links without alternate path: CORE-SW <-> BLDG-A-SW, CORE-SW <-> BLDG-B-SW, CORE-SW <-> BLDG-C-SW, EDGE-R1 <-> CORE-SW

### Decision: Quality of Service (QoS / MQC Priority Queuing)
- **Selected Solution**: `Dedicated Voice VLAN Segmentation + IEEE 802.1p / DSCP EF Edge Isolation`
- **Condition Triggered**: 3 Voice/Priority VLAN(s) detected (BLDG-A-Voice, BLDG-B-Voice, BLDG-C-Voice)
- **Standard / Mathematical Basis**: *RFC 3246 (EF PHB), RFC 4594 DiffServ Guidelines & Cisco MQC LLQ*
- **Engineering Reasoning**: VoIP traffic is segregated onto dedicated Voice VLANs separate from Workstation Data and WiFi broadcasts, preventing bulk TCP window bursts from introducing jitter on RTP voice flows.
- **Inputs Used**: priority_subnets=3, explicit_qos=False

### Decision: Infrastructure Security & Traffic Control (Trunk & ACLs)
- **Selected Solution**: `Restricted 802.1Q Trunks + Named Extended ACLs + VTY SSH ACL + Native VLAN 999`
- **Condition Triggered**: Enterprise zero-trust perimeter & inter-VLAN/control-plane hardening
- **Standard / Mathematical Basis**: *NIST SP 800-125, IEEE 802.1Q Hardening & Cisco IOS Security BCP*
- **Engineering Reasoning**: Policy: WiFi traffic isolated from Server Farm (VLAN 100) and Management (VLAN 99) via Extended ACL; NAT overload on edge.. Switch trunks strictly enforce 'switchport trunk allowed vlan <list>' with unused Native VLAN 999 and 'switchport nonegotiate' (disabling DTP) to eliminate VLAN hopping. Named Extended ACLs enforce wireless-to-server/management isolation with explicit final 'permit ip any any' documented, and VTY SSH access is pinned to management addresses via ACL_MGMT_VTY.
- **Inputs Used**: security_policy=WiFi traffic isolated from Server Farm (VLAN 100) and Management (VLAN 99) via Extended ACL; NAT overload on edge.
