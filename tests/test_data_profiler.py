import pandas as pd
import pytest

from src.data_profiler import (
    calculate_missing_percentage,
    validate_missing_values
)


def test_no_missing_values():
    df = pd.DataFrame({
        "customer_id": ["C101", "C102"],
        "age": [22, 25]
    })

    results = validate_missing_values(df, threshold=5.0)

    assert results[0]["missing_count"] == 0
    assert results[0]["status"] == "PASSED"


def test_missing_values_detected():
    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "age": [22, 25, 24]
    })

    results = validate_missing_values(df, threshold=5.0)

    assert results[0]["missing_count"] == 1
    assert results[0]["missing_percentage"] == 33.33
    assert results[0]["status"] == "FAILED"


def test_threshold_boundary():
    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103", "C104"]
    })

    results = validate_missing_values(df, threshold=25.0)

    assert results[0]["missing_percentage"] == 25.0
    assert results[0]["status"] == "PASSED"


def test_empty_dataset():
    df = pd.DataFrame(columns=["customer_id", "age"])

    with pytest.raises(ValueError):
        calculate_missing_percentage(df)