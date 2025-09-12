from math import ceil
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from opentelemetry import trace

from app.schemas.common.pagination import PaginationInfo

# Tracer OpenTelemetry pour ce module
tracer = trace.get_tracer(__name__)


class PaginationHelper:
    """Utilitaire pour gérer la pagination des requêtes SQLAlchemy"""
    
    @staticmethod
    async def paginate_query(
        db: AsyncSession,
        query: Select,
        page: int,
        limit: int
    ) -> tuple[list, PaginationInfo]:
        """
        Pagine une requête SQLAlchemy et retourne les résultats avec les infos de pagination

        Args:
            db: Session de base de données
            query: Requête SQLAlchemy à paginer
            page: Numéro de page (commence à 1)
            limit: Nombre d'éléments par page

        Returns:
            Tuple contenant (liste_resultats, informations_pagination)
        """

        with tracer.start_as_current_span("pagination_query") as span:
            # Ajouter des attributs au span pour le monitoring
            span.set_attribute("pagination.page", page)
            span.set_attribute("pagination.limit", limit)
            span.set_attribute("pagination.offset", (page - 1) * limit)
            
            # Calculer le nombre total d'éléments
            with tracer.start_as_current_span("pagination_count_query") as count_span:
                # On utilise une sous-requête pour compter les résultats
                count_query = select(func.count()).select_from(query.subquery())
                total_result = await db.execute(count_query)
                total_count = total_result.scalar() or 0
                
                count_span.set_attribute("pagination.total_count", total_count)
            
            # Calculer les informations de pagination
            total_pages = ceil(total_count / limit) if limit > 0 else 0
            offset = (page - 1) * limit
            
            span.set_attribute("pagination.total_pages", total_pages)
            span.set_attribute("pagination.has_next", page < total_pages)
            span.set_attribute("pagination.has_previous", page > 1)
            
            # Construire la requête paginée
            with tracer.start_as_current_span("pagination_data_query") as data_span:
                paginated_query = query.offset(offset).limit(limit)
                result = await db.execute(paginated_query)
                items = result.scalars().all()
                
                data_span.set_attribute("pagination.items_returned", len(items))
            
            # Créer les informations de pagination
            pagination_info = PaginationInfo(
                total_count=total_count,
                page=page,
                limit=limit,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
            
            # Ajouter des métriques finales au span principal
            span.set_attribute("pagination.efficiency_ratio", len(items) / limit if limit > 0 else 0)
            span.set_attribute("pagination.is_first_page", page == 1)
            span.set_attribute("pagination.is_last_page", page >= total_pages)
            
            return items, pagination_info

    @staticmethod
    def validate_pagination_params(page: int, limit: int) -> tuple[int, int]:
        """
        Valide et normalise les paramètres de pagination

        Args:
            page: Numéro de page
            limit: Nombre d'éléments par page

        Returns:
            Tuple (page, limit) validé
        """
        # Assurer que la page est au minimum 1
        page = max(1, page)

        # Assurer que la limite est dans les bornes acceptables
        limit = max(1, min(100, limit))

        return page, limit
