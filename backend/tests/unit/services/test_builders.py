import pytest
import pytest_asyncio

from app.core.enum import RoleEnum, GiftStatusEnum
from app.models import User, Group, UserGroup, Gift, GiftIdeas, GiftShared
from app.schemas import UserDisplaySchema
from app.services.builders import (
    build_user_display,
    build_user_tiers,
    build_gift_public_response,
    build_gift_idea_schema,
    build_gift_shared_schema,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_build_user_display_success(unit_db_session):
    user = User(email="u1@example.com", prenom="U1", nom="Test")
    group = Group(nom_groupe="G1", description="")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    ug = UserGroup(utilisateur_id=user.id, groupe_id=group.id, role=RoleEnum.ADMIN, surnom="Boss")
    unit_db_session.add(ug)
    await unit_db_session.commit()

    display = await build_user_display(user.id, group.id, unit_db_session)
    assert isinstance(display, UserDisplaySchema)
    assert display.id == user.id
    assert display.surnom == "Boss"
    assert display.role == RoleEnum.ADMIN


@pytest.mark.unit
@pytest.mark.asyncio
async def test_build_user_display_not_in_group_raises(unit_db_session):
    user = User(email="u2@example.com", prenom="U2", nom="Test")
    group = Group(nom_groupe="G2", description="")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    with pytest.raises(Exception):
        await build_user_display(user.id, group.id, unit_db_session)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_build_gift_public_response_basic(unit_db_session):
    # Arrange: users and group
    dest = User(email="dest@example.com", prenom="Dest", nom="One")
    group = Group(nom_groupe="Gifts", description=None)
    unit_db_session.add_all([dest, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(dest)
    await unit_db_session.refresh(group)

    unit_db_session.add(UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE))
    await unit_db_session.commit()

    gift = Gift(
        destinataire_id=dest.id,
        nom="Livre",
        description="Roman",
        priorite=1,
        statut=GiftStatusEnum.DISPONIBLE,
        prix=25.0,
    )
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    # Act
    resp = await build_gift_public_response(gift, group.id, unit_db_session)

    # Assert
    assert resp.id == gift.id
    assert resp.destinataire.id == dest.id
    assert resp.nom == "Livre"
    assert resp.statut == GiftStatusEnum.DISPONIBLE
    assert resp.reserve_par is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_build_gift_idea_and_shared_schema(unit_db_session):
    # Arrange users, group and memberships
    preneur = User(email="p@example.com", prenom="Preneur", nom="P")
    participant = User(email="pa@example.com", prenom="Part", nom="T")
    proposer = User(email="pp@example.com", prenom="Prop", nom="E")
    dest = User(email="d@example.com", prenom="Dest", nom="D")
    group = Group(nom_groupe="G3", description=None)
    unit_db_session.add_all([preneur, participant, proposer, dest, group])
    await unit_db_session.commit()
    for u in (preneur, participant, proposer, dest):
        await unit_db_session.refresh(u)
    await unit_db_session.refresh(group)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=preneur.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=participant.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=proposer.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    idea = GiftIdeas(proposee_par_id=proposer.id, visibilite=True)
    unit_db_session.add(idea)
    await unit_db_session.commit()
    await unit_db_session.refresh(idea)

    gift = Gift(
        destinataire_id=dest.id,
        nom="Jeu",
        priorite=1,
        statut=GiftStatusEnum.DISPONIBLE,
        gift_idea_id=idea.id,
    )
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    shared = GiftShared(
        preneur_id=preneur.id,
        cadeau_id=gift.id,
        participant_id=participant.id,
        montant=10.0,
        rembourse=False,
    )
    unit_db_session.add(shared)
    await unit_db_session.commit()
    await unit_db_session.refresh(shared)

    # Act
    idea_schema = await build_gift_idea_schema(idea, group.id, unit_db_session)
    shared_schema = await build_gift_shared_schema(shared, group.id, unit_db_session)

    # Assert
    assert idea_schema.id == idea.id
    assert idea_schema.proposee_par.id == proposer.id
    assert shared_schema.id == shared.id
    assert shared_schema.preneur.id == preneur.id
    assert shared_schema.participant.id == participant.id

