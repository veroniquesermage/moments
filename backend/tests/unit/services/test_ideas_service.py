import pytest
from uuid import uuid4
from sqlalchemy import text

from app.core.enum import RoleEnum, GiftStatusEnum
from app.models import User, Group, UserGroup, Gift, GiftIdeas
from app.schemas.gift import GiftIdeaCreate, GiftCreate
from app.services.ideas_service import GiftIdeasService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_gift_idea_success(unit_db_session, mock_trace_service):
    proposer = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Proposer", nom="N")
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Dest", nom="D")
    group = Group(nom_groupe="G", description=None)
    unit_db_session.add_all([proposer, dest, group])
    await unit_db_session.commit()
    for obj in (proposer, dest, group):
        await unit_db_session.refresh(obj)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=proposer.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    idea = GiftIdeaCreate(
        gift=GiftCreate(destinataire_id=dest.id, nom="Livre", priorite=1, description=None, prix=20.0),
        visibilite=True,
    )
    await GiftIdeasService.create_gift_idea(unit_db_session, proposer, idea)

    # Verify: Gift and GiftIdeas exist and linked
    gift = (await unit_db_session.execute(
        text("SELECT id, gift_idea_id FROM cadeaux WHERE destinataire_id = :d"),
        {"d": dest.id},
    )).first()
    assert gift is not None and gift[1] is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_gift_idea_for_self_forbidden(unit_db_session):
    user = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Self", nom="S")
    unit_db_session.add(user)
    await unit_db_session.commit()
    await unit_db_session.refresh(user)

    idea = GiftIdeaCreate(
        gift=GiftCreate(destinataire_id=user.id, nom="Jeu", priorite=1),
        visibilite=False,
    )
    with pytest.raises(Exception):
        await GiftIdeasService.create_gift_idea(unit_db_session, user, idea)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_my_ideas(unit_db_session, mock_trace_service):
    proposer = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Pro", nom="P")
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Des", nom="T")
    group = Group(nom_groupe="Ideas", description=None)
    unit_db_session.add_all([proposer, dest, group])
    await unit_db_session.commit()
    for obj in (proposer, dest, group):
        await unit_db_session.refresh(obj)

    unit_db_session.add_all([
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
        nom="BD",
        priorite=1,
        statut=GiftStatusEnum.DISPONIBLE,
        gift_idea_id=idea.id,
    )
    unit_db_session.add(gift)
    await unit_db_session.commit()

    ideas = await GiftIdeasService.get_my_ideas(unit_db_session, proposer, group.id)
    assert len(ideas) == 1
    assert ideas[0].gift.nom == "BD"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_change_visibility_and_delete_idea(unit_db_session, mock_trace_service):
    proposer = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Pro", nom="P")
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Des", nom="T")
    unit_db_session.add_all([proposer, dest])
    await unit_db_session.commit()
    for obj in (proposer, dest):
        await unit_db_session.refresh(obj)

    idea = GiftIdeas(proposee_par_id=proposer.id, visibilite=False)
    unit_db_session.add(idea)
    await unit_db_session.commit()
    await unit_db_session.refresh(idea)

    # change visibility OK
    await GiftIdeasService.change_visibility(unit_db_session, proposer, idea.id, True)
    refreshed = (await unit_db_session.execute(
        text("SELECT visibilite FROM idees_cadeaux WHERE id = :i"), {"i": idea.id}
    )).first()
    assert bool(refreshed[0]) is True

    # delete OK
    gift = Gift(destinataire_id=dest.id, nom="Obj", priorite=1, statut=GiftStatusEnum.DISPONIBLE, gift_idea_id=idea.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    await GiftIdeasService.delete_gift_idea(unit_db_session, proposer, idea.id)
    row = (await unit_db_session.execute(
        text("SELECT id FROM idees_cadeaux WHERE id = :i"), {"i": idea.id}
    )).first()
    assert row is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_duplicate_gift_idea(unit_db_session, mock_trace_service):
    proposer = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Pro", nom="P")
    dest1 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="B")
    dest2 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="C", nom="D")
    unit_db_session.add_all([proposer, dest1, dest2])
    await unit_db_session.commit()
    for obj in (proposer, dest1, dest2):
        await unit_db_session.refresh(obj)

    idea = GiftIdeas(proposee_par_id=proposer.id, visibilite=True)
    unit_db_session.add(idea)
    await unit_db_session.commit()
    await unit_db_session.refresh(idea)

    gift = Gift(destinataire_id=dest1.id, nom="Puzzle", priorite=1, statut=GiftStatusEnum.DISPONIBLE, gift_idea_id=idea.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    await GiftIdeasService.duplicate_gift_idea(unit_db_session, proposer, idea.id, dest2.id)

    duplicated = (await unit_db_session.execute(
        text("SELECT id FROM cadeaux WHERE destinataire_id = :d AND nom = :n"),
        {"d": dest2.id, "n": "Puzzle"},
    )).first()
    assert duplicated is not None
