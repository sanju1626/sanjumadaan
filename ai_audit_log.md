# NetArchitect AI Adversarial Audit Log (`CIC-307` Deliverable)

**Author**: Sanju Madaan · **Roll No.**: `00714803124` · **Section / Batch**: `5C1`  

> **Purpose**: Record real, reproducible software & networking flaws produced in the initial unreviewed AI draft (`git commit 8faf5edebdbb32725a9438c79fda4144001620e7`, archived in `audit/raw/`), demonstrate exact execution failures, analyze root causes at the bit/protocol/physics level, trace end-to-end packet flow before vs. after remediation, and link each fix to automated regression tests.

---

## Baseline Raw Draft Reference

- **Git Commit Audited**: `8faf5edebdbb32725a9438c79fda4144001620e7` (`"raw AI draft"`)
- **Archived Raw Files**:
  - [audit/raw/raw_vlsm.py](file:///c:/Users/welcome/Downloads/sanjumadaan/audit/raw/raw_vlsm.py) & `git show 8faf5ed:engine/vlsm_engine.py`
  - [audit/raw/raw_media.py](file:///c:/Users/welcome/Downloads/sanjumadaan/audit/raw/raw_media.py) & `git show 8faf5ed:engine/media_engine.py`
  - [audit/raw/raw_config.py](file:///c:/Users/welcome/Downloads/sanjumadaan/audit/raw/raw_config.py) & `git show 8faf5ed:engine/config_generator.py`

---

## Defect Audit #1 — Python Two's-Complement Wildcard Sign Bug, 40-Bit Mask Overflow & Missing RFC 3021 / Validation Guards (L3 Addressing)

### 1. Original Generation Prompt
> *"Compute subnet masks, wildcard masks, aligned VLSM allocations, and RFC 3021 point-to-point prefixes using pure bitwise integer operators (`<<`, `>>`, `&`, `|`, `~`) without Python's `ipaddress` module."*

### 2. Buggy Raw Draft Code (`git show 8faf5ed:engine/vlsm_engine.py`, lines 21–49 & [audit/raw/raw_vlsm.py](file:///c:/Users/welcome/Downloads/sanjumadaan/audit/raw/raw_vlsm.py))
```python
    for item in sorted_req:
        name = item["name"]
        hosts = item["hosts"]
        
        # Raw AI implementation:
        need = hosts + 2
        prefix = 32 - math.ceil(math.log2(need))
        size = 1 << (32 - prefix)
        ...
        mask = (0xFFFFFFFF << (32 - prefix)) # Raw AI flaw: missing & 0xFFFFFFFF
        wildcard = ~mask # Raw AI flaw: missing & 0xFFFFFFFF yields negative integer in Python!
        
        network_ip = start
        broadcast_ip = end - 1
        first_host = network_ip + 1
        last_host = broadcast_ip - 1 # Raw AI flaw: wrong for /31 or /32
```

### 3. Bit-Level & Protocol-Arithmetic Root Cause
1. **Arbitrary-Precision Bitwise Inversion (`~`)**: Python `int` objects have infinite sign extension rather than fixed 32-bit unsigned width (`uint32_t`). When calculating a `/24` mask via `(0xFFFFFFFF << 8)`, the intermediate integer becomes `0xFFFFFFFF00` (40 bits, `1,099,511,627,264` instead of `0xFFFFFF00` = `4,294,967,040`). Applying unary `~mask` inverts all leading zeroes to infinite leading ones, producing **`-1,099,511,627,521` (`-0xFFFFFFFF01`)** instead of **`255` (`0x000000FF`)**. Any bitwise broadcast computation `network_int | wildcard` without explicit `& 0xFFFFFFFF` becomes a negative integer (`-1,099,343,200,001`).
2. **RFC 3021 `/31` & Input Hygiene Omitted**: Even when `allow_rfc3021=True` was passed with `hosts=2`, the raw code unconditionally added `+ 2` (`2 + 2 = 4 -> /30`), wasting 50% of P2P address space and using `broadcast_ip - 1` instead of `/31` two-host semantics (`network` & `network + 1`, no broadcast). Duplicate subnet names were also silently accepted.

### 4. Exact Captured Detection Output (Executed Against `8faf5ed`)
```text
--- [1] VLSM Bitwise & Prefix Arithmetic Checks ---
Subnets returned (hosts=60, hosts=2 with allow_rfc3021=True):
  {'name': 'LAN-A', ..., 'prefix': 26, ...}
  {'name': 'P2P-1', 'requested_hosts': 2, 'prefix': 30, 'network': '10.10.0.64', ...}

Direct formula test from 8faf5ed:engine/vlsm_engine.py lines 35-36 (prefix=/24):
  raw_mask     = 0xffffffff00 (bit_length=40) vs oracle 0xffffff00 -> equal=False
  raw_wildcard = -1099511627521 (-0xffffffff01) vs oracle 255 (0xff) -> equal=False
Duplicate subnet names check in 8faf5ed -> Did NOT raise InvalidParameterError! Returned: ['DUP 10.10.0.0', 'DUP 10.10.0.16']

int('10.10.0.0') | raw_wildcard(~(0xFFFFFFFF<<8)) = -1099343200001
```

### 5. Fixed Production Code ([engine/addr.py](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/addr.py#L33-L52) & [engine/vlsm_engine.py](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/vlsm_engine.py#L301-L365))
```python
# engine/addr.py lines 33-52
def prefix_to_mask_int(prefix: int) -> int:
    if not isinstance(prefix, int) or prefix < 0 or prefix > 32:
        raise InvalidParameterError(f"Prefix length must be an integer between 0 and 32, got {prefix}")
    if prefix == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF

def prefix_to_wildcard_int(prefix: int) -> int:
    mask = prefix_to_mask_int(prefix)
    return (~mask) & 0xFFFFFFFF
```
Plus explicit prefix rules in `vlsm_engine.py` (`is_p2p` + `allow_rfc3021` -> `/31`, `is_loopback` -> `/32`, default P2P -> `/30`), duplicate name/VLAN checks, and contiguous per-area group cursor advancement.

### 6. Numbered End-to-End Packet-Flow Analysis (P2P WAN Link / OSPF Subnet Matching)
| Step | Before Fix (Unreviewed Draft / Corrupt Wildcard) | After Fix ([`engine/addr.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/addr.py) + [`engine/vlsm_engine.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/vlsm_engine.py)) |
| :--- | :--- | :--- |
| **1. Bitwise Mask Computation** | For `/24`, `mask` holds 40 bits (`0xFFFFFFFF00`) and `~mask` evaluates to negative integer `-1099511627521`. Downstream arithmetic `net | wildcard` produces negative address `-1099343200001`. | `prefix_to_mask_int(24)` returns exact `0xFFFFFF00` (`255.255.255.0`); `prefix_to_wildcard_int(24)` returns exact `0x000000FF` (`0.0.0.255`), matching Python's `ipaddress.IPv4Network` oracle across `/0`–`/32`. |
| **2. P2P Allocation (`allow_rfc3021=True`)** | Allocates `10.10.0.64/30` (4 IPs) for a 2-host link despite explicit `allow_rfc3021=True`, wasting 2 IPv4 addresses per link (`50%` efficiency loss). | Allocates `10.10.0.64/31` (`255.255.255.254`, usable hosts `.64` and `.65`, `N/A (RFC 3021 /31)` broadcast), raising P2P efficiency from `50%` to `100%`. |
| **3. Frame & IPv4 Header Creation** | Host on `LAN-A` (`10.10.0.2`) sends ICMP Echo to P2P interface; if negative/corrupt broadcast or wrong mask leaks into ACL/NAT calculation, edge fails. | Frame leaves host MAC -> Core SVI MAC; IP src `10.10.0.2`, dst `10.10.9.129`, TTL `128`. |
| **4. Routing Lookup & ARP** | If wildcard arithmetic fails contiguity check (`mask_int + wildcard_int != 0xFFFFFFFF`), router ACL/OSPF matching silently misses interfaces. | Core router matches connected/OSPF route with valid `0.0.0.3` wildcard, decrements TTL `128 -> 127`, forwards across Ethernet/optical frame to `EDGE-R1`. |

### 7. Verification Regression Tests & Viva Defense
- **Regression Tests**: [`test_wildcard_mask_arithmetic_contiguous`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_vlsm.py#L16-L24), [`test_300_case_seeded_fuzzing_vs_ipaddress_oracle`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_vlsm.py#L97-L120), [`test_rfc3021_slash_31_point_to_point`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_vlsm.py#L123-L132), [`test_duplicate_subnet_name_raises`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_vlsm.py#L160-L164).
- **Lesson**: Never assume fixed-width C integer semantics in Python; always clamp bit-shift and inversion outputs with `& 0xFFFFFFFF` at every operator boundary.
- **Viva Defense Summary**: *"In Python, integers are arbitrary-precision signed objects, not 32-bit unsigned registers. Our initial draft ran `~mask` without `& 0xFFFFFFFF`, producing a negative 40-bit integer that failed integer equality checks against `ipaddress.IPv4Network.hostmask` and corrupted integer broadcast math. Wrapping both shifts and complements in `& 0xFFFFFFFF` inside `engine/addr.py` keeps every subnet calculation pure-bitwise while proving `100%` oracle parity across 300 seeded fuzz scenarios."*

---

## Defect Audit #2 — Physical Media Boundary Bypass (`NaN`, Forced Copper/MMF) & Omitted Optical Connector Losses (L1 Physics)

### 1. Original Generation Prompt
> *"Recommend or validate Cat6a (`<=100m`), OM4 MMF (`101-400m`), and OS2 SMF (`>400m`) for 10 GbE links; enforce `PhysicalDistanceViolationError` on forced copper/MMF violations, reject invalid/NaN distances, and compute optical span loss including `2 x 0.3 dB` connectors plus splice losses."*

### 2. Buggy Raw Draft Code (`git show 8faf5ed:engine/media_engine.py`, lines 14–66 & [audit/raw/raw_media.py](file:///c:/Users/welcome/Downloads/sanjumadaan/audit/raw/raw_media.py))
```python
    if distance_m <= 0:
        raise InvalidParameterError(f"Distance must be positive, got {distance_m}")
    ...
    if forced_media == "copper":
        # Raw AI flaw: forgets to check distance_m > 100 when forced!
        return {
            "media_type": "Cat6a 10GBASE-T",
            "standard": "IEEE 802.3an",
            "distance_m": distance_m,
            "transceiver": "10GBASE-T RJ45"
        }
    ...
        # Raw AI flaw in optical budget: calculates loss as dist_km * 0.35 without connector loss (2 * 0.3 dB)
        if dist_km <= 10:
            loss = dist_km * 0.35
            budget = 6.2
```

### 3. Physics & Numerical Root Cause
1. **Unchecked Forced Media Bypass**: `forced_media == "copper"` returned success unconditionally, allowing a `180 m` Cat6a link despite IEEE 802.3an (`10GBASE-T`) limiting copper channels to `100 m` due to insertion loss and high-frequency Alien Near-End Crosstalk (`ANEXT`). Similarly, `forced_media == "mmf"` at `401 m` silently ignored the user's explicit constraint instead of raising `PhysicalDistanceViolationError` (modal dispersion limit at 850 nm).
2. **IEEE 754 `NaN` Comparison Fall-Through**: Because `float('nan') <= x` is always `False` in IEEE 754 arithmetic, `distance_m = float('nan')` passed `distance_m <= 0` and fell into the final `else` (`> 80 km`), returning `"Beyond 80 km carrier DWDM / amplified span required"` for `NaN` metres!
3. **Omitted `2 x 0.3 dB = 0.6 dB` LC/SC Connector Losses & Splice Parameter**: Raw optical attenuation counted fiber glass loss only (`km * 0.35 dB/km` or `km * 0.25 dB/km`), under-reporting actual span loss by `>= 0.6 dB` (and ignoring fusion splices entirely), which causes marginal links (`16.5 km` or `40 km + 0.4 dB` splice) to pass design checks when they exceed receiver sensitivity.

### 4. Exact Captured Detection Output (Executed Against `8faf5ed`)
```text
--- [2] Physical Media & Optical Budget Checks ---
Forced copper at 180.0m -> FAILED TO RAISE PhysicalDistanceViolationError! Returned: {'media_type': 'Cat6a 10GBASE-T', 'standard': 'IEEE 802.3an', 'distance_m': 180.0, 'transceiver': '10GBASE-T RJ45'}
10.0 km (10GBASE-LR) in 8faf5ed -> loss_db=3.5 dB, margin_db=2.7 dB (Expected: 3.5 + 0.6 connectors = 4.10 dB loss, 2.10 dB margin!)
40.0 km (10GBASE-ER) in 8faf5ed -> loss_db=10.0 dB, margin_db=0.9 dB (Expected: 10.0 + 0.6 connectors = 10.60 dB loss, 0.30 dB margin!)
NaN distance -> FAILED TO RAISE InvalidParameterError! Passed silently!

--- [4] NaN Distance Output ---
recommend_media(float('nan')) returned: {'media_type': 'OS2 SMF', 'transceiver': 'Carrier DWDM / Amplified Span', 'distance_km': nan, ...}
```

### 5. Fixed Production Code ([engine/media_engine.py](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/media_engine.py#L71-L211))
```python
    if not isinstance(distance_m, (int, float)) or math.isnan(distance_m) or math.isinf(distance_m):
        raise InvalidParameterError(f"Distance for link '{link_name}' must be a finite real number, got {distance_m}")
    ...
    if forced_media:
        forced = forced_media.strip().lower()
        if forced in ("copper", "cat6a", "10gbase-t") and distance_m > 100.0:
            raise PhysicalDistanceViolationError(... "NEXT/ANEXT" ...)
        elif forced in ("mmf", "om4", "10gbase-sr") and distance_m > 400.0:
            raise PhysicalDistanceViolationError(... "modal dispersion limit" ...)
    ...
    total_loss = (distance_km * atten_rate) + connector_loss + splice_loss_db  # connector_loss = 0.6 dB
    margin = power_budget - total_loss
    if margin < 0:
        raise OpticalBudgetError(..., loss_db=round(total_loss, 2), budget_db=power_budget, margin_db=round(margin, 2))
```

### 6. Numbered L1 Signal & Link Behavior Trace (`BLDG-A-SW` `180 m` Campus Backbone & `40 km + 0.4 dB splice` MAN Span)
| Step | Before Fix (`8faf5ed`) | After Fix ([`engine/media_engine.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/media_engine.py)) |
| :--- | :--- | :--- |
| **1. Design-Time Validation (`forced_media="copper"`, `180 m`)** | Accepts `Cat6a 10GBASE-T` for `CORE-SW <-> BLDG-A-SW` (`180 m`) without raising an error. | Immediately blocks invalid topology by raising `PhysicalDistanceViolationError` citing IEEE 802.3an 100 m limit and NEXT/ANEXT degradation. |
| **2. Physical Line Encoding / Attenuation** | PAM16 (`10GBASE-T`) over `180 m` copper loses ~`1.8x` rated SNR, causing constant FCS/CRC errors at L2 and interface flapping. | Auto-selects `OM4 MMF (10GBASE-SR, 850 nm)` for `180 m` (`<= 400 m` modal dispersion limit), maintaining clean 10 GbE symbol eye openings. |
| **3. Long-Haul Optical Budget (`40 km` ER + `0.4 dB` splice)** | Computes `40 * 0.25 = 10.0 dB <= 10.9 dB` (false `+0.9 dB` margin pass!). In field deployment, actual optical power arriving at `REM2-R` SFP+ is `-11.0 dB` below Tx (`-0.1 dB` below Rx sensitivity). | Computes `10.0 + 0.6 (2x LC connectors) + 0.4 (splices) = 11.0 dB > 10.9 dB` -> raises `OpticalBudgetError` (`-0.10 dB` margin) so engineer upgrades optic to `10GBASE-ZR` (`23.0 dB` budget, `12.00 dB` margin). |

### 7. Verification Regression Tests & Viva Defense
- **Regression Tests**: [`test_forced_copper_violation`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_media.py#L64-L68), [`test_forced_mmf_violation`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_media.py#L71-L75), [`test_invalid_distance_nan`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_media.py#L51-L54), [`test_optical_budget_connector_and_splice_math`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_media.py#L90-L98), [`test_optical_budget_error`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_media.py#L84-L87).
- **Viva Defense Summary**: *"In the raw draft, forcing copper at 180 m succeeded silently, NaN fell through comparisons into carrier DWDM, and optical loss omitted the mandatory 0.6 dB (2 x 0.3 dB) LC connector insertion loss. Adding IEEE 754 `math.isnan`/`isinf` guards and strict connector-inclusive link budgeting catches near-threshold failures—such as a 40 km ER link with 0.4 dB of splices exceeding 10.9 dB—before hardware is procured."*

---

## Defect Audit #3 — Unconstrained 802.1Q Trunks, Native VLAN 1 & Inverted OSPF Wildcard Mask + Complete Packet-Flow Analysis (L2/L3 Control & Data Plane)

### 1. Original Generation Prompt
> *"Generate Cisco IOS switch trunks with explicit `switchport trunk allowed vlan`, Native VLAN 999, and `switchport nonegotiate`; generate OSPF using bitwise wildcard masks and `passive-interface default`; isolate Campus WiFi (`VLAN 12/22/32`) from Servers (`VLAN 100`) and Management (`VLAN 99`) via Named Extended ACLs."*

### 2. Buggy Raw Draft Code (`git show 8faf5ed:engine/config_generator.py`, lines 5–26 & [audit/raw/raw_config.py](file:///c:/Users/welcome/Downloads/sanjumadaan/audit/raw/raw_config.py))
```python
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
    ...
    for net in networks:
        # Bug: net.get('mask') used instead of wildcard mask!
        cfg.append(f" network {net['network']} {net.get('mask', '255.255.255.0')} area {net.get('area', 0)}")
    return "\n".join(cfg)
```
*(Note: In later multi-device integration during Phase 4, automated self-checks also caught substring matching bugs—`"B" in "BLDG-C-SW"` and `"R-CHE" in "P2P-BLR-CHE"`—plus missing `ACL_MGMT_VTY` definitions on perimeter/L2 devices, all resolved and enforced via [`run_configuration_self_check`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L814-L934).)*

### 3. Protocol & Security Root Cause
1. **Unrestricted Trunk & VLAN Hopping Surface**: Omitting `switchport trunk allowed vlan <list>` leaves `1-4094` enabled on trunks; leaving Native VLAN at `1` while DTP auto-negotiation remains active enables **double-tagging VLAN hopping** and unnecessary broadcast/BPDU flooding into non-present VLANs.
2. **Inverted Cisco OSPF Wildcard Semantics**: Cisco IOS `network <net> <wildcard> area <id>` interprets `0` bits as *"must match"* and `1` bits as *"don't care"*. Supplying a subnet mask `255.255.254.0` (`11111111.11111111.11111110.00000000`) tells OSPF to **ignore the first 23 network bits** and match ONLY host bits `.0` (`x.x.[even].0`), activating OSPF on unintended interfaces across the entire IPv4 space (`0.0.0.0–255.255.255.254`) while failing to advertise the intended `/23` subnet consistently! Missing `passive-interface default` also leaks OSPF Hello LSAs out access VLAN SVIs (`Vlan10..100`) toward end-user PCs.

### 4. Exact Captured Detection Output (Executed Against `8faf5ed`)
```text
--- [3] Cisco IOS Trunk & OSPF Config Generator Checks ---
Raw 8faf5ed generate_trunk_config('GigabitEthernet0/1', allowed_vlans=[10, 20]):
interface GigabitEthernet0/1
 description Uplink Trunk
 switchport mode trunk
 no shutdown
  Contains 'switchport trunk allowed vlan'? -> False
  Contains 'switchport trunk native vlan 999'? -> False
  Contains 'switchport nonegotiate'? -> False

Raw 8faf5ed generate_ospf_config(...):
router ospf 1
 router-id 10.255.255.1
 network 10.10.0.0 255.255.254.0 area 0
  Emitted subnet mask 255.255.254.0 instead of wildcard 0.0.1.255? -> True
```

### 5. Fixed Production Code ([engine/config_generator.py](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L240-L262) & [`_generate_l3_switch_config`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L427-L525))
```ios
interface GigabitEthernet0/1
 description Uplink Trunk to CORE-SW [Media: OM4 MMF, Distance: 320m]
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,11,12,20,21,22,30,31,32,99,100
 switchport nonegotiate
 no shutdown
...
router ospf 1
 router-id 10.255.255.1
 passive-interface default
 no passive-interface GigabitEthernet1/0/1
 network 10.10.0.0 0.0.1.255 area 0
 network 10.10.9.128 0.0.0.3 area 0
```

### 6. Numbered End-to-End Packet-Flow Trace (Before vs. After Fix)

#### Trace A — WiFi Client (`HOST_BLDG_A_WiFi`, `10.10.5.2/24`, VLAN 12) -> Server Farm (`HOST_Servers_Farm`, `10.10.9.2/26`, VLAN 100)
*(Policy: WiFi MUST be denied access to `10.10.9.0/26`)*

| Step | Layer / Component | Before Fix (`8faf5ed` Draft) | After Fix ([`CORE-SW.cfg`](file:///c:/Users/welcome/Downloads/sanjumadaan/exports/campus_lan/CORE-SW.cfg) + [`BLDG-A-SW.cfg`](file:///c:/Users/welcome/Downloads/sanjumadaan/exports/campus_lan/BLDG-A-SW.cfg)) |
| :--- | :--- | :--- | :--- |
| **1. Host Frame Construction** | L3/L2 on `10.10.5.2` | Dest IP `10.10.9.2` is outside `10.10.5.0/24`; host ARPs for gateway `10.10.5.1` (`Vlan12`), builds Ethernet II frame `SrcMAC=Host_WiFi -> DstMAC=CORE-SW_Vlan12`, `IP: 10.10.5.2 -> 10.10.9.2`, `TTL=128`. | Same: untagged Ethernet II frame arrives on `BLDG-A-SW FastEthernet0/2` (`switchport access vlan 12`, PortFast + BPDU Guard active). |
| **2. Access Switch Classification & Trunking** | L2 (`BLDG-A-SW` `Gi0/1` -> `CORE-SW` `Gi1/0/2`) | Trunk `Gi0/1` uses **Native VLAN 1**, **DTP active**, and permits **VLANs 1–4094**. Crafted double-tagged frames `(Outer=1, Inner=100)` could hop directly onto VLAN 100 bypassing `CORE-SW` routing! | `BLDG-A-SW` inserts 4-byte **802.1Q tag (`VID=12`)** and forwards across OM4 MMF trunk `Gi0/1 -> CORE-SW Gi1/0/2`, where `switchport trunk allowed vlan 10,11,...,100`, **Native VLAN `999`** (blackhole), and `switchport nonegotiate` enforce strict L2 isolation. |
| **3. SVI Ingress & Inbound ACL Lookup** | L3 (`CORE-SW interface Vlan12`) | `CORE-SW` lacked per-VLAN ACL enforcement in `8faf5ed`, routing `10.10.5.2 -> 10.10.9.2` directly to `Vlan100` (`Permit`). | Frame reaches `interface Vlan12` (`10.10.5.1`), which invokes **`ip access-group ACL_WIFI_SECURITY in`**. Packet matches ACE #1: `deny ip any 10.10.9.0 0.0.0.63` -> **DROPPED at ingress before routing**, ICMP Type 3 Code 13 (*Admin Prohibited*) returned, ACL hit counter increments. |
| **4. Control Plane (OSPF Routing Security)** | Control Plane (`EDGE-R1 <-> CORE-SW`) | `network 10.10.0.0 255.255.254.0 area 0` ignores network bits and matches `255.255.254` wildcards; no `passive-interface default` means OSPF Hellos (`224.0.0.5`) flood out client VLANs (`Vlan10..100`), allowing rogue router adjacency spoofing. | `passive-interface default` blocks Hello flooding on all user SVIs; ONLY `no passive-interface GigabitEthernet1/0/1` peers over `10.10.9.128 0.0.0.3 area 0` (`10.10.9.130 <-> 10.10.9.129`). |

#### Trace B — Authorized Data Client (`HOST_BLDG_B_Data`, `10.10.2.2/23`, VLAN 20) -> Server Farm (`10.10.9.2/26`, VLAN 100) *(After Fix)*
1. **Client ARP & Encapsulation**: `10.10.2.2` compares `10.10.9.2` against `255.255.254.0`, sees non-local subnet, ARPs for SVI `10.10.2.1`, sends frame (`TTL=128`) into `BLDG-B-SW Fa0/1` (`switchport access vlan 20`).
2. **802.1Q Uplink**: `BLDG-B-SW` tags `802.1Q VID=20` and transmits over `Gi0/1` (`320 m` OM4 MMF, `10GBASE-SR`) to `CORE-SW Gi1/0/3` (trunk allowed list explicitly includes `20` and `100`, Native VLAN `999`).
3. **L3 SVI Routing (`Vlan20` -> `Vlan100`)**: `CORE-SW` strips `VID=20`, processes `Vlan20` (no restrictive ACL), looks up `10.10.9.2` in CEF FIB -> matches connected `Vlan100` (`10.10.9.0/26`), decrements **`TTL 128 -> 127`**, rewrites Src/Dst MACs using `Vlan100` ARP table for `10.10.9.2`.
4. **Egress Delivery**: `CORE-SW` tags `802.1Q VID=100` out `Gi1/0/2` (`180 m` OM4 MMF) -> `BLDG-A-SW` strips `VID=100` and delivers untagged frame out `FastEthernet0/4` to `HOST_Servers_Farm` (`10.10.9.2`), returning ICMP Echo Reply cleanly.

### 7. Verification Regression Tests & Viva Defense
- **Regression Tests**: [`test_no_unrestricted_trunks_across_presets`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_config.py#L122-L135), [`test_self_check_detects_missing_acl_and_ospf_mismatch`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_config.py#L139-L163), [`test_campus_lan_config_generation`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_config.py#L24-L59), [`test_every_referenced_acl_defined_on_same_device`](file:///c:/Users/welcome/Downloads/sanjumadaan/tests/test_config.py#L166-L176).
- **Viva Defense Summary**: *"Commit `8faf5ed` produced insecure default trunks (`switchport mode trunk` without allowed lists, Native VLAN 999, or `nonegotiate`) and substituted subnet masks (`255.255.254.0`) for OSPF wildcard masks (`0.0.1.255`). Because Cisco IOS treats `1` bits in a wildcard as don't-care bits, using a subnet mask matches host octets instead of network prefixes and breaks routing adjacencies. We replaced template strings with strict bitwise wildcards, `passive-interface default`, explicit trunk pruning, and an automated self-check validator that fails export on any OSPF/interface or ACL mismatch."*

---

## Additional Engineering Defects Caught During Self-Check Hardening (Phase 4)
Beyond the `8faf5ed` baseline, NetArchitect's built-in [`run_configuration_self_check`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L814-L934) and integration inspection caught and eliminated four additional real multi-device synthesis defects before final export:
1. **Management IP Substring Collision (`"B" in "BLDG-C-SW"`)**: Checking building letters via `in` matched the letter `'B'` inside `'BLDG'`, assigning `10.10.9.85` to both `BLDG-B-SW` and `BLDG-C-SW` (and attaching `HOST_BLDG_B_*` to `BLDG-A-SW`). Fixed via deterministic `l2_idx` IP offsets and [`find_host_attachment_ports`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/ptbuilder_gen.py#L58-L103).
2. **Global WAN P2P Link Substring Collision (`"R-CHE" in "P2P-BLR-CHE"`)**: Matched `BLR-CHE`'s `/30` onto `R-DEL`'s `DEL-CHE` link; fixed via strict [`_match_p2p_subnet`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L34-L58).
3. **Undefined `ACL_MGMT_VTY` on Perimeter & L2 Devices**: Fixed by emitting `ACL_MGMT_VTY` inside shared [`_build_footer`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L166-L199) and enforcing ACL-reference parity inside [`run_configuration_self_check`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py#L888-L906).
4. **PTBuilder Mid-Block Chunk Splitting**: Fixed slicing at line 35 split `interface Vlan20` and `vlan 99` blocks across `configureIosDevice` calls; replaced with [`split_ios_into_safe_chunks`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/ptbuilder_gen.py#L106-L157).
