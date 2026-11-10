# NetArchitect Verification Guide

## 1. Automated Verification (`pytest -v`)
Run the full automated unit, fuzz-oracle, pipeline, and Streamlit smoke suite:
```bash
pip install -r requirements.txt
pytest -v
```
This executes checks across:
- **Media physics** (`tests/test_media.py`): distance boundaries `100/101/400/401 m`, `10/40/80/81 km`, `0`/`negative`/`NaN`/`Inf`, forced copper/MMF violations, connector + splice optical math.
- **Bitwise VLSM oracle parity** (`tests/test_vlsm.py`): 300-case seeded fuzz tests against Python's `ipaddress.IPv4Network`, wildcard arithmetic across `/0`–`/32`, exact boundary fits, `+1` host exhaustion, RFC 3021 `/31`, and contiguous multi-area group allocation.
- **Routing & Topology** (`tests/test_routing.py`, `tests/test_topology.py`): `49` vs `50` subnet OSPF boundary, exact vs. covering route summaries, `5 us/km + 50 us/hop` latency, N-1 partition errors, and latency budget exceptions.
- **Validation & IOS Self-Check** (`tests/test_validation.py`, `tests/test_config.py`, `tests/test_ptbuilder.py`): unrestricted trunk prevention, duplicate IP rejection, OSPF/interface mismatch detection, missing ACL detection, and block-safe PTBuilder chunking.
- **Streamlit UI Smoke Tests** (`tests/test_ui_smoke.py`): renders all 11 UI pages and interactive fault buttons cleanly.

---

## 2. CLI Export Verification
Generate fresh Cisco IOS configs, rationales, lab guides, and PTBuilder scripts:
```bash
python cli.py --preset campus --out exports/ --platform pt --emit-ptbuilder
python cli.py --preset man    --out exports/ --platform pt --emit-ptbuilder
python cli.py --preset wan    --out exports/ --no-crypto --platform pt --emit-ptbuilder
```
Confirm `[OK] ... passed self-check` prints for every preset.

---

## 3. Manual Cisco Packet Tracer Verification (Local Student Execution)
> NetArchitect never claims topologies were verified inside Packet Tracer unless you actually run them in your local Packet Tracer install.

1. Open [lab/README.md](file:///c:/Users/welcome/Downloads/sanjumadaan/lab/README.md) and install PTBuilder (`github.com/kimmknight/PTBuilder`).
2. Load `lab/<preset>/ptbuilder_<preset>.js` inside Packet Tracer **Extensions > Builder Code Editor** and click **Run** (or paste Section (d) manually per `lab/<preset>/lab_guide.md` in strict order: `L2 -> L3 -> Routers`).
3. Power `3650-24PS` switches (`AC-POWER-SUPPLY` in Physical view) and expand 4-port `2911` routers (`R-DEL`) if needed.
4. Execute and screenshot every checklist command in Section (f) of `lab/<preset>/lab_guide.md`:
   - `show ip interface brief`
   - `show vlan brief`
   - `show interfaces trunk`
   - `show spanning-tree`
   - `show ip route` & `show ip ospf neighbor` (& `show ip bgp summary` on Global WAN)
   - `show access-lists` + **MUST FAIL** Campus WiFi-to-Server ping test (`10.10.5.2 -> 10.10.9.2`)
   - **Failover test**: `shutdown` primary Metro MAN / WAN link and verify reconvergence.
