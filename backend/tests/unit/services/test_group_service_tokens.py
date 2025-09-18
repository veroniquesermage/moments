import pytest
from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException

from app.core.enum import RoleEnum
from app.models import Invitation, Group, User, UserGroup
from app.services.group_service import GroupService
from app.utils.date_helper import now_paris


@pytest.mark.unit
@pytest.mark.asyncio
async def test_join_group_with_token_success(unit_db_session):
    """Test successful group joining with valid token"""
    # Setup users and group
    inviter = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Inviter", nom="User")
    joiner = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Joiner", nom="User")
    group = Group(nom_groupe="Test Group")

    unit_db_session.add_all([inviter, joiner, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(inviter)
    await unit_db_session.refresh(joiner)
    await unit_db_session.refresh(group)

    # Create valid invitation
    token = str(uuid4())
    invitation = Invitation(
        email=joiner.email,
        groupe_id=group.id,
        envoye_par_id=inviter.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=False
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act
    result = await GroupService.join_group_with_token(unit_db_session, joiner, token)

    # Assert
    assert result.id == group.id
    assert result.nom_groupe == "Test Group"

    # Verify user is now member of the group
    from sqlalchemy import select, and_
    user_group_result = await unit_db_session.execute(
        select(UserGroup).where(
            and_(
                UserGroup.utilisateur_id == joiner.id,
                UserGroup.groupe_id == group.id
            )
        )
    )
    user_group = user_group_result.scalar_one_or_none()
    assert user_group is not None
    assert user_group.role == RoleEnum.MEMBRE

    # Verify invitation is marked as used
    await unit_db_session.refresh(invitation)
    assert invitation.utilise is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_join_group_with_token_invalid_token(unit_db_session):
    """Test group joining with invalid token"""
    # Setup user
    joiner = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Joiner", nom="User")
    unit_db_session.add(joiner)
    await unit_db_session.commit()
    await unit_db_session.refresh(joiner)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await GroupService.join_group_with_token(unit_db_session, joiner, "invalid-token")

    assert exc_info.value.status_code == 400
    assert "Ce lien d'invitation n'est plus valide" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_join_group_with_token_expired_token(unit_db_session):
    """Test group joining with expired token"""
    # Setup users and group
    inviter = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Inviter", nom="User")
    joiner = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Joiner", nom="User")
    group = Group(nom_groupe="Test Group")

    unit_db_session.add_all([inviter, joiner, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(inviter)
    await unit_db_session.refresh(joiner)
    await unit_db_session.refresh(group)

    # Create expired invitation
    token = str(uuid4())
    invitation = Invitation(
        email=joiner.email,
        groupe_id=group.id,
        envoye_par_id=inviter.id,
        date_envoi=now_paris().replace(tzinfo=None) - timedelta(days=31),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) - timedelta(days=1),  # Expired
        utilise=False
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await GroupService.join_group_with_token(unit_db_session, joiner, token)

    assert exc_info.value.status_code == 400
    assert "Ce lien d'invitation a expiré" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_join_group_with_token_already_member(unit_db_session):
    """Test group joining when user is already a member"""
    # Setup users and group
    inviter = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Inviter", nom="User")
    joiner = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Joiner", nom="User")
    group = Group(nom_groupe="Test Group")

    unit_db_session.add_all([inviter, joiner, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(inviter)
    await unit_db_session.refresh(joiner)
    await unit_db_session.refresh(group)

    # User is already a member
    user_group = UserGroup(
        utilisateur_id=joiner.id,
        groupe_id=group.id,
        role=RoleEnum.MEMBRE
    )
    unit_db_session.add(user_group)

    # Create valid invitation
    token = str(uuid4())
    invitation = Invitation(
        email=joiner.email,
        groupe_id=group.id,
        envoye_par_id=inviter.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=False
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await GroupService.join_group_with_token(unit_db_session, joiner, token)

    assert exc_info.value.status_code == 400
    assert "Vous êtes déjà membre de ce groupe" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_join_group_with_token_already_used(unit_db_session):
    """Test group joining with already used token"""
    # Setup users and group
    inviter = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Inviter", nom="User")
    joiner = User(email=f"{uuid4().hex[:8]}@example.com", prenom="Joiner", nom="User")
    group = Group(nom_groupe="Test Group")

    unit_db_session.add_all([inviter, joiner, group])
    await unit_db_session.commit()
    await unit_db_session.refresh(inviter)
    await unit_db_session.refresh(joiner)
    await unit_db_session.refresh(group)

    # Create already used invitation
    token = str(uuid4())
    invitation = Invitation(
        email=joiner.email,
        groupe_id=group.id,
        envoye_par_id=inviter.id,
        date_envoi=now_paris().replace(tzinfo=None),
        token=token,
        date_expiration=now_paris().replace(tzinfo=None) + timedelta(days=30),
        utilise=True  # Already used
    )
    unit_db_session.add(invitation)
    await unit_db_session.commit()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await GroupService.join_group_with_token(unit_db_session, joiner, token)

    assert exc_info.value.status_code == 400
    assert "Vous avez déjà rejoint ce groupe" in str(exc_info.value.detail)