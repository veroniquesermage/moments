from app.schemas import CamelModel


class FeedbackRequest(CamelModel):
    composant: str
    commentaire: str