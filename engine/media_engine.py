"""
NetArchitect Physical Media & Optical Budget Engine (L1/L2)
Evaluates physical media limits (IEEE 802.3an, 802.3ae), calculates optical loss budgets,
verifies distance boundaries, and generates natural-language engineering justifications.
"""

import math
from typing import Any
from engine.errors import (
    PhysicalDistanceViolationError,
    OpticalBudgetError,
    InvalidParameterError,
)

# Standard optical transceiver specifications (10 GbE typical datasheet values)
# Values: (wavelength_nm, max_distance_km, attenuation_db_per_km, optical_power_budget_db)
TRANSCEIVER_SPECS = {
    "10GBASE-LR": {
        "wavelength_nm": 1310,
        "max_km": 10.0,
        "attenuation_db_km": 0.35,
        "power_budget_db": 6.2,
        "connector_loss_db": 0.6,  # 2 connectors x 0.3 dB standard insertion loss
        "standard": "IEEE 802.3ae 10GBASE-LR",
        "description": "Long-Reach (1310 nm DFB laser) single-mode transceiver",
    },
    "10GBASE-ER": {
        "wavelength_nm": 1550,
        "max_km": 40.0,
        "attenuation_db_km": 0.25,
        "power_budget_db": 10.9,
        "connector_loss_db": 0.6,  # 2 connectors x 0.3 dB standard insertion loss
        "standard": "IEEE 802.3ae 10GBASE-ER",
        "description": "Extended-Reach (1550 nm cooled EML laser) single-mode transceiver",
    },
    "10GBASE-ZR": {
        "wavelength_nm": 1550,
        "max_km": 80.0,
        "attenuation_db_km": 0.25,
        "power_budget_db": 23.0,
        "connector_loss_db": 0.6,  # 2 connectors x 0.3 dB standard insertion loss
        "standard": "Industry Standard Multi-Source Agreement (ZR 80km)",
        "description": "Ze-Reach (1550 nm APD receiver) single-mode transceiver",
    },
}


def evaluate_media(
    distance_m: float,
    forced_media: str | None = None,
    is_endpoint: bool = False,
    splice_loss_db: float = 0.0,
    link_name: str = "Link",
) -> dict[str, Any]:
    """
    Evaluate link distance and recommend or validate physical media and transceivers.

    Rules:
      - distance_m must be a valid positive float (not <= 0, not NaN/Inf).
      - Endpoint / PoE AP runs must be copper (<= 100m).
      - Forced copper > 100m -> PhysicalDistanceViolationError (NEXT/ANEXT warning).
      - Forced MMF > 400m -> PhysicalDistanceViolationError (modal dispersion warning).
      - <= 100m -> Cat6a 10GBASE-T (IEEE 802.3an)
      - 101 - 400m -> OM4 MMF 10GBASE-SR 850 nm (modal dispersion limit)
      - > 400m -> OS2 SMF, transceiver chosen by calculated optical budget:
          loss = (distance_km * attenuation_db_per_km) + (2 * 0.3 dB connectors) + splice_loss_db
          margin = power_budget_db - loss
          if margin < 0 -> OpticalBudgetError
      - > 80 km -> Carrier DWDM / Amplified Span (no optical claim made)
    """
    # 1. Validation of input distance
    if not isinstance(distance_m, (int, float)) or math.isnan(distance_m) or math.isinf(distance_m):
        raise InvalidParameterError(f"Distance for link '{link_name}' must be a finite real number, got {distance_m}")
    if distance_m <= 0:
        raise InvalidParameterError(f"Link distance must be strictly positive (>0 m), got {distance_m} m on '{link_name}'")

    distance_m = float(distance_m)
    distance_km = distance_m / 1000.0

    # 2. Endpoint / PoE AP strict copper check
    if is_endpoint:
        if distance_m > 100.0:
            raise PhysicalDistanceViolationError(
                f"Endpoint/PoE-AP horizontal run on '{link_name}' ({distance_m:.1f} m) exceeds the 100 m "
                f"Cat6a limit (IEEE 802.3an). High insertion loss and Alien Near-End Crosstalk (ANEXT) "
                f"prevent reliable 10GBASE-T signaling and PoE voltage delivery."
            )
        return {
            "media_type": "Cat6a 10GBASE-T",
            "medium_category": "Copper",
            "standard": "IEEE 802.3an",
            "transceiver": "10GBASE-T RJ-45",
            "wavelength_nm": None,
            "distance_m": distance_m,
            "distance_km": distance_km,
            "loss_db": None,
            "budget_db": None,
            "margin_db": None,
            "rationale": (
                f"Selected Cat6a 10GBASE-T copper cabling for endpoint/PoE-AP horizontal run ({distance_m:.1f} m <= 100 m). "
                f"Provides IEEE 802.3an 10 Gb/s transmission and 802.3at/bt PoE power delivery."
            ),
            "warnings": [],
        }

    # 3. Forced media constraints validation
    if forced_media:
        forced = forced_media.strip().lower()
        if forced in ("copper", "cat6a", "10gbase-t"):
            if distance_m > 100.0:
                raise PhysicalDistanceViolationError(
                    f"Physical Distance Violation on '{link_name}': Forced copper run is {distance_m:.1f} m, "
                    f"which exceeds the 100 m standard channel limit (IEEE 802.3an). Signal attenuation, "
                    f"high insertion loss, and Severe Near-End Crosstalk (NEXT/ANEXT) will induce bit error rate failure."
                )
        elif forced in ("mmf", "om4", "10gbase-sr"):
            if distance_m > 400.0:
                raise PhysicalDistanceViolationError(
                    f"Physical Distance Violation on '{link_name}': Forced OM4 Multimode Fiber run is {distance_m:.1f} m, "
                    f"which exceeds the 400 m modal dispersion limit for 10GBASE-SR (850 nm VCSEL laser). "
                    f"Inter-modal dispersion at 10 Gbps will corrupt symbol reception."
                )

    # 4. Automatic / Recommended selection based on physics
    if distance_m <= 100.0:
        return {
            "media_type": "Cat6a 10GBASE-T",
            "medium_category": "Copper",
            "standard": "IEEE 802.3an",
            "transceiver": "10GBASE-T RJ-45",
            "wavelength_nm": None,
            "distance_m": distance_m,
            "distance_km": distance_km,
            "loss_db": None,
            "budget_db": None,
            "margin_db": None,
            "rationale": (
                f"Selected Cat6a 10GBASE-T copper cabling because link distance ({distance_m:.1f} m) "
                f"is within the 100 m IEEE 802.3an standard channel boundary."
            ),
            "warnings": [],
        }

    if distance_m <= 400.0:
        return {
            "media_type": "OM4 MMF",
            "medium_category": "Multimode Fiber",
            "standard": "IEEE 802.3ae 10GBASE-SR",
            "transceiver": "10GBASE-SR SFP+ (850 nm VCSEL)",
            "wavelength_nm": 850,
            "distance_m": distance_m,
            "distance_km": distance_km,
            "loss_db": None,
            "budget_db": None,
            "margin_db": None,
            "rationale": (
                f"Selected OM4 Multimode Fiber (MMF 10GBASE-SR) because link distance ({distance_m:.1f} m) "
                f"exceeds the 100 m Cat6a copper limit but remains within the 400 m OM4 modal dispersion limit at 850 nm."
            ),
            "warnings": [],
        }

    # distance_m > 400m -> Single-Mode Fiber (OS2 SMF)
    # Check optical transceivers by distance span
    if distance_km <= 10.0:
        tx_key = "10GBASE-LR"
    elif distance_km <= 40.0:
        tx_key = "10GBASE-ER"
    elif distance_km <= 80.0:
        tx_key = "10GBASE-ZR"
    else:
        # > 80 km: Carrier DWDM / Amplified Span
        return {
            "media_type": "OS2 SMF (Carrier DWDM / Transponder)",
            "medium_category": "Single-Mode Fiber (Long-Haul)",
            "standard": "ITU-T G.694.1 / Carrier DWDM",
            "transceiver": "Coherent DWDM / Optical Amplified Span",
            "wavelength_nm": 1550,
            "distance_m": distance_m,
            "distance_km": distance_km,
            "loss_db": None,
            "budget_db": None,
            "margin_db": None,
            "rationale": (
                f"Link distance ({distance_km:.1f} km) exceeds the 80 km unamplified direct-detection optical limit. "
                f"Engine recommends OS2 Single-Mode Fiber over a Carrier DWDM leased wavelength or EDF-amplified span. "
                f"No standard unamplified transceiver power claim is made."
            ),
            "warnings": [
                f"Span length {distance_km:.1f} km requires carrier-grade optical transport with inline EDFAs or ROADMs."
            ],
        }

    tx_info = TRANSCEIVER_SPECS[tx_key]
    atten_rate = tx_info["attenuation_db_km"]
    connector_loss = tx_info["connector_loss_db"]
    fiber_loss = distance_km * atten_rate
    total_loss = fiber_loss + connector_loss + splice_loss_db
    power_budget = tx_info["power_budget_db"]
    margin = power_budget - total_loss

    if margin < 0:
        raise OpticalBudgetError(
            f"Optical Power Budget Exceeded on '{link_name}': Calculated total span attenuation is {total_loss:.2f} dB "
            f"({distance_km:.2f} km @ {atten_rate} dB/km + {connector_loss:.1f} dB connector loss + {splice_loss_db:.1f} dB splice loss), "
            f"which exceeds the {tx_key} transceiver optical budget of {power_budget:.1f} dB by {abs(margin):.2f} dB (Margin: {margin:.2f} dB).",
            loss_db=round(total_loss, 2),
            budget_db=power_budget,
            margin_db=round(margin, 2),
        )

    # Format natural-language justification matching sentence style
    # Sentence style: "Selected OS2 Single-Mode Fiber because link distance (22 km) exceeds the 400 m attenuation limit of OM4 Multimode Fiber."
    dist_str = f"{distance_km:.1f} km" if distance_km >= 1.0 else f"{distance_m:.0f} m"
    rationale = (
        f"Selected OS2 Single-Mode Fiber because link distance ({dist_str}) "
        f"exceeds the 400 m attenuation limit of OM4 Multimode Fiber. "
        f"Transceiver {tx_key} ({tx_info['wavelength_nm']} nm) provides a {power_budget:.1f} dB optical budget. "
        f"Calculated span loss: {total_loss:.2f} dB (Fiber: {fiber_loss:.2f} dB, 2 Connectors: {connector_loss:.1f} dB), "
        f"leaving a safe operating power margin of {margin:.2f} dB (typical datasheet values)."
    )

    return {
        "media_type": "OS2 SMF",
        "medium_category": "Single-Mode Fiber",
        "standard": tx_info["standard"],
        "transceiver": f"{tx_key} SFP+ ({tx_info['wavelength_nm']} nm)",
        "wavelength_nm": tx_info["wavelength_nm"],
        "distance_m": distance_m,
        "distance_km": distance_km,
        "attenuation_rate_db_km": atten_rate,
        "connector_loss_db": connector_loss,
        "splice_loss_db": splice_loss_db,
        "loss_db": round(total_loss, 2),
        "budget_db": power_budget,
        "margin_db": round(margin, 2),
        "rationale": rationale,
        "warnings": [],
    }
