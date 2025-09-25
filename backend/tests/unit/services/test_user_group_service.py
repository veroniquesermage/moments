import pytest
from uuid import uuid4
from sqlalchemy import text

from fastapi import HTTPException

from app.core.enum import RoleEnum, GiftStatusEnum
from app.models import User, Group, UserGroup, Gift
from app.schemas import UserDisplaySchema, ExportManagedAccountRequest
from app.schemas.mailing.invite_request import InviteRequest
from app.services.user_group_service import UserGroupService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_users_lists(unit_db_session):
    a = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="A")
    b = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="B", nom="B")
    c = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="C", nom="C")
    g = Group(nom_groupe="G1", description=None)
    unit_db_session.add_all([a, b, c, g])
    await unit_db_session.commit()
    for o in (a, b, c, g):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=a.id, groupe_id=g.id, role=RoleEnum.ADMIN, surnom="AA"),
        UserGroup(utilisateur_id=b.id, groupe_id=g.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=c.id, groupe_id=g.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # get all
    all_users = await UserGroupService.get_users(unit_db_session, g.id)
    assert {u.id for u in all_users} == {a.id, b.id, c.id}

    # get except current
    others = await UserGroupService.get_users_except_current_user(unit_db_session, a, g.id)
    assert {u.id for u in others} == {b.id, c.id}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_group_admins_and_user_group(unit_db_session):
    admin = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Admin", nom="A")
    member = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Mem", nom="M")
    g = Group(nom_groupe="G2", description=None)
    unit_db_session.add_all([admin, member, g])
    await unit_db_session.commit()
    for o in (admin, member, g):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=admin.id, groupe_id=g.id, role=RoleEnum.ADMIN),
        UserGroup(utilisateur_id=member.id, groupe_id=g.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    admins = await UserGroupService.get_group_admins(unit_db_session, g.id)
    assert len(admins) == 1 and admins[0].utilisateur_id == admin.id

    ug = await UserGroupService.get_user_group(unit_db_session, member.id, g.id)
    assert ug is not None and ug.utilisateur_id == member.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nickname_and_delete_self(unit_db_session, mock_trace_service):
    u = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="U", nom="U")
    g = Group(nom_groupe="G3", description=None)
    unit_db_session.add_all([u, g])
    await unit_db_session.commit()
    await unit_db_session.refresh(u)
    await unit_db_session.refresh(g)

    unit_db_session.add(UserGroup(utilisateur_id=u.id, groupe_id=g.id, role=RoleEnum.MEMBRE))
    await unit_db_session.commit()

    await UserGroupService.update_nickname(unit_db_session, u, g.id, "Nick")
    row = (await unit_db_session.execute(
        text("SELECT surnom FROM utilisateur_groupe WHERE utilisateur_id = :u AND groupe_id = :g"),
        {"u": u.id, "g": g.id},
    )).first()
    assert row[0] == "Nick"

    # delete self (leave group)
    await UserGroupService.delete_user_group(unit_db_session, u, g.id, None)
    left = (await unit_db_session.execute(
        text("SELECT 1 FROM utilisateur_groupe WHERE utilisateur_id = :u AND groupe_id = :g"),
        {"u": u.id, "g": g.id},
    )).first()
    assert left is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_member_as_admin_and_update_role(unit_db_session, mock_trace_service):
    admin = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Admin", nom="A")
    member = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Mem", nom="M")
    g = Group(nom_groupe="G4", description=None)
    unit_db_session.add_all([admin, member, g])
    await unit_db_session.commit()
    for o in (admin, member, g):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=admin.id, groupe_id=g.id, role=RoleEnum.ADMIN),
        UserGroup(utilisateur_id=member.id, groupe_id=g.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # Update role as admin
    updated = await UserGroupService.update_role(
        unit_db_session,
        g.id,
        admin,
        [UserDisplaySchema(id=member.id, prenom=member.prenom, nom=member.nom, role=RoleEnum.ADMIN, is_compte_tiers=False)],
    )
    # returns others than current user
    assert any(u.id == member.id for u in updated)

    # Delete member as admin
    await UserGroupService.delete_user_group(unit_db_session, admin, g.id, member.id)
    left = (await unit_db_session.execute(
        text("SELECT 1 FROM utilisateur_groupe WHERE utilisateur_id = :u AND groupe_id = :g"),
        {"u": member.id, "g": g.id},
    )).first()
    assert left is None

    # Non admin exclusion should fail
    # Re-add member
    unit_db_session.add(UserGroup(utilisateur_id=member.id, groupe_id=g.id, role=RoleEnum.MEMBRE))
    await unit_db_session.commit()
    with pytest.raises(Exception):
        await UserGroupService.delete_user_group(unit_db_session, member, g.id, admin.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_user_to_group_and_duplicates(unit_db_session):
    u = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="U", nom="U")
    g = Group(nom_groupe="G5", description=None)
    unit_db_session.add_all([u, g])
    await unit_db_session.commit()
    await unit_db_session.refresh(u)
    await unit_db_session.refresh(g)

    ug = await UserGroupService.add_user_to_group(unit_db_session, g.id, u.id, "S")
    assert ug.utilisateur_id == u.id and ug.groupe_id == g.id

    with pytest.raises(Exception):
        await UserGroupService.add_user_to_group(unit_db_session, g.id, u.id, "S")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_groups_for_user_and_existing_emails(unit_db_session):
    a = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="A")
    b = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="B", nom="B")
    g1 = Group(nom_groupe="G6", description=None)
    g2 = Group(nom_groupe="G7", description=None)
    unit_db_session.add_all([a, b, g1, g2])
    await unit_db_session.commit()
    for o in (a, b, g1, g2):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=a.id, groupe_id=g1.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=a.id, groupe_id=g2.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=b.id, groupe_id=g1.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    groups = await UserGroupService.get_all_groups_for_user(unit_db_session, a.id)
    assert set(groups) == {g1.id, g2.id}

    existing_emails = await UserGroupService.get_existing_users_in_group(
        unit_db_session, g1.id, InviteRequest(emails=[a.email, "x@y.z"])
    )
    assert existing_emails == [a.email]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_users_with_shared_groups(unit_db_session):
    a = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="A")
    b = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="B", nom="B")
    c = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="C", nom="C")
    g1 = Group(nom_groupe="G8", description=None)
    g2 = Group(nom_groupe="G9", description=None)
    unit_db_session.add_all([a, b, c, g1, g2])
    await unit_db_session.commit()
    for o in (a, b, c, g1, g2):
        await unit_db_session.refresh(o)

    # a shares groups with b and c
    unit_db_session.add_all([
        UserGroup(utilisateur_id=a.id, groupe_id=g1.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=b.id, groupe_id=g1.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=a.id, groupe_id=g2.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=c.id, groupe_id=g2.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    users = await UserGroupService.get_users_with_shared_groups(unit_db_session, [g1.id, g2.id], a.id)
    assert {u.id for u in users} == {b.id, c.id}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_tiers_from_group_success_and_errors(unit_db_session, mock_trace_service):
    parent = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Par", nom="Ent")
    tiers = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Kid", nom="K", is_compte_tiers=True)
    stranger = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Str", nom="A")
    group = Group(nom_groupe="GRT", description=None)
    unit_db_session.add_all([parent, tiers, stranger, group])
    await unit_db_session.commit()
    for o in (parent, tiers, stranger, group):
        await unit_db_session.refresh(o)

    # Assign management
    tiers.gere_par = parent.id
    await unit_db_session.commit()

    # Add tiers to group
    unit_db_session.add_all([
        UserGroup(utilisateur_id=parent.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=tiers.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # Success removal by parent
    await UserGroupService.remove_tiers_from_group(unit_db_session, parent, group.id, tiers.id)
    left = (await unit_db_session.execute(
        text("SELECT 1 FROM utilisateur_groupe WHERE utilisateur_id = :u AND groupe_id = :g"),
        {"u": tiers.id, "g": group.id},
    )).first()
    assert left is None

    # Error: not managed by current user
    with pytest.raises(HTTPException):
        await UserGroupService.remove_tiers_from_group(unit_db_session, stranger, group.id, tiers.id)

    # Error: not in group
    with pytest.raises(HTTPException):
        await UserGroupService.remove_tiers_from_group(unit_db_session, parent, group.id, tiers.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_forgotten_members_detection(unit_db_session):
    """Test la détection des membres oubliés (tous leurs cadeaux sont DISPONIBLE)"""

    # Créer des utilisateurs et un groupe
    current_user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Current", nom="User")
    forgotten_user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Forgotten", nom="User")
    not_forgotten_user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="NotForgotten", nom="User")
    no_gifts_user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="NoGifts", nom="User")
    group = Group(nom_groupe="TestGroup", description="Test")

    unit_db_session.add_all([current_user, forgotten_user, not_forgotten_user, no_gifts_user, group])
    await unit_db_session.commit()
    for o in (current_user, forgotten_user, not_forgotten_user, no_gifts_user, group):
        await unit_db_session.refresh(o)

    # Ajouter les utilisateurs au groupe
    unit_db_session.add_all([
        UserGroup(utilisateur_id=current_user.id, groupe_id=group.id, role=RoleEnum.ADMIN),
        UserGroup(utilisateur_id=forgotten_user.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=not_forgotten_user.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=no_gifts_user.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # Créer des cadeaux
    # forgotten_user : tous ses cadeaux sont DISPONIBLE -> oublié
    gift1 = Gift(
        destinataire_id=forgotten_user.id,
        nom="Gift 1",
        priorite=1,
        statut=GiftStatusEnum.DISPONIBLE
    )
    gift2 = Gift(
        destinataire_id=forgotten_user.id,
        nom="Gift 2",
        priorite=2,
        statut=GiftStatusEnum.DISPONIBLE
    )

    # not_forgotten_user : au moins un cadeau réservé -> pas oublié
    gift3 = Gift(
        destinataire_id=not_forgotten_user.id,
        nom="Gift 3",
        priorite=1,
        statut=GiftStatusEnum.DISPONIBLE
    )
    gift4 = Gift(
        destinataire_id=not_forgotten_user.id,
        nom="Gift 4",
        priorite=2,
        statut=GiftStatusEnum.RESERVE,
        reserve_par_id=current_user.id  # Réservé par current_user
    )

    # no_gifts_user : aucun cadeau -> pas oublié

    unit_db_session.add_all([gift1, gift2, gift3, gift4])
    await unit_db_session.commit()

    # Tester la méthode get_users_except_current_user
    users = await UserGroupService.get_users_except_current_user(unit_db_session, current_user, group.id)

    # Vérifier les résultats (current_user ne doit pas être dans les résultats)
    users_by_id = {u.id: u for u in users}
    assert current_user.id not in users_by_id, "current_user should not be in results"

    # forgotten_user doit être marqué comme oublié (tous ses cadeaux sont DISPONIBLE)
    forgotten = users_by_id[forgotten_user.id]
    assert forgotten.is_forgotten is True, f"forgotten_user should be forgotten but is_forgotten={forgotten.is_forgotten}"

    # not_forgotten_user ne doit pas être oublié (a un cadeau réservé)
    not_forgotten = users_by_id[not_forgotten_user.id]
    assert not_forgotten.is_forgotten is False, f"not_forgotten_user should not be forgotten but is_forgotten={not_forgotten.is_forgotten}"

    # no_gifts_user ne doit pas être oublié (aucun cadeau)
    no_gifts = users_by_id[no_gifts_user.id]
    assert no_gifts.is_forgotten is False, f"no_gifts_user should not be forgotten but is_forgotten={no_gifts.is_forgotten}"
