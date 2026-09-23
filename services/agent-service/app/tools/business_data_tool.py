from typing import Any


class LocalMockBusinessDataClient:
    """Read-only demonstration data; not a production enterprise system."""

    _reservations: dict[str, dict[str, Any]] = {
        "ABC123": {
            "reservation_id": "ABC123",
            "status": "confirmed",
            "check_in": "2026-10-15",
            "check_out": "2026-10-20",
            "cancellation_deadline": "2026-10-10",
            "cancellation_penalty": 0,
            "data_source": "LOCAL MOCK DATA",
        }
    }

    def get_reservation(self, reservation_id: str) -> dict[str, Any] | None:
        record = self._reservations.get(reservation_id.upper())
        return dict(record) if record else None
