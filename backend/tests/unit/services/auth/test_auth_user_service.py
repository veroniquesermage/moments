import pytest
from uuid import uuid4

from app.models import User, Group, UserGroup
from app.core.enum import RoleEnum
from app.schemas.auth.complete_profile import CompleteProfileRequest
from app.schemas.user_tiers_request import UserTiersRequest
from app.services.auth.user_service import UserService
from app.utils.password_utils import PasswordUtils


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_and_create_user(unit_db_session, mock_trace_service):
    email = f"{uuid4().hex[:8]}@ex.com"
    # get_or_create -> create
    user_schema, created = await UserService.get_or_create_user(unit_db_session, email, "A", "B", "gid")
    assert created is True and user_schema.email is None  # email optional in schema, but user is created

    # create_user conflict
    with pytest.raises(Exception):
        await UserService.create_user(unit_db_session, email, "A", "B", PasswordUtils.hash_password("x"))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_id_and_mail_and_ensure_mail_available(unit_db_session):
    u1 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="U1", nom="N1", password=PasswordUtils.hash_password("p"))
    u2 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="U2", nom="N2", google_id="gid")
    unit_db_session.add_all([u1, u2])
    await unit_db_session.commit()
    await unit_db_session.refresh(u1)
    await unit_db_session.refresh(u2)

    # get by id/mail
    by_id = await UserService.get_user_by_id(unit_db_session, u1.id)
    assert by_id.id == u1.id
    by_mail = await UserService.get_user_by_mail(unit_db_session, u2.email)
    assert by_mail.id == u2.id

    # ensure_mail_available cases
    avail = await UserService.ensure_mail_available(unit_db_session, "free@example.com")
    assert avail is True
    with pytest.raises(Exception):
        await UserService.ensure_mail_available(unit_db_session, u1.email)  # has password -> 409
    with pytest.raises(Exception):
        await UserService.ensure_mail_available(unit_db_session, u2.email)  # google id -> 423


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_and_change_and_reset_password(unit_db_session, mock_trace_service):
    u = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Old", nom="Name", password=PasswordUtils.hash_password("a"))
    unit_db_session.add(u)
    await unit_db_session.commit()
    await unit_db_session.refresh(u)

    # complete
    sch = await UserService.complete_user(unit_db_session, u.id, CompleteProfileRequest(given_name="New", family_name="Family"))
    assert sch.prenom == "New" and sch.nom == "Family"

    # change password
    user_changed = await UserService.change_password(unit_db_session, u.email, PasswordUtils.hash_password("b"))
    assert user_changed.password is not None

    # reset password by email
    sch2 = await UserService.reset_password(unit_db_session, u.email, PasswordUtils.hash_password("c"))
    assert sch2.has_password is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_and_get_managed_accounts(unit_db_session, mock_trace_service):
    parent = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Par", nom="Ent")
    group = Group(nom_groupe="UG", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([parent, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(parent)
    await unit_db_session.refresh(group)

    unit_db_session.add(UserGroup(utilisateur_id=parent.id, groupe_id=group.id, role=RoleEnum.MEMBRE))
    await unit_db_session.commit()

    req = UserTiersRequest(prenom="Kid", nom="K", surnom="Kiki")
    tiers = await UserService.create_managed_account(req, parent, group.id, unit_db_session)
    assert tiers.prenom == "Kid" and tiers.is_compte_tiers is True

    # ensure present in group
    managed = await UserService.get_managed_account(parent, group.id, unit_db_session)
    assert any(u.prenom == "Kid" for u in managed)

