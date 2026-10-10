import pandas as pd

from src.recovery_engine import recover_missing_values


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