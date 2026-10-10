import pandas as pd


def validate_schema(df, expected_schema):
    results = []

    # Check 1: Required columns
    for column, expected_type in expected_schema.items():

        if column not in df.columns:
            results.append({
                "check": "required_column",
                "column": column,
                "expected": expected_type,
                "actual": None,
                "status": "FAILED",
                "message": f"Required column '{column}' is missing."
            })

            continue

        # Check 2: Data types
        actual_type = str(df[column].dtype)

        if actual_type != expected_type:
            results.append({
                "check": "data_type",
                "column": column,
                "expected": expected_type,
                "actual": actual_type,
                "status": "FAILED",
                "message": (
                    f"Column '{column}' has type '{actual_type}', "
                    f"but expected '{expected_type}'."
                )
            })
        else:
            results.append({
                "check": "data_type",
                "column": column,
                "expected": expected_type,
                "actual": actual_type,
                "status": "PASSED",
                "message": f"Column '{column}' has the expected data type."
            })

    # Check 3: Unexpected columns
    for column in df.columns:
        if column not in expected_schema:
            results.append({
                "check": "unexpected_column",
                "column": column,
                "expected": None,
                "actual": str(df[column].dtype),
                "status": "WARNING",
                "message": f"Unexpected column '{column}' found."
            })

    return results


def main():
    file_path = "data/raw/customers.csv"

    df = pd.read_csv(file_path)

    expected_schema = {
        "customer_id": "str",
        "age": "int64",
        "city": "str"
    }

    results = validate_schema(df, expected_schema)

    print("Schema Validation Report")
    print("-" * 75)

    for result in results:
        print(
            f"Check: {result['check']} | "
            f"Column: {result['column']} | "
            f"Status: {result['status']} | "
            f"Message: {result['message']}"
        )


if __name__ == "__main__":
    main()