import pandas as pd

from src.data_profiler import validate_missing_values
from src.schema_validator import validate_schema


def run_pipeline(file_path):
    print("=" * 70)
    print("OPSPILOT AI - DATA PIPELINE VALIDATION")
    print("=" * 70)

    # Step 1: Load dataset
    try:
        df = pd.read_csv(file_path)
        print(f"\n[INFO] Dataset loaded successfully: {file_path}")
        print(f"[INFO] Rows: {len(df)}, Columns: {len(df.columns)}")

    except FileNotFoundError:
        print(f"\n[ERROR] Dataset file not found: {file_path}")
        return {
            "status": "FAILED",
            "error": "FILE_NOT_FOUND"
        }

    except pd.errors.EmptyDataError:
        print("\n[ERROR] Dataset file is empty.")
        return {
            "status": "FAILED",
            "error": "EMPTY_FILE"
        }

    # Step 2: Define expected schema
    expected_schema = {
        "customer_id": "str",
        "age": "int64",
        "city": "str"
    }

    # Step 3: Run schema validation
    schema_results = validate_schema(df, expected_schema)

    print("\n--- SCHEMA VALIDATION ---")

    for result in schema_results:
        print(
            f"{result['status']} | "
            f"{result['check']} | "
            f"{result['column']} | "
            f"{result['message']}"
        )

    # Step 4: Run missing-value validation
    missing_results = validate_missing_values(df, threshold=5.0)

    print("\n--- MISSING VALUE VALIDATION ---")

    for result in missing_results:
        print(
            f"{result['status']} | "
            f"{result['column']} | "
            f"Missing: {result['missing_count']} | "
            f"Missing %: {result['missing_percentage']}%"
        )

    # Step 5: Determine overall status
    all_results = schema_results + [
        {
            "status": result["status"],
            "check": "missing_values",
            "column": result["column"]
        }
        for result in missing_results
    ]

    failed_checks = [
        result for result in all_results
        if result["status"] == "FAILED"
    ]

    if failed_checks:
        overall_status = "FAILED"
    else:
        overall_status = "PASSED"

    print("\n" + "=" * 70)
    print(f"OVERALL PIPELINE STATUS: {overall_status}")
    print(f"Total failed checks: {len(failed_checks)}")
    print("=" * 70)

    return {
        "status": overall_status,
        "schema_results": schema_results,
        "missing_results": missing_results,
        "failed_checks": failed_checks
    }


if __name__ == "__main__":
    run_pipeline("data/raw/customers.csv")