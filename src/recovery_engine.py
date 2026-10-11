import pandas as pd
from pathlib import Path


def save_recovered_data(df, output_path):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_file, index=False)

    return str(output_file)
def validate_recovery(original_df, recovered_df):
    original_missing = int(original_df.isna().sum().sum())
    recovered_missing = int(recovered_df.isna().sum().sum())

    missing_columns = [
        column
        for column in original_df.columns
        if column not in recovered_df.columns
    ]

    added_columns = [
        column
        for column in recovered_df.columns
        if column not in original_df.columns
    ]

    changed_dtypes = {}

    for column in original_df.columns:
        if column in recovered_df.columns:
            original_dtype = str(original_df[column].dtype)
            recovered_dtype = str(recovered_df[column].dtype)

            if original_dtype != recovered_dtype:
                changed_dtypes[column] = {
                    "original": original_dtype,
                    "recovered": recovered_dtype
                }

    if recovered_missing < original_missing:
        missing_value_status = "IMPROVED"
    elif recovered_missing == original_missing:
        missing_value_status = "UNCHANGED"
    else:
        missing_value_status = "WORSENED"

    schema_valid = (
        len(missing_columns) == 0
        and len(added_columns) == 0
        and len(changed_dtypes) == 0
    )

    return {
        "status": missing_value_status,
        "schema_valid": schema_valid,
        "missing_columns": missing_columns,
        "added_columns": added_columns,
        "changed_dtypes": changed_dtypes,
        "original_missing_values": original_missing,
        "recovered_missing_values": recovered_missing,
        "remaining_missing_values": recovered_missing
    }

def recover_missing_values(df, recovery_rules):
    recovered_df = df.copy()
    recovery_log = []

    for column, rule in recovery_rules.items():
        if column not in recovered_df.columns:
            recovery_log.append({
                "column": column,
                "status": "SKIPPED",
                "reason": "Column does not exist"
            })
            continue

        missing_count = int(recovered_df[column].isna().sum())

        if missing_count == 0:
            continue

        if rule["strategy"] == "fill_value":
            fill_value = rule["value"]

            recovered_df[column] = recovered_df[column].fillna(
                fill_value
            )

            recovery_log.append({
                "column": column,
                "status": "RECOVERED",
                "recovered_count": missing_count,
                "strategy": "fill_value"
            })

        else:
            recovery_log.append({
                "column": column,
                "status": "SKIPPED",
                "reason": "Unsupported recovery strategy"
            })

    return recovered_df, recovery_log