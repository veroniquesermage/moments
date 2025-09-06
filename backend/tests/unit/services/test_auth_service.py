import pytest
from types import SimpleNamespace
from uuid import uuid4

from app.models import User, Group, UserGroup
from app.core.enum import RoleEnum
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.auth.change_password import ChangePassword
from app.schemas.user import UserSchema
from app.services.auth.auth_service import AuthService
from app.services.token_service import TokenService
from app.utils.password_utils import PasswordUtils


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_tokens_sets_cookies(unit_db_session):
    user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Foo", nom="Bar")
    unit_db_session.add(user)
    await unit_db_session.commit()
    await unit_db_session.refresh(user)

    resp = await AuthService.create_tokens(unit_db_session, UserSchema.from_user(user), remember_me=True)
    # Collect all Set-Cookie headers
    all_cookies = "\n".join(v.decode() for k, v in resp.raw_headers if k.decode().lower() == "set-cookie")
    assert "refresh_token=" in all_cookies
    assert "access_token=" in all_cookies


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_access_token_success(unit_db_session):
    user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Ref", nom="Token")
    unit_db_session.add(user)
    await unit_db_session.commit()
    await unit_db_session.refresh(user)

    # Create stored refresh token + actual JWT
    jti = uuid4().hex
    stored = await TokenService.store_refresh_token(unit_db_session, user.id, jti)
    token = TokenService.create_refresh_token({"sub": str(user.id), "jti": jti, "remember_me": True}, stored.expires_at)

    request = SimpleNamespace(cookies={"refresh_token": token})
    resp = await AuthService.refresh_access_token(unit_db_session, request)
    assert "refresh_token=" in resp.headers.get("set-cookie", "")
    assert resp.status_code == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_logout_deletes_cookies(unit_db_session):
    user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Out", nom="Log")
    unit_db_session.add(user)
    await unit_db_session.commit()
    await unit_db_session.refresh(user)

    jti = uuid4().hex
    stored = await TokenService.store_refresh_token(unit_db_session, user.id, jti)
    token = TokenService.create_refresh_token({"sub": str(user.id), "jti": jti, "remember_me": False}, stored.expires_at)

    request = SimpleNamespace(cookies={"refresh_token": token})
    resp = await AuthService.logout(unit_db_session, request)
    all_cookies = "\n".join(v.decode() for k, v in resp.raw_headers if k.decode().lower() == "set-cookie")
    # Ensure cookies cleared (Set-Cookie with Max-Age=0 or expires in past)
    assert "access_token=" in all_cookies
    assert "refresh_token=" in all_cookies
    assert ("max-age=0" in all_cookies.lower()) or ("expires=" in all_cookies.lower())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_change_password_flow(unit_db_session, mock_trace_service):
    raw = "oldpwd"
    hashed = PasswordUtils.hash_password(raw)
    user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="B", password=hashed)
    unit_db_session.add(user)
    await unit_db_session.commit()
    await unit_db_session.refresh(user)

    await AuthService.change_password(unit_db_session, user, ChangePassword(old_password=raw, new_password="newpwd"))
    # Verify changed
    refreshed = await unit_db_session.get(User, user.id)
    assert PasswordUtils.verify_password("newpwd", refreshed.password)

    # wrong old password
    with pytest.raises(Exception):
        await AuthService.change_password(unit_db_session, refreshed, ChangePassword(old_password="bad", new_password="x"))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_mail_and_request_password_reset(unit_db_session, monkeypatch):
    sent = {}

    async def fake_send_validation(db, email, token):
        sent["email"] = email
        sent["token"] = token
        return {"success": True}

    async def fake_send_token_password(db, email, token):
        sent["pwd_email"] = email
        sent["pwd_token"] = token
        return {"success": True}

    monkeypatch.setattr("app.services.mailing.mail_service.MailService.send_validation_email", fake_send_validation)
    monkeypatch.setattr("app.services.mailing.mail_service.MailService.send_token_password", fake_send_token_password)

    # Available email
    await AuthService.check_mail(unit_db_session, LoginRequest(email="avail@example.com", password="p", remember_me=True))
    assert "email" in sent and sent["email"] == "avail@example.com"

    # Existing user should raise
    user = User(email="exist@example.com", prenom="E", nom="X", password=PasswordUtils.hash_password("a"))
    unit_db_session.add(user)
    await unit_db_session.commit()

    with pytest.raises(Exception):
        await AuthService.check_mail(unit_db_session, LoginRequest(email="exist@example.com", password="p", remember_me=False))

    # request_password_reset should email
    await AuthService.request_password_reset(unit_db_session, "exist@example.com")
    assert sent.get("pwd_email") == "exist@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authenticate_credentials_user_and_reset_password(unit_db_session, mock_trace_service):
    # Signup flow
    token = TokenService.generate_signup_token("new@example.com", PasswordUtils.hash_password("pw"), remember_me=True)
    resp = await AuthService.authenticate_credentials_user(
        RegisterRequest(token=token, prenom="Neo", nom="Trinity"), unit_db_session
    )
    assert resp.status_code == 200

    # Reset password token flow
    pwd_token = TokenService.generate_password_token("new@example.com")
    reset_resp = await AuthService.reset_password(unit_db_session, request=SimpleNamespace(token=pwd_token, new_password="npw"))
    assert reset_resp.status_code == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_reset_token_valid_and_expired(unit_db_session, monkeypatch):
    email = "x@example.com"
    token = TokenService.generate_password_token(email)
    sub = await AuthService.verify_reset_token(unit_db_session, token)
    assert sub == email

    # Force expiration for new tokens
    from app.services.token_service import TokenService as TS
    old = TS.EXPIRATION_MINUTES_PASSWORD
    TS.EXPIRATION_MINUTES_PASSWORD = -1
    try:
        expired = TS.generate_password_token(email)
        with pytest.raises(Exception):
            await AuthService.verify_reset_token(unit_db_session, expired)
    finally:
        TS.EXPIRATION_MINUTES_PASSWORD = old


@pytest.mark.unit
@pytest.mark.asyncio
async def test_switch_to_tiers_and_parent(unit_db_session, mock_trace_service):
    # Setup parent and managed account
    parent = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Parent", nom="P")
    tiers = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Tiers", nom="T", is_compte_tiers=True)
    unit_db_session.add_all([parent, tiers])
    await unit_db_session.commit()
    await unit_db_session.refresh(parent)
    await unit_db_session.refresh(tiers)

    tiers.gere_par = parent.id
    await unit_db_session.commit()

    group = Group(nom_groupe="GAuth", description=None, code=uuid4().hex[:10])
    unit_db_session.add(group)
    await unit_db_session.commit()
    await unit_db_session.refresh(group)

    # both must be in group for each check to pass
    unit_db_session.add_all([
        UserGroup(utilisateur_id=tiers.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=parent.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # switch to tiers
    resp1 = await AuthService.switch_to_tiers(unit_db_session, tiers.id, parent, group.id)
    assert resp1.status_code == 200

    # switch to parent (from child)
    resp2 = await AuthService.switch_to_parent(unit_db_session, tiers, group.id)
    assert resp2.status_code == 200
