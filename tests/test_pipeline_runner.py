import pandas as pd

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