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
from app.core.enum import GiftStatusEnum
from app.models import User, Gift, GiftIdeas


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
        gifts = await GiftService.get_my_gifts(unit_db_session, user.id)

        # Assert
        assert len(gifts) == 1
        assert gifts[0].nom == "Cadeau Test"

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
        gifts = await GiftService.get_my_gifts(unit_db_session, user.id)
        assert len(gifts) == 1

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
        gifts = await GiftService.get_my_gifts(unit_db_session, user.id)
        assert len(gifts) == 0

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
        final_gifts = await GiftService.get_my_gifts(unit_db_session, user.id)
        assert len(final_gifts) == 1