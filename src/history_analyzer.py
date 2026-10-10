from src.failure_history import get_pipeline_history


def analyze_pipeline_history(db_path="data/processed/failure_history.db"):
    history = get_pipeline_history(db_path)

    if not history:
        return {
            "total_runs": 0,
            "latest_status": None,
            "consecutive_failures": 0,
            "failure_pattern": "NO_HISTORY"
        }

    latest_run = history[0]

    consecutive_failures = 0

    for run in history:
        if run["status"] == "FAILED":
            consecutive_failures += 1
        else:
            break

    if latest_run["status"] == "PASSED":
        failure_pattern = "LATEST_RUN_PASSED"

    elif consecutive_failures >= 3:
        failure_pattern = "REPEATED_FAILURE"

    else:
        failure_pattern = "RECENT_FAILURE"

    return {
        "total_runs": len(history),
        "latest_status": latest_run["status"],
        "consecutive_failures": consecutive_failures,
        "failure_pattern": failure_pattern
    }