import enum


class UserRole(str, enum.Enum):
    """ enum for user role"""
    USER = "user"
    ADMIN = "admin"


class TaskStatus(str, enum.Enum):
    """Status tasks"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    """Priority levels for tasks."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MeetingStatus(str, enum.Enum):
    """Status meetings"""
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class TeamRole(str, enum.Enum):
    """ enum for users role in tems"""
    EXECUTOR = "EXECUTOR"
    MANAGER = "MANAGER"
