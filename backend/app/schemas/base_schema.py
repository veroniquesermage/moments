from pydantic import BaseModel

class CamelModel(BaseModel):
    class Config:
        alias_generator = lambda field: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field.split('_'))
        )
        validate_by_name = True
