from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.pipeline_runner import run_pipeline


app = FastAPI(
    title="OpsPilot AI",
    description="Autonomous Data Pipeline Debugging Agent API",
    version="0.1.0",
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class PipelineRunRequest(BaseModel):
    file_path: str = Field(
        ...,
        description="Path to the input CSV file, relative to the project root or absolute.",
        min_length=1,
    )


@app.get("/")
def root():
    return {
        "name": "OpsPilot AI",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OpsPilot AI",
    }


@app.post("/pipeline/run")
def execute_pipeline(request: PipelineRunRequest):
    supplied_path = Path(request.file_path)

    if not supplied_path.is_absolute():
        supplied_path = PROJECT_ROOT / supplied_path

    try:
        file_path = supplied_path.resolve(strict=True)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Input dataset was not found.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="The supplied path is not a file.",
        )

    if file_path.suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Only CSV input files are supported.",
        )

    try:
        result = run_pipeline(str(file_path))
        return result

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Pipeline execution failed. Check the application logs.",
        )