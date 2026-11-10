"""
First unreviewed AI draft for Media Engine.
"""
from engine.errors import PhysicalDistanceViolationError, OpticalBudgetError, InvalidParameterError

# Typical AI draft for media recommendation
def recommend_media(distance_m: float, forced_media: str | None = None, is_endpoint: bool = False):
    if distance_m <= 0:
        raise InvalidParameterError(f"Distance must be positive, got {distance_m}")
    
    if is_endpoint and distance_m > 100:
        raise PhysicalDistanceViolationError("Endpoint runs must be copper and <= 100m")

    # Raw AI implementation:
    if forced_media == "copper":
        # Raw AI flaw: forgets to check distance_m > 100 when forced!
        return {
            "media_type": "Cat6a 10GBASE-T",
            "standard": "IEEE 802.3an",
            "distance_m": distance_m,
            "transceiver": "10GBASE-T RJ45"
        }

    if distance_m <= 100:
        return {
            "media_type": "Cat6a 10GBASE-T",
            "standard": "IEEE 802.3an",
            "distance_m": distance_m,
            "transceiver": "10GBASE-T RJ45",
            "rationale": "Selected Cat6a (10GBASE-T) because run is <= 100m."
        }
    elif distance_m <= 400:
        return {
            "media_type": "OM4 MMF",
            "standard": "10GBASE-SR",
            "distance_m": distance_m,
            "transceiver": "10GBASE-SR (850nm)",
            "rationale": "Selected OM4 MMF (10GBASE-SR) for backbone run 101-400m."
        }
    else:
        # Distance > 400m OS2 SMF
        dist_km = distance_m / 1000.0
        # Raw AI flaw in optical budget: calculates loss as dist_km * 0.35 without connector loss (2 * 0.3 dB)
        if dist_km <= 10:
            loss = dist_km * 0.35
            budget = 6.2
            transceiver = "10GBASE-LR (1310nm)"
        elif dist_km <= 40:
            loss = dist_km * 0.25
            budget = 10.9
            transceiver = "10GBASE-ER (1550nm)"
        elif dist_km <= 80:
            loss = dist_km * 0.25 # Raw AI flaw: wrong attenuation coefficient for ZR or missing connector budget
            budget = 23.0
            transceiver = "10GBASE-ZR (1550nm)"
        else:
            return {
                "media_type": "OS2 SMF",
                "transceiver": "Carrier DWDM / Amplified Span",
                "distance_km": dist_km,
                "loss_db": None,
                "budget_db": None,
                "margin_db": None,
                "rationale": "Beyond 80 km carrier DWDM / amplified span required."
            }
        
        margin = budget - loss
        if margin < 0:
            raise OpticalBudgetError("Optical power budget exceeded")
            
        return {
            "media_type": "OS2 SMF",
            "transceiver": transceiver,
            "distance_km": dist_km,
            "loss_db": round(loss, 2),
            "budget_db": budget,
            "margin_db": round(margin, 2),
            "rationale": f"Selected OS2 Single-Mode Fiber because distance exceeds 400m."
        }
