import pandas as pd
import json
from src.pipeline_runner import run_pipeline


def test_pipeline_passes_with_valid_data(tmp_path):
    df = pd.DataFrame({
        "customer_id": ["C101", "C102", "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    file_path = tmp_path / "valid_customers.csv"
    df.to_csv(file_path, index=False)

    result = run_pipeline(str(file_path))

    assert result["status"] == "PASSED"
    assert len(result["failed_checks"]) == 0


def test_pipeline_fails_with_missing_values(tmp_path):
    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    file_path = tmp_path / "invalid_customers.csv"
    df.to_csv(file_path, index=False)

    result = run_pipeline(str(file_path))

    assert result["status"] == "FAILED"
    assert len(result["failed_checks"]) > 0


def test_pipeline_fails_when_file_is_missing(tmp_path):
    file_path = tmp_path / "does_not_exist.csv"

    result = run_pipeline(str(file_path))

    assert result["status"] == "FAILED"
    assert result["error"] == "FILE_NOT_FOUND"

def test_pipeline_returns_failure_diagnosis(tmp_path):
    import pandas as pd

    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    file_path = tmp_path / "customers_with_missing_ids.csv"
    df.to_csv(file_path, index=False)

    result = run_pipeline(str(file_path))

    assert result["status"] == "FAILED"
    assert len(result["diagnoses"]) == 1

    diagnosis = result["diagnoses"][0]

    assert diagnosis["failure_type"] == "MISSING_VALUES"
    assert diagnosis["column"] == "customer_id"
    assert diagnosis["severity"] == "HIGH"
    assert diagnosis["automatic_recovery"] is False


def test_pipeline_has_no_diagnosis_for_valid_data(tmp_path):
    import pandas as pd

    df = pd.DataFrame({
        "customer_id": ["C101", "C102", "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    file_path = tmp_path / "valid_customers.csv"
    df.to_csv(file_path, index=False)

    result = run_pipeline(str(file_path))

    assert result["status"] == "PASSED"
    assert result["diagnoses"] == []




def test_pipeline_generates_json_report(tmp_path, monkeypatch):
    import pandas as pd

    from src import pipeline_runner

    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    input_path = tmp_path / "customers.csv"
    df.to_csv(input_path, index=False)

    # Keep the generated report inside pytest's temporary directory.
    monkeypatch.chdir(tmp_path)

    result = pipeline_runner.run_pipeline(str(input_path))

    report_path = tmp_path / "reports" / "pipeline_report.json"

    assert report_path.exists()
    assert result["status"] == "FAILED"

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["project"] == "Autonomous Data Pipeline Debugging Agent"
    assert report["status"] == "FAILED"
    assert report["total_failed_checks"] == 1
    assert report["diagnoses"][0]["column"] == "customer_id"

def test_pipeline_logs_execution_events(tmp_path, monkeypatch):
    import logging
    import pandas as pd

    from src import pipeline_runner

    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    input_path = tmp_path / "customers.csv"
    df.to_csv(input_path, index=False)

    # Run the pipeline in a temporary directory.
    monkeypatch.chdir(tmp_path)

    logger = logging.getLogger("pipeline")

    # Prevent previous test handlers from pointing to old directories.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    result = pipeline_runner.run_pipeline(str(input_path))

    log_file = tmp_path / "logs" / "pipeline.log"

    assert log_file.exists()
    assert result["status"] == "FAILED"

    content = log_file.read_text(encoding="utf-8")

    assert "Pipeline execution started" in content
    assert "Dataset loaded successfully" in content
    assert "Schema validation completed" in content
    assert "Missing-value validation failed" in content
    assert "JSON report generated" in content

def test_pipeline_saves_run_to_database(tmp_path, monkeypatch):
    import pandas as pd

    from src import pipeline_runner
    from src.failure_history import get_pipeline_history

    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "age": [22, 25, 24],
        "city": ["Bhopal", "Indore", "Jabalpur"]
    })

    input_path = tmp_path / "customers.csv"
    df.to_csv(input_path, index=False)

    # Is test ka output temporary directory mein rahega.
    monkeypatch.chdir(tmp_path)

    result = pipeline_runner.run_pipeline(str(input_path))

    history = get_pipeline_history()

    assert result["status"] == "FAILED"
    assert "run_id" in result
    assert len(history) == 1
    assert history[0]["run_id"] == result["run_id"]
    assert history[0]["status"] == "FAILED"
    assert history[0]["total_failed_checks"] == 1
    
def test_pipeline_includes_history_analysis(tmp_path):
    import pandas as pd
    from src.pipeline_runner import run_pipeline

    csv_file = tmp_path / "customers.csv"

    df = pd.DataFrame({
        "customer_id": ["C101", "C102"],
        "age": [22, 25],
        "city": ["Bhopal", "Indore"]
    })

    df.to_csv(csv_file, index=False)

    result = run_pipeline(str(csv_file))

    assert "history_analysis" in result
    assert result["history_analysis"]["total_runs"] >= 1
    assert result["history_analysis"]["latest_status"] == "PASSED"
    assert result["history_analysis"]["failure_pattern"] == "LATEST_RUN_PASSED"

def test_json_report_includes_history_analysis(tmp_path):
    import json
    import pandas as pd
    from src.pipeline_runner import run_pipeline

    csv_file = tmp_path / "customers.csv"
    report_file = tmp_path / "report.json"

    df = pd.DataFrame({
        "customer_id": ["C101", "C102"],
        "age": [22, 25],
        "city": ["Bhopal", "Indore"]
    })

    df.to_csv(csv_file, index=False)

    # Check the actual report path used by your pipeline.
    result = run_pipeline(str(csv_file))

    assert "history_analysis" in result