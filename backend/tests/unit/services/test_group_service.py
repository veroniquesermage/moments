import pytest
from uuid import uuid4
from sqlalchemy import text

from app.core.enum import RoleEnum
from app.models import User, Group, UserGroup
from app.schemas.group import GroupCreate, GroupUpdate
from app.services.group_service import GroupService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_and_join_group_flow(unit_db_session, mock_trace_service):
    # Arrange
    creator = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Jim", nom="Beam")
    joiner = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Jack", nom="D")
    unit_db_session.add_all([creator, joiner])
    await unit_db_session.commit()
    await unit_db_session.refresh(creator)
    await unit_db_session.refresh(joiner)

    # Create group
    created = await GroupService.create_group(
        unit_db_session, creator, GroupCreate(nom_groupe="Famille", description="desc")
    )
    assert created.nom_groupe == "Famille"

    # Ensure creator is admin of the group
    ug = (await unit_db_session.execute(
        text("SELECT role FROM utilisateur_groupe WHERE utilisateur_id = :u AND groupe_id = :g"),
        {"u": creator.id, "g": created.id},
    )).first()
    assert ug is not None and ug[0] == RoleEnum.ADMIN

    # Join with code
    group_db = await GroupService.get_group(unit_db_session, created.id)
    joined = await GroupService.join_group(unit_db_session, joiner, group_db.code)
    assert joined.id == created.id

    # get_groups for joiner
    groups = await GroupService.get_groups(unit_db_session, joiner)
    assert len(groups) == 1 and groups[0].id == created.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_join_group_invalid_code(unit_db_session):
    u = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="B")
    unit_db_session.add(u)
    await unit_db_session.commit()
    await unit_db_session.refresh(u)

    with pytest.raises(Exception):
        await GroupService.join_group(unit_db_session, u, "NOTACODE")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_group_admin_only(unit_db_session, mock_trace_service):
    admin = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Admin", nom="A")
    member = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Member", nom="M")
    group = Group(nom_groupe="G", description="d", code=uuid4().hex[:10])
    unit_db_session.add_all([admin, member, group])
    await unit_db_session.commit()
    for obj in (admin, member, group):
        await unit_db_session.refresh(obj)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=admin.id, groupe_id=group.id, role=RoleEnum.ADMIN),
        UserGroup(utilisateur_id=member.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # Non admin cannot update
    with pytest.raises(Exception):
        await GroupService.update_group(
            unit_db_session, member, GroupUpdate(nom_groupe="Nouveau", description=None), group.id
        )

    # Admin can update
    updated = await GroupService.update_group(
        unit_db_session, admin, GroupUpdate(nom_groupe="Nouveau", description=None), group.id
    )
    assert updated.nom_groupe == "Nouveau"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_code_invitation_changes(unit_db_session, mock_trace_service):
    admin = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Admin", nom="A")
    group = Group(nom_groupe="G2", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([admin, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(admin)
    await unit_db_session.refresh(group)

    unit_db_session.add(UserGroup(utilisateur_id=admin.id, groupe_id=group.id, role=RoleEnum.ADMIN))
    await unit_db_session.commit()

    old = group.code
    await GroupService.update_code_invitation(unit_db_session, admin, group.id)
    # reload
    group_db = await GroupService.get_group(unit_db_session, group.id)
    assert group_db.code != old


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_group_details(unit_db_session, mock_trace_service):
    admin1 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Alfa", nom="Z")
    admin2 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Bravo", nom="Z")
    viewer = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Viewer", nom="V")
    group = Group(nom_groupe="GG", description=None, code="LMNOPQRSTU")
    unit_db_session.add_all([admin1, admin2, viewer, group])
    await unit_db_session.commit()
    for obj in (admin1, admin2, viewer, group):
        await unit_db_session.refresh(obj)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=admin1.id, groupe_id=group.id, role=RoleEnum.ADMIN, surnom="Cap"),
        UserGroup(utilisateur_id=admin2.id, groupe_id=group.id, role=RoleEnum.ADMIN),
        UserGroup(utilisateur_id=viewer.id, groupe_id=group.id, role=RoleEnum.MEMBRE, surnom="V1"),
    ])
    await unit_db_session.commit()

    details = await GroupService.get_group_details(unit_db_session, viewer, group.id)
    assert details.groupe.id == group.id
    # admins list: surname if exists else prenom
    assert "Cap" in details.admins
    assert admin2.prenom in details.admins
    assert details.surnom == "V1"
    assert details.prenom == viewer.prenom


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_group_as_admin(unit_db_session, mock_trace_service):
    admin = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Admin", nom="A")
    group = Group(nom_groupe="ToDelete", description=None, code="Q" * 10)
    unit_db_session.add_all([admin, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(admin)
    await unit_db_session.refresh(group)

    unit_db_session.add(UserGroup(utilisateur_id=admin.id, groupe_id=group.id, role=RoleEnum.ADMIN))
    await unit_db_session.commit()

    await GroupService.delete_group(unit_db_session, admin, group.id)

    with pytest.raises(Exception):
        await GroupService.get_group(unit_db_session, group.id)
