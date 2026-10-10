from src.failure_history import save_pipeline_run
from src.history_analyzer import analyze_pipeline_history


def test_detects_repeated_failures(tmp_path):
    db_path = str(tmp_path / "history.db")

    for _ in range(3):
        save_pipeline_run(
            status="FAILED",
            total_failed_checks=1,
            dataset_path="data/raw/customers.csv",
            db_path=db_path
        )

    result = analyze_pipeline_history(db_path)

    assert result["total_runs"] == 3
    assert result["latest_status"] == "FAILED"
    assert result["consecutive_failures"] == 3
    assert result["failure_pattern"] == "REPEATED_FAILURE"


def test_detects_latest_success(tmp_path):
    db_path = str(tmp_path / "history.db")

    save_pipeline_run(
        status="FAILED",
        total_failed_checks=1,
        dataset_path="data/raw/customers.csv",
        db_path=db_path
    )

    save_pipeline_run(
        status="PASSED",
        total_failed_checks=0,
        dataset_path="data/raw/customers.csv",
        db_path=db_path
    )

    result = analyze_pipeline_history(db_path)

    assert result["latest_status"] == "PASSED"
    assert result["consecutive_failures"] == 0
    assert result["failure_pattern"] == "LATEST_RUN_PASSED"


def test_handles_empty_history(tmp_path):
    db_path = str(tmp_path / "history.db")

    result = analyze_pipeline_history(db_path)

    assert result["total_runs"] == 0
    assert result["latest_status"] is None
    assert result["failure_pattern"] == "NO_HISTORY"

def test_repeated_failures_include_recommended_action(tmp_path):
    db_path = str(tmp_path / "history.db")

    for _ in range(3):
        save_pipeline_run(
            status="FAILED",
            total_failed_checks=1,
            dataset_path="data/raw/customers.csv",
            db_path=db_path
        )

    result = analyze_pipeline_history(db_path)

    assert result["failure_pattern"] == "REPEATED_FAILURE"
    assert "Investigate recurring failures" in result["recommended_action"]