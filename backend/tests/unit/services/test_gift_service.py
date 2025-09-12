"""
Tests unitaires corrigés pour GiftService
Version adaptée à la nouvelle structure hiérarchique
"""
import pytest
from fastapi import HTTPException
from uuid import uuid4

from app.services.gift_service import GiftService
from app.schemas.gift.gift_create import GiftCreate
from app.schemas.gift.gift_update import GiftUpdate
from app.schemas.gift.gift_status import GiftStatus
from app.schemas.gift import GiftDeliveryUpdate, GiftPurchaseUpdate, GiftPriority
from app.schemas import UserTiersResponse
from app.core.enum import GiftActionEnum, GiftStatusEnum, RoleEnum
from app.models import User, Gift, GiftIdeas, Group, UserGroup, GiftShared


class TestGiftServiceFixed:
    """Tests unitaires corrigés pour GiftService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_my_gifts_success_fixed(self, unit_db_session, mock_trace_service):
        """Test: récupération réussie des cadeaux d'un utilisateur - Version corrigée"""
        # Arrange - Créer tout dans la même session
        user = User(
            email=f"test{uuid4().hex[:8]}@example.com",
            prenom="Test",
            nom="User",
            google_id=f"google{uuid4().hex[:8]}"
        )
        unit_db_session.add(user)
        await unit_db_session.commit()
        await unit_db_session.refresh(user)

        # Créer un cadeau pour cet utilisateur
        gift = Gift(
            nom="Cadeau Test",
            description="Description test",
            prix=50.0,
            destinataire_id=user.id,
            statut=GiftStatusEnum.DISPONIBLE,
            priorite=1
        )
        unit_db_session.add(gift)
        await unit_db_session.commit()
        await unit_db_session.refresh(gift)

        # Act
        result = await GiftService.get_my_gifts(unit_db_session, user.id)

        # Assert
        assert len(result.items) == 1
        assert result.items[0].nom == "Cadeau Test"
        assert result.pagination.total_count == 1
        assert result.pagination.page == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_gift_success_fixed(self, unit_db_session, mock_trace_service):
        """Test: création réussie d'un cadeau - Version corrigée"""
        # Arrange - Créer un utilisateur
        user = User(
            email=f"create{uuid4().hex[:8]}@example.com",
            prenom="Create",
            nom="User",
            google_id=f"create{uuid4().hex[:8]}"
        )
        unit_db_session.add(user)
        await unit_db_session.commit()
        await unit_db_session.refresh(user)

        gift_data = GiftCreate(
            destinataire_id=user.id,
            nom="Nouveau Cadeau",
            description="Description du nouveau cadeau",
            prix=75.0,
            priorite=2
        )

        # Act
        result = await GiftService.create_gift(unit_db_session, user, gift_data)

        # Assert
        assert result is not None
        assert result.nom == "Nouveau Cadeau"

        # Vérifier en base
        gifts_result = await GiftService.get_my_gifts(unit_db_session, user.id)
        assert len(gifts_result.items) == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_gift_bug_fix_fixed(self, unit_db_session, mock_trace_service):
        """
        Test CRITIQUE: Fix du bug ligne 165-168 - Version corrigée
        Tentative de modification d'un cadeau sans gift_idea par un autre utilisateur
        """
        # Arrange - Créer deux utilisateurs
        user1 = User(
            email=f"user1{uuid4().hex[:8]}@example.com",
            prenom="User1", nom="Test", google_id=f"user1{uuid4().hex[:8]}"
        )
        user2 = User(
            email=f"user2{uuid4().hex[:8]}@example.com",
            prenom="User2", nom="Test", google_id=f"user2{uuid4().hex[:8]}"
        )

        unit_db_session.add_all([user1, user2])
        await unit_db_session.commit()
        await unit_db_session.refresh(user1)
        await unit_db_session.refresh(user2)

        # Créer un cadeau appartenant à user2, sans gift_idea
        gift = Gift(
            nom="Cadeau d'un autre",
            description="Description",
            destinataire_id=user2.id,
            gift_idea_id=None,  # Pas d'idée associée
            statut=GiftStatusEnum.DISPONIBLE,
            priorite=1
        )
        unit_db_session.add(gift)
        await unit_db_session.commit()
        await unit_db_session.refresh(gift)

        # Act & Assert - user1 tente de modifier le cadeau de user2
        updates = GiftUpdate(
            id=gift.id,
            destinataire_id=user2.id,
            nom="Nouveau nom",
            priorite=1
        )

        with pytest.raises(HTTPException) as exc_info:
            await GiftService.update_gift(
                unit_db_session,
                user1,  # user1 tente de modifier
                gift.id,
                updates
            )

        # Vérifications
        assert exc_info.value.status_code == 400
        assert "Vous ne pouvez modifier que vos propres cadeaux" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_gift_authorized_fixed(self, unit_db_session, mock_trace_service):
        """Test: modification autorisée de son propre cadeau - Version corrigée"""
        # Arrange - Créer utilisateur et cadeau dans la même session
        user = User(
            email=f"update{uuid4().hex[:8]}@example.com",
            prenom="Update", nom="User", google_id=f"update{uuid4().hex[:8]}"
        )
        unit_db_session.add(user)
        await unit_db_session.commit()
        await unit_db_session.refresh(user)

        gift = Gift(
            nom="Cadeau Original",
            description="Description originale",
            prix=100.0,
            destinataire_id=user.id,
            statut=GiftStatusEnum.DISPONIBLE,
            priorite=1
        )
        unit_db_session.add(gift)
        await unit_db_session.commit()
        await unit_db_session.refresh(gift)

        # Act - Modifier son propre cadeau
        updates = GiftUpdate(
            id=gift.id,
            destinataire_id=user.id,
            nom="Cadeau Modifié",
            description="Description modifiée",
            priorite=1
        )

        result = await GiftService.update_gift(
            unit_db_session,
            user,
            gift.id,
            updates
        )

        # Assert
        assert result.nom == "Cadeau Modifié"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_gift_success_fixed(self, unit_db_session, mock_trace_service):
        """Test: suppression réussie d'un cadeau - Version corrigée"""
        # Arrange
        user = User(
            email=f"delete{uuid4().hex[:8]}@example.com",
            prenom="Delete", nom="User", google_id=f"delete{uuid4().hex[:8]}"
        )
        unit_db_session.add(user)
        await unit_db_session.commit()
        await unit_db_session.refresh(user)

        gift = Gift(
            nom="Cadeau à supprimer",
            destinataire_id=user.id,
            statut=GiftStatusEnum.DISPONIBLE,
            priorite=1
        )
        unit_db_session.add(gift)
        await unit_db_session.commit()
        await unit_db_session.refresh(gift)

        # Act
        await GiftService.delete_gift(unit_db_session, gift.id, user)

        # Assert - Vérifier que le cadeau n'existe plus
        gifts_result = await GiftService.get_my_gifts(unit_db_session, user.id)
        assert len(gifts_result.items) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_change_status_success_fixed(self, unit_db_session, mock_trace_service):
        """Test: changement de statut d'un cadeau - Version corrigée"""
        # Arrange - Créer utilisateur et cadeau
        user = User(
            email=f"status{uuid4().hex[:8]}@example.com",
            prenom="Status", nom="User", google_id=f"status{uuid4().hex[:8]}"
        )
        unit_db_session.add(user)
        await unit_db_session.commit()
        await unit_db_session.refresh(user)

        gift = Gift(
            nom="Cadeau pour statut",
            destinataire_id=user.id,
            statut=GiftStatusEnum.DISPONIBLE,
            priorite=1
        )
        unit_db_session.add(gift)
        await unit_db_session.commit()
        await unit_db_session.refresh(gift)

        # Act
        new_status = GiftStatus(status=GiftStatusEnum.RESERVE)
        result = await GiftService.change_status(
            unit_db_session,
            user,  # user réserve un cadeau (peut être le sien ou celui d'un autre)
            gift.id,
            new_status
        )

        # Assert
        assert result is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_gift_not_found_fixed(self, unit_db_session):
        """Test: récupération d'un cadeau inexistant - Version corrigée"""
        # Act & Assert - ID qui n'existe pas
        with pytest.raises(HTTPException) as exc_info:
            await GiftService.get_gift(unit_db_session, 999999, 1, 1)

        assert exc_info.value.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_gift_lifecycle_complete_fixed(self, unit_db_session, mock_trace_service, mock_mail_service):
        """Test d'intégration: cycle de vie complet d'un cadeau - Version corrigée"""
        # Arrange - Créer un utilisateur
        user = User(
            email=f"lifecycle{uuid4().hex[:8]}@example.com",
            prenom="Lifecycle", nom="User", google_id=f"lifecycle{uuid4().hex[:8]}"
        )
        unit_db_session.add(user)
        await unit_db_session.commit()
        await unit_db_session.refresh(user)

        # 1. Création
        gift_data = GiftCreate(
            destinataire_id=user.id,
            nom="Cadeau Lifecycle",
            description="Test du cycle de vie",
            prix=200.0,
            priorite=1
        )
        created_gift = await GiftService.create_gift(unit_db_session, user, gift_data)
        assert created_gift is not None

        # 2. Modification
        updates = GiftUpdate(
            id=created_gift.id,
            destinataire_id=user.id,
            nom="Cadeau Modifié",
            priorite=1
        )
        updated_gift = await GiftService.update_gift(
            unit_db_session, user, created_gift.id, updates
        )
        assert updated_gift.nom == "Cadeau Modifié"

        # 3. Changement de statut
        status_change = GiftStatus(status=GiftStatusEnum.RESERVE)
        reserved_gift = await GiftService.change_status(
            unit_db_session, user, created_gift.id, status_change
        )
        assert reserved_gift is not None

        # 4. Vérification finale
        final_gifts_result = await GiftService.get_my_gifts(unit_db_session, user.id)
        assert len(final_gifts_result.items) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_eligibility_all_paths(unit_db_session):
    creator = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="C", nom="U")
    taker = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="T", nom="U")
    other = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="O", nom="U")
    unit_db_session.add_all([creator, taker, other])
    await unit_db_session.commit()
    for u in (creator, taker, other):
        await unit_db_session.refresh(u)

    # Disponible gift → RESERVER/PRENDRE OK
    g1 = Gift(destinataire_id=creator.id, nom="G1", priorite=1, statut=GiftStatusEnum.DISPONIBLE)
    # Reserved by taker
    g2 = Gift(destinataire_id=creator.id, nom="G2", priorite=1, statut=GiftStatusEnum.RESERVE, reserve_par_id=taker.id)
    # Taken by taker
    g3 = Gift(destinataire_id=creator.id, nom="G3", priorite=1, statut=GiftStatusEnum.PRIS, reserve_par_id=taker.id)
    unit_db_session.add_all([g1, g2, g3])
    await unit_db_session.commit()
    for g in (g1, g2, g3):
        await unit_db_session.refresh(g)

    el1 = await GiftService.verify_eligibility(unit_db_session, g1.id, other, GiftActionEnum.RESERVER)
    assert el1.ok is True
    el2 = await GiftService.verify_eligibility(unit_db_session, g1.id, other, GiftActionEnum.PRENDRE)
    assert el2.ok is True

    # PRENDRE autorisé si RESERVE par le même utilisateur
    el3 = await GiftService.verify_eligibility(unit_db_session, g2.id, taker, GiftActionEnum.PRENDRE)
    assert el3.ok is True

    # ANNULER_RESERVATION quand non réservé → False
    el4 = await GiftService.verify_eligibility(unit_db_session, g1.id, other, GiftActionEnum.ANNULER_RESERVATION)
    assert el4.ok is False

    # RETIRER autorisé uniquement si PRIS et par le preneur
    el5 = await GiftService.verify_eligibility(unit_db_session, g3.id, taker, GiftActionEnum.RETIRER)
    assert el5.ok is True
    el6 = await GiftService.verify_eligibility(unit_db_session, g3.id, other, GiftActionEnum.RETIRER)
    assert el6.ok is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_set_gift_delivery_create_and_unauthorized(unit_db_session, mock_trace_service):
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="D", nom="D")
    taker = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="T", nom="T")
    group_code = uuid4().hex[:10]
    unit_db_session.add_all([dest, taker])
    await unit_db_session.commit()
    await unit_db_session.refresh(dest)
    await unit_db_session.refresh(taker)

    # group exists only to pass ID around; GiftService.set_gift_detail relies on builders using group membership
    group = Group(nom_groupe="Gifts", description=None, code=group_code)
    unit_db_session.add(group)
    await unit_db_session.commit()
    await unit_db_session.refresh(group)
    unit_db_session.add_all([
        UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=taker.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    gift = Gift(destinataire_id=dest.id, nom="Livraison", priorite=1, statut=GiftStatusEnum.PRIS, reserve_par_id=taker.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    detail = await GiftService.set_gift_delivery(unit_db_session, taker, gift.id, True, group.id)
    assert detail.delivery and detail.delivery.recu is True

    # Unauthorized user
    with pytest.raises(HTTPException):
        await GiftService.set_gift_delivery(unit_db_session, dest, gift.id, False, group.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_gift_purchase_paths(unit_db_session, mock_trace_service):
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="D", nom="D")
    taker = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="T", nom="T")
    tiers = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="X", nom="Y", is_compte_tiers=True)
    group = Group(nom_groupe="GP", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([dest, taker, tiers, group])
    await unit_db_session.commit()
    for u in (dest, taker, tiers, group):
        await unit_db_session.refresh(u)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=dest.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=taker.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=tiers.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    gift = Gift(destinataire_id=dest.id, nom="Achat", priorite=1, statut=GiftStatusEnum.PRIS, reserve_par_id=taker.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    # Success: set prix/commentaire/compte_tiers
    upd = GiftPurchaseUpdate(gift_id=gift.id, prix_reel=42.5, commentaire="note", compte_tiers=UserTiersResponse(
        id=tiers.id, prenom=tiers.prenom, nom=tiers.nom, surnom=None, is_compte_tiers=True
    ))
    await GiftService.update_gift_purchase(unit_db_session, taker, gift.id, upd)

    # Unauthorized user
    upd2 = GiftPurchaseUpdate(gift_id=gift.id, prix_reel=None, commentaire=None, compte_tiers=None)
    with pytest.raises(HTTPException):
        await GiftService.update_gift_purchase(unit_db_session, dest, gift.id, upd2)


    # ---------------------------------------------------------------------
    # Additional coverage: update_all_gifts, get_visible_gifts_for_member,
    # update_gift_delivery, get_gifts_by_account, define_user_role
    # ---------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_all_gifts_order_and_forbidden(unit_db_session):
    owner = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Own", nom="Er")
    other = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Oth", nom="Er")
    unit_db_session.add_all([owner, other])
    await unit_db_session.commit()
    await unit_db_session.refresh(owner)
    await unit_db_session.refresh(other)

    g1 = Gift(destinataire_id=owner.id, nom="A", priorite=1, statut=GiftStatusEnum.DISPONIBLE)
    g2 = Gift(destinataire_id=owner.id, nom="B", priorite=2, statut=GiftStatusEnum.DISPONIBLE)
    unit_db_session.add_all([g1, g2])
    await unit_db_session.commit()
    await unit_db_session.refresh(g1)
    await unit_db_session.refresh(g2)

    # Reorder priorities
    payload = [GiftPriority(id=g1.id, priority=2), GiftPriority(id=g2.id, priority=1)]
    updated = await GiftService.update_all_gifts(unit_db_session, owner, payload)
    assert [g.nom for g in updated] == ["B", "A"]

    # Add a gift from another user → forbidden
    g3 = Gift(destinataire_id=other.id, nom="C", priorite=3, statut=GiftStatusEnum.DISPONIBLE)
    unit_db_session.add(g3)
    await unit_db_session.commit()
    await unit_db_session.refresh(g3)

    with pytest.raises(HTTPException):
        await GiftService.update_all_gifts(unit_db_session, owner, [GiftPriority(id=g3.id, priority=1)])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_visible_gifts_for_member_visibility(unit_db_session):
    proposer = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Pro", nom="P")
    dest = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Des", nom="T")
    unit_db_session.add_all([proposer, dest])
    await unit_db_session.commit()
    await unit_db_session.refresh(proposer)
    await unit_db_session.refresh(dest)

    # Gift with no idea (visible)
    g_no = Gift(destinataire_id=dest.id, nom="NoIdea", priorite=1, statut=GiftStatusEnum.DISPONIBLE)
    # Gift with hidden idea
    idea_hidden = GiftIdeas(proposee_par_id=proposer.id, visibilite=False)
    # Gift with visible idea
    idea_visible = GiftIdeas(proposee_par_id=proposer.id, visibilite=True)
    unit_db_session.add_all([g_no, idea_hidden, idea_visible])
    await unit_db_session.commit()
    await unit_db_session.refresh(idea_hidden)
    await unit_db_session.refresh(idea_visible)

    g_hidden = Gift(destinataire_id=dest.id, nom="Hidden", priorite=2, statut=GiftStatusEnum.DISPONIBLE, gift_idea_id=idea_hidden.id)
    g_visible = Gift(destinataire_id=dest.id, nom="Visible", priorite=3, statut=GiftStatusEnum.DISPONIBLE, gift_idea_id=idea_visible.id)
    unit_db_session.add_all([g_hidden, g_visible])
    await unit_db_session.commit()

    visible_result = await GiftService.get_visible_gifts_for_member(unit_db_session, dest.id)
    names = [g.nom for g in visible_result.items]
    assert "NoIdea" in names
    assert "Visible" in names
    assert "Hidden" not in names


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_gift_delivery_update_existing_and_unauthorized(unit_db_session, mock_trace_service):
    u = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="U", nom="U")
    other = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="O", nom="O")
    group = Group(nom_groupe="GLiv", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([u, other, group])
    await unit_db_session.commit()
    for o in (u, other, group):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=u.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=other.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    gift = Gift(destinataire_id=u.id, nom="Liv", priorite=1, statut=GiftStatusEnum.PRIS, reserve_par_id=u.id)
    unit_db_session.add(gift)
    await unit_db_session.commit()
    await unit_db_session.refresh(gift)

    upd = GiftDeliveryUpdate(lieu_livraison="Maison", recu=False)
    res = await GiftService.update_gift_delivery(unit_db_session, u, gift.id, upd)
    assert res.lieu_livraison == "Maison"

    with pytest.raises(HTTPException):
        await GiftService.update_gift_delivery(unit_db_session, other, gift.id, GiftDeliveryUpdate(lieu_livraison="X"))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_gifts_by_account_grouping_and_totals(unit_db_session, mock_trace_service):
    current = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Cur", nom="R")
    dest1 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="D1", nom="N")
    dest2 = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="D2", nom="N")
    tiers = User(email=f"{uuid4().hex[:8]}@ex.com", prenom="Tiers", nom="N")
    group = Group(nom_groupe="GAcc", description=None, code=uuid4().hex[:10])
    unit_db_session.add_all([current, dest1, dest2, tiers, group])
    await unit_db_session.commit()
    for o in (current, dest1, dest2, tiers, group):
        await unit_db_session.refresh(o)

    unit_db_session.add_all([
        UserGroup(utilisateur_id=current.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=dest1.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=dest2.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
        UserGroup(utilisateur_id=tiers.id, groupe_id=group.id, role=RoleEnum.MEMBRE),
    ])
    await unit_db_session.commit()

    # Gift followed (reserved by current) with purchase info in my name
    g_follow_mine = Gift(destinataire_id=dest1.id, nom="Mine", priorite=1, statut=GiftStatusEnum.PRIS, reserve_par_id=current.id)
    # Gift followed (reserved by current) with purchase info under tiers
    g_follow_tiers = Gift(destinataire_id=dest2.id, nom="TiersGift", priorite=2, statut=GiftStatusEnum.PRIS, reserve_par_id=current.id)
    # Gift shared where current is participant (montant used)
    g_shared = Gift(destinataire_id=dest1.id, nom="Shared", priorite=3, statut=GiftStatusEnum.PARTAGE, reserve_par_id=dest2.id)
    unit_db_session.add_all([g_follow_mine, g_follow_tiers, g_shared])
    await unit_db_session.commit()
    for g in (g_follow_mine, g_follow_tiers, g_shared):
        await unit_db_session.refresh(g)

    # Add partage for g_shared where current participates
    ps = GiftShared(preneur_id=dest2.id, participant_id=current.id, cadeau_id=g_shared.id, montant=20.0, rembourse=False)
    unit_db_session.add(ps)
    await unit_db_session.commit()

    # Add purchase info via service for both followed gifts
    upd_mine = GiftPurchaseUpdate(gift_id=g_follow_mine.id, prix_reel=30.0, commentaire=None, compte_tiers=None)
    await GiftService.update_gift_purchase(unit_db_session, current, g_follow_mine.id, upd_mine)

    upd_tiers = GiftPurchaseUpdate(
        gift_id=g_follow_tiers.id, prix_reel=70.0, commentaire=None,
        compte_tiers=UserTiersResponse(id=tiers.id, prenom=tiers.prenom, nom=tiers.nom, surnom=None, is_compte_tiers=True)
    )
    await GiftService.update_gift_purchase(unit_db_session, current, g_follow_tiers.id, upd_tiers)

    grouped_result = await GiftService.get_gifts_by_account(unit_db_session, current, group.id)
    labels = {g.account_label: g.total for g in grouped_result.items}
    totals = sorted(round(float(t), 2) for t in labels.values())
    # At minimum, the shared gift contribution (20.0) must be present
    assert 20.0 in totals


@pytest.mark.unit
def test_define_user_role_cases():
    # Minimal in-memory Gift-like object using actual models for consistency
    creator = User(id=1, email="a@b", prenom="A")
    taker = User(id=2, email="c@d", prenom="B")
    gift = Gift(destinataire_id=creator.id, nom="X", priorite=1, statut=GiftStatusEnum.DISPONIBLE, reserve_par_id=taker.id)
    # Attach related objects minimalistically
    gift.destinataire = creator
    gift.reserve_par = taker

    from app.core.enum import RoleUtilisateur
    # CREATEUR
    assert GiftService.define_user_role(creator, gift, []) == RoleUtilisateur.CREATEUR
    # PRENEUR
    assert GiftService.define_user_role(taker, gift, []) == RoleUtilisateur.PRENEUR
    # PARTICIPANT
    from app.schemas import UserDisplaySchema
    from app.schemas.gift import GiftSharedSchema
    participant = User(id=3, email="p@q", prenom="P")
    partages = [GiftSharedSchema(id=1, preneur=UserDisplaySchema(id=taker.id, prenom=taker.prenom), cadeau_id=42,
                                 participant=UserDisplaySchema(id=participant.id, prenom=participant.prenom), montant=10.0, rembourse=False)]
    assert GiftService.define_user_role(participant, gift, partages) == RoleUtilisateur.PARTICIPANT
    # SPECTATEUR
    stranger = User(id=4, email="s@t", prenom="S")
    assert GiftService.define_user_role(stranger, gift, partages) == RoleUtilisateur.SPECTATEUR
