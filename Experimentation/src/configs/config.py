from typing import Optional

import yaml
from pydantic import BaseModel as PBM
from pydantic import Field


class ModelConfig(PBM):
    name: str = Field(..., description="Model name to save with")
    models_string: Optional[str] = Field(None, description="model string")
    tokenizer_name: Optional[str] = Field(
        None, description="Name of the tokenizer to use"
    )
    temperature: float | int = Field(
        ..., description="Temperature to use the models with"
    )
    max_tokens: int = Field(...)
    batch_size: Optional[int] = Field(None, description="batch size for local models")


class ErrorHandlingConfig(PBM):
    backoff_factor: int = Field(
        default=1, description="Backoff factor for retrying api query"
    )
    max_retries: int = Field(
        default=3, description="Max number of retries for api queries"
    )


class DataConfig(PBM):
    images_generic_path: Optional[str] = Field(
        None, description="The generic path to the image files"
    )
    images: Optional[str] = Field(None, description="Path of the image folder")
    dataset: str = Field(..., description="The path to the dataset")


class PromptConfig(PBM):
    type: str = Field(..., description="Which prompt to use")
    single: bool = Field(
        default=True, description="Whether to prompt the model with single attribute"
    )


class ResultsConfig(PBM):
    suffix: str = Field(..., description="unique suffix to save results with")
    results_path: Optional[str] = Field(
        default="results", description="Path to the model responses"
    )
    responses_path: Optional[str] = Field(
        default="model_responses",
        description="Path to where the api responses will be saved.",
    )


class Config(PBM):
    max_workers: int = Field(
        1, description="Number of workers (Batch-size) to use for parallel generation"
    )
    model: ModelConfig = Field(..., description="Model config")
    error_handling: Optional[ErrorHandlingConfig] = Field(
        None, description="Error handling for api calls"
    )
    data: DataConfig = Field(..., description="Data config")
    prompt: PromptConfig = Field(..., description="Prompt config")
    results: ResultsConfig = Field(..., description="Results config")


def load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return Config(**data)
