def analyze_missing_values(missing_results):
    diagnoses = []

    for result in missing_results:

        if result["status"] != "FAILED":
            continue

        column = result["column"]
        missing_count = result["missing_count"]
        missing_percentage = result["missing_percentage"]
        threshold = result["threshold"]

        if column == "customer_id":
            likely_cause = (
                "Customer identifiers may be missing in the source data "
                "or may have been lost during an upstream transformation."
            )

            recommended_action = (
                "Inspect the source records and upstream transformation "
                "steps. Recover identifiers from the authoritative source "
                "if possible."
            )

        else:
            likely_cause = (
                "The source data or an upstream transformation may have "
                "introduced missing values."
            )

            recommended_action = (
                "Inspect the affected records and trace the upstream "
                "data source or transformation."
            )

        diagnosis = {
            "failure_type": "MISSING_VALUES",
            "column": column,
            "missing_count": missing_count,
            "missing_percentage": missing_percentage,
            "threshold": threshold,
            "severity": "HIGH" if missing_percentage >= 20 else "MEDIUM",
            "likely_cause": likely_cause,
            "recommended_action": recommended_action,
            "automatic_recovery": False
        }

        diagnoses.append(diagnosis)

    return diagnoses