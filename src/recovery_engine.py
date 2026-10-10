import pandas as pd


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