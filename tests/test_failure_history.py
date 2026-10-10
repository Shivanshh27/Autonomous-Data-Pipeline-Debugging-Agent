from src.failure_history import (
    initialize_database,
    save_pipeline_run,
    get_pipeline_history
)


def test_database_initialization(tmp_path):
    db_path = tmp_path / "history.db"

    result = initialize_database(str(db_path))

    assert db_path.exists()
    assert result == str(db_path)


def test_save_pipeline_run(tmp_path):
    db_path = tmp_path / "history.db"

    run_id = save_pipeline_run(
        status="FAILED",
        total_failed_checks=1,
        dataset_path="data/raw/customers.csv",
        db_path=str(db_path)
    )

    assert run_id == 1

    history = get_pipeline_history(str(db_path))

    assert len(history) == 1
    assert history[0]["status"] == "FAILED"
    assert history[0]["total_failed_checks"] == 1


def test_multiple_pipeline_runs(tmp_path):
    db_path = tmp_path / "history.db"

    save_pipeline_run(
        status="FAILED",
        total_failed_checks=1,
        dataset_path="data/raw/customers.csv",
        db_path=str(db_path)
    )

    save_pipeline_run(
        status="PASSED",
        total_failed_checks=0,
        dataset_path="data/raw/customers.csv",
        db_path=str(db_path)
    )

    history = get_pipeline_history(str(db_path))

    assert len(history) == 2
    assert history[0]["status"] == "PASSED"
    assert history[1]["status"] == "FAILED"