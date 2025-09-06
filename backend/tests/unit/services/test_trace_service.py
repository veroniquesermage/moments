import pytest
from sqlalchemy import text

from app.services.trace_service import TraceService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_trace_inserts(unit_db_session):
    await TraceService.record_trace(
        unit_db_session,
        utilisateur="Test User",
        trace_type="UNIT",
        message="Trace message",
        payload={"k": "v"},
    )

    row = (await unit_db_session.execute(
        text("SELECT utilisateur, type, message FROM traces WHERE type = 'UNIT'")
    )).first()
    assert row is not None
    assert row[0] == "Test User"
    assert row[1] == "UNIT"
    assert row[2] == "Trace message"
