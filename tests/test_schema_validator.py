import pandas as pd

from src.schema_validator import validate_schema


def test_missing_required_column():
    df = pd.DataFrame({
        "customer_id": ["C101", "C102"],
        "age": [22, 25]
    })

    expected_schema = {
        "customer_id": "str",
        "age": "int64",
        "city": "str"
    }

    results = validate_schema(df, expected_schema)

    city_result = next(
        result for result in results
        if result["column"] == "city"
        and result["check"] == "required_column"
    )

    assert city_result["status"] == "FAILED"


def test_incorrect_data_type():
    df = pd.DataFrame({
        "customer_id": ["C101", "C102"],
        "age": ["twenty-two", "twenty-five"],
        "city": ["Bhopal", "Indore"]
    })

    expected_schema = {
        "customer_id": "str",
        "age": "int64",
        "city": "str"
    }

    results = validate_schema(df, expected_schema)

    age_result = next(
        result for result in results
        if result["column"] == "age"
        and result["check"] == "data_type"
    )

    assert age_result["status"] == "FAILED"


def test_unexpected_column():
    df = pd.DataFrame({
        "customer_id": ["C101"],
        "age": [22],
        "city": ["Bhopal"],
        "email": ["test@example.com"]
    })

    expected_schema = {
        "customer_id": "str",
        "age": "int64",
        "city": "str"
    }

    results = validate_schema(df, expected_schema)

    email_result = next(
        result for result in results
        if result["column"] == "email"
        and result["check"] == "unexpected_column"
    )

    assert email_result["status"] == "WARNING"