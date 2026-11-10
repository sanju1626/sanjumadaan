# Architectural Decision & Rationale Report: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
Generated algorithmically by **NetArchitect Explainable Decision Engine**.

## Executive Summary
This report documents all deterministic design choices, mathematical boundary calculations, and standard protocol justifications applied during automated network synthesis.

---
## Formal Architectural Decision Records (ADRs)

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF (Carrier DWDM / Transponder) with Coherent DWDM / Optical Amplified Span`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *ITU-T G.694.1 / Carrier DWDM*
- **Engineering Reasoning**: Link distance (1150.0 km) exceeds the 80 km unamplified direct-detection optical limit. Engine recommends OS2 Single-Mode Fiber over a Carrier DWDM leased wavelength or EDF-amplified span. No standard unamplified transceiver power claim is made.
- **Inputs Used**: distance=1150.0 km, link=Link
- **Warnings**: Span length 1150.0 km requires carrier-grade optical transport with inline EDFAs or ROADMs.

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF (Carrier DWDM / Transponder) with Coherent DWDM / Optical Amplified Span`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *ITU-T G.694.1 / Carrier DWDM*
- **Engineering Reasoning**: Link distance (1740.0 km) exceeds the 80 km unamplified direct-detection optical limit. Engine recommends OS2 Single-Mode Fiber over a Carrier DWDM leased wavelength or EDF-amplified span. No standard unamplified transceiver power claim is made.
- **Inputs Used**: distance=1740.0 km, link=Link
- **Warnings**: Span length 1740.0 km requires carrier-grade optical transport with inline EDFAs or ROADMs.

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF (Carrier DWDM / Transponder) with Coherent DWDM / Optical Amplified Span`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *ITU-T G.694.1 / Carrier DWDM*
- **Engineering Reasoning**: Link distance (840.0 km) exceeds the 80 km unamplified direct-detection optical limit. Engine recommends OS2 Single-Mode Fiber over a Carrier DWDM leased wavelength or EDF-amplified span. No standard unamplified transceiver power claim is made.
- **Inputs Used**: distance=840.0 km, link=Link
- **Warnings**: Span length 840.0 km requires carrier-grade optical transport with inline EDFAs or ROADMs.

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF (Carrier DWDM / Transponder) with Coherent DWDM / Optical Amplified Span`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *ITU-T G.694.1 / Carrier DWDM*
- **Engineering Reasoning**: Link distance (290.0 km) exceeds the 80 km unamplified direct-detection optical limit. Engine recommends OS2 Single-Mode Fiber over a Carrier DWDM leased wavelength or EDF-amplified span. No standard unamplified transceiver power claim is made.
- **Inputs Used**: distance=290.0 km, link=Link
- **Warnings**: Span length 290.0 km requires carrier-grade optical transport with inline EDFAs or ROADMs.

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF (Carrier DWDM / Transponder) with Coherent DWDM / Optical Amplified Span`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *ITU-T G.694.1 / Carrier DWDM*
- **Engineering Reasoning**: Link distance (1760.0 km) exceeds the 80 km unamplified direct-detection optical limit. Engine recommends OS2 Single-Mode Fiber over a Carrier DWDM leased wavelength or EDF-amplified span. No standard unamplified transceiver power claim is made.
- **Inputs Used**: distance=1760.0 km, link=Link
- **Warnings**: Span length 1760.0 km requires carrier-grade optical transport with inline EDFAs or ROADMs.

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF with 10GBASE-ER SFP+ (1550 nm)`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-ER*
- **Engineering Reasoning**: Selected OS2 Single-Mode Fiber because link distance (30.0 km) exceeds the 400 m attenuation limit of OM4 Multimode Fiber. Transceiver 10GBASE-ER (1550 nm) provides a 10.9 dB optical budget. Calculated span loss: 8.10 dB (Fiber: 7.50 dB, 2 Connectors: 0.6 dB), leaving a safe operating power margin of 2.80 dB (typical datasheet values). Optical loss: 8.1 dB, Budget: 10.9 dB, Margin: 2.8 dB.
- **Inputs Used**: distance=30.0 km, link=Link

### Decision: Subnet Prefix Sizing: DEL-IoT
- **Selected Solution**: `10.0.0.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'DEL-IoT', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: DEL-Scanners
- **Selected Solution**: `10.0.2.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(200+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'DEL-Scanners', 200 endpoints required. Sizing arithmetic: 200 hosts + 2 = 202 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 78.1%.
- **Inputs Used**: requested_hosts=200, allocated_block_size=256

### Decision: Subnet Prefix Sizing: DEL-Corp
- **Selected Solution**: `10.0.3.0/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(100+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'DEL-Corp', 100 endpoints required. Sizing arithmetic: 100 hosts + 2 = 102 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 78.1%.
- **Inputs Used**: requested_hosts=100, allocated_block_size=128

### Decision: Subnet Prefix Sizing: MUM-IoT
- **Selected Solution**: `10.0.4.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'MUM-IoT', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: MUM-Scanners
- **Selected Solution**: `10.0.6.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(200+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'MUM-Scanners', 200 endpoints required. Sizing arithmetic: 200 hosts + 2 = 202 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 78.1%.
- **Inputs Used**: requested_hosts=200, allocated_block_size=256

### Decision: Subnet Prefix Sizing: BLR-IoT
- **Selected Solution**: `10.0.8.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLR-IoT', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: BLR-Scanners
- **Selected Solution**: `10.0.10.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(200+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'BLR-Scanners', 200 endpoints required. Sizing arithmetic: 200 hosts + 2 = 202 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 78.1%.
- **Inputs Used**: requested_hosts=200, allocated_block_size=256

### Decision: Subnet Prefix Sizing: CHE-IoT
- **Selected Solution**: `10.0.12.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'CHE-IoT', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: CHE-Scanners
- **Selected Solution**: `10.0.14.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(200+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'CHE-Scanners', 200 endpoints required. Sizing arithmetic: 200 hosts + 2 = 202 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 78.1%.
- **Inputs Used**: requested_hosts=200, allocated_block_size=256

### Decision: Subnet Prefix Sizing: Cloud-VPC-Subnet
- **Selected Solution**: `10.0.16.0/24 (Mask: 255.255.255.0, Wildcard: 0.0.0.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(250+2)) = /24
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'Cloud-VPC-Subnet', 250 endpoints required. Sizing arithmetic: 250 hosts + 2 = 252 -> 256 = 2^8 -> /24. Block capacity: 256 addresses (254 usable). Allocation efficiency: 97.7%.
- **Inputs Used**: requested_hosts=250, allocated_block_size=256

### Decision: Subnet Prefix Sizing: P2P-DEL-MUM
- **Selected Solution**: `10.0.17.0/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-DEL-MUM', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-DEL-BLR
- **Selected Solution**: `10.0.17.4/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-DEL-BLR', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-MUM-BLR
- **Selected Solution**: `10.0.17.8/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-MUM-BLR', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-BLR-CHE
- **Selected Solution**: `10.0.17.12/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-BLR-CHE', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-DEL-CHE
- **Selected Solution**: `10.0.17.16/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-DEL-CHE', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-DEL-CLOUD
- **Selected Solution**: `10.0.17.32/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-DEL-CLOUD', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Layer 2 VLAN Segmentation Structure
- **Selected Solution**: `802.1Q Segregated Broadcast Domains (9 active VLANs)`
- **Condition Triggered**: Multi-department / Multi-functional enterprise campus endpoint segregation
- **Standard / Mathematical Basis**: *IEEE 802.1Q Tagged Frame Architecture*
- **Engineering Reasoning**: Configured discrete 802.1Q VLANs: VLAN 10 (DEL-IoT), VLAN 11 (DEL-Scanners), VLAN 12 (DEL-Corp), VLAN 20 (MUM-IoT), VLAN 21 (MUM-Scanners), VLAN 30 (BLR-IoT), VLAN 31 (BLR-Scanners), VLAN 40 (CHE-IoT), VLAN 41 (CHE-Scanners). Prevents broadcast storms across disparate departments, isolates voice VoIP jitter from data bursts, and enforces strict Layer 3 boundary inspection at the Core SVI.
- **Inputs Used**: vlans=VLAN 10 (DEL-IoT), VLAN 11 (DEL-Scanners), VLAN 12 (DEL-Corp), VLAN 20 (MUM-IoT), VLAN 21 (MUM-Scanners), VLAN 30 (BLR-IoT), VLAN 31 (BLR-Scanners), VLAN 40 (CHE-IoT), VLAN 41 (CHE-Scanners)

### Decision: Topology Architecture Tier
- **Selected Solution**: `Two-Tier Collapsed Core (Core/Distribution combined)`
- **Condition Triggered**: Access Switches <= 4 and Endpoints < 2500 -> Collapsed Core
- **Standard / Mathematical Basis**: *Cisco Enterprise Campus 3.0 Hierarchical Design Principles*
- **Engineering Reasoning**: Selected Two-Tier Collapsed Core architecture. With 1 access switches and 2362 endpoints across 1 building(s), a dedicated distribution layer is unnecessary. Collapsing Core and Distribution into high-throughput L3 switches eliminates an active forwarding hop (saving ~50 us latency), lowers hardware Capex/Opex, and simplifies STP root placement while maintaining access uplink oversubscription at 1.2:1 (well within the <=20:1 enterprise campus best-practice ceiling).
- **Inputs Used**: access_switches=1, total_endpoints=2362, buildings=1, oversubscription_ratio=1.2:1

### Decision: Routing Architecture & Protocol Selection
- **Selected Solution**: `Multi-Area OSPFv2 + eBGP (Exterior Border Gateway Protocol)`
- **Condition Triggered**: Multi-Site / Scaling Threshold / Cloud Boundary -> Multi-Area OSPF + eBGP
- **Standard / Mathematical Basis**: *RFC 2328 (OSPFv2), RFC 4632 (Classless Inter-domain Routing & Summarization), RFC 4271 (BGP-4), RFC 6996 (Autonomous System Number Reservation for Private Use)*
- **Engineering Reasoning**: Network spans 5 site(s) with 16 subnets (multi-site topology). Multi-Area OSPF is mandatory to constrain Link-State Advertisement (LSA) flooding within area boundaries. Area Border Routers (ABRs) generate Type 3 Summary LSAs using 'area <id> range' summarization, protecting Area 0 from remote link flap SPF recalculations and shrinking routing table size. Cloud VPC interconnect / Multi-AS boundary detected. Standard practice mandates eBGP peering (RFC 4271) using private 16-bit Autonomous System Numbers (RFC 6996: AS 64512–65534). eBGP enforces policy-based administrative route control, path-vector loop prevention (AS-Path), and strict failure domain isolation between enterprise campus/WAN and public cloud provider infrastructure.
- **Inputs Used**: site_count=5, subnet_count=16, has_cloud_vpc=True, is_multi_as=True

### Decision: Topology Resiliency & Failover Latency
- **Selected Solution**: `Partial / Single-Homed Access or Leaf Topology (5/6 redundant links)`
- **Condition Triggered**: Non-redundant single-homed links detected during N-1 link-removal sweep
- **Standard / Mathematical Basis**: *Graph Theory All-Pairs Shortest Path & N-1 Link Survivability*
- **Engineering Reasoning**: Baseline maximum shortest-path latency is 9.05 ms. N-1 check: 5 link(s) reconverge cleanly; 1 allowed single-homed leaf link(s) isolate a leaf endpoint; 0 backbone/uplink failure(s) partition the graph (none). Calculated worst-case latency: 9.05 ms. Note: Design latency targets are computed objectives based on standard 5 us/km optical propagation delay and 50 us/hop switching latency under uncontended bandwidth assumptions — never guaranteed under arbitrary queuing contention or carrier network congestion.
- **Inputs Used**: nodes=5, links=6, baseline_latency_ms=9.05, n_minus_1_full=False
- **Warnings**: Single-homed links without alternate path: R-DEL <-> CLOUD-EDGE

### Decision: Quality of Service (QoS / MQC Priority Queuing)
- **Selected Solution**: `Control-Plane / IoT Separation & DiffServ Per-Hop Baseline`
- **Condition Triggered**: Multi-service WAN traffic separating telemetry, scanners, corporate, and overlay tunnels
- **Standard / Mathematical Basis**: *RFC 3246 (EF PHB), RFC 4594 DiffServ Guidelines & Cisco MQC LLQ*
- **Engineering Reasoning**: Separate subnets isolate continuous scanner/IoT bursts from corporate traffic and BGP/OSPF control packets, prepared for DiffServ DSCP EF/AF marking across WAN GRE spans.
- **Inputs Used**: priority_subnets=0, explicit_qos=False

### Decision: Infrastructure Security & Traffic Control (Trunk & ACLs)
- **Selected Solution**: `Restricted 802.1Q Trunks + Named Extended ACLs + VTY SSH ACL + Native VLAN 999`
- **Condition Triggered**: Enterprise zero-trust perimeter & inter-VLAN/control-plane hardening
- **Standard / Mathematical Basis**: *NIST SP 800-125, IEEE 802.1Q Hardening & Cisco IOS Security BCP*
- **Engineering Reasoning**: Policy: Point-to-point GRE tunnels over WAN links with optional IPsec crypto profile; eBGP route filtering and prefix limits.. Switch trunks strictly enforce 'switchport trunk allowed vlan <list>' with unused Native VLAN 999 and 'switchport nonegotiate' (disabling DTP) to eliminate VLAN hopping. Named Extended ACLs enforce wireless-to-server/management isolation with explicit final 'permit ip any any' documented, and VTY SSH access is pinned to management addresses via ACL_MGMT_VTY.
- **Inputs Used**: security_policy=Point-to-point GRE tunnels over WAN links with optional IPsec crypto profile; eBGP route filtering and prefix limits.
