"""
UI Smoke Tests (Streamlit AppTest)
Verifies app.py and all 11 Streamlit page modules render cleanly with zero exceptions
and tests interactive Custom Designer error-trigger buttons without crashes.
"""

from pathlib import Path
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def test_streamlit_all_11_pages_render_without_exception():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    assert not at.exception, f"App failed on boot: {at.exception}"

    pages = list(at.sidebar.radio[0].options)
    assert len(pages) == 11

    for page_name in pages:
        at.sidebar.radio[0].set_value(page_name).run()
        assert not at.exception, f"Page '{page_name}' raised exception: {at.exception}"


def test_streamlit_preset_switching_and_custom_fault_buttons():
    at = AppTest.from_file(APP_PATH, default_timeout=25)
    at.run()

    # Switch across all 3 presets and verify core pages render with live MAN/WAN charts & edge tables
    for preset in list(at.sidebar.selectbox[0].options):
        at.sidebar.selectbox[0].set_value(preset).run()
        assert not at.exception, f"Preset '{preset}' failed on Dashboard: {at.exception}"
        for subpage in (
            "Physical Media",
            "VLSM Calculator",
            "Routing & Architecture",
            "Cisco Config Generator",
            "Architectural Decision Log",
            "Packet Tracer Verification",
        ):
            at.sidebar.radio[0].set_value(subpage).run()
            assert not at.exception, f"Preset '{preset}' failed on '{subpage}': {at.exception}"

    # Open Custom Network Designer and click all 3 adversarial fault test buttons
    at.sidebar.radio[0].set_value("Custom Network Designer").run()
    assert not at.exception

    dist_btn = next(b for b in at.button if "Distance Violation" in b.label)
    dist_btn.click().run()
    assert not at.exception

    addr_btn = next(b for b in at.button if "Address Exhaustion" in b.label)
    addr_btn.click().run()
    assert not at.exception

    opt_btn = next(b for b in at.button if "Optical Budget" in b.label)
    opt_btn.click().run()
    assert not at.exception


def test_streamlit_routing_page_works_without_scipy(monkeypatch):
    """Ensure Streamlit Cloud environments without optional scipy render Routing & Architecture cleanly."""
    import sys

    monkeypatch.setitem(sys.modules, "scipy", None)
    at = AppTest.from_file(APP_PATH, default_timeout=25)
    at.run()
    for preset in list(at.sidebar.selectbox[0].options):
        at.sidebar.selectbox[0].set_value(preset).run()
        at.sidebar.radio[0].set_value("Routing & Architecture").run()
        assert not at.exception, f"Routing & Architecture failed without scipy for '{preset}': {at.exception}"
