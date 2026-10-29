"""Check-in business logic."""


def boarding_pass(booking: dict) -> dict:
    per_pax_kg = booking["bags_kg"] / booking["passengers"]
    return {
        "pnr": booking["pnr"],
        "route": booking["route"],
        "passengers": booking["passengers"],
        "baggage_per_passenger_kg": round(per_pax_kg, 1),
        "status": "CHECKED_IN",
    }
