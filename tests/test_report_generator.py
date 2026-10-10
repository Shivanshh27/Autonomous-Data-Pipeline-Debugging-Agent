import json

from src.report_generator import generate_report


def test_generates_json_report(tmp_path):
    pipeline_result = {
        "status": "FAILED",
        "failed_checks": [
            {
                "column": "customer_id",
                "status": "FAILED"
            }
        ],
        "schema_results": [],
        "missing_results": [],
        "diagnoses": [
            {
                "failure_type": "MISSING_VALUES",
                "column": "customer_id",
                "severity": "HIGH",
                "automatic_recovery": False
            }
        ]
    }

    output_path = tmp_path / "reports" / "pipeline_report.json"

    report = generate_report(pipeline_result, output_path)

    assert output_path.exists()
    assert report["status"] == "FAILED"
    assert report["total_failed_checks"] == 1
    assert len(report["diagnoses"]) == 1

    with output_path.open("r", encoding="utf-8") as file:
        saved_report = json.load(file)

    assert saved_report["status"] == "FAILED"
    assert saved_report["diagnoses"][0]["column"] == "customer_id"