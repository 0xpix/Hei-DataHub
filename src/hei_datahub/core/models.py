"""
Pydantic models mirroring the JSON Schema for type-safe validation.
"""
from datetime import date
from typing import Any, Optional

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
    category: str = Field(
        ...,
        alias="category",
        description="Dataset category (Climate, Land Cover, etc.)",
    )
    description: str = Field(
        ..., alias="description", min_length=1, description="Detailed description"
    )
    source: str = Field(
        ...,
        alias="source",
        min_length=1,
        description="Human-readable origin",
    )
    access_method: str = Field(
        ...,
        alias="access_method",
        min_length=1,
        description="Machine-readable access identifier (GEE:..., PY:..., etc.)",
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
    reference: Optional[str] = Field(None, alias="reference", description="Formal citation or DOI")
    tags: Optional[list[str]] = Field(None, alias="tags")
    file_format: Optional[str] = Field(None, alias="file_format")
    size: Optional[str] = Field(None, alias="size")
    data_types: Optional[list[str]] = Field(None, alias="data_types")
    used_in_projects: Optional[list[str]] = Field(None, alias="used_in_projects")
    schema_fields: Optional[list[SchemaField]] = Field(None, alias="schema_fields")
    last_updated: Optional[date] = Field(None, alias="last_updated")
    dependencies: Optional[str] = Field(None, alias="dependencies")
    preprocessing_steps: Optional[str] = Field(None, alias="preprocessing_steps")
    linked_documentation: Optional[list[str]] = Field(None, alias="linked_documentation")
    cite: Optional[str] = Field(None, alias="cite")
    spatial_resolution: Optional[str] = Field(None, alias="spatial_resolution")
    temporal_resolution: Optional[str] = Field(None, alias="temporal_resolution")
    temporal_coverage: Optional[str] = Field(None, alias="temporal_coverage")
    spatial_coverage: Optional[str] = Field(None, alias="spatial_coverage")
    codes: Optional[list[str]] = Field(None, alias="codes")
    extras: Optional[dict[str, Any]] = Field(None, alias="extras")

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

    @field_validator("access_method")
    @classmethod
    def validate_access_method(cls, v: str) -> str:
        """Ensure Access Method starts with a valid prefix."""
        valid_prefixes = ("GEE:", "PY:", "FILE:", "API:")
        if not v.startswith(valid_prefixes):
            raise ValueError(f"Access Method must start with one of: {', '.join(valid_prefixes)}")
        if "\n" in v:
            raise ValueError("Access Method must be single-line")
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary with aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)
