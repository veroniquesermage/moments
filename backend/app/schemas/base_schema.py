from pydantic import BaseModel, ConfigDict


class CamelModel(BaseModel):
    model_config = ConfigDict(
        # génère les alias camelCase
        alias_generator=lambda field: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field.split("_"))
        ),
        # autorise la validation par le nom de champ (pour populate_by_name)
        populate_by_name=True,
        # équivalent de l'ancien orm_mode=True
        from_attributes=True,
    )
