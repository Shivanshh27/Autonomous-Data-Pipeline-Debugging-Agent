from src.failure_analyzer import analyze_missing_values


def test_detects_missing_customer_ids():
    missing_results = [
        {
            "column": "customer_id",
            "missing_count": 2,
            "missing_percentage": 40.0,
            "threshold": 5.0,
            "status": "FAILED"
        }
    ]

    diagnoses = analyze_missing_values(missing_results)

    assert len(diagnoses) == 1
    assert diagnoses[0]["failure_type"] == "MISSING_VALUES"
    assert diagnoses[0]["column"] == "customer_id"
    assert diagnoses[0]["severity"] == "HIGH"
    assert diagnoses[0]["automatic_recovery"] is False


def test_ignores_passed_checks():
    missing_results = [
        {
            "column": "age",
            "missing_count": 0,
            "missing_percentage": 0.0,
            "threshold": 5.0,
            "status": "PASSED"
        }
    ]

    diagnoses = analyze_missing_values(missing_results)

    assert diagnoses == []


def test_generates_recommended_action():
    missing_results = [
        {
            "column": "city",
            "missing_count": 1,
            "missing_percentage": 10.0,
            "threshold": 5.0,
            "status": "FAILED"
        }
    ]

    diagnoses = analyze_missing_values(missing_results)

    assert len(diagnoses) == 1
    assert diagnoses[0]["likely_cause"]
    assert diagnoses[0]["recommended_action"]
    assert diagnoses[0]["automatic_recovery"] is False