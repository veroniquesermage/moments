import pytest

from app.services.auth.login_attempt_service import LoginAttemptService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_attempt_increment_block_and_reset(unit_db_session):
    email = "block@example.com"

    # Initially not blocked
    assert await LoginAttemptService.is_blocked(unit_db_session, email) is False

    # Increment attempts MAX times
    for _ in range(LoginAttemptService.MAX_ATTEMPTS):
        await LoginAttemptService.increment_attempt(unit_db_session, email)

    # Should be blocked now
    assert await LoginAttemptService.is_blocked(unit_db_session, email) is True

    # Reset and check
    await LoginAttemptService.reset_attempts(unit_db_session, email)
    assert await LoginAttemptService.is_blocked(unit_db_session, email) is False

