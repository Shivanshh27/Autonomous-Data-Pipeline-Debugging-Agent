import logging

from src.logger import get_logger


def test_logger_writes_to_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    logger = get_logger("test_pipeline_logger")

    logger.info("Test pipeline started")
    logger.error("Test pipeline failed")

    for handler in logger.handlers:
        handler.flush()

    log_file = tmp_path / "logs" / "pipeline.log"

    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")

    assert "Test pipeline started" in content
    assert "Test pipeline failed" in content
    assert "INFO" in content
    assert "ERROR" in content