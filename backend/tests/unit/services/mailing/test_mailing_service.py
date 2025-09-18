import pytest
from uuid import uuid4

from app.core.enum import GiftStatusEnum, RoleEnum
from app.models import User, Group, UserGroup, Gift
from app.schemas.mailing import FeedbackRequest
from app.schemas.mailing.invite_request import InviteRequest
from app.services.mailing.mail_service import MailService


class DummyResp:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {"ok": True}

    def json(self):
        return self._payload


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_feedback_success_and_error(unit_db_session, monkeypatch):
    user = User(email=f"{uuid4().hex[:8]}@example.com", prenom="U", nom="N")
    unit_db_session.add(user)
    await unit_db_session.commit()
    await unit_db_session.refresh(user)

    # Success path
    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_feedback",
        lambda feedback_request, current_user: DummyResp(200),
    )
    await MailService.send_feedback(FeedbackRequest(composant="c", commentaire="x"), unit_db_session, user)

    # Error path -> non-200 triggers HTTPException
    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_feedback",
        lambda feedback_request, current_user: DummyResp(500, {"err": True}),
    )
    with pytest.raises(Exception):
        await MailService.send_feedback(FeedbackRequest(composant="c", commentaire="x"), unit_db_session, user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_invites_filters_existing_and_handles_status(unit_db_session, monkeypatch):
    # Setup group and users
    existing_email = f"{uuid4().hex[:8]}@example.com"
    new_email = f"{uuid4().hex[:8]}@example.com"
    owner = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Own", nom="Er")
    member = User(email=existing_email, prenom="Mem", nom="Ber")
    unit_db_session.add_all([owner, member])
    await unit_db_session.commit()
    await unit_db_session.refresh(owner)
    await unit_db_session.refresh(member)

    group = Group(nom_groupe="GMail", description=None)
    unit_db_session.add(group)
    await unit_db_session.commit()
    await unit_db_session.refresh(group)

    # Add member to group so it will be filtered out
    unit_db_session.add_all([
        UserGroup(utilisateur_id=owner.id, groupe_id=group.id, role=RoleEnum.ADMIN),
        UserGroup(utilisateur_id=member.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    captured = {}

    def fake_send_invites(invitations_data, group_resp, current_user):
        # should have filtered 'exists@example.com'
        captured["emails"] = [invitation['email'] for invitation in invitations_data]
        return DummyResp(200)

    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_invites_with_tokens",
        fake_send_invites,
    )

    invites = InviteRequest(emails=[existing_email, new_email])
    await MailService.send_invites(invites, group.id, unit_db_session, owner)
    assert captured.get("emails") == [new_email]

    # Error path -> non-200 raises
    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_invites_with_tokens",
        lambda invitations_data, group_resp, current_user: DummyResp(500, {"err": True}),
    )
    with pytest.raises(Exception):
        await MailService.send_invites(invites, group.id, unit_db_session, owner)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_alert_update_does_not_raise(unit_db_session, monkeypatch):
    dest = User(email=f"{uuid4().hex[:8]}@example.com", prenom="D", nom="D")
    reserver = User(email=f"{uuid4().hex[:8]}@example.com", prenom="R", nom="R")
    unit_db_session.add_all([dest, reserver])
    await unit_db_session.commit()
    await unit_db_session.refresh(dest)
    await unit_db_session.refresh(reserver)

    gift = Gift(destinataire_id=dest.id, nom="Obj", priorite=1, statut=GiftStatusEnum.RESERVE, reserve_par_id=reserver.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    async def ok_adapter(g, u):
        return DummyResp(200)

    async def ko_adapter(g, u):
        return DummyResp(500)

    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_alert_update",
        ok_adapter,
    )
    await MailService.send_alert_update(gift, dest, unit_db_session)

    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_alert_update",
        ko_adapter,
    )
    # Should not raise even if non-200
    await MailService.send_alert_update(gift, dest, unit_db_session)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validation_and_password_mails(unit_db_session, monkeypatch):
    # Success paths
    async def ok_validation(email, token):
        return DummyResp(200)

    async def ok_reset(email, token):
        return DummyResp(200)

    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_validation_email",
        ok_validation,
    )
    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_token_password",
        ok_reset,
    )

    uniq = f"{uuid4().hex[:8]}@example.com"
    await MailService.send_validation_email(unit_db_session, uniq, "tok")
    await MailService.send_token_password(unit_db_session, uniq, "tok")

    # Error paths
    async def ko_validation(email, token):
        return DummyResp(500, {"err": True})

    async def ko_reset(email, token):
        return DummyResp(500, {"err": True})

    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_validation_email",
        ko_validation,
    )
    monkeypatch.setattr(
        "app.services.mailing.mailjet_adapter.MailjetAdapter.send_token_password",
        ko_reset,
    )

    with pytest.raises(Exception):
        await MailService.send_validation_email(unit_db_session, uniq, "tok")
    with pytest.raises(Exception):
        await MailService.send_token_password(unit_db_session, uniq, "tok")
