"""Tests unitaires pour PaginationHelper"""
import pytest
from sqlalchemy import select
from app.core.pagination import PaginationHelper
from app.models import User
from app.schemas.common.pagination import PaginationInfo


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_pagination_params():
    """Test: validation des paramètres de pagination"""
    # Test page invalide (< 1) devrait être normalisée à 1
    page, limit = PaginationHelper.validate_pagination_params(-1, 20)
    assert page == 1
    assert limit == 20
    
    # Test limite trop grande devrait être normalisée à 100
    page, limit = PaginationHelper.validate_pagination_params(1, 200)
    assert page == 1
    assert limit == 100
    
    # Test limite trop petite devrait être normalisée à 1
    page, limit = PaginationHelper.validate_pagination_params(2, 0)
    assert page == 2
    assert limit == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_query_basic(unit_db_session):
    """Test: pagination basique avec PaginationHelper"""
    # Arrange - Créer quelques utilisateurs
    users = []
    for i in range(5):
        user = User(
            email=f"test{i}@example.com",
            prenom=f"User{i}",
            nom="Test",
            google_id=f"google{i}"
        )
        unit_db_session.add(user)
        users.append(user)
    
    await unit_db_session.commit()
    
    # Requête de base
    base_query = select(User).order_by(User.id)
    
    # Act - Page 1 (3 éléments)
    items, pagination_info = await PaginationHelper.paginate_query(
        unit_db_session, base_query, page=1, limit=3
    )
    
    # Assert
    assert len(items) == 3
    assert pagination_info.page == 1
    assert pagination_info.limit == 3
    assert pagination_info.total_count == 5
    assert pagination_info.total_pages == 2
    assert pagination_info.has_next == True
    assert pagination_info.has_previous == False
    
    # Act - Page 2 (2 éléments restants)
    items2, pagination_info2 = await PaginationHelper.paginate_query(
        unit_db_session, base_query, page=2, limit=3
    )
    
    # Assert
    assert len(items2) == 2
    assert pagination_info2.page == 2
    assert pagination_info2.has_next == False
    assert pagination_info2.has_previous == True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_query_empty_result(unit_db_session):
    """Test: pagination avec résultat vide"""
    # Requête qui ne retourne rien
    empty_query = select(User).where(User.email == "inexistant@example.com")
    
    # Act
    items, pagination_info = await PaginationHelper.paginate_query(
        unit_db_session, empty_query, page=1, limit=10
    )
    
    # Assert
    assert len(items) == 0
    assert pagination_info.total_count == 0
    assert pagination_info.total_pages == 0
    assert pagination_info.has_next == False
    assert pagination_info.has_previous == False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_query_page_out_of_range(unit_db_session):
    """Test: pagination avec page hors limites"""
    # Arrange - Créer des utilisateurs avec un email spécifique
    test_email_prefix = "pagetest"
    for i in range(2):
        user = User(
            email=f"{test_email_prefix}{i}@example.com",
            prenom=f"PageTest{i}",
            nom="Test", 
            google_id=f"pagetest{i}"
        )
        unit_db_session.add(user)
    
    await unit_db_session.commit()
    
    # Requête filtrée pour isoler nos données de test
    base_query = select(User).where(User.email.like(f"{test_email_prefix}%")).order_by(User.id)
    
    # Act - Demander page 5 alors qu'il n'y en a qu'1
    items, pagination_info = await PaginationHelper.paginate_query(
        unit_db_session, base_query, page=5, limit=10
    )
    
    # Assert - Doit retourner une page vide mais valide
    assert len(items) == 0
    assert pagination_info.page == 5
    assert pagination_info.total_count == 2
    assert pagination_info.total_pages == 1
    assert pagination_info.has_next == False
    assert pagination_info.has_previous == True