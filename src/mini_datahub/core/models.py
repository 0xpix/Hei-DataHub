"""
Pydantic models mirroring the JSON Schema for type-safe validation.
"""
from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SchemaField(BaseModel):
    """A field/column definition in a dataset schema."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Data type")
    description: Optional[str] = Field(None, description="Field description")


class DatasetMetadata(BaseModel):
    """
    Complete metadata model for a dataset.

    Uses aliases to match the human-readable keys in YAML (with underscores).
    """

    # Required fields
    id: str = Field(
        ...,
        alias="id",
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
        min_length=1,
        max_length=100,
        description="Unique identifier (slug)",
    )
    dataset_name: str = Field(
        ...,
        alias="dataset_name",
        min_length=1,
        max_length=200,
        description="Human-readable name",
    )
    description: str = Field(
        ..., alias="description", min_length=1, description="Detailed description"
    )
    source: str = Field(
        ...,
        alias="source",
        min_length=1,
        description="URL or library snippet showing origin",
    )
    date_created: date = Field(
        ..., alias="date_created", description="Date when dataset was created"
    )
    storage_location: str = Field(
        ...,
        alias="storage_location",
        min_length=1,
        description="Where the actual data is stored",
    )

    # Optional fields
    file_format: Optional[str] = Field(None, alias="file_format")
    size: Optional[str] = Field(None, alias="size")
    data_types: Optional[List[str]] = Field(None, alias="data_types")
    used_in_projects: Optional[List[str]] = Field(None, alias="used_in_projects")
    schema_fields: Optional[List[SchemaField]] = Field(None, alias="schema_fields")
    last_updated: Optional[date] = Field(None, alias="last_updated")
    dependencies: Optional[str] = Field(None, alias="dependencies")
    preprocessing_steps: Optional[str] = Field(None, alias="preprocessing_steps")
    linked_documentation: Optional[List[str]] = Field(None, alias="linked_documentation")
    cite: Optional[str] = Field(None, alias="cite")
    spatial_resolution: Optional[str] = Field(None, alias="spatial_resolution")
    temporal_resolution: Optional[str] = Field(None, alias="temporal_resolution")
    temporal_coverage: Optional[str] = Field(None, alias="temporal_coverage")
    spatial_coverage: Optional[str] = Field(None, alias="spatial_coverage")
    codes: Optional[List[str]] = Field(None, alias="codes")
    extras: Optional[Dict[str, Any]] = Field(None, alias="extras")

    class Config:
        populate_by_name = True

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is a valid slug."""
        if not v:
            raise ValueError("ID cannot be empty")
        if not v[0].isalnum():
            raise ValueError("ID must start with an alphanumeric character")
        return v.lower()

    def to_dict(self) -> dict:
        """Convert to dictionary with aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)
