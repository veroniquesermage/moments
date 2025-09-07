import pytest
from uuid import uuid4
from sqlalchemy import text

from app.core.enum import RoleEnum, GiftStatusEnum, RoleUtilisateur
from app.models import User, Group, UserGroup, Gift, GiftShared
from app.schemas import UserDisplaySchema
from app.schemas.gift import GiftSharedSchema, GiftStatus
from app.services.sharing_service import SharingService
from app.services.gift_service import GiftService


def _ud(u: User) -> UserDisplaySchema:
    return UserDisplaySchema(id=u.id, nom=u.nom, prenom=u.prenom, role=None, is_compte_tiers=u.is_compte_tiers)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_save_all_shares_and_status_toggle(unit_db_session, mock_trace_service):
    # Arrange
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Dest", nom="D")
    preneur = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Preneur", nom="P")
    part = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Part", nom="T")
    group = Group(nom_groupe="S", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([dest, preneur, part, group])
    await unit_db_session.commit()
    for o in (dest, preneur, part, group):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=preneur.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=part.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    gift = Gift(destinataire_id=dest.id, nom="Item", priorite=1, statut=GiftStatusEnum.PRIS, reserve_par_id=preneur.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    updates = [
        GiftSharedSchema(id=0, preneur=_ud(preneur), cadeau_id=gift.id, participant=_ud(part), montant=12.5, rembourse=False)
    ]

    # Act
    detail = await SharingService.save_all_shares(unit_db_session, preneur, gift.id, updates, group.id)

    # Assert DB inserts
    rows = (await unit_db_session.execute(
        text("SELECT COUNT(1) FROM cadeaux_partages WHERE cadeau_id = :g"), {"g": gift.id}
    )).first()[0]
    assert rows == 1
    # Status toggled to PARTAGE
    refreshed = await GiftService.get_gift_or_raise(unit_db_session, gift.id)
    assert refreshed.statut == GiftStatusEnum.PARTAGE
    assert detail.est_partage is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_shares_for_user(unit_db_session):
    a = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="A", nom="A")
    b = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="B", nom="B")
    group = Group(nom_groupe="GS", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([a, b, group])
    await unit_db_session.commit()
    for o in (a, b, group):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=a.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=b.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    gift = Gift(destinataire_id=a.id, nom="G", priorite=1, statut=GiftStatusEnum.DISPONIBLE)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    sh = GiftShared(preneur_id=a.id, participant_id=b.id, cadeau_id=gift.id, montant=10.0, rembourse=False)
    unit_db_session.add(sh)
    await unit_db_session.commit()

    preneur_view = await SharingService.get_shares_for_user(unit_db_session, gift.id, a.id, RoleUtilisateur.PRENEUR)
    part_view = await SharingService.get_shares_for_user(unit_db_session, gift.id, b.id, RoleUtilisateur.PARTICIPANT)
    assert preneur_view and part_view
    assert preneur_view[0].participant.id == b.id
    assert part_view[0].preneur.id == a.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_set_gift_refund_and_delete_share(unit_db_session, mock_trace_service):
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="D", nom="D")
    preneur = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="P", nom="P")
    part = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="T", nom="T")
    group = Group(nom_groupe="GZ", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([dest, preneur, part, group])
    await unit_db_session.commit()
    for o in (dest, preneur, part, group):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=preneur.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=part.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    gift = Gift(destinataire_id=dest.id, nom="Obj", priorite=1, statut=GiftStatusEnum.PARTAGE, reserve_par_id=preneur.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    sh = GiftShared(preneur_id=preneur.id, participant_id=part.id, cadeau_id=gift.id, montant=10.0, rembourse=False)
    unit_db_session.add(sh)
    await unit_db_session.commit()
    await unit_db_session.refresh(sh)

    shared_schema = GiftSharedSchema(
        id=sh.id,
        preneur=_ud(preneur),
        cadeau_id=gift.id,
        participant=_ud(part),
        montant=10.0,
        rembourse=True,
    )

    detail = await SharingService.set_gift_refund(unit_db_session, preneur, shared_schema, group.id)
    assert detail.partage[0].rembourse is True

    # Delete share and ensure status goes back to PRIS
    await SharingService.delete_share(unit_db_session, preneur, sh.id, group.id)
    gift_ref = await GiftService.get_gift_or_raise(unit_db_session, gift.id)
    assert gift_ref.statut == GiftStatusEnum.PRIS
