import pandas as pd

from src.recovery_engine import (
    recover_missing_values,
    validate_recovery
)
from src.recovery_engine import save_recovered_data
def test_fills_missing_values_without_modifying_original():
    df = pd.DataFrame({
        "city": ["Bhopal", None, "Indore"]
    })

    rules = {
        "city": {
            "strategy": "fill_value",
            "value": "Unknown"
        }
    }

    recovered_df, recovery_log = recover_missing_values(df, rules)

    # Recovered data should contain no missing city values.
    assert recovered_df["city"].isna().sum() == 0

    # The missing value should be replaced with the configured value.
    assert recovered_df.loc[1, "city"] == "Unknown"

    # The original DataFrame must remain unchanged.
    assert pd.isna(df.loc[1, "city"])

    # Recovery should be recorded.
    assert recovery_log[0]["status"] == "RECOVERED"
    assert recovery_log[0]["recovered_count"] == 1

def test_skips_nonexistent_column():
    df = pd.DataFrame({
        "city": ["Bhopal", "Indore"]
    })

    rules = {
        "country": {
            "strategy": "fill_value",
            "value": "India"
        }
    }

    recovered_df, recovery_log = recover_missing_values(df, rules)

    assert list(recovered_df.columns) == ["city"]
    assert recovery_log[0]["status"] == "SKIPPED"
    assert recovery_log[0]["reason"] == "Column does not exist"


def test_skips_unsupported_strategy():
    df = pd.DataFrame({
        "city": ["Bhopal", None]
    })

    rules = {
        "city": {
            "strategy": "unknown_strategy"
        }
    }

    recovered_df, recovery_log = recover_missing_values(df, rules)

    assert pd.isna(recovered_df.loc[1, "city"])
    assert recovery_log[0]["status"] == "SKIPPED"
    assert recovery_log[0]["reason"] == "Unsupported recovery strategy"

def test_validates_successful_recovery():
    original_df = pd.DataFrame({
        "city": ["Bhopal", None, "Indore"]
    })

    recovered_df = original_df.copy()
    recovered_df["city"] = recovered_df["city"].fillna("Unknown")

    result = validate_recovery(original_df, recovered_df)

    assert result["status"] == "IMPROVED"
    assert result["original_missing_values"] == 1
    assert result["recovered_missing_values"] == 0
    assert result["remaining_missing_values"] == 0

def test_detects_changed_data_type():
    original_df = pd.DataFrame({
        "age": pd.Series([20, 25], dtype="int64")
    })

    recovered_df = pd.DataFrame({
        "age": pd.Series([20, 25], dtype="float64")
    })

    result = validate_recovery(original_df, recovered_df)

    assert result["schema_valid"] is False
    assert "age" in result["changed_dtypes"]


def test_detects_missing_column():
    original_df = pd.DataFrame({
        "customer_id": ["C101", "C102"],
        "city": ["Bhopal", "Indore"]
    })

    recovered_df = pd.DataFrame({
        "customer_id": ["C101", "C102"]
    })

    result = validate_recovery(original_df, recovered_df)

    assert result["schema_valid"] is False
    assert "city" in result["missing_columns"]

def test_saves_recovered_data_without_changing_original(tmp_path):
    original_df = pd.DataFrame({
        "city": ["Bhopal", None, "Indore"]
    })

    recovered_df = original_df.copy()
    recovered_df["city"] = recovered_df["city"].fillna("Unknown")

    original_file = tmp_path / "customers.csv"
    output_file = tmp_path / "processed" / "customers_recovered.csv"

    original_df.to_csv(original_file, index=False)

    saved_path = save_recovered_data(recovered_df, output_file)

    saved_df = pd.read_csv(saved_path)
    unchanged_original = pd.read_csv(original_file)

    assert saved_df["city"].isna().sum() == 0
    assert saved_df.loc[1, "city"] == "Unknown"
    assert pd.isna(unchanged_original.loc[1, "city"])