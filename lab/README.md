# Cisco Packet Tracer Lab Pack & PTBuilder Automation Guide

This folder contains reproducible Cisco Packet Tracer lab manuals (`lab_guide.md`) and programmatic JavaScript topology builders (`ptbuilder_<preset>.js`) for all three NetArchitect presets (`campus_lan`, `metro_man`, `global_wan`).

> [!IMPORTANT]
> **Verification Notice**: These configurations and automation scripts have been validated algorithmically by NetArchitect's automated self-check and unit tests. They have **not** been pre-executed in Cisco Packet Tracer — please follow the verification checklists inside each preset's `lab_guide.md` and capture screenshots once you run them in your Packet Tracer environment.

---

## 1. Installing PTBuilder (`github.com/kimmknight/PTBuilder`)

1. Open **Cisco Packet Tracer** (v8.2.x or newer recommended).
2. Download or clone `PTBuilder` from `https://github.com/kimmknight/PTBuilder`.
3. Follow the repository instructions to place the `.js` / `.ptb` extension files into your Packet Tracer extensions folder, or open **Extensions > Scripting > Configure PtScript Modules** (depending on your PT version).
4. Once enabled, open **Extensions > Builder Code Editor** inside Packet Tracer.

---

## 2. Running a Generated Script

1. Open the desired preset script:
   - `lab/campus_lan/ptbuilder_campus_lan.js`
   - `lab/metro_man/ptbuilder_metro_man.js`
   - `lab/global_wan/ptbuilder_global_wan.js`
2. Copy the **entire JavaScript file** and paste it into the **Builder Code Editor** window in Packet Tracer.
3. Click **Run** (`Execute`).
4. PTBuilder will automatically:
   - Place every router, L3 switch, and L2 switch on a clean grid layout.
   - Connect every physical link with exact interface names and straight/crossover cables.
   - Spawn 1 test `PC-PT` or `Server-PT` per subnet and configure static IP, mask, and gateway via `configurePcIp()`.
   - Push the Cisco IOS configurations in safe `<= 40`-line batches (`L2 Switches -> L3 Switches -> Routers`).
5. Click **Fast Forward Time** (`Alt+D`) twice in Packet Tracer to accelerate Rapid-PVST+ and OSPF/BGP neighbor convergence.

---

## 3. What To Do When a Command Fails in Packet Tracer

Cisco Packet Tracer simulates a subset of real Cisco IOS commands. If a command or cable fails during automated execution or manual paste:

1. **Missing Power Supply on Catalyst 3650-24PS (`% Ambiguous / Invalid interface`)**:
   - In Packet Tracer, a `3650-24PS` switch ships **powered off** without a PSU inserted.
   - Click the `CORE-SW` / `HQ-CORE` icon -> **Physical** tab -> drag an **`AC-POWER-SUPPLY`** into the power bay, wait for boot, then re-paste the config from `lab_guide.md`.
2. **Router Port Count Exceeded on `2911` (`R-DEL` in Global WAN)**:
   - A stock `2911` router has 3 built-in ports (`Gi0/0`, `Gi0/1`, `Gi0/2`). `R-DEL` requires 4+ ports (`Gi0/3`).
   - Power off the router in **Physical** view, insert an **`EHWIC-4ESG`** or **`HWIC-1GE-SFP`** module (or swap to `Router-PT` with `PT-ROUTER-NM-1CGE` modules), power on, and adjust the interface slot name if your PT version assigns `Gi0/1/0` instead of `Gi0/3`.
3. **IPsec Crypto Profile Errors on Global WAN**:
   - Basic Packet Tracer router IOS images often reject `crypto ipsec profile` commands on GRE tunnels.
   - Generate configurations with `--no-crypto`:
     ```bash
     python cli.py --preset wan --out exports/ --no-crypto --emit-ptbuilder
     ```
4. **Trunk Encapsulation Rejection (`2960` vs `3650` / `3560`)**:
   - `2960-24TT` L2 switches do not support `switchport trunk encapsulation dot1q` (NetArchitect omits it automatically on `2960`).
   - L3 switch configs include `switchport trunk encapsulation dot1q` for `3560-24PS` / `3650-24PS` compatibility; if your `3650-24PS` PT version runs IOS-XE (dot1q-only) and prints `% Invalid input` for that single line, the immediately following `switchport mode trunk` command still applies cleanly (*verify in your PT version*).
5. **Checking Line-by-Line CLI Errors**:
   - Open the device's **CLI** tab and inspect any `% Invalid input detected at '^' marker` line, then match against Section (f) & (h) of `lab/<preset>/lab_guide.md`.
