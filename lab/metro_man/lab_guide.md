# Cisco Packet Tracer Lab Guide: Metro MAN Profile (Tri-Site Metropolitan Ring)

> [!NOTE]
> All IP plans, subnet masks, wildcard masks, interface descriptions, and verification expectations in this guide are **computed directly by the NetArchitect Engine**.
> **Never assume verified in Packet Tracer until you run the topology and confirm every checklist item below.**

---

## (a) Device Inventory, PT Models & Interface-Count Table

| Device Name | OSI Role | Packet Tracer Model | Links Used | Required Hardware / Power Modules (Verify in PT) |
| :--- | :--- | :--- | :---: | :--- |
| `HQ-CORE` | Headquarters Core Routing Switch (ABR Area 0) | `3650-24PS` | 2 | Insert `AC-POWER-SUPPLY` in PSU slot to power on (24x Gi built-in). |
| `REM1-R` | Remote Branch 1 Edge Router | `2911` | 3 | Built-in 3x Gi (`Gi0/0`, `Gi0/1`, `Gi0/2`). |
| `REM2-R` | Remote Branch 2 Edge Router | `2911` | 3 | Built-in 3x Gi (`Gi0/0`, `Gi0/1`, `Gi0/2`). |

---

## (b) Physical Cabling & Optical Media Table

*Note on `--platform pt`: 10 GbE optical trunks/WAN links are modeled using GigabitEthernet copper interfaces in Packet Tracer, with the true calculated L1 medium and optical power budget recorded in each interface `description`.*

| Link ID | Endpoint A (`Port`) | Endpoint B (`Port`) | PT Cable Type | Physical Distance | Engineered Medium & Optic | Optical Margin |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `HQ-REM1` | `HQ-CORE` (`GigabitEthernet1/0/1`) | `REM1-R` (`GigabitEthernet0/0`) | Copper Straight-Through | 15.0 km | OS2 SMF (10GBASE-ER SFP+ (1550 nm)) | 6.55 dB |
| `HQ-REM2` | `HQ-CORE` (`GigabitEthernet1/0/2`) | `REM2-R` (`GigabitEthernet0/0`) | Copper Straight-Through | 35.0 km | OS2 SMF (10GBASE-ER SFP+ (1550 nm)) | 1.55 dB |
| `REM1-REM2` | `REM1-R` (`GigabitEthernet0/1`) | `REM2-R` (`GigabitEthernet0/1`) | Copper Cross-Over | 22.0 km | OS2 SMF (10GBASE-ER SFP+ (1550 nm)) | 4.8 dB |

---

## (c) Bitwise-Allocated IP Addressing Plan & Test Hosts

- **Root Prefix**: `172.16.0.0/16`
- **Overall Allocation Efficiency**: `63.4%`

### Subnet & Gateway Plan

| Subnet / VLAN Name | VLAN | CIDR Block | Subnet Mask | Wildcard Mask | Default Gateway | Broadcast |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `HQ-Users` | 10 | `172.16.0.0/23` | `255.255.254.0` | `0.0.1.255` | `172.16.0.1` | `172.16.1.255` |
| `REM1-Users` | 20 | `172.16.2.0/25` | `255.255.255.128` | `0.0.0.127` | `172.16.2.1` | `172.16.2.127` |
| `REM2-Users` | 30 | `172.16.2.128/25` | `255.255.255.128` | `0.0.0.127` | `172.16.2.129` | `172.16.2.255` |
| `HQ-Servers` | 100 | `172.16.3.0/26` | `255.255.255.192` | `0.0.0.63` | `172.16.3.1` | `172.16.3.63` |
| `FinTech-Colo` | 150 | `172.16.3.64/26` | `255.255.255.192` | `0.0.0.63` | `172.16.3.65` | `172.16.3.127` |
| `HQ-Mgmt` | 99 | `172.16.3.128/27` | `255.255.255.224` | `0.0.0.31` | `172.16.3.129` | `172.16.3.159` |
| `P2P-HQ-REM1` | Routed P2P | `172.16.3.160/30` | `255.255.255.252` | `0.0.0.3` | `172.16.3.161` | `172.16.3.163` |
| `P2P-HQ-REM2` | Routed P2P | `172.16.3.164/30` | `255.255.255.252` | `0.0.0.3` | `172.16.3.165` | `172.16.3.167` |
| `P2P-REM1-REM2` | Routed P2P | `172.16.3.168/30` | `255.255.255.252` | `0.0.0.3` | `172.16.3.169` | `172.16.3.171` |

### End-Device (PC-PT / Server-PT) Static Test Plan (1–2 Hosts per Subnet)

| End-Device Hostname | Type | Target Subnet / VLAN | Static IP Address | Subnet Mask | Default Gateway | Attachment Port (Host 1) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HOST_HQ_Users` | PC-PT | `HQ-Users` (VLAN 10) | `172.16.0.2` | `255.255.254.0` | `172.16.0.1` | `HQ-CORE` (`GigabitEthernet1/0/3`, straight) |
| `HOST_HQ_Users_2` | PC-PT | `HQ-Users` (VLAN 10) | `172.16.0.3` | `255.255.254.0` | `172.16.0.1` | Optional extra host (switch default access port) |
| `HOST_REM1_Users` | PC-PT | `REM1-Users` (VLAN 20) | `172.16.2.2` | `255.255.255.128` | `172.16.2.1` | `REM1-R` (`GigabitEthernet0/2`, cross) |
| `HOST_REM1_Users_2` | PC-PT | `REM1-Users` (VLAN 20) | `172.16.2.3` | `255.255.255.128` | `172.16.2.1` | Optional extra host (switch default access port) |
| `HOST_REM2_Users` | PC-PT | `REM2-Users` (VLAN 30) | `172.16.2.130` | `255.255.255.128` | `172.16.2.129` | `REM2-R` (`GigabitEthernet0/2`, cross) |
| `HOST_REM2_Users_2` | PC-PT | `REM2-Users` (VLAN 30) | `172.16.2.131` | `255.255.255.128` | `172.16.2.129` | Optional extra host (switch default access port) |
| `HOST_HQ_Servers` | Server-PT | `HQ-Servers` (VLAN 100) | `172.16.3.2` | `255.255.255.192` | `172.16.3.1` | `HQ-CORE` (`GigabitEthernet1/0/4`, straight) |
| `HOST_HQ_Servers_2` | Server-PT | `HQ-Servers` (VLAN 100) | `172.16.3.3` | `255.255.255.192` | `172.16.3.1` | Optional extra host (switch default access port) |
| `HOST_FinTech_Colo` | Server-PT | `FinTech-Colo` (VLAN 150) | `172.16.3.66` | `255.255.255.192` | `172.16.3.65` | `HQ-CORE` (`GigabitEthernet1/0/5`, straight) |
| `HOST_FinTech_Colo_2` | Server-PT | `FinTech-Colo` (VLAN 150) | `172.16.3.67` | `255.255.255.192` | `172.16.3.65` | Optional extra host (switch default access port) |
| `HOST_HQ_Mgmt` | PC-PT | `HQ-Mgmt` (VLAN 99) | `172.16.3.130` | `255.255.255.224` | `172.16.3.129` | `HQ-CORE` (`GigabitEthernet1/0/6`, straight) |
| `HOST_HQ_Mgmt_2` | PC-PT | `HQ-Mgmt` (VLAN 99) | `172.16.3.131` | `255.255.255.224` | `172.16.3.129` | Optional extra host (switch default access port) |

---

## (d) Per-Device Configurations in Paste Order

> [!IMPORTANT]
> Paste configurations strictly in **bottom-up OSI order**: **L2 Access Switches first -> L3 Core Switches second -> Perimeter / WAN Routers third**.
> Always verify RSA key generation (`crypto key generate rsa modulus 2048`) if SSH fails to initialize in Packet Tracer.

### Step 1: `HQ-CORE` (`3650-24PS` — L3_SWITCH)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: HQ-CORE (Model: 3650-24PS, Role: Headquarters Core Routing Switch (ABR Area 0))
! Scenario: Metro MAN Profile (Tri-Site Metropolitan Ring)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname HQ-CORE
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
! Modular QoS CLI (MQC) Low-Latency Queuing Architecture
class-map match-any CM_VOIP_FINTECH
 match ip dscp ef
 match ip dscp cs5
!
policy-map PM_METRO_QOS_EGRESS
 class CM_VOIP_FINTECH
  priority percent 35
 class class-default
  fair-queue
!
! VLAN Database Definition
vlan 10
 name HQ-Users
vlan 100
 name HQ-Servers
vlan 150
 name FinTech-Colo
vlan 99
 name HQ-Mgmt
vlan 999
 name Parking_Native_Blackhole
!
! Physical Interfaces (Trunks & Routed P2P)
interface GigabitEthernet1/0/1
 description Routed Point-to-Point Uplink to REM1-R [Media: OS2 SMF, Distance: 15.0 km]
 no switchport
 ip address 172.16.3.161 255.255.255.252
 ip ospf cost 10
 service-policy output PM_METRO_QOS_EGRESS
 no shutdown
!
interface GigabitEthernet1/0/2
 description Routed Point-to-Point Uplink to REM2-R [Media: OS2 SMF, Distance: 35.0 km]
 no switchport
 ip address 172.16.3.165 255.255.255.252
 ip ospf cost 20
 service-policy output PM_METRO_QOS_EGRESS
 no shutdown
!
! Local Direct-Attach Access Ports (SVI Activation for End-Hosts)
interface GigabitEthernet1/0/3
 description Local Access Port for HQ-Users (VLAN 10)
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface GigabitEthernet1/0/4
 description Local Access Port for HQ-Servers (VLAN 100)
 switchport mode access
 switchport access vlan 100
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface GigabitEthernet1/0/5
 description Local Access Port for FinTech-Colo (VLAN 150)
 switchport mode access
 switchport access vlan 150
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface GigabitEthernet1/0/6
 description Local Access Port for HQ-Mgmt (VLAN 99)
 switchport mode access
 switchport access vlan 99
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
! Switch Virtual Interfaces (SVI Layer 3 Default Gateways)
interface Vlan10
 description SVI Default Gateway for HQ-Users
 ip address 172.16.0.1 255.255.254.0
 no shutdown
!
interface Vlan100
 description SVI Default Gateway for HQ-Servers
 ip address 172.16.3.1 255.255.255.192
 no shutdown
!
interface Vlan150
 description SVI Default Gateway for FinTech-Colo
 ip address 172.16.3.65 255.255.255.192
 no shutdown
!
interface Vlan99
 description SVI Default Gateway for HQ-Mgmt
 ip address 172.16.3.129 255.255.255.224
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.1
 passive-interface default
 no passive-interface GigabitEthernet1/0/1
 no passive-interface GigabitEthernet1/0/2
 network 172.16.0.0 0.0.1.255 area 0
 network 172.16.3.0 0.0.0.63 area 0
 network 172.16.3.64 0.0.0.63 area 0
 network 172.16.3.128 0.0.0.31 area 0
 network 172.16.3.160 0.0.0.3 area 0
 network 172.16.3.164 0.0.0.3 area 0
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 172.16.3.128 0.0.0.31
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

### Step 2: `REM1-R` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: REM1-R (Model: 2911, Role: Remote Branch 1 Edge Router)
! Scenario: Metro MAN Profile (Tri-Site Metropolitan Ring)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname REM1-R
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
! Modular QoS CLI (MQC) Low-Latency Queuing Architecture
class-map match-any CM_VOIP_FINTECH
 match ip dscp ef
 match ip dscp cs5
!
policy-map PM_METRO_QOS_EGRESS
 class CM_VOIP_FINTECH
  priority percent 35
 class class-default
  fair-queue
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to HQ-CORE [Media: OS2 SMF, Distance: 15.0 km]
 ip address 172.16.3.162 255.255.255.252
 ip ospf cost 10
 service-policy output PM_METRO_QOS_EGRESS
 no shutdown
!
interface GigabitEthernet0/1
 description Routed Link to REM2-R [Media: OS2 SMF, Distance: 22.0 km]
 ip address 172.16.3.169 255.255.255.252
 ip ospf cost 100
 service-policy output PM_METRO_QOS_EGRESS
 no shutdown
!
interface GigabitEthernet0/2
 description Local LAN Gateway for REM1-Users (VLAN 20 Untagged Access)
 ip address 172.16.2.1 255.255.255.128
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.2
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface GigabitEthernet0/1
 network 172.16.3.160 0.0.0.3 area 0
 network 172.16.3.168 0.0.0.3 area 0
 network 172.16.2.0 0.0.0.127 area 0
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 172.16.3.128 0.0.0.31
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

### Step 3: `REM2-R` (`2911` — ROUTER)

```ios
! ===========================================================================
! NetArchitect Cisco IOS Configuration File
! Device: REM2-R (Model: 2911, Role: Remote Branch 2 Edge Router)
! Scenario: Metro MAN Profile (Tri-Site Metropolitan Ring)
! Target Platform: PT (Packet Tracer Compatible Syntax - Verify in PT)
! Generated algorithmically with bitwise-verified address structures
! ===========================================================================
version 15.0
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname REM2-R
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
! Modular QoS CLI (MQC) Low-Latency Queuing Architecture
class-map match-any CM_VOIP_FINTECH
 match ip dscp ef
 match ip dscp cs5
!
policy-map PM_METRO_QOS_EGRESS
 class CM_VOIP_FINTECH
  priority percent 35
 class class-default
  fair-queue
!
! Physical Routed Interfaces
interface GigabitEthernet0/0
 description Routed Link to HQ-CORE [Media: OS2 SMF, Distance: 35.0 km]
 ip address 172.16.3.166 255.255.255.252
 ip ospf cost 20
 service-policy output PM_METRO_QOS_EGRESS
 no shutdown
!
interface GigabitEthernet0/1
 description Routed Link to REM1-R [Media: OS2 SMF, Distance: 22.0 km]
 ip address 172.16.3.170 255.255.255.252
 ip ospf cost 100
 service-policy output PM_METRO_QOS_EGRESS
 no shutdown
!
interface GigabitEthernet0/2
 description Local LAN Gateway for REM2-Users (VLAN 30 Untagged Access)
 ip address 172.16.2.129 255.255.255.128
 no shutdown
!
! Interior Gateway Protocol: OSPFv2 (RFC 2328)
router ospf 1
 router-id 10.255.255.3
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface GigabitEthernet0/1
 network 172.16.3.164 0.0.0.3 area 0
 network 172.16.3.168 0.0.0.3 area 0
 network 172.16.2.128 0.0.0.127 area 0
!
!
! Management Access Control List (VTY Protection)
ip access-list standard ACL_MGMT_VTY
 permit 172.16.3.128 0.0.0.31
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
- **Expected**: All active VLANs (`10, 20, 30, 100, 150, 99`) and parking VLAN `999` (`Parking_Native_Blackhole`) appear as `active`.

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
