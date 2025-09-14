from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Paramètres de pagination pour les requêtes API"""
    page: int = Field(1, ge=1, description="Numéro de page (commence à 1)")
    limit: int = Field(20, ge=1, le=100, description="Nombre d'éléments par page")


class PaginationInfo(BaseModel):
    """Informations de pagination pour les réponses API"""
    total_count: int = Field(description="Nombre total d'éléments")
    page: int = Field(description="Numéro de page actuelle")
    limit: int = Field(description="Nombre d'éléments par page")
    total_pages: int = Field(description="Nombre total de pages")
    has_next: bool = Field(description="Indique s'il y a une page suivante")
    has_previous: bool = Field(description="Indique s'il y a une page précédente")


class PaginatedResponse(BaseModel, Generic[T]):
    """Réponse paginée générique"""
    items: list[T] = Field(description="Liste des éléments paginés")
    pagination: PaginationInfo = Field(description="Informations de pagination")