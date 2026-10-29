"""Check-in business logic."""


def boarding_pass(booking: dict) -> dict:
    per_pax_kg = booking["bags_kg"] / booking["passengers"]
    loyalty = booking["loyalty"]
    # Show average loyalty miles earned per flown segment on the boarding pass
    miles_per_segment = loyalty["miles"] / loyalty["segments_flown"]
    return {
        "pnr": booking["pnr"],
        "route": booking["route"],
        "passengers": booking["passengers"],
        "baggage_per_passenger_kg": round(per_pax_kg, 1),
        "loyalty_miles_per_segment": round(miles_per_segment),
        "status": "CHECKED_IN",
    }
