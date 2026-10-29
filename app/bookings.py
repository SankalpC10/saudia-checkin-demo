"""Deterministic fake booking store: the same PNR always returns the same booking."""
import hashlib

ROUTES = ["JED-RUH", "RUH-DXB", "JED-CAI", "RUH-LHR", "DMM-JED", "MED-IST"]


def get_booking(pnr: str) -> dict:
    h = int(hashlib.sha256(pnr.upper().encode()).hexdigest(), 16)
    return {
        "pnr": pnr.upper(),
        "route": ROUTES[h % len(ROUTES)],
        "passengers": 1 + (h >> 8) % 4,
        "bags_kg": 23 * (1 + (h >> 16) % 3),
        # ~30% of travellers are new loyalty members with no segments flown yet
        "loyalty": {"miles": (h >> 24) % 50000, "segments_flown": 0 if (h >> 40) % 10 < 3 else 1 + (h >> 32) % 40},
    }
