import pandas as pd

def calculate_missing_percentage(df):
    total_rows = len(df)

    if total_rows == 0:
        raise ValueError("Dataset is empty. Cannot calculate missing percentage.")

    missing_counts = df.isnull().sum()

    missing_percentage = (missing_counts / total_rows) * 100

    return missing_counts, missing_percentage


def validate_missing_values(df, threshold=5.0):
    missing_counts, missing_percentage = calculate_missing_percentage(df)

    results = []

    for column in df.columns:
        missing_count = int(missing_counts[column])
        percentage = float(missing_percentage[column])

        if percentage > threshold:
            status = "FAILED"
        else:
            status = "PASSED"

        results.append({
            "column": column,
            "missing_count": missing_count,
            "missing_percentage": round(percentage, 2),
            "threshold": threshold,
            "status": status
        })

    return results


def main():
    file_path = "data/raw/customers.csv"

    df = pd.read_csv(file_path)

    print("Customer Dataset")
    print(df)

    print("\nDataset Shape:")
    print(df.shape)

    print("\nMissing Value Validation")
    print("-" * 75)

    results = validate_missing_values(df, threshold=5.0)

    for result in results:
        print(
            f"Column: {result['column']} | "
            f"Missing: {result['missing_count']} | "
            f"Missing %: {result['missing_percentage']}% | "
            f"Threshold: {result['threshold']}% | "
            f"Status: {result['status']}"
        )


if __name__ == "__main__":
    main()