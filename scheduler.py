from datetime import timedelta

OWNED_RECHECK_DAYS = 30  # how long until an OWNED problem gets spot-checked again

def calculate_next_status(current_status, result, attempt_date):
    """
    Given the current status, the result of today's attempt ('Cold' or 'Help'),
    and the date of the attempt, returns (new_status, next_revisit_date).
    """
    if result == "Help":
        new_status = "SEEDED"
        next_revisit = attempt_date + timedelta(days=2)
        return new_status, next_revisit

    if result == "Cold":
        if current_status == "SEEDED":
            new_status = "COLD-1"
            next_revisit = attempt_date + timedelta(days=3)
        elif current_status == "COLD-1":
            new_status = "COLD-2"
            next_revisit = attempt_date + timedelta(days=7)
        elif current_status in ("COLD-2", "OWNED"):
            new_status = "OWNED"
            next_revisit = attempt_date + timedelta(days=OWNED_RECHECK_DAYS)
        else:
            raise ValueError(f"Unexpected status: {current_status}")
        return new_status, next_revisit

    raise ValueError(f"Unknown result: {result}")