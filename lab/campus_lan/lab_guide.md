# Cisco Packet Tracer Lab Guide: Campus LAN Profile (Single-Site Enterprise)

> [!NOTE]
> All IP plans, subnet masks, wildcard masks, interface descriptions, and verification expectations in this guide are **computed directly by the NetArchitect Engine**.
> **Never assume verified in Packet Tracer until you run the topology and confirm every checklist item below.**

---

## (a) Device Inventory, PT Models & Interface-Count Table

| Device Name | OSI Role | Packet Tracer Model | Links Used | Required Hardware / Power Modules (Verify in PT) |
| :--- | :--- | :--- | :---: | :--- |
| `EDGE-R1` | Perimeter Router & NAT Gateway | `2911` | 1 | Built-in 3x Gi (`Gi0/0`, `Gi0/1`, `Gi0/2`). |
| `CORE-SW` | Collapsed Core & Distribution L3 Switch (STP Root) | `3650-24PS` | 4 | Insert `AC-POWER-SUPPLY` in PSU slot to power on (24x Gi built-in). |
| `BLDG-A-SW` | Building A Access Switch | `2960-24TT` | 1 | Built-in 24x Fa + 2x Gi (no extra module needed). |
| `BLDG-B-SW` | Building B Access Switch | `2960-24TT` | 1 | Built-in 24x Fa + 2x Gi (no extra module needed). |
| `BLDG-C-SW` | Building C Access Switch | `2960-24TT` | 1 | Built-in 24x Fa + 2x Gi (no extra module needed). |

---

## (b) Physical Cabling & Optical Media Table

*Note on `--platform pt`: 10 GbE optical trunks/WAN links are modeled using GigabitEthernet copper interfaces in Packet Tracer, with the true calculated L1 medium and optical power budget recorded in each interface `description`.*

| Link ID | Endpoint A (`Port`) | Endpoint B (`Port`) | PT Cable Type | Physical Distance | Engineered Medium & Optic | Optical Margin |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `EDGE-CORE` | `EDGE-R1` (`GigabitEthernet0/0`) | `CORE-SW` (`GigabitEthernet1/0/1`) | Copper Straight-Through | 30 m | Cat6a 10GBASE-T (10GBASE-T RJ-45) | N/A |
| `CORE-BLDG-A` | `CORE-SW` (`GigabitEthernet1/0/2`) | `BLDG-A-SW` (`GigabitEthernet0/1`) | Copper Cross-Over | 180 m | OM4 MMF (10GBASE-SR SFP+ (850 nm VCSEL)) | N/A |
| `CORE-BLDG-B` | `CORE-SW` (`GigabitEthernet1/0/3`) | `BLDG-B-SW` (`GigabitEthernet0/1`) | Copper Cross-Over | 320 m | OM4 MMF (10GBASE-SR SFP+ (850 nm VCSEL)) | N/A |
| `CORE-BLDG-C` | `CORE-SW` (`GigabitEthernet1/0/4`) | `BLDG-C-SW` (`GigabitEthernet0/1`) | Copper Cross-Over | 395 m | OM4 MMF (10GBASE-SR SFP+ (850 nm VCSEL)) | N/A |

---

## (c) Bitwise-Allocated IP Addressing Plan & Test Hosts

- **Root Prefix**: `10.10.0.0/16`
- **Overall Allocation Efficiency**: `69.87%`

### Subnet & Gateway Plan

| Subnet / VLAN Name | VLAN | CIDR Block | Subnet Mask | Wildcard Mask | Default Gateway | Broadcast |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `BLDG-A-Data` | 10 | `10.10.0.0/23` | `255.255.254.0` | `0.0.1.255` | `10.10.0.1` | `10.10.1.255` |
| `BLDG-B-Data` | 20 | `10.10.2.0/23` | `255.255.254.0` | `0.0.1.255` | `10.10.2.1` | `10.10.3.255` |
| `BLDG-C-Data` | 30 | `10.10.4.0/24` | `255.255.255.0` | `0.0.0.255` | `10.10.4.1` | `10.10.4.255` |
| `BLDG-A-WiFi` | 12 | `10.10.5.0/24` | `255.255.255.0` | `0.0.0.255` | `10.10.5.1` | `10.10.5.255` |
| `BLDG-B-WiFi` | 22 | `10.10.6.0/24` | `255.255.255.0` | `0.0.0.255` | `10.10.6.1` | `10.10.6.255` |
| `BLDG-A-Voice` | 11 | `10.10.7.0/25` | `255.255.255.128` | `0.0.0.127` | `10.10.7.1` | `10.10.7.127` |
| `BLDG-B-Voice` | 21 | `10.10.7.128/25` | `255.255.255.128` | `0.0.0.127` | `10.10.7.129` | `10.10.7.255` |
| `BLDG-C-WiFi` | 32 | `10.10.8.0/25` | `255.255.255.128` | `0.0.0.127` | `10.10.8.1` | `10.10.8.127` |
| `BLDG-C-Voice` | 31 | `10.10.8.128/25` | `255.255.255.128` | `0.0.0.127` | `10.10.8.129` | `10.10.8.255` |
| `Servers-Farm` | 100 | `10.10.9.0/26` | `255.255.255.192` | `0.0.0.63` | `10.10.9.1` | `10.10.9.63` |
| `HQ-Management` | 99 | `10.10.9.64/26` | `255.255.255.192` | `0.0.0.63` | `10.10.9.65` | `10.10.9.127` |
| `P2P-EDGE-CORE` | Routed P2P | `10.10.9.128/30` | `255.255.255.252` | `0.0.0.3` | `10.10.9.129` | `10.10.9.131` |

### End-Device (PC-PT / Server-PT) Static Test Plan (1–2 Hosts per Subnet)

| End-Device Hostname | Type | Target Subnet / VLAN | Static IP Address | Subnet Mask | Default Gateway | Attachment Port (Host 1) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HOST_BLDG_A_Data` | PC-PT | `BLDG-A-Data` (VLAN 10) | `10.10.0.2` | `255.255.254.0` | `10.10.0.1` | `BLDG-A-SW` (`FastEthernet0/1`, straight) |
| `HOST_BLDG_A_Data_2` | PC-PT | `BLDG-A-Data` (VLAN 10) | `10.10.0.3` | `255.255.254.0` | `10.10.0.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_B_Data` | PC-PT | `BLDG-B-Data` (VLAN 20) | `10.10.2.2` | `255.255.254.0` | `10.10.2.1` | `BLDG-B-SW` (`FastEthernet0/1`, straight) |
| `HOST_BLDG_B_Data_2` | PC-PT | `BLDG-B-Data` (VLAN 20) | `10.10.2.3` | `255.255.254.0` | `10.10.2.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_C_Data` | PC-PT | `BLDG-C-Data` (VLAN 30) | `10.10.4.2` | `255.255.255.0` | `10.10.4.1` | `BLDG-C-SW` (`FastEthernet0/1`, straight) |
| `HOST_BLDG_C_Data_2` | PC-PT | `BLDG-C-Data` (VLAN 30) | `10.10.4.3` | `255.255.255.0` | `10.10.4.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_A_WiFi` | PC-PT | `BLDG-A-WiFi` (VLAN 12) | `10.10.5.2` | `255.255.255.0` | `10.10.5.1` | `BLDG-A-SW` (`FastEthernet0/2`, straight) |
| `HOST_BLDG_A_WiFi_2` | PC-PT | `BLDG-A-WiFi` (VLAN 12) | `10.10.5.3` | `255.255.255.0` | `10.10.5.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_B_WiFi` | PC-PT | `BLDG-B-WiFi` (VLAN 22) | `10.10.6.2` | `255.255.255.0` | `10.10.6.1` | `BLDG-B-SW` (`FastEthernet0/2`, straight) |
| `HOST_BLDG_B_WiFi_2` | PC-PT | `BLDG-B-WiFi` (VLAN 22) | `10.10.6.3` | `255.255.255.0` | `10.10.6.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_A_Voice` | PC-PT | `BLDG-A-Voice` (VLAN 11) | `10.10.7.2` | `255.255.255.128` | `10.10.7.1` | `BLDG-A-SW` (`FastEthernet0/3`, straight) |
| `HOST_BLDG_A_Voice_2` | PC-PT | `BLDG-A-Voice` (VLAN 11) | `10.10.7.3` | `255.255.255.128` | `10.10.7.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_B_Voice` | PC-PT | `BLDG-B-Voice` (VLAN 21) | `10.10.7.130` | `255.255.255.128` | `10.10.7.129` | `BLDG-B-SW` (`FastEthernet0/3`, straight) |
| `HOST_BLDG_B_Voice_2` | PC-PT | `BLDG-B-Voice` (VLAN 21) | `10.10.7.131` | `255.255.255.128` | `10.10.7.129` | Optional extra host (switch default access port) |
| `HOST_BLDG_C_WiFi` | PC-PT | `BLDG-C-WiFi` (VLAN 32) | `10.10.8.2` | `255.255.255.128` | `10.10.8.1` | `BLDG-C-SW` (`FastEthernet0/2`, straight) |
| `HOST_BLDG_C_WiFi_2` | PC-PT | `BLDG-C-WiFi` (VLAN 32) | `10.10.8.3` | `255.255.255.128` | `10.10.8.1` | Optional extra host (switch default access port) |
| `HOST_BLDG_C_Voice` | PC-PT | `BLDG-C-Voice` (VLAN 31) | `10.10.8.130` | `255.255.255.128` | `10.10.8.129` | `BLDG-C-SW` (`FastEthernet0/3`, straight) |
| `HOST_BLDG_C_Voice_2` | PC-PT | `BLDG-C-Voice` (VLAN 31) | `10.10.8.131` | `255.255.255.128` | `10.10.8.129` | Optional extra host (switch default access port) |
| `HOST_Servers_Farm` | Server-PT | `Servers-Farm` (VLAN 100) | `10.10.9.2` | `255.255.255.192` | `10.10.9.1` | `BLDG-A-SW` (`FastEthernet0/4`, straight) |
| `HOST_Servers_Farm_2` | Server-PT | `Servers-Farm` (VLAN 100) | `10.10.9.3` | `255.255.255.192` | `10.10.9.1` | Optional extra host (switch default access port) |
| `HOST_HQ_Management` | PC-PT | `HQ-Management` (VLAN 99) | `10.10.9.66` | `255.255.255.192` | `10.10.9.65` | `BLDG-A-SW` (`FastEthernet0/5`, straight) |
| `HOST_HQ_Management_2` | PC-PT | `HQ-Management` (VLAN 99) | `10.10.9.67` | `255.255.255.192` | `10.10.9.65` | Optional extra host (switch default access port) |

---

## (d) Per-Device Configurations in Paste Order

> [!IMPORTANT]
> Paste configurations strictly in **bottom-up OSI order**: **L2 Access Switches first -> L3 Core Switches second -> Perimeter / WAN Routers third**.
> Always verify RSA key generation (`crypto key generate rsa modulus 2048`) if SSH fails to initialize in Packet Tracer.

### Step 1: `BLDG-A-SW` (`2960-24TT` — L2_SWITCH)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: BLDG-A-SW (Model: 2960-24TT, Role: Building A Access Switch)
! Scenario: Campus LAN Profile (Single-Site Enterprise)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname BLDG-A-SW
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
! Layer 2 Spanning-Tree Optimization
spanning-tree mode rapid-pvst
spanning-tree extend system-id
spanning-tree portfast default
spanning-tree portfast bpduguard default
!
! VLAN Database Definition
vlan 10
 name BLDG-A-Data
vlan 20
 name BLDG-B-Data
vlan 30
 name BLDG-C-Data
vlan 12
 name BLDG-A-WiFi
vlan 22
 name BLDG-B-WiFi
vlan 11
 name BLDG-A-Voice
vlan 21
 name BLDG-B-Voice
vlan 32
 name BLDG-C-WiFi
vlan 31
 name BLDG-C-Voice
vlan 100
 name Servers-Farm
vlan 99
 name HQ-Management
vlan 999
 name Parking_Native_Blackhole
!
! Interface Allocations & Cabling
interface GigabitEthernet0/1
 description Uplink Trunk to CORE-SW [Media: OM4 MMF, Distance: 180m]
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
!
! Access Edge Ports (Host-facing PortFast & BPDU Guard)
interface FastEthernet0/1
 description Access Port for BLDG-A-Data (VLAN 10)
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/2
 description Access Port for BLDG-A-WiFi (VLAN 12)
 switchport mode access
 switchport access vlan 12
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/3
 description Access Port for BLDG-A-Voice (VLAN 11)
 switchport mode access
 switchport access vlan 11
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/4
 description Access Port for Servers-Farm (VLAN 100)
 switchport mode access
 switchport access vlan 100
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/5
 description Access Port for HQ-Management (VLAN 99)
 switchport mode access
 switchport access vlan 99
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface range FastEthernet0/6 - 24
 description Default Access Edge Ports (Building A)
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
! Out-of-Band Management SVI
interface Vlan99
 description Management Interface for BLDG-A-SW
 ip address 10.10.9.76 255.255.255.192
 no shutdown
!
ip default-gateway 10.10.9.65
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 10.10.9.64 0.0.0.63
 deny any log
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
 access-class ACL_MGMT_VTY in
line vty 5 15
 transport input none
!
end
write memory
```

### Step 2: `BLDG-B-SW` (`2960-24TT` — L2_SWITCH)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: BLDG-B-SW (Model: 2960-24TT, Role: Building B Access Switch)
! Scenario: Campus LAN Profile (Single-Site Enterprise)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname BLDG-B-SW
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
! Layer 2 Spanning-Tree Optimization
spanning-tree mode rapid-pvst
spanning-tree extend system-id
spanning-tree portfast default
spanning-tree portfast bpduguard default
!
! VLAN Database Definition
vlan 10
 name BLDG-A-Data
vlan 20
 name BLDG-B-Data
vlan 30
 name BLDG-C-Data
vlan 12
 name BLDG-A-WiFi
vlan 22
 name BLDG-B-WiFi
vlan 11
 name BLDG-A-Voice
vlan 21
 name BLDG-B-Voice
vlan 32
 name BLDG-C-WiFi
vlan 31
 name BLDG-C-Voice
vlan 100
 name Servers-Farm
vlan 99
 name HQ-Management
vlan 999
 name Parking_Native_Blackhole
!
! Interface Allocations & Cabling
interface GigabitEthernet0/1
 description Uplink Trunk to CORE-SW [Media: OM4 MMF, Distance: 320m]
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
!
! Access Edge Ports (Host-facing PortFast & BPDU Guard)
interface FastEthernet0/1
 description Access Port for BLDG-B-Data (VLAN 20)
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/2
 description Access Port for BLDG-B-WiFi (VLAN 22)
 switchport mode access
 switchport access vlan 22
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/3
 description Access Port for BLDG-B-Voice (VLAN 21)
 switchport mode access
 switchport access vlan 21
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface range FastEthernet0/4 - 24
 description Default Access Edge Ports (Building B)
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
! Out-of-Band Management SVI
interface Vlan99
 description Management Interface for BLDG-B-SW
 ip address 10.10.9.77 255.255.255.192
 no shutdown
!
ip default-gateway 10.10.9.65
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 10.10.9.64 0.0.0.63
 deny any log
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
 access-class ACL_MGMT_VTY in
line vty 5 15
 transport input none
!
end
write memory
```

### Step 3: `BLDG-C-SW` (`2960-24TT` — L2_SWITCH)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: BLDG-C-SW (Model: 2960-24TT, Role: Building C Access Switch)
! Scenario: Campus LAN Profile (Single-Site Enterprise)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname BLDG-C-SW
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
! Layer 2 Spanning-Tree Optimization
spanning-tree mode rapid-pvst
spanning-tree extend system-id
spanning-tree portfast default
spanning-tree portfast bpduguard default
!
! VLAN Database Definition
vlan 10
 name BLDG-A-Data
vlan 20
 name BLDG-B-Data
vlan 30
 name BLDG-C-Data
vlan 12
 name BLDG-A-WiFi
vlan 22
 name BLDG-B-WiFi
vlan 11
 name BLDG-A-Voice
vlan 21
 name BLDG-B-Voice
vlan 32
 name BLDG-C-WiFi
vlan 31
 name BLDG-C-Voice
vlan 100
 name Servers-Farm
vlan 99
 name HQ-Management
vlan 999
 name Parking_Native_Blackhole
!
! Interface Allocations & Cabling
interface GigabitEthernet0/1
 description Uplink Trunk to CORE-SW [Media: OM4 MMF, Distance: 395m]
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
!
! Access Edge Ports (Host-facing PortFast & BPDU Guard)
interface FastEthernet0/1
 description Access Port for BLDG-C-Data (VLAN 30)
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/2
 description Access Port for BLDG-C-WiFi (VLAN 32)
 switchport mode access
 switchport access vlan 32
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface FastEthernet0/3
 description Access Port for BLDG-C-Voice (VLAN 31)
 switchport mode access
 switchport access vlan 31
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface range FastEthernet0/4 - 24
 description Default Access Edge Ports (Building C)
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
! Out-of-Band Management SVI
interface Vlan99
 description Management Interface for BLDG-C-SW
 ip address 10.10.9.78 255.255.255.192
 no shutdown
!
ip default-gateway 10.10.9.65
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 10.10.9.64 0.0.0.63
 deny any log
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
 access-class ACL_MGMT_VTY in
line vty 5 15
 transport input none
!
end
write memory
```

### Step 4: `CORE-SW` (`3650-24PS` — L3_SWITCH)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: CORE-SW (Model: 3650-24PS, Role: Collapsed Core & Distribution L3 Switch (STP Root))
! Scenario: Campus LAN Profile (Single-Site Enterprise)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname CORE-SW
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
! Layer 3 Switching Architecture
ip routing
ip cef
!
! Spanning-Tree Root Determinism
spanning-tree mode rapid-pvst
spanning-tree extend system-id
spanning-tree vlan 1-4094 priority 4096
!
! VLAN Database Definition
vlan 10
 name BLDG-A-Data
vlan 20
 name BLDG-B-Data
vlan 30
 name BLDG-C-Data
vlan 12
 name BLDG-A-WiFi
vlan 22
 name BLDG-B-WiFi
vlan 11
 name BLDG-A-Voice
vlan 21
 name BLDG-B-Voice
vlan 32
 name BLDG-C-WiFi
vlan 31
 name BLDG-C-Voice
vlan 100
 name Servers-Farm
vlan 99
 name HQ-Management
vlan 999
 name Parking_Native_Blackhole
!
! Physical Interfaces (Trunks & Routed P2P)
interface GigabitEthernet1/0/1
 description Routed Point-to-Point Uplink to EDGE-R1 [Media: Cat6a 10GBASE-T, Distance: 30 m]
 no switchport
 ip address 10.10.9.130 255.255.255.252
 no shutdown
!
interface GigabitEthernet1/0/2
 description Downlink Trunk to Access Switch BLDG-A-SW [Media: OM4 MMF, Distance: 180 m]
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
!
interface GigabitEthernet1/0/3
 description Downlink Trunk to Access Switch BLDG-B-SW [Media: OM4 MMF, Distance: 320 m]
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
!
interface GigabitEthernet1/0/4
 description Downlink Trunk to Access Switch BLDG-C-SW [Media: OM4 MMF, Distance: 395 m]
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
!
! Switch Virtual Interfaces (SVI Layer 3 Default Gateways)
interface Vlan10
 description SVI Default Gateway for BLDG-A-Data
 ip address 10.10.0.1 255.255.254.0
 no shutdown
!
interface Vlan20
 description SVI Default Gateway for BLDG-B-Data
 ip address 10.10.2.1 255.255.254.0
 no shutdown
!
interface Vlan30
 description SVI Default Gateway for BLDG-C-Data
 ip address 10.10.4.1 255.255.255.0
 no shutdown
!
interface Vlan12
 description SVI Default Gateway for BLDG-A-WiFi
 ip address 10.10.5.1 255.255.255.0
 ip access-group ACL_WIFI_SECURITY in
 no shutdown
!
interface Vlan22
 description SVI Default Gateway for BLDG-B-WiFi
 ip address 10.10.6.1 255.255.255.0
 ip access-group ACL_WIFI_SECURITY in
 no shutdown
!
interface Vlan11
 description SVI Default Gateway for BLDG-A-Voice
 ip address 10.10.7.1 255.255.255.128
 no shutdown
!
interface Vlan21
 description SVI Default Gateway for BLDG-B-Voice
 ip address 10.10.7.129 255.255.255.128
 no shutdown
!
interface Vlan32
 description SVI Default Gateway for BLDG-C-WiFi
 ip address 10.10.8.1 255.255.255.128
 ip access-group ACL_WIFI_SECURITY in
 no shutdown
!
interface Vlan31
 description SVI Default Gateway for BLDG-C-Voice
 ip address 10.10.8.129 255.255.255.128
 no shutdown
!
interface Vlan100
 description SVI Default Gateway for Servers-Farm
 ip address 10.10.9.1 255.255.255.192
 no shutdown
!
interface Vlan99
 description SVI Default Gateway for HQ-Management
 ip address 10.10.9.65 255.255.255.192
 no shutdown
!
! Named Extended ACL: WiFi Traffic Restriction
! Denies wireless clients access to Server Farm (VLAN 100) and Management (VLAN 99)
! Explicit permit any any retained for general campus/Internet traffic
ip access-list extended ACL_WIFI_SECURITY
 remark Deny WiFi access to Production Server Farm
 deny ip any 10.10.9.0 0.0.0.63
 deny ip any 10.10.9.64 0.0.0.63
 remark Explicit permit for remaining campus and Internet destinations
 permit ip any any
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.1
 passive-interface default
 no passive-interface GigabitEthernet1/0/1
 network 10.10.0.0 0.0.1.255 area 0
 network 10.10.2.0 0.0.1.255 area 0
 network 10.10.4.0 0.0.0.255 area 0
 network 10.10.5.0 0.0.0.255 area 0
 network 10.10.6.0 0.0.0.255 area 0
 network 10.10.7.0 0.0.0.127 area 0
 network 10.10.7.128 0.0.0.127 area 0
 network 10.10.8.0 0.0.0.127 area 0
 network 10.10.8.128 0.0.0.127 area 0
 network 10.10.9.0 0.0.0.63 area 0
 network 10.10.9.64 0.0.0.63 area 0
 network 10.10.9.128 0.0.0.3 area 0
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 10.10.9.64 0.0.0.63
 deny any log
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
 access-class ACL_MGMT_VTY in
line vty 5 15
 transport input none
!
end
write memory
```

### Step 5: `EDGE-R1` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: EDGE-R1 (Model: 2911, Role: Perimeter Router & NAT Gateway)
! Scenario: Campus LAN Profile (Single-Site Enterprise)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname EDGE-R1
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
 description Routed Link to CORE-SW [Media: Cat6a 10GBASE-T, Distance: 30 m]
 ip address 10.10.9.129 255.255.255.252
 ip nat inside
 no shutdown
!
interface GigabitEthernet0/1
 description WAN Internet Uplink (RFC 5737 Documentation IP)
 ip address 203.0.113.2 255.255.255.252
 ip nat outside
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.2
 passive-interface default
 no passive-interface GigabitEthernet0/0
 network 10.10.9.128 0.0.0.3 area 0
!
! Network Address Translation: NAT Overload / PAT (RFC 3022 & RFC 5737)
ip access-list standard ACL_NAT_PERMIT
 permit 10.10.0.0 0.0.255.255
!
ip nat inside source list ACL_NAT_PERMIT interface GigabitEthernet0/1 overload
ip route 0.0.0.0 0.0.0.0 203.0.113.1
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 10.10.9.64 0.0.0.63
 deny any log
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
 access-class ACL_MGMT_VTY in
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
- **Expected**: All active VLANs (`10, 20, 30, 12, 22, 11, 21, 32, 31, 100, 99`) and parking VLAN `999` (`Parking_Native_Blackhole`) appear as `active`.

### 3. 802.1Q Trunk Security (`show interfaces trunk`)
- Run on **CORE-SW** and **Access Switches**.
- **Expected**: Mode = `on` (with DTP disabled), Encapsulation = `802.1q`, Native VLAN = `999`, Status = `trunking`, and **Vlans allowed on trunk** shows ONLY the explicit allowed list (never `1-4094`).

### 4. Spanning Tree Root (`show spanning-tree`)
- Run on **CORE-SW / HQ-CORE**.
- **Expected**: Protocol displays `rstp` (`rapid-pvst`), and the Core Switch displays **"This bridge is the root"** with Priority `4096` (plus SysID extension).

### 5. Dynamic Routing Table (`show ip route`)
- Run on **all L3 devices**.
- **Expected**: Connected (`C`), Local (`L`), and OSPF (`O` / `O IA`) routes exist for all remote subnets.

### 6. OSPF Neighbor Adjacencies (`show ip ospf neighbor`)
- Run on **EDGE-R1 / CORE-SW / HQ-CORE / REM1-R / REM2-R**.
- **Expected**: Neighbor states show `FULL`.

### 7. Security ACL & NAT Verification (`show access-lists` & `show ip nat translations`)
- Run `show access-lists` on **CORE-SW**: Inspect `ACL_WIFI_SECURITY` hit counters.
- **MUST PASS Ping Test**: Ping from Data host (`10.10.0.2`) to Server (`10.10.9.2`) -> **Reply received (0% loss)**.
- **MUST FAIL Security ACL Test**: Ping from WiFi host (`10.10.5.2`) to Server (`10.10.9.2`) -> **Destination host unreachable / Administratively prohibited (100% blocked by `ACL_WIFI_SECURITY`)**.
- Run `show ip nat translations` on **EDGE-R1** after pinging the WAN ISP IP (`203.0.113.1`) -> Verify Inside Global `203.0.113.2:<port>` PAT mapping.

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
