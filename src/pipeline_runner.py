import pandas as pd

from src.data_profiler import validate_missing_values
from src.schema_validator import validate_schema
from src.failure_analyzer import analyze_missing_values
from src.report_generator import generate_report
from src.logger import get_logger
from src.failure_history import save_pipeline_run
from src.history_analyzer import analyze_pipeline_history
from src.recovery_engine import (
    recover_missing_values,
    validate_recovery,
    save_recovered_data,
    decide_recovery_action
)
def run_pipeline(file_path):
    logger = get_logger()
    logger.info("Pipeline execution started")
    logger.info(f"Input dataset: {file_path}")

    print("=" * 70)
    print("AUTONOMOUS DATA PIPELINE DEBUGGING AGENT")
    print("=" * 70)

    # Step 1: Load dataset
    try:
        df = pd.read_csv(file_path)
        logger.info(
            f"Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns"
        )
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
    recovery_rules = {
        "city": {
            "strategy": "fill_value",
            "value": "Unknown"
        }
    }
    # Step 3: Run schema validation
    schema_results = validate_schema(df, expected_schema)

    logger.info("Schema validation completed")

    if any(result["status"] == "FAILED" for result in schema_results):
        logger.error("Schema validation failed")

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
    logger.info("Missing-value validation completed")

    if any(result["status"] == "FAILED" for result in missing_results):
        logger.error("Missing-value validation failed")

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

    if overall_status == "FAILED":
        logger.error("Pipeline execution completed with failures")
    else:
        logger.info("Pipeline execution completed successfully")

    
    # Step 6: Analyze missing-value failures
    diagnoses = analyze_missing_values(missing_results)

    if diagnoses:
        print("\n--- FAILURE DIAGNOSIS ---")

        for diagnosis in diagnoses:
            print(f"\nFailure Type: {diagnosis['failure_type']}")
            print(f"Column: {diagnosis['column']}")
            print(f"Severity: {diagnosis['severity']}")
            print(
                f"Missing Percentage: "
                f"{diagnosis['missing_percentage']}%"
            )

            print(f"\nLikely Cause:")
            print(diagnosis["likely_cause"])

            print(f"\nRecommended Action:")
            print(diagnosis["recommended_action"])

            print(
                f"\nAutomatic Recovery: "
                f"{'ENABLED' if diagnosis['automatic_recovery'] else 'DISABLED'}"
            )

    print("\n" + "=" * 70)
    print(f"OVERALL PIPELINE STATUS: {overall_status}")
    print(f"Total failed checks: {len(failed_checks)}")
    print("=" * 70)
    
    # Step 7: Run recovery only when configured rules can apply
    recovery_result = {
        "attempted": False,
        "status": "NOT_NEEDED",
        "decisions": [],
        "recovery_log": [],
        "validation": None,
        "post_recovery_validation": None,
        "output_path": None
    }

    for column, rule in recovery_rules.items():
        if column not in df.columns:
            decision = decide_recovery_action(
                column=column,
                missing_count=1,
                recovery_rules=recovery_rules,
                schema_valid=False
            )

            recovery_result["decisions"].append(decision)

            print(
                f"\nRecovery Decision for '{column}': "
                f"{decision['decision']}"
            )

            continue

        missing_count = int(df[column].isna().sum())

        decision = decide_recovery_action(
            column=column,
            missing_count=missing_count,
            recovery_rules=recovery_rules,
            schema_valid=not any(
                result["status"] == "FAILED"
                for result in schema_results
            )
        )

        recovery_result["decisions"].append(decision)

        print(
            f"\nRecovery Decision for '{column}': "
            f"{decision['decision']}"
        )

        if decision["decision"] != "ALLOW_RECOVERY":
            continue

        recovered_df, recovery_log = recover_missing_values(
            df,
            {column: rule}
        )

        # Compare original and recovered data
        validation_result = validate_recovery(df, recovered_df)

        post_recovery_schema_results = validate_schema(
            recovered_df,
            expected_schema
        )

        post_recovery_missing_results = validate_missing_values(
            recovered_df,
            threshold=5.0
        )

        post_recovery_failed_checks = [
            result
            for result in (
                post_recovery_schema_results
                + post_recovery_missing_results
            )
            if result["status"] == "FAILED"
        ]

        post_recovery_status = (
            "PASSED"
            if not post_recovery_failed_checks
            else "FAILED"
        )

        output_path = "data/processed/customers_recovered.csv"
        saved_path = save_recovered_data(recovered_df, output_path)

        if (
            validation_result["status"] == "IMPROVED"
            and validation_result["schema_valid"]
        ):
            recovery_result["status"] = "SUCCESS"
        else:
            recovery_result["status"] = "FAILED"

        recovery_result["attempted"] = True
        recovery_result["recovery_log"].extend(recovery_log)
        recovery_result["validation"] = validation_result
        recovery_result["output_path"] = saved_path
        recovery_result["post_recovery_validation"] = {
            "status": post_recovery_status,
            "schema_results": post_recovery_schema_results,
            "missing_results": post_recovery_missing_results,
            "failed_checks": post_recovery_failed_checks
        }

        logger.info("Recovery execution completed")

    if recovery_result["attempted"]:
        print("\n--- RECOVERY RESULT ---")
        print(f"Recovery Log: {recovery_result['recovery_log']}")
        print(f"Validation: {recovery_result['validation']}")
        print(f"Recovered Dataset: {recovery_result['output_path']}")

    pipeline_result = {
    "status": overall_status,
    "schema_results": schema_results,
    "missing_results": missing_results,
    "failed_checks": failed_checks,
    "diagnoses": diagnoses,
    "recovery_result": recovery_result
}

    

    # Save pipeline execution history
    run_id = save_pipeline_run(
        status=overall_status,
        total_failed_checks=len(failed_checks),
        dataset_path=file_path
    )

    # Analyze execution history

    history_analysis = analyze_pipeline_history()

    pipeline_result["history_analysis"] = history_analysis
    pipeline_result["run_id"] = run_id
    
    report_path = "reports/pipeline_report.json"
    generate_report(pipeline_result, report_path)
    logger.info(f"JSON report generated: {report_path}")

    print(f"\n[INFO] JSON report saved to: {report_path}")
    
    print("\n--- PIPELINE HISTORY ANALYSIS ---")
    print(f"Total Runs: {history_analysis['total_runs']}")
    print(f"Latest Status: {history_analysis['latest_status']}")
    print(
        f"Consecutive Failures: "
        f"{history_analysis['consecutive_failures']}"
    )
    print(f"Failure Pattern: {history_analysis['failure_pattern']}")
    print(
        f"Recommended Action: "
        f"{history_analysis['recommended_action']}"
    )
    logger.info(f"Pipeline run saved to database. Run ID: {run_id}")

    print(f"[INFO] Pipeline run saved to database. Run ID: {run_id}")


    return pipeline_result


if __name__ == "__main__":
    run_pipeline("data/processed/customers_recovery_test.csv")