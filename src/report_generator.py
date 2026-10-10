import json
from datetime import datetime, timezone
from pathlib import Path


def generate_report(pipeline_result, output_path):
    report = {
        "project": "Autonomous Data Pipeline Debugging Agent",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": pipeline_result["status"],
        "run_id": pipeline_result.get("run_id"),
        "total_failed_checks": len(
            pipeline_result.get("failed_checks", [])
        ),
        "schema_results": pipeline_result.get("schema_results", []),
        "missing_results": pipeline_result.get("missing_results", []),
        "diagnoses": pipeline_result.get("diagnoses", []),
        "history_analysis": pipeline_result.get("history_analysis"),
        "error": pipeline_result.get("error")
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report