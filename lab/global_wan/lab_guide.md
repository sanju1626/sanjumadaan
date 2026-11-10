# Cisco Packet Tracer Lab Guide: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)

> [!NOTE]
> All IP plans, subnet masks, wildcard masks, interface descriptions, and verification expectations in this guide are **computed directly by the NetArchitect Engine**.
> **Never assume verified in Packet Tracer until you run the topology and confirm every checklist item below.**

---

## (a) Device Inventory, PT Models & Interface-Count Table

| Device Name | OSI Role | Packet Tracer Model | Links Used | Required Hardware / Power Modules (Verify in PT) |
| :--- | :--- | :--- | :---: | :--- |
| `R-DEL` | Delhi Hub Router & OSPF Backbone Area 0 / ABR / BGP Speaker | `2911` | 5 | Built-in 3x Gi (`Gi0/0-0/2`); needs 5 Gi ports -> add `HWIC-1GE-SFP` or `EHWIC-4ESG` (or use `Router-PT` with `PT-ROUTER-NM-1CGE`). *Verify exact slot naming in your PT version.* |
| `R-MUM` | Mumbai Regional Router (OSPF Area 1) | `2911` | 3 | Built-in 3x Gi (`Gi0/0`, `Gi0/1`, `Gi0/2`). |
| `R-BLR` | Bangalore Tech Hub Router (OSPF Area 2) | `2911` | 4 | Built-in 3x Gi (`Gi0/0-0/2`); needs 4 Gi ports -> add `HWIC-1GE-SFP` or `EHWIC-4ESG` (or use `Router-PT` with `PT-ROUTER-NM-1CGE`). *Verify exact slot naming in your PT version.* |
| `R-CHE` | Chennai Maritime Node Router (OSPF Area 3) | `2911` | 3 | Built-in 3x Gi (`Gi0/0`, `Gi0/1`, `Gi0/2`). |
| `CLOUD-EDGE` | Cloud Provider Customer Gateway (VPC Edge) | `ISR4331` | 2 | Built-in 3x Gi (`Gi0/0/0-0/0/2`); verify interface prefix (`Gi0/0/x` vs `Gi0/x`) in your PT version. |

---

## (b) Physical Cabling & Optical Media Table

*Note on `--platform pt`: 10 GbE optical trunks/WAN links are modeled using GigabitEthernet copper interfaces in Packet Tracer, with the true calculated L1 medium and optical power budget recorded in each interface `description`.*

| Link ID | Endpoint A (`Port`) | Endpoint B (`Port`) | PT Cable Type | Physical Distance | Engineered Medium & Optic | Optical Margin |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `DEL-MUM` | `R-DEL` (`GigabitEthernet0/0`) | `R-MUM` (`GigabitEthernet0/0`) | Copper Cross-Over | 1150.0 km | OS2 SMF (Carrier DWDM / Transponder) (Coherent DWDM / Optical Amplified Span) | N/A |
| `DEL-BLR` | `R-DEL` (`GigabitEthernet0/1`) | `R-BLR` (`GigabitEthernet0/0`) | Copper Cross-Over | 1740.0 km | OS2 SMF (Carrier DWDM / Transponder) (Coherent DWDM / Optical Amplified Span) | N/A |
| `MUM-BLR` | `R-MUM` (`GigabitEthernet0/1`) | `R-BLR` (`GigabitEthernet0/1`) | Copper Cross-Over | 840.0 km | OS2 SMF (Carrier DWDM / Transponder) (Coherent DWDM / Optical Amplified Span) | N/A |
| `BLR-CHE` | `R-BLR` (`GigabitEthernet0/2`) | `R-CHE` (`GigabitEthernet0/0`) | Copper Cross-Over | 290.0 km | OS2 SMF (Carrier DWDM / Transponder) (Coherent DWDM / Optical Amplified Span) | N/A |
| `DEL-CHE` | `R-DEL` (`GigabitEthernet0/2`) | `R-CHE` (`GigabitEthernet0/1`) | Copper Cross-Over | 1760.0 km | OS2 SMF (Carrier DWDM / Transponder) (Coherent DWDM / Optical Amplified Span) | N/A |
| `DEL-CLOUD` | `R-DEL` (`GigabitEthernet0/3`) | `CLOUD-EDGE` (`GigabitEthernet0/0`) | Copper Cross-Over | 30.0 km | OS2 SMF (10GBASE-ER SFP+ (1550 nm)) | 2.8 dB |

---

## (c) Bitwise-Allocated IP Addressing Plan & Test Hosts

- **Root Prefix**: `10.0.0.0/16`
- **Overall Allocation Efficiency**: `67.87%`

### Subnet & Gateway Plan

| Subnet / VLAN Name | VLAN | CIDR Block | Subnet Mask | Wildcard Mask | Default Gateway | Broadcast |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `DEL-IoT` | 10 | `10.0.0.0/23` | `255.255.254.0` | `0.0.1.255` | `10.0.0.1` | `10.0.1.255` |
| `DEL-Scanners` | 11 | `10.0.2.0/24` | `255.255.255.0` | `0.0.0.255` | `10.0.2.1` | `10.0.2.255` |
| `DEL-Corp` | 12 | `10.0.3.0/25` | `255.255.255.128` | `0.0.0.127` | `10.0.3.1` | `10.0.3.127` |
| `MUM-IoT` | 20 | `10.0.4.0/23` | `255.255.254.0` | `0.0.1.255` | `10.0.4.1` | `10.0.5.255` |
| `MUM-Scanners` | 21 | `10.0.6.0/24` | `255.255.255.0` | `0.0.0.255` | `10.0.6.1` | `10.0.6.255` |
| `BLR-IoT` | 30 | `10.0.8.0/23` | `255.255.254.0` | `0.0.1.255` | `10.0.8.1` | `10.0.9.255` |
| `BLR-Scanners` | 31 | `10.0.10.0/24` | `255.255.255.0` | `0.0.0.255` | `10.0.10.1` | `10.0.10.255` |
| `CHE-IoT` | 40 | `10.0.12.0/23` | `255.255.254.0` | `0.0.1.255` | `10.0.12.1` | `10.0.13.255` |
| `CHE-Scanners` | 41 | `10.0.14.0/24` | `255.255.255.0` | `0.0.0.255` | `10.0.14.1` | `10.0.14.255` |
| `Cloud-VPC-Subnet` | Routed P2P | `10.0.16.0/24` | `255.255.255.0` | `0.0.0.255` | `10.0.16.1` | `10.0.16.255` |
| `P2P-DEL-MUM` | Routed P2P | `10.0.17.0/30` | `255.255.255.252` | `0.0.0.3` | `10.0.17.1` | `10.0.17.3` |
| `P2P-DEL-BLR` | Routed P2P | `10.0.17.4/30` | `255.255.255.252` | `0.0.0.3` | `10.0.17.5` | `10.0.17.7` |
| `P2P-MUM-BLR` | Routed P2P | `10.0.17.8/30` | `255.255.255.252` | `0.0.0.3` | `10.0.17.9` | `10.0.17.11` |
| `P2P-BLR-CHE` | Routed P2P | `10.0.17.12/30` | `255.255.255.252` | `0.0.0.3` | `10.0.17.13` | `10.0.17.15` |
| `P2P-DEL-CHE` | Routed P2P | `10.0.17.16/30` | `255.255.255.252` | `0.0.0.3` | `10.0.17.17` | `10.0.17.19` |
| `P2P-DEL-CLOUD` | Routed P2P | `10.0.17.32/30` | `255.255.255.252` | `0.0.0.3` | `10.0.17.33` | `10.0.17.35` |

### End-Device (PC-PT / Server-PT) Static Test Plan (1–2 Hosts per Subnet)

| End-Device Hostname | Type | Target Subnet / VLAN | Static IP Address | Subnet Mask | Default Gateway | Attachment Port (Host 1) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HOST_DEL_IoT` | PC-PT | `DEL-IoT` (VLAN 10) | `10.0.0.2` | `255.255.254.0` | `10.0.0.1` | `R-DEL` (802.1Q trunk — add optional 2960 switch) |
| `HOST_DEL_IoT_2` | PC-PT | `DEL-IoT` (VLAN 10) | `10.0.0.3` | `255.255.254.0` | `10.0.0.1` | Optional extra host (switch default access port) |
| `HOST_DEL_Scanners` | PC-PT | `DEL-Scanners` (VLAN 11) | `10.0.2.2` | `255.255.255.0` | `10.0.2.1` | `R-DEL` (802.1Q trunk — add optional 2960 switch) |
| `HOST_DEL_Scanners_2` | PC-PT | `DEL-Scanners` (VLAN 11) | `10.0.2.3` | `255.255.255.0` | `10.0.2.1` | Optional extra host (switch default access port) |
| `HOST_DEL_Corp` | PC-PT | `DEL-Corp` (VLAN 12) | `10.0.3.2` | `255.255.255.128` | `10.0.3.1` | `R-DEL` (802.1Q trunk — add optional 2960 switch) |
| `HOST_DEL_Corp_2` | PC-PT | `DEL-Corp` (VLAN 12) | `10.0.3.3` | `255.255.255.128` | `10.0.3.1` | Optional extra host (switch default access port) |
| `HOST_MUM_IoT` | PC-PT | `MUM-IoT` (VLAN 20) | `10.0.4.2` | `255.255.254.0` | `10.0.4.1` | `R-MUM` (802.1Q trunk — add optional 2960 switch) |
| `HOST_MUM_IoT_2` | PC-PT | `MUM-IoT` (VLAN 20) | `10.0.4.3` | `255.255.254.0` | `10.0.4.1` | Optional extra host (switch default access port) |
| `HOST_MUM_Scanners` | PC-PT | `MUM-Scanners` (VLAN 21) | `10.0.6.2` | `255.255.255.0` | `10.0.6.1` | `R-MUM` (802.1Q trunk — add optional 2960 switch) |
| `HOST_MUM_Scanners_2` | PC-PT | `MUM-Scanners` (VLAN 21) | `10.0.6.3` | `255.255.255.0` | `10.0.6.1` | Optional extra host (switch default access port) |
| `HOST_BLR_IoT` | PC-PT | `BLR-IoT` (VLAN 30) | `10.0.8.2` | `255.255.254.0` | `10.0.8.1` | `R-BLR` (802.1Q trunk — add optional 2960 switch) |
| `HOST_BLR_IoT_2` | PC-PT | `BLR-IoT` (VLAN 30) | `10.0.8.3` | `255.255.254.0` | `10.0.8.1` | Optional extra host (switch default access port) |
| `HOST_BLR_Scanners` | PC-PT | `BLR-Scanners` (VLAN 31) | `10.0.10.2` | `255.255.255.0` | `10.0.10.1` | `R-BLR` (802.1Q trunk — add optional 2960 switch) |
| `HOST_BLR_Scanners_2` | PC-PT | `BLR-Scanners` (VLAN 31) | `10.0.10.3` | `255.255.255.0` | `10.0.10.1` | Optional extra host (switch default access port) |
| `HOST_CHE_IoT` | PC-PT | `CHE-IoT` (VLAN 40) | `10.0.12.2` | `255.255.254.0` | `10.0.12.1` | `R-CHE` (802.1Q trunk — add optional 2960 switch) |
| `HOST_CHE_IoT_2` | PC-PT | `CHE-IoT` (VLAN 40) | `10.0.12.3` | `255.255.254.0` | `10.0.12.1` | Optional extra host (switch default access port) |
| `HOST_CHE_Scanners` | PC-PT | `CHE-Scanners` (VLAN 41) | `10.0.14.2` | `255.255.255.0` | `10.0.14.1` | `R-CHE` (802.1Q trunk — add optional 2960 switch) |
| `HOST_CHE_Scanners_2` | PC-PT | `CHE-Scanners` (VLAN 41) | `10.0.14.3` | `255.255.255.0` | `10.0.14.1` | Optional extra host (switch default access port) |
| `HOST_Cloud_VPC_Subnet` | Server-PT | `Cloud-VPC-Subnet` (VLAN LAN) | `10.0.16.2` | `255.255.255.0` | `10.0.16.1` | `CLOUD-EDGE` (`GigabitEthernet0/2`, cross) |
| `HOST_Cloud_VPC_Subnet_2` | Server-PT | `Cloud-VPC-Subnet` (VLAN LAN) | `10.0.16.3` | `255.255.255.0` | `10.0.16.1` | Optional extra host (switch default access port) |

---

## (d) Per-Device Configurations in Paste Order

> [!IMPORTANT]
> Paste configurations strictly in **bottom-up OSI order**: **L2 Access Switches first -> L3 Core Switches second -> Perimeter / WAN Routers third**.
> Always verify RSA key generation (`crypto key generate rsa modulus 2048`) if SSH fails to initialize in Packet Tracer.

### Step 1: `R-DEL` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: R-DEL (Model: 2911, Role: Delhi Hub Router & OSPF Backbone Area 0 / ABR / BGP Speaker)
! Scenario: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname R-DEL
!
boot-start-marker
boot-end-marker
!
no ip domain-lookup
ip domain-name netarchitect.lab
!
! AAA & Local Administrative Security
username admin privilege 15 secret CHANGE_ME
enable secret CHANGE_ME
!
! Generate RSA 2048 key for SSH v2: (crypto key generate rsa modulus 2048)
ip ssh version 2
!
! Layer 3 Routing & Forwarding
ip cef
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to R-MUM [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1150.0 km]
 ip address 10.0.17.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description Routed Link to R-BLR [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1740.0 km]
 ip address 10.0.17.5 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description Routed Link to R-CHE [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1760.0 km]
 ip address 10.0.17.17 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/3
 description Routed Link to CLOUD-EDGE [Media: OS2 SMF, Distance: 30.0 km]
 ip address 10.0.17.33 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/4
 description Trunk to Local Site LAN Distribution
 no ip address
 no shutdown
!
interface GigabitEthernet0/4.10
 description Subinterface Gateway for DEL-IoT (VLAN 10)
 encapsulation dot1Q 10
 ip address 10.0.0.1 255.255.254.0
 no shutdown
!
interface GigabitEthernet0/4.11
 description Subinterface Gateway for DEL-Scanners (VLAN 11)
 encapsulation dot1Q 11
 ip address 10.0.2.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/4.12
 description Subinterface Gateway for DEL-Corp (VLAN 12)
 encapsulation dot1Q 12
 ip address 10.0.3.1 255.255.255.128
 no shutdown
!
! Point-to-Point Secure WAN Encapsulation -> R-MUM
interface Tunnel0
 description GRE Overlay Span to R-MUM (No-Crypto PT Mode)
 ip address 10.254.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 10.0.17.2
 no shutdown
!
! Point-to-Point Secure WAN Encapsulation -> R-BLR
interface Tunnel1
 description GRE Overlay Span to R-BLR (No-Crypto PT Mode)
 ip address 10.254.0.5 255.255.255.252
 tunnel source GigabitEthernet0/1
 tunnel destination 10.0.17.6
 no shutdown
!
! Point-to-Point Secure WAN Encapsulation -> R-CHE
interface Tunnel2
 description GRE Overlay Span to R-CHE (No-Crypto PT Mode)
 ip address 10.254.0.9 255.255.255.252
 tunnel source GigabitEthernet0/2
 tunnel destination 10.0.17.18
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.2
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface GigabitEthernet0/1
 no passive-interface GigabitEthernet0/2
 network 10.0.17.0 0.0.0.3 area 0
 network 10.0.17.4 0.0.0.3 area 0
 network 10.0.17.16 0.0.0.3 area 0
 network 10.0.0.0 0.0.1.255 area 0
 network 10.0.2.0 0.0.0.255 area 0
 network 10.0.3.0 0.0.0.127 area 0
! ABR Inter-Area Route Summarization (RFC 4632 Classless Summary)
 area 1 range 10.0.4.0 255.255.252.0
 area 2 range 10.0.8.0 255.255.252.0
 area 3 range 10.0.12.0 255.255.252.0
!
! Exterior Border Gateway Protocol: eBGP (RFC 4271 / RFC 6996 Private ASN)
router bgp 65001
 bgp router-id 192.168.255.1
 bgp log-neighbor-changes
 neighbor 10.0.17.34 remote-as 65010
 neighbor 10.0.17.34 description eBGP Peering to Cloud VPC
 network 10.0.0.0 mask 255.255.0.0
!
! Discard Route to Null0 to satisfy BGP network synchronization
ip route 10.0.0.0 255.255.0.0 Null0 250
!
!
! Line Console & VTY Control Plane Protection
line con 0
 exec-timeout 10 0
 logging synchronous
 login local
line aux 0
line vty 0 4
 exec-timeout 10 0
 logging synchronous
 login local
 transport input ssh
line vty 5 15
 transport input none
!
end
write memory
```

### Step 2: `R-MUM` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: R-MUM (Model: 2911, Role: Mumbai Regional Router (OSPF Area 1))
! Scenario: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname R-MUM
!
boot-start-marker
boot-end-marker
!
no ip domain-lookup
ip domain-name netarchitect.lab
!
! AAA & Local Administrative Security
username admin privilege 15 secret CHANGE_ME
enable secret CHANGE_ME
!
! Generate RSA 2048 key for SSH v2: (crypto key generate rsa modulus 2048)
ip ssh version 2
!
! Layer 3 Routing & Forwarding
ip cef
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to R-DEL [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1150.0 km]
 ip address 10.0.17.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description Routed Link to R-BLR [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 840.0 km]
 ip address 10.0.17.9 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description Trunk to Local Site LAN Distribution
 no ip address
 no shutdown
!
interface GigabitEthernet0/2.20
 description Subinterface Gateway for MUM-IoT (VLAN 20)
 encapsulation dot1Q 20
 ip address 10.0.4.1 255.255.254.0
 no shutdown
!
interface GigabitEthernet0/2.21
 description Subinterface Gateway for MUM-Scanners (VLAN 21)
 encapsulation dot1Q 21
 ip address 10.0.6.1 255.255.255.0
 no shutdown
!
! Point-to-Point Secure WAN Encapsulation -> R-DEL
interface Tunnel0
 description GRE Overlay Span to R-DEL (No-Crypto PT Mode)
 ip address 10.254.0.2 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 10.0.17.1
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.3
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface GigabitEthernet0/1
 network 10.0.17.0 0.0.0.3 area 1
 network 10.0.17.8 0.0.0.3 area 1
 network 10.0.4.0 0.0.1.255 area 1
 network 10.0.6.0 0.0.0.255 area 1
!
!
! Line Console & VTY Control Plane Protection
line con 0
 exec-timeout 10 0
 logging synchronous
 login local
line aux 0
line vty 0 4
 exec-timeout 10 0
 logging synchronous
 login local
 transport input ssh
line vty 5 15
 transport input none
!
end
write memory
```

### Step 3: `R-BLR` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: R-BLR (Model: 2911, Role: Bangalore Tech Hub Router (OSPF Area 2))
! Scenario: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname R-BLR
!
boot-start-marker
boot-end-marker
!
no ip domain-lookup
ip domain-name netarchitect.lab
!
! AAA & Local Administrative Security
username admin privilege 15 secret CHANGE_ME
enable secret CHANGE_ME
!
! Generate RSA 2048 key for SSH v2: (crypto key generate rsa modulus 2048)
ip ssh version 2
!
! Layer 3 Routing & Forwarding
ip cef
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to R-DEL [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1740.0 km]
 ip address 10.0.17.6 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description Routed Link to R-MUM [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 840.0 km]
 ip address 10.0.17.10 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description Routed Link to R-CHE [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 290.0 km]
 ip address 10.0.17.13 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/3
 description Trunk to Local Site LAN Distribution
 no ip address
 no shutdown
!
interface GigabitEthernet0/3.30
 description Subinterface Gateway for BLR-IoT (VLAN 30)
 encapsulation dot1Q 30
 ip address 10.0.8.1 255.255.254.0
 no shutdown
!
interface GigabitEthernet0/3.31
 description Subinterface Gateway for BLR-Scanners (VLAN 31)
 encapsulation dot1Q 31
 ip address 10.0.10.1 255.255.255.0
 no shutdown
!
! Point-to-Point Secure WAN Encapsulation -> R-DEL
interface Tunnel0
 description GRE Overlay Span to R-DEL (No-Crypto PT Mode)
 ip address 10.254.0.6 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 10.0.17.5
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.4
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface GigabitEthernet0/1
 no passive-interface GigabitEthernet0/2
 network 10.0.17.4 0.0.0.3 area 2
 network 10.0.17.8 0.0.0.3 area 2
 network 10.0.17.12 0.0.0.3 area 2
 network 10.0.8.0 0.0.1.255 area 2
 network 10.0.10.0 0.0.0.255 area 2
!
!
! Line Console & VTY Control Plane Protection
line con 0
 exec-timeout 10 0
 logging synchronous
 login local
line aux 0
line vty 0 4
 exec-timeout 10 0
 logging synchronous
 login local
 transport input ssh
line vty 5 15
 transport input none
!
end
write memory
```

### Step 4: `R-CHE` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: R-CHE (Model: 2911, Role: Chennai Maritime Node Router (OSPF Area 3))
! Scenario: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname R-CHE
!
boot-start-marker
boot-end-marker
!
no ip domain-lookup
ip domain-name netarchitect.lab
!
! AAA & Local Administrative Security
username admin privilege 15 secret CHANGE_ME
enable secret CHANGE_ME
!
! Generate RSA 2048 key for SSH v2: (crypto key generate rsa modulus 2048)
ip ssh version 2
!
! Layer 3 Routing & Forwarding
ip cef
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to R-BLR [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 290.0 km]
 ip address 10.0.17.14 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description Routed Link to R-DEL [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1760.0 km]
 ip address 10.0.17.18 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description Trunk to Local Site LAN Distribution
 no ip address
 no shutdown
!
interface GigabitEthernet0/2.40
 description Subinterface Gateway for CHE-IoT (VLAN 40)
 encapsulation dot1Q 40
 ip address 10.0.12.1 255.255.254.0
 no shutdown
!
interface GigabitEthernet0/2.41
 description Subinterface Gateway for CHE-Scanners (VLAN 41)
 encapsulation dot1Q 41
 ip address 10.0.14.1 255.255.255.0
 no shutdown
!
! Point-to-Point Secure WAN Encapsulation -> R-DEL
interface Tunnel0
 description GRE Overlay Span to R-DEL (No-Crypto PT Mode)
 ip address 10.254.0.10 255.255.255.252
 tunnel source GigabitEthernet0/1
 tunnel destination 10.0.17.17
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.5
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface GigabitEthernet0/1
 network 10.0.17.12 0.0.0.3 area 3
 network 10.0.17.16 0.0.0.3 area 3
 network 10.0.12.0 0.0.1.255 area 3
 network 10.0.14.0 0.0.0.255 area 3
!
!
! Line Console & VTY Control Plane Protection
line con 0
 exec-timeout 10 0
 logging synchronous
 login local
line aux 0
line vty 0 4
 exec-timeout 10 0
 logging synchronous
 login local
 transport input ssh
line vty 5 15
 transport input none
!
end
write memory
```

### Step 5: `CLOUD-EDGE` (`ISR4331` — CLOUD)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: CLOUD-EDGE (Model: ISR4331, Role: Cloud Provider Customer Gateway (VPC Edge))
! Scenario: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname CLOUD-EDGE
!
boot-start-marker
boot-end-marker
!
no ip domain-lookup
ip domain-name netarchitect.lab
!
! AAA & Local Administrative Security
username admin privilege 15 secret CHANGE_ME
enable secret CHANGE_ME
!
! Generate RSA 2048 key for SSH v2: (crypto key generate rsa modulus 2048)
ip ssh version 2
!
! Layer 3 Routing & Forwarding
ip cef
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to R-DEL [Media: OS2 SMF, Distance: 30.0 km]
 ip address 10.0.17.34 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description Local LAN Gateway for Cloud-VPC-Subnet
 ip address 10.0.16.1 255.255.255.0
 no shutdown
!
! Exterior Border Gateway Protocol: eBGP (RFC 4271 / RFC 6996 Private ASN)
router bgp 65010
 bgp router-id 192.168.255.5
 bgp log-neighbor-changes
 neighbor 10.0.17.33 remote-as 65001
 neighbor 10.0.17.33 description eBGP Peering to Enterprise Delhi Hub
 network 10.0.16.0 mask 255.255.255.0
!
! Discard Route to Null0 to satisfy BGP network synchronization
ip route 10.0.16.0 255.255.255.0 Null0 250
!
!
! Line Console & VTY Control Plane Protection
line con 0
 exec-timeout 10 0
 logging synchronous
 login local
line aux 0
line vty 0 4
 exec-timeout 10 0
 logging synchronous
 login local
 transport input ssh
line vty 5 15
 transport input none
!
end
write memory
```

---

## (e) Manual Build Steps (If Not Using PTBuilder)

1. Open **Cisco Packet Tracer** (v8.2+ recommended).
2. Drag devices onto the logical workspace matching Section (a).
   - For `3650-24PS` L3 switches: open the **Physical** tab and drag an `AC-POWER-SUPPLY` into the empty power bay until the green link lights activate.
   - For `2911` routers requiring >3 Gigabit ports: power off the router, insert an `EHWIC-4ESG` or `HWIC-1GE-SFP` module, and power back on (*verify slot numbers in your PT version*).
3. Connect all physical cables strictly per the interface mapping in Section (b).
4. Place 1–2 `PC-PT` / `Server-PT` devices per subnet and assign the static IP/Mask/Gateway from Section (c).
5. Open each device's **CLI** tab, enter `enable` -> `configure terminal`, and paste the configurations from Section (d) in the exact order shown.
6. Wait ~30 seconds (or click **Fast Forward Time** in PT) for Rapid-PVST+ and OSPF/BGP neighbor adjacencies to converge.

---

## (f) Verification Checklist & Expected Outputs

Run these exact commands on the specified devices and verify your output matches:

### 1. Interface Status (`show ip interface brief`)
- Run on **all L3 switches and routers**.
- **Expected**: Every configured GigabitEthernet interface, subinterface, and SVI (`Vlan10`, etc.) shows Status = `up`, Protocol = `up`.

### 2. VLAN Database (`show vlan brief`)
- Run on **all L2 and L3 switches**.
- **Expected**: All active VLANs (`10, 11, 12, 20, 21, 30, 31, 40, 41`) and parking VLAN `999` (`Parking_Native_Blackhole`) appear as `active`.

### 3. 802.1Q Trunk Security (`show interfaces trunk`)
- Run on **CORE-SW** and **Access Switches**.
- **Expected**: Mode = `on` (with DTP disabled), Encapsulation = `802.1q`, Native VLAN = `999`, Status = `trunking`, and **Vlans allowed on trunk** shows ONLY the explicit allowed list (never `1-4094`).

### 4. Spanning Tree Root (`show spanning-tree`)
- Run on **CORE-SW / HQ-CORE**.
- **Expected**: Protocol displays `rstp` (`rapid-pvst`), and the Core Switch displays **"This bridge is the root"** with Priority `4096` (plus SysID extension).

### 5. Dynamic Routing Table (`show ip route`)
- Run on **all L3 devices**.
- **Expected**: Connected (`C`), Local (`L`), and OSPF (`O` / `O IA`) routes exist for all remote subnets.

### 6. Multi-Area OSPF & eBGP Neighbors (`show ip ospf neighbor` & `show ip bgp summary`)
- Run `show ip ospf neighbor` on **R-DEL**: Expected state `FULL/DR` or `FULL/BDR` for `R-MUM`, `R-BLR`, and `R-CHE`.
- Run `show ip bgp summary` on **R-DEL**: Expected neighbor `AS 65010` (`CLOUD-EDGE`) in state `Established` (or numeric PfxRcd >= 1).

### 8. Link Failover & Convergence Test
- On a redundant link (e.g., `HQ-CORE` <-> `REM1-R` in Metro MAN, or `R-DEL` <-> `R-MUM` in Global WAN):
  1. Start continuous `ping -t` from branch host to HQ/Delhi server.
  2. Enter `interface <uplink>` -> `shutdown` on the primary link.
  3. Observe OSPF reconverge via the alternate ring/mesh path (`show ip route` updates automatically).
  4. Verify connectivity resumes after ~1–3 ping timeouts.
  5. Restore link with `no shutdown`.

---

## (g) Viva & Submission Screenshot Slots

Capture and save the following screenshots in your lab submission report:
- [ ] **Screenshot 1**: Full Packet Tracer logical topology showing green link triangles.
- [ ] **Screenshot 2**: `show ip interface brief` & `show vlan brief` on Core Switch.
- [ ] **Screenshot 3**: `show interfaces trunk` confirming Native VLAN 999 and explicit allowed VLANs.
- [ ] **Screenshot 4**: `show ip route` & `show ip ospf neighbor` (plus `show ip bgp summary` for WAN).
- [ ] **Screenshot 5**: Successful end-to-end `ping`/`traceroute` AND blocked ACL test (`Destination unreachable` + incremented ACL hit counters).
- [ ] **Screenshot 6**: Failover reconvergence proof after shutting down a primary ring/backbone link.

---

## (h) Troubleshooting Common Packet Tracer Issues

| Symptom | Root Cause | Resolution |
| :--- | :--- | :--- |
| Interfaces remain red (`administratively down`) | `3650-24PS` lacks power supply OR `no shutdown` missed | Insert `AC-POWER-SUPPLY` in Physical view; issue `no shutdown` on physical interface and SVIs. |
| OSPF stuck in `EXSTART` / `INIT` | Link mismatched subnet mask or passive-interface active | Verify both sides of `/30` match `255.255.255.252` and `no passive-interface <intf>` is applied. |
| Trunk drops VLAN traffic | VLAN missing from `switchport trunk allowed vlan` or VLAN not created | Run `show vlan brief` on both switches and ensure VLAN IDs exist in `vlan.dat`. |
| SSH commands rejected by PT | Hostname/domain-name or RSA key missing | Ensure `ip domain-name netarchitect.lab` and `crypto key generate rsa modulus 2048` are executed. |
| Trunk command rejected (`encapsulation dot1q`) | `3650-24PS` runs IOS-XE (dot1q-only) whereas `3560-24PS` requires explicit encap | Ignore `% Invalid input` on `3650-24PS` (`switchport mode trunk` still applies), or verify on `3560-24PS`. |
| GRE/IPsec commands fail in PT | Basic PT router image lacks crypto IPsec profile support | Re-generate configs using `--no-crypto` flag to run clean GRE over Packet Tracer. |
