# audit/raw/raw_media.py
# Raw AI generated code before adversarial audit
def recommend_media(distance_m: float, forced_media: str | None = None, is_endpoint: bool = False):
    if distance_m <= 0:
        raise Exception(f"Distance must be positive, got {distance_m}")
    if forced_media == "copper":
        return {"media_type": "Cat6a 10GBASE-T", "distance_m": distance_m}
    if distance_m <= 100:
        return {"media_type": "Cat6a 10GBASE-T"}
    elif distance_m <= 400:
        return {"media_type": "OM4 MMF"}
    else:
        dist_km = distance_m / 1000.0
        loss = dist_km * 0.35 # Missing connector losses (2 x 0.3 dB)
        budget = 6.2
        margin = budget - loss
        return {"media_type": "OS2 SMF", "loss_db": loss, "margin_db": margin}
