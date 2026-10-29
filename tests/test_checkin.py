from fastapi.testclient import TestClient

from app.bookings import get_booking
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_checkin_returns_boarding_pass():
    body = client.post("/checkin/ABC123").json()
    assert body["status"] == "CHECKED_IN"
    assert body["pnr"] == "ABC123"


def test_booking_is_deterministic():
    assert get_booking("xyz789") == get_booking("XYZ789")
