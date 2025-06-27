from src.schemas.user import UserPayload


def is_member_of_team(current_user: UserPayload, team_id: int) -> bool:
    """Check if the user is a member of the specified team."""
    return any(team.team_id == team_id for team in current_user.teams)
