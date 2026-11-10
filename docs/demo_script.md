# NetArchitect — 3-Minute Timed Video & Viva Walkthrough Script

**Presenter**: Sanju Madaan · **Roll No.**: `00714803124` · **Batch / Section**: `5C1` · **Course**: CIC-307  

> **Total Runtime**: 3 minutes 00 seconds (`180 s`) · Screen record VS Code terminal + Streamlit Light Pastel Dashboard (and Packet Tracer if executed locally).

---

### [0:00 – 0:30] Introduction, Problem Statement & 3 Presets (`30 s`)
- **Action**: Show [Dashboard] with **Campus LAN** loaded in the pastel UI.
- **Narration**: *"Hi, I'm presenting NetArchitect for CIC-307 Computer Networks. Manual enterprise network planning breaks easily due to miscalculated VLSM masks, under-estimated optical attenuation, or permissive switch configs. NetArchitect solves this deterministically using pure bitwise Python arithmetic, explainable Architectural Decision Records, and a validated Cisco IOS + PTBuilder generator—without external LLMs or API keys."*
- **Action**: Click **Scenario Selection**, briefly switch to **Metro MAN** and **Global WAN** to show live recalculated metrics.

### [0:30 – 1:10] Custom Validation Faults & Bitwise VLSM (`40 s`)
- **Action**: Navigate to **Custom Network Designer** -> click **Test Distance Violation** and **Test Address Exhaustion**.
- **Narration**: *"Our validation layer enforces physical laws and capacity limits strictly. Forcing copper beyond 100 m immediately raises `PhysicalDistanceViolationError` citing IEEE 802.3an NEXT/ANEXT degradation, while overflowing a /24 triggers `AddressSpaceExhaustedError` safely without crashing the app."*
- **Action**: Switch to **VLSM Calculator** on Campus LAN and hover over the **Address-Space Block Map** + show the **Arithmetic Step** column (`300 hosts + 2 = 302 -> 512 = 2^9 -> /23`).
- **Narration**: *"All prefixes, masks, and ~mask wildcards are calculated using bitwise `<<`, `&`, `|`, and `~` in descending power-of-two order with zero overlap—verified by a 300-case fuzz suite against Python's `ipaddress` oracle inside `pytest`."*

### [1:10 – 1:50] Physical Media Budget, Topology Graph & Explainable ADRs (`40 s`)
- **Action**: Switch to **Physical Media** (Metro MAN loaded) showing the Plotly **Optical Power Budget vs. Span Loss** bar chart; then open **Routing & Architecture**.
- **Narration**: *"On Metro MAN links, every 10 GbE SMF span counts fiber loss plus 0.6 dB for dual connectors. On the interactive topology graph, edges are colored by medium with 5 us/km + 50 us/hop latency calculation, N-1 single-link failover simulation, and MQC EF queuing—framed as an uncontended design objective rather than a guarantee."*
- **Action**: Open **Architectural Decision Log** and expand 1–2 `"Why?"` records + show **Download rationale.md**.

### [1:50 – 2:30] AI Adversarial Audit Log & Packet-Flow Analysis (`40 s`)
- **Action**: Switch to **AI Audit Lab**, show **Flaw #1 (Two's Complement Wildcard Bug)**, **Flaw #2 (Missing 0.6 dB Connector Loss / Copper Bypass)**, and **Flaw #3 (Unconstrained Trunk & OSPF Wildcard)** side-by-side diffs + Packet-Flow Trace table.
- **Narration**: *"In commit `8faf5ed`, the unreviewed draft forgot `& 0xFFFFFFFF`, producing a negative 40-bit wildcard `-1099511627521`, let NaN fall through to DWDM, emitted unconstrained VLAN 1–4094 trunks, and used subnet masks inside OSPF. We trace exactly how ACL `ACL_WIFI_SECURITY`, Native VLAN 999, `nonegotiate`, and wildcard matching drop unauthorized WiFi traffic while forwarding authorized Data VLAN frames."*

### [2:30 – 3:00] Cisco Configs, PTBuilder Automation & Test Proof (`30 s`)
- **Action**: Show **Cisco Config Generator** (`CORE-SW` tab showing SVI ACLs, OSPF wildcards, explicit trunks, Self-Check PASSED badge, `.zip` download) -> **Packet Tracer Verification** showing `ptbuilder_campus_lan.js` -> switch briefly to VS Code terminal running `pytest -v` showing `all tests PASSED`.
- **Narration**: *"Every export passes automated zero-duplicate-IP, ACL completeness, and OSPF-interface parity self-checks before generating copy-paste `.cfg` files and block-safe PTBuilder scripts. Thank you!"*

---

### Quick Viva Q&A Preparation
- **Why `& 0xFFFFFFFF` in `(~mask) & 0xFFFFFFFF`?** Python integers have arbitrary bit width; unary `~` flips infinite leading zeros into negative two's-complement numbers (`-0xFFFFFFFF01`). Masking `& 0xFFFFFFFF` clamps cleanly to 32-bit unsigned IPv4 space.
- **Why Passive-Interface Default in OSPF?** Stops OSPF Hellos (`224.0.0.5`) from flooding user VLANs (`Vlan10..100`) where malicious hosts could spoof DR/BDR adjacencies.
- **Why Native VLAN 999 + `nonegotiate`?** Neutralizes DTP spoofing and double-tagged VLAN hopping attacks via Native VLAN 1.
- **Why `--no-crypto` on Global WAN PT mode?** Basic Cisco Packet Tracer IOS router images omit `crypto ipsec profile` support on GRE tunnels; toggling `--no-crypto` yields valid clean GRE tunnels for PT lab convergence while preserving full IPsec AES-256 profiles for real IOS hardware.
