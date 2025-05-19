from sqlalchemy import select

from app.core.logger import logger
from app.models.gift import Gift


class GiftService:


    @staticmethod
    async def get_gifts(db, effective_user_id):
        logger.info(f"Récupération des cadeaux de l'utilisateur {effective_user_id}")
        result = await db.execute(select(Gift).where(Gift.utilisateur_id == effective_user_id))
        return result.scalars().all()




