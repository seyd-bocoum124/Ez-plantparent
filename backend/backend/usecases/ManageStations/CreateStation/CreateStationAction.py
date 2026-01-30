from infrastructure.database import get_db
from entities.models import Station

from pydantic import BaseModel, Field, ConfigDict

from entities.repositories import Repository


class CreateStationParams(BaseModel):
    user_id: int | None = Field(
        None,
        description="L'ID de l'utilisateur propriétaire"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Le nom de la station",
        examples=["Aurore"]
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="La localisation",
        examples=["macadresse"]
    )

    model_config = ConfigDict(
        extra="forbid"
    )



class CreateStationAction:
    def __init__(self, repo:Repository):
        if repo is None:
            db = get_db()
            self.repo = Repository(db)

        else:
            self.repo = repo


    def execute(self, params: CreateStationParams) -> Station:
        #build params
        station = Station(id=None, user_id=params.user_id, name=params.name, location=params.location)

        #persist
        self.repo.create_station(station)

        return station