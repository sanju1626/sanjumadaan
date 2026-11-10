# NetArchitect Design Decisions & Engineering Rationale

1. **Pure Bitwise Integer Arithmetic over String Manipulation or `ipaddress`**
   - *Decision*: Implement IPv4 parsing, subnet masks, inverted wildcards, power-of-two alignment, and non-overlap verification solely via bit shifts (`<<`, `>>`), AND (`&`), OR (`|`), and bounded NOT (`~x & 0xFFFFFFFF`), isolating Python's `ipaddress` module inside `tests/` as an oracle.
   - *Rationale*: Demonstrates foundational CIDR binary arithmetic in a Computer Networks viva while catching real Python sign-extension pitfalls (see Audit Flaw #1 in [ai_audit_log.md](file:///c:/Users/welcome/Downloads/sanjumadaan/ai_audit_log.md)).

2. **Contiguous Group Allocation (`group_by="group"`) for Multi-Area OSPF**
   - *Decision*: Align each OSPF Area's VLSM blocks within its own power-of-two boundary before advancing the global allocation cursor.
   - *Rationale*: Naive global descending sort scatters areas across non-contiguous CIDRs, making Cisco ABR `area <id> range` route summarization either impossible or overly broad (leaking Cloud VPC space into Area 1).

3. **Single-Area vs. Multi-Area OSPF Boundary (`< 50` vs. `>= 50` Subnets / Multi-Site)**
   - *Decision*: Trigger Area 0 for single-site networks under 50 subnets, switching to Multi-Area OSPF (`RFC 4632` ABR summaries) for `>= 50` subnets or multi-site topologies, and isolating external Cloud domains via eBGP (`RFC 4271` / `RFC 6996` private ASNs `65001–65010`).
   - *Rationale*: Keeps SPF Dijkstra database size and LSA flooding bounded at scale without premature multi-area ABR complexity on small single-site campuses.

4. **Strict L1 Media Boundaries & Connector-Inclusive Optical Budgeting**
   - *Decision*: Include `2 x 0.3 dB = 0.6 dB` LC/SC connector losses plus fusion splice losses on all `>400 m` SMF runs and explicitly disallow forced copper (`>100 m`) or MMF (`>400 m`).
   - *Rationale*: Prevents marginal long-haul links from passing false optical feasibility checks and flags `>80 km` DWDM links honestly without fabricated transceiver margins.

5. **Block-Safe PTBuilder Chunking & Config Self-Check**
   - *Decision*: Parse generated IOS files into intact multi-line blocks (`interface`, `vlan`, `router ospf`, `line`) before batching into `<=38`-line `configureIosDevice()` calls, and enforce pre-export self-checks across all generated devices.
   - *Rationale*: Prevents `enable`/`configure terminal` resets mid-interface block inside PTBuilder and eliminates duplicate IPs, undefined ACLs, and substring host-cabling collisions.
