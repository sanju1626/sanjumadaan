# NetArchitect Submission & Deployment Checklist

**Student**: Sanju Madaan · **Roll No.**: `00714803124` · **Batch / Section**: `5C1` · **Course**: CIC-307  

## 1. Completed Code & Automated Deliverables
- [x] Pure bitwise VLSM + RFC 3021 /31 + RFC 4632 group summaries ([`engine/addr.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/addr.py), [`engine/vlsm_engine.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/vlsm_engine.py))
- [x] L1 Physical Media & Optical Budget Engine ([`engine/media_engine.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/media_engine.py))
- [x] Deterministic Routing, Topology Tier & N-1 Graph Resiliency ([`engine/routing_engine.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/routing_engine.py), [`engine/topology.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/topology.py))
- [x] Explainable Decision Records ([`engine/decision_engine.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/decision_engine.py))
- [x] Strict Custom Parameter Validation ([`engine/validation.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/validation.py))
- [x] Cisco IOS Generator + Self-Check Validator ([`engine/config_generator.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/config_generator.py))
- [x] Reproducible PTBuilder Scripts & Lab Guides ([`engine/ptbuilder_gen.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/ptbuilder_gen.py), [`engine/lab_pack.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/engine/lab_pack.py), [`lab/`](file:///c:/Users/welcome/Downloads/sanjumadaan/lab/))
- [x] 3 Exported Preset Configurations & Rationales ([`exports/`](file:///c:/Users/welcome/Downloads/sanjumadaan/exports/))
- [x] 11-Page Light Pastel Streamlit Web App ([`app.py`](file:///c:/Users/welcome/Downloads/sanjumadaan/app.py), [`ui/`](file:///c:/Users/welcome/Downloads/sanjumadaan/ui/), [`.streamlit/config.toml`](file:///c:/Users/welcome/Downloads/sanjumadaan/.streamlit/config.toml))
- [x] Genuine Adversarial AI Audit Log from commit `8faf5ed` ([`ai_audit_log.md`](file:///c:/Users/welcome/Downloads/sanjumadaan/ai_audit_log.md))
- [x] Documentation & Demo Guide ([`README.md`](file:///c:/Users/welcome/Downloads/sanjumadaan/README.md), [`docs/`](file:///c:/Users/welcome/Downloads/sanjumadaan/docs/))

---

## 2. Manual User Action Items Required Before Final Turn-In

### Action A — Push Clean Final Commit to GitHub
```bash
git status
git add .
git commit -m "Complete NetArchitect CIC-307 application, exports, lab pack, AI audit log, and docs"
git branch -M main
git remote add origin https://github.com/<your-username>/NetArchitect.git
git push -u origin main
```

### Action B — Deploy Live Hosted Site on Streamlit Community Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Create app** -> select `<your-username>/NetArchitect` (`main` branch).
3. Set **Main file path**: `app.py`.
4. Click **Deploy** and confirm all 11 pages load using `requirements.txt` (zero secrets needed).

### Action C — Run Three Topologies in Cisco Packet Tracer & Save Screenshots
1. Open Cisco Packet Tracer (v8.2+ recommended).
2. Follow [`lab/README.md`](file:///c:/Users/welcome/Downloads/sanjumadaan/lab/README.md) to run `ptbuilder_campus_lan.js`, `ptbuilder_metro_man.js`, and `ptbuilder_global_wan.js` (remember `AC-POWER-SUPPLY` on `3650-24PS` & `EHWIC` port module on `R-DEL`).
3. Verify each item in Section (f) of each `lab/<preset>/lab_guide.md` and capture screenshots (topologies, `show vlan brief`, `show interfaces trunk`, `show ip route`, MUST-FAIL ACL ping test, and failover test).

### Action D — Record 3-Minute Demo & Viva Video
Follow [`docs/demo_script.md`](file:///c:/Users/welcome/Downloads/sanjumadaan/docs/demo_script.md) (`3:00` runtime) walking through the hosted/local Streamlit UI, tests, Packet Tracer verification, and AI Audit Log findings.
