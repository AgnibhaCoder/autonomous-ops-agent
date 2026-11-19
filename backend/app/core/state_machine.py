from app.db.models import TaskStatus

# Valid transitions map: Current State -> Set of Allowed Next States
ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.RUNNING},
    TaskStatus.RUNNING: {
        TaskStatus.AWAITING_APPROVAL,
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
    },
    TaskStatus.AWAITING_APPROVAL: {
        TaskStatus.RUNNING,     # Approved: resume execution
        TaskStatus.REJECTED,    # Rejected: replan or halt
        TaskStatus.FAILED,
    },
    TaskStatus.REJECTED: {
        TaskStatus.RUNNING,     # Agent attempts replanning based on rejection
        TaskStatus.FAILED,
    },
    TaskStatus.COMPLETED: set(), # Terminal state
    TaskStatus.FAILED: set(),    # Terminal state
}

def validate_transition(current_status: TaskStatus, new_status: TaskStatus) -> bool:
    """Returns True if the transition is allowed, raises ValueError if invalid."""
    if new_status in ALLOWED_TRANSITIONS.get(current_status, set()):
        return True
    raise ValueError(
        f"Invalid state transition: Cannot move from {current_status.value} to {new_status.value}."
    )