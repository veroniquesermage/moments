"""
Fixtures spécialisées pour les utilisateurs
"""
import pytest
import pytest_asyncio
from uuid import uuid4

from app.models import User, Group, UserGroup
from app.core.enum import RoleUtilisateur


@pytest.fixture
def user_factory():
    """Factory pour créer des utilisateurs avec des données variées"""
    def _create_user(**overrides) -> User:
        unique_id = str(uuid4())[:8]
        defaults = {
            "email": f"user{unique_id}@example.com",
            "prenom": "Test",
            "nom": "User",
            "google_id": f"google{unique_id}"
        }
        defaults.update(overrides)
        return User(**defaults)
    
    return _create_user


@pytest.fixture
def group_factory():
    """Factory pour créer des groupes"""
    def _create_group(**overrides) -> Group:
        unique_id = str(uuid4())[:8]
        defaults = {
            "nom": f"Groupe {unique_id}",
            "description": "Description du groupe test",
            "code_invitation": unique_id
        }
        defaults.update(overrides)
        return Group(**defaults)
    
    return _create_group


@pytest_asyncio.fixture
async def users_with_group(unit_db_session, user_factory, group_factory):
    """Créer un groupe avec plusieurs utilisateurs"""
    # Créer le groupe
    admin_user = user_factory(prenom="Admin", nom="User")
    member_user = user_factory(prenom="Member", nom="User")
    
    unit_db_session.add(admin_user)
    unit_db_session.add(member_user)
    await unit_db_session.commit()
    await unit_db_session.refresh(admin_user)
    await unit_db_session.refresh(member_user)
    
    # Créer le groupe
    group = group_factory(createur_id=admin_user.id)
    unit_db_session.add(group)
    await unit_db_session.commit()
    await unit_db_session.refresh(group)
    
    # Ajouter les relations utilisateur-groupe
    admin_relation = UserGroup(
        utilisateur_id=admin_user.id,
        groupe_id=group.id,
        role=RoleUtilisateur.ADMIN
    )
    member_relation = UserGroup(
        utilisateur_id=member_user.id,
        groupe_id=group.id,
        role=RoleUtilisateur.MEMBRE
    )
    
    unit_db_session.add(admin_relation)
    unit_db_session.add(member_relation)
    await unit_db_session.commit()
    
    return {
        "admin_user": admin_user,
        "member_user": member_user,
        "group": group
    }