# Architectural Decision & Rationale Report: Metro MAN Profile (Tri-Site Metropolitan Ring)
Generated algorithmically by **NetArchitect Explainable Decision Engine**.

## Executive Summary
This report documents all deterministic design choices, mathematical boundary calculations, and standard protocol justifications applied during automated network synthesis.

---
## Formal Architectural Decision Records (ADRs)

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF with 10GBASE-ER SFP+ (1550 nm)`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-ER*
- **Engineering Reasoning**: Selected OS2 Single-Mode Fiber because link distance (15.0 km) exceeds the 400 m attenuation limit of OM4 Multimode Fiber. Transceiver 10GBASE-ER (1550 nm) provides a 10.9 dB optical budget. Calculated span loss: 4.35 dB (Fiber: 3.75 dB, 2 Connectors: 0.6 dB), leaving a safe operating power margin of 6.55 dB (typical datasheet values). Optical loss: 4.35 dB, Budget: 10.9 dB, Margin: 6.55 dB.
- **Inputs Used**: distance=15.0 km, link=Link

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF with 10GBASE-ER SFP+ (1550 nm)`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-ER*
- **Engineering Reasoning**: Selected OS2 Single-Mode Fiber because link distance (35.0 km) exceeds the 400 m attenuation limit of OM4 Multimode Fiber. Transceiver 10GBASE-ER (1550 nm) provides a 10.9 dB optical budget. Calculated span loss: 9.35 dB (Fiber: 8.75 dB, 2 Connectors: 0.6 dB), leaving a safe operating power margin of 1.55 dB (typical datasheet values). Optical loss: 9.35 dB, Budget: 10.9 dB, Margin: 1.55 dB.
- **Inputs Used**: distance=35.0 km, link=Link

### Decision: Physical Layer Media (Link)
- **Selected Solution**: `OS2 SMF with 10GBASE-ER SFP+ (1550 nm)`
- **Condition Triggered**: Distance > 400m (OS2 SMF required)
- **Standard / Mathematical Basis**: *IEEE 802.3ae 10GBASE-ER*
- **Engineering Reasoning**: Selected OS2 Single-Mode Fiber because link distance (22.0 km) exceeds the 400 m attenuation limit of OM4 Multimode Fiber. Transceiver 10GBASE-ER (1550 nm) provides a 10.9 dB optical budget. Calculated span loss: 6.10 dB (Fiber: 5.50 dB, 2 Connectors: 0.6 dB), leaving a safe operating power margin of 4.80 dB (typical datasheet values). Optical loss: 6.1 dB, Budget: 10.9 dB, Margin: 4.8 dB.
- **Inputs Used**: distance=22.0 km, link=Link

### Decision: Subnet Prefix Sizing: HQ-Users
- **Selected Solution**: `172.16.0.0/23 (Mask: 255.255.254.0, Wildcard: 0.0.1.255)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(300+2)) = /23
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'HQ-Users', 300 endpoints required. Sizing arithmetic: 300 hosts + 2 = 302 -> 512 = 2^9 -> /23. Block capacity: 512 addresses (510 usable). Allocation efficiency: 58.6%.
- **Inputs Used**: requested_hosts=300, allocated_block_size=512

### Decision: Subnet Prefix Sizing: REM1-Users
- **Selected Solution**: `172.16.2.0/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(80+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'REM1-Users', 80 endpoints required. Sizing arithmetic: 80 hosts + 2 = 82 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 62.5%.
- **Inputs Used**: requested_hosts=80, allocated_block_size=128

### Decision: Subnet Prefix Sizing: REM2-Users
- **Selected Solution**: `172.16.2.128/25 (Mask: 255.255.255.128, Wildcard: 0.0.0.127)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(70+2)) = /25
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'REM2-Users', 70 endpoints required. Sizing arithmetic: 70 hosts + 2 = 72 -> 128 = 2^7 -> /25. Block capacity: 128 addresses (126 usable). Allocation efficiency: 54.7%.
- **Inputs Used**: requested_hosts=70, allocated_block_size=128

### Decision: Subnet Prefix Sizing: HQ-Servers
- **Selected Solution**: `172.16.3.0/26 (Mask: 255.255.255.192, Wildcard: 0.0.0.63)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(60+2)) = /26
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'HQ-Servers', 60 endpoints required. Sizing arithmetic: 60 hosts + 2 = 62 -> 64 = 2^6 -> /26. Block capacity: 64 addresses (62 usable). Allocation efficiency: 93.8%.
- **Inputs Used**: requested_hosts=60, allocated_block_size=64

### Decision: Subnet Prefix Sizing: FinTech-Colo
- **Selected Solution**: `172.16.3.64/26 (Mask: 255.255.255.192, Wildcard: 0.0.0.63)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(60+2)) = /26
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'FinTech-Colo', 60 endpoints required. Sizing arithmetic: 60 hosts + 2 = 62 -> 64 = 2^6 -> /26. Block capacity: 64 addresses (62 usable). Allocation efficiency: 93.8%.
- **Inputs Used**: requested_hosts=60, allocated_block_size=64

### Decision: Subnet Prefix Sizing: HQ-Mgmt
- **Selected Solution**: `172.16.3.128/27 (Mask: 255.255.255.224, Wildcard: 0.0.0.31)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(20+2)) = /27
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'HQ-Mgmt', 20 endpoints required. Sizing arithmetic: 20 hosts + 2 = 22 -> 32 = 2^5 -> /27. Block capacity: 32 addresses (30 usable). Allocation efficiency: 62.5%.
- **Inputs Used**: requested_hosts=20, allocated_block_size=32

### Decision: Subnet Prefix Sizing: P2P-HQ-REM1
- **Selected Solution**: `172.16.3.160/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-HQ-REM1', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-HQ-REM2
- **Selected Solution**: `172.16.3.164/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-HQ-REM2', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Subnet Prefix Sizing: P2P-REM1-REM2
- **Selected Solution**: `172.16.3.168/30 (Mask: 255.255.255.252, Wildcard: 0.0.0.3)`
- **Condition Triggered**: need = hosts + 2 -> 32 - ceil(log2(2+2)) = /30
- **Standard / Mathematical Basis**: *RFC 1878 / RFC 4632 Variable Length Subnet Masking*
- **Engineering Reasoning**: For subnet 'P2P-REM1-REM2', 2 endpoints required. Sizing arithmetic: 2 hosts + 2 = 4 -> 4 = 2^2 -> /30. Block capacity: 4 addresses (2 usable). Allocation efficiency: 50.0%.
- **Inputs Used**: requested_hosts=2, allocated_block_size=4

### Decision: Layer 2 VLAN Segmentation Structure
- **Selected Solution**: `802.1Q Segregated Broadcast Domains (6 active VLANs)`
- **Condition Triggered**: Multi-department / Multi-functional enterprise campus endpoint segregation
- **Standard / Mathematical Basis**: *IEEE 802.1Q Tagged Frame Architecture*
- **Engineering Reasoning**: Configured discrete 802.1Q VLANs: VLAN 10 (HQ-Users), VLAN 20 (REM1-Users), VLAN 30 (REM2-Users), VLAN 100 (HQ-Servers), VLAN 150 (FinTech-Colo), VLAN 99 (HQ-Mgmt). Prevents broadcast storms across disparate departments, isolates voice VoIP jitter from data bursts, and enforces strict Layer 3 boundary inspection at the Core SVI.
- **Inputs Used**: vlans=VLAN 10 (HQ-Users), VLAN 20 (REM1-Users), VLAN 30 (REM2-Users), VLAN 100 (HQ-Servers), VLAN 150 (FinTech-Colo), VLAN 99 (HQ-Mgmt)

### Decision: Topology Architecture Tier
- **Selected Solution**: `Two-Tier Collapsed Core (Core/Distribution combined)`
- **Condition Triggered**: Access Switches <= 4 and Endpoints < 2500 -> Collapsed Core
- **Standard / Mathematical Basis**: *Cisco Enterprise Campus 3.0 Hierarchical Design Principles*
- **Engineering Reasoning**: Selected Two-Tier Collapsed Core architecture. With 1 access switches and 596 endpoints across 1 building(s), a dedicated distribution layer is unnecessary. Collapsing Core and Distribution into high-throughput L3 switches eliminates an active forwarding hop (saving ~50 us latency), lowers hardware Capex/Opex, and simplifies STP root placement while maintaining access uplink oversubscription at 1.2:1 (well within the <=20:1 enterprise campus best-practice ceiling).
- **Inputs Used**: access_switches=1, total_endpoints=596, buildings=1, oversubscription_ratio=1.2:1

### Decision: Routing Architecture & Protocol Selection
- **Selected Solution**: `Multi-Area OSPFv2`
- **Condition Triggered**: Multi-Site / Scaling Threshold / Cloud Boundary -> Multi-Area OSPF + eBGP
- **Standard / Mathematical Basis**: *RFC 2328 (OSPFv2), RFC 4632 (Classless Inter-domain Routing & Summarization)*
- **Engineering Reasoning**: Network spans 3 site(s) with 9 subnets (multi-site topology). Multi-Area OSPF is mandatory to constrain Link-State Advertisement (LSA) flooding within area boundaries. Area Border Routers (ABRs) generate Type 3 Summary LSAs using 'area <id> range' summarization, protecting Area 0 from remote link flap SPF recalculations and shrinking routing table size.
- **Inputs Used**: site_count=3, subnet_count=9, has_cloud_vpc=False, is_multi_as=False

### Decision: Layer 2 Loop Prevention & Spanning-Tree
- **Selected Solution**: `Rapid Per-VLAN Spanning Tree Plus (Rapid-PVST+, Priority 4096)`
- **Condition Triggered**: Layer 2 switched topology requires deterministic root bridge & sub-second port convergence
- **Standard / Mathematical Basis**: *IEEE 802.1w Rapid Spanning Tree Protocol (RSTP)*
- **Engineering Reasoning**: Selected IEEE 802.1w Rapid Spanning Tree via Cisco Rapid-PVST+. Core L3 switch is explicitly pinned as root bridge with 'spanning-tree vlan 1-4094 priority 4096'. Host-facing access ports enable 'spanning-tree portfast' and 'spanning-tree bpduguard enable' to bypass listening/learning delays and shut down errant switch injections immediately.
- **Inputs Used**: protocol=rapid-pvst, core_priority=4096, access_features=portfast + bpduguard

### Decision: Topology Resiliency & Failover Latency
- **Selected Solution**: `Full N-1 Link Redundancy Verified (3/3 links reconverge within budget)`
- **Condition Triggered**: Every single-link failure preserves full graph connectivity and meets latency budget
- **Standard / Mathematical Basis**: *Graph Theory All-Pairs Shortest Path & N-1 Link Survivability*
- **Engineering Reasoning**: Simulated removing each of the 3 link(s) individually: all 3 failures reconverged without partition within the 5.0 ms design objective. Calculated worst-case latency: 0.23 ms. Note: Design latency targets are computed objectives based on standard 5 us/km optical propagation delay and 50 us/hop switching latency under uncontended bandwidth assumptions — never guaranteed under arbitrary queuing contention or carrier network congestion.
- **Inputs Used**: nodes=3, links=3, baseline_latency_ms=0.225, n_minus_1_full=True

### Decision: Quality of Service (QoS / MQC Priority Queuing)
- **Selected Solution**: `Modular QoS CLI (MQC) Low-Latency Queuing (LLQ) - 35% EF Priority Bandwidth`
- **Condition Triggered**: Real-time FinTech / Voice priority queue declared with tight latency objective
- **Standard / Mathematical Basis**: *RFC 3246 (EF PHB), RFC 4594 DiffServ Guidelines & Cisco MQC LLQ*
- **Engineering Reasoning**: Policy: MQC Low-Latency Queuing (LLQ) prioritizing FinTech Co-Lo and Voice with DSCP EF (Expedited Forwarding). Implemented class-map CM_VOIP_FINTECH matching DSCP EF (46) & CS5 (40) and policy-map PM_METRO_QOS_EGRESS granting 'priority percent 35' with class-default 'fair-queue' (WFQ) across EVPL metro links so control/low-latency frames bypass bulk queueing delay.
- **Inputs Used**: priority_subnets=1, explicit_qos=True

### Decision: Infrastructure Security & Traffic Control (Trunk & ACLs)
- **Selected Solution**: `Restricted 802.1Q Trunks + Named Extended ACLs + VTY SSH ACL + Native VLAN 999`
- **Condition Triggered**: Enterprise zero-trust perimeter & inter-VLAN/control-plane hardening
- **Standard / Mathematical Basis**: *NIST SP 800-125, IEEE 802.1Q Hardening & Cisco IOS Security BCP*
- **Engineering Reasoning**: Policy: Default Secure. Switch trunks strictly enforce 'switchport trunk allowed vlan <list>' with unused Native VLAN 999 and 'switchport nonegotiate' (disabling DTP) to eliminate VLAN hopping. Named Extended ACLs enforce wireless-to-server/management isolation with explicit final 'permit ip any any' documented, and VTY SSH access is pinned to management addresses via ACL_MGMT_VTY.
- **Inputs Used**: security_policy=Default Secure
