# NetArchitect Architecture Specification

## 1. Design Philosophy
NetArchitect separates **pure algorithmic synthesis (`engine/`)**, **static topologies (`scenarios/`)**, **verification (`tests/`)**, and **presentation (`ui/`)** so every calculation can run headless from CLI/pytest or interactively in Streamlit with identical results.

---

## 2. Engine Subsystem Breakdown

### `engine/errors.py`
Defines the strict exception hierarchy rooted at `NetArchitectError`:
- `PhysicalDistanceViolationError` (Cat6a >100 m, OM4 >400 m, horizontal endpoint >100 m)
- `OpticalBudgetError` (calculated span attenuation exceeds transceiver power budget)
- `AddressSpaceExhaustedError` (remaining VLSM space cannot satisfy aligned power-of-two block)
- `LatencyBudgetError` (baseline or post-failover shortest-path latency exceeds design budget)
- `ResiliencyViolationError` (N-1 single-link removal partitions a redundant topology)
- `InvalidParameterError` (bad CIDR, host bits set, NaN/Inf/<=0 distance, VLAN 1002–1005, duplicates, self-check errors)

### `engine/addr.py` & `engine/vlsm_engine.py`
- Zero reliance on Python `ipaddress` outside `tests/`.
- `need = hosts + 2` -> `prefix = 32 - ceil(log2(need))` (with optional RFC 3021 `/31` for explicit P2P links and `/32` for loopbacks).
- Sorted descending stably; cursor alignment enforced via `(cursor + size - 1) & ~(size - 1)`.
- Subnet masks computed as `(0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF`; wildcards as `(~mask) & 0xFFFFFFFF`.
- Contiguous group allocation (`group_by="group"`) prevents cross-area leakage in Global WAN so ABR `area <id> range` summaries align cleanly (`summarize_subnets()` reports `exact: bool`).

### `engine/media_engine.py`
- Evaluates `Cat6a 10GBASE-T` (`<=100 m`), `OM4 MMF 10GBASE-SR` (`101–400 m`), `OS2 SMF 10GBASE-LR` (`<=10 km`, `6.2 dB`), `10GBASE-ER` (`<=40 km`, `10.9 dB`), `10GBASE-ZR` (`<=80 km`, `23.0 dB`), and Carrier DWDM (`>80 km`).
- Optical formula: `loss_db = distance_km * attenuation_db_km + 2 * 0.3 + splice_loss_db`.

### `engine/topology.py` & `engine/routing_engine.py`
- Builds an undirected weighted NetworkX graph (`latency_us = distance_km * 5.0 + 50.0`).
- Verifies connectivity, baseline worst-case latency, and simulates every single-link failure (`N-1`).
- Computes `core_backbone_resilient` and `is_resilient_n_minus_1` dynamically from evaluation outcomes.
- Routing rules: 1 site and `<50` subnets -> OSPF Area 0 (`RFC 2328`); multi-site or `>=50` subnets -> Multi-Area OSPF (`RFC 4632` ABR ranges); cloud/multi-AS -> eBGP (`RFC 4271`, `RFC 6996`).

### `engine/config_generator.py`, `engine/ptbuilder_gen.py` & `engine/lab_pack.py`
- Synthesizes complete device configs (L2 `2960-24TT`, L3 `3650-24PS`, `2911`/`ISR4331`).
- Enforces `run_configuration_self_check()`: zero duplicate IPs, zero subnet overlaps (`<=` half-open check), `wildcard == (~mask) & 0xFFFFFFFF`, explicit trunk VLANs matching declared scenario VLANs, OSPF network-to-interface subnet matching, and ACL reference completeness.
- `ptbuilder_gen.py` inspects the generated device configs via `find_host_attachment_ports()` and chunks IOS CLI pushes into logical block-safe `<=38`-line calls via `split_ios_into_safe_chunks()`.
