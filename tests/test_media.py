"""
Unit Tests for Physical Media & Optical Budget Engine (IEEE 802.3an, 802.3ae)
Tests:
  - Distance boundary transitions: 100 vs 101 m, 400 vs 401 m
  - Optical boundary transitions: 10 vs 10.001 km, 40 vs 40.001 km, 80 vs 81 km
  - Error conditions: 0 distance, negative distance, NaN, Inf
  - Forced copper > 100 m -> PhysicalDistanceViolationError
  - Forced MMF > 400 m -> PhysicalDistanceViolationError
  - Excessive splice/fiber loss -> OpticalBudgetError
"""

import pytest
import math
from engine.media_engine import evaluate_media
from engine.errors import (
    PhysicalDistanceViolationError,
    OpticalBudgetError,
    InvalidParameterError,
)


def test_copper_cat6a_boundary():
    # 100 m is maximum valid Cat6a copper distance
    res = evaluate_media(100.0)
    assert res["media_type"] == "Cat6a 10GBASE-T"
    assert res["medium_category"] == "Copper"
    assert "802.3an" in res["standard"]


def test_mmf_boundary_lower():
    # 101 m transitions to OM4 Multimode Fiber (MMF 10GBASE-SR)
    res = evaluate_media(101.0)
    assert res["media_type"] == "OM4 MMF"
    assert res["transceiver"] == "10GBASE-SR SFP+ (850 nm VCSEL)"
    assert res["wavelength_nm"] == 850


def test_mmf_boundary_upper():
    # 400 m is the maximum OM4 modal dispersion limit at 10 Gbps
    res = evaluate_media(400.0)
    assert res["media_type"] == "OM4 MMF"


def test_smf_boundary_transition():
    # 401 m transitions to Single-Mode Fiber (OS2 SMF 10GBASE-LR)
    res = evaluate_media(401.0)
    assert res["media_type"] == "OS2 SMF"
    assert "10GBASE-LR" in res["transceiver"]
    assert res["wavelength_nm"] == 1310


def test_lr_boundary_10km():
    # 10.0 km uses 10GBASE-LR (budget 6.2 dB)
    res = evaluate_media(10000.0)
    assert "10GBASE-LR" in res["transceiver"]
    assert res["loss_db"] == round(10.0 * 0.35 + 0.6, 2)  # 4.10 dB
    assert res["margin_db"] > 0


def test_lr_to_er_boundary_10_001km():
    # 10.001 km (10,001 m) transitions from LR to ER (1550 nm, budget 10.9 dB)
    res = evaluate_media(10001.0)
    assert "10GBASE-ER" in res["transceiver"]
    assert res["wavelength_nm"] == 1550


def test_er_boundary_40km():
    # 40.0 km uses 10GBASE-ER
    res = evaluate_media(40000.0)
    assert "10GBASE-ER" in res["transceiver"]
    assert res["margin_db"] > 0


def test_er_to_zr_boundary_40_001km():
    # 40.001 km (40,001 m) transitions from ER to ZR (budget 23.0 dB)
    res = evaluate_media(40001.0)
    assert "10GBASE-ZR" in res["transceiver"]


def test_zr_boundary_80km():
    # 80.0 km uses 10GBASE-ZR
    res = evaluate_media(80000.0)
    assert "10GBASE-ZR" in res["transceiver"]
    assert res["margin_db"] > 0


def test_zr_to_dwdm_boundary_81km():
    # 81 km exceeds direct detection optics -> requires Carrier DWDM / Amplified Span
    res = evaluate_media(81000.0)
    assert "Carrier DWDM" in res["media_type"]
    assert res["loss_db"] is None
    assert len(res["warnings"]) > 0


def test_invalid_distance_zero():
    with pytest.raises(InvalidParameterError):
        evaluate_media(0.0)


def test_invalid_distance_negative():
    with pytest.raises(InvalidParameterError):
        evaluate_media(-50.0)


def test_invalid_distance_nan():
    with pytest.raises(InvalidParameterError):
        evaluate_media(float("nan"))


def test_invalid_distance_inf():
    with pytest.raises(InvalidParameterError):
        evaluate_media(float("inf"))


def test_forced_copper_violation():
    # Forced copper at 100.1 m must raise PhysicalDistanceViolationError
    with pytest.raises(PhysicalDistanceViolationError) as exc_info:
        evaluate_media(100.1, forced_media="copper")
    assert "Physical Distance Violation" in str(exc_info.value)
    assert "100 m" in str(exc_info.value)


def test_forced_mmf_violation():
    # Forced MMF at 401 m must raise PhysicalDistanceViolationError
    with pytest.raises(PhysicalDistanceViolationError) as exc_info:
        evaluate_media(401.0, forced_media="om4")
    assert "modal dispersion" in str(exc_info.value)


def test_endpoint_copper_only():
    # Endpoints beyond 100m must raise error
    with pytest.raises(PhysicalDistanceViolationError):
        evaluate_media(105.0, is_endpoint=True)


def test_optical_budget_error():
    # Adding high artificial splice loss to exceed 10GBASE-LR budget
    with pytest.raises(OpticalBudgetError) as exc_info:
        evaluate_media(9000.0, splice_loss_db=15.0)  # 9km * 0.35 + 0.6 + 15 = 18.75 > 6.2 dB
    assert exc_info.value.loss_db > exc_info.value.budget_db
    assert exc_info.value.margin_db < 0


def test_optical_budget_connector_and_splice_math():
    # 22 km ER (1550 nm): 22 * 0.25 dB/km = 5.5 dB + 0.6 dB connectors + 0.4 dB splice = 6.5 dB
    # Budget is 10.9 dB -> Margin = 10.9 - 6.5 = 4.4 dB
    res = evaluate_media(22000.0, splice_loss_db=0.4)
    assert res["loss_db"] == 6.5
    assert res["budget_db"] == 10.9
    assert res["margin_db"] == 4.4


def test_sentence_style_justification():
    # Verify exact sentence structure from rubric
    res = evaluate_media(22000.0)
    assert "Selected OS2 Single-Mode Fiber because link distance (22.0 km) exceeds the 400 m attenuation limit of OM4 Multimode Fiber." in res["rationale"]
