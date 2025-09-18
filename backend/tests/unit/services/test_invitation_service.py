import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.models import Invitation, Group, User
from app.services.invitation_service import InvitationService
from app.utils.date_helper import now_paris


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_and_use_token_success(unit_db_session):
    """Test successful token validation and usage"""
    # Setup
    user = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Test", nom="User")
    group = Group(nom_groupe="Test Group")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    # Create valid invitation
    token = str(uuid4())
    invitation = Invitation(
        email="invitee@example.com",
        groupe_id=group.id,
        envoye_par_id=user.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=False
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act
    result = await InvitationService.validate_and_use_token(unit_db_session, token)

    # Assert
    assert result.is_valid is True
    assert result.error_message is None
    assert result.invitation.id == invitation.id
    assert result.group.id == group.id

    # Verify token is marked as used
    await unit_db_session.refresh(invitation)
    assert invitation.utilise is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_and_use_token_not_found(unit_db_session):
    """Test token validation with non-existent token"""
    # Act
    result = await InvitationService.validate_and_use_token(unit_db_session, "invalid-token")

    # Assert
    assert result.is_valid is False
    assert "Ce lien d'invitation n'est plus valide" in result.error_message
    assert result.invitation is None
    assert result.group is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_and_use_token_already_used(unit_db_session):
    """Test token validation with already used token"""
    # Setup
    user = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Test", nom="User")
    group = Group(nom_groupe="Test Group")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    # Create already used invitation
    token = str(uuid4())
    invitation = Invitation(
        email="invitee@example.com",
        groupe_id=group.id,
        envoye_par_id=user.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=True  # Already used
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act
    result = await InvitationService.validate_and_use_token(unit_db_session, token)

    # Assert
    assert result.is_valid is False
    assert "Vous avez déjà rejoint ce groupe" in result.error_message
    assert result.invitation is None
    assert result.group is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_and_use_token_expired(unit_db_session):
    """Test token validation with expired token"""
    # Setup
    user = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Test", nom="User")
    group = Group(nom_groupe="Test Group")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    # Create expired invitation
    token = str(uuid4())
    invitation = Invitation(
        email="invitee@example.com",
        groupe_id=group.id,
        envoye_par_id=user.id,
        date_envoi=now_paris().replace(tzinfo=None) - timedelta(days=31),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) - timedelta(days=1),  # Expired
        utilise=False
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act
    result = await InvitationService.validate_and_use_token(unit_db_session, token)

    # Assert
    assert result.is_valid is False
    assert "Ce lien d'invitation a expiré" in result.error_message
    assert result.invitation is None
    assert result.group is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_group_from_token_success(unit_db_session):
    """Test successful group retrieval from token"""
    # Setup
    user = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Test", nom="User")
    group = Group(nom_groupe="Test Group")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    # Create valid invitation
    token = str(uuid4())
    invitation = Invitation(
        email="invitee@example.com",
        groupe_id=group.id,
        envoye_par_id=user.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=False
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act
    result = await InvitationService.get_group_from_token(unit_db_session, token)

    # Assert
    assert result is not None
    assert result.id == group.id
    assert result.nom_groupe == "Test Group"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_group_from_token_not_found(unit_db_session):
    """Test group retrieval with non-existent token"""
    # Act
    result = await InvitationService.get_group_from_token(unit_db_session, "invalid-token")

    # Assert
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_group_from_token_already_used(unit_db_session):
    """Test group retrieval with already used token"""
    # Setup
    user = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Test", nom="User")
    group = Group(nom_groupe="Test Group")
    unit_db_session.add_all([user, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(user)
    await unit_db_session.refresh(group)

    # Create used invitation
    token = str(uuid4())
    invitation = Invitation(
        email="invitee@example.com",
        groupe_id=group.id,
        envoye_par_id=user.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=True  # Already used
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act
    result = await InvitationService.get_group_from_token(unit_db_session, token)

    # Assert
    assert result is None