from backend.models.team import Team
from backend.schemas.team import TeamRead
from backend.crud.basecrud import BaseCRUD


class TeamCRUD(BaseCRUD):
    """CRUD operations for Team model."""

    def __init__(self):
        super().__init__(Team, TeamRead)


team_crud = TeamCRUD()
