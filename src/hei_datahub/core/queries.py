"""
Query parsing and AST for structured searches.

Supports syntax like:
- source:github
- format:csv
- date:>2025-01
- size:<100MB
- tag:climate
- "quoted terms"
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, List, Optional
import re


class QueryOperator(Enum):
    """Query operators for field comparisons."""
    EQ = "="
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    CONTAINS = ":"


@dataclass
class QueryTerm:
    """A single query term (field:value or free text)."""
    field: Optional[str] = None
    operator: QueryOperator = QueryOperator.CONTAINS
    value: str = ""
    is_free_text: bool = False


@dataclass
class ParsedQuery:
    """Parsed and structured query."""
    terms: List[QueryTerm]
    free_text_query: str = ""  # Combined free text for FTS

    def has_field_filters(self) -> bool:
        """Check if query has any field-specific filters."""
        return any(not term.is_free_text for term in self.terms)

    def get_field_terms(self, field: str) -> List[QueryTerm]:
        """Get all terms for a specific field."""
        return [t for t in self.terms if t.field == field]


class QueryParseError(Exception):
    """Error parsing query."""
    pass


class QueryParser:
    """
    Parse structured search queries.

    Supported fields:
    - source: Source URL/library
    - format: File format
    - type: Data type
    - tag: Tags
    - date_created: Creation date
    - size: Dataset size
    - name: Dataset name
    - id: Dataset ID
    - project: Used in projects
    """

    SUPPORTED_FIELDS = {
        "source", "format", "type", "tag", "tags",
        "date_created", "date", "size", "name", "id", "project"
    }

    # Pattern to match various field query formats:
    # field:value, field:>value, field:<value, field:"value"
    # Note: The colon is always present, followed by optional operator
    FIELD_PATTERN = re.compile(
        r'(\w+):(>=|<=|>|<)?"([^"]+)"|(\w+):(>=|<=|>|<)?(\S+)'
    )

    # Pattern to match quoted strings
    QUOTED_PATTERN = re.compile(r'"([^"]+)"')

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a query string into a structured query.

        Args:
            query: Raw query string

        Returns:
            ParsedQuery with structured terms

        Raises:
            QueryParseError: If query is malformed
        """
        if not query or not query.strip():
            return ParsedQuery(terms=[], free_text_query="")

        terms: List[QueryTerm] = []
        remaining = query

        # Extract field:value patterns
        for match in self.FIELD_PATTERN.finditer(query):
            if match.group(1):  # Quoted value
                field = match.group(1).lower()
                op_str = match.group(2) or ":"  # Default to : if no operator
                operator = self._parse_operator(op_str)
                value = match.group(3)
            else:  # Unquoted value
                field = match.group(4).lower()
                op_str = match.group(5) or ":"  # Default to : if no operator
                operator = self._parse_operator(op_str)
                value = match.group(6)

            if field not in self.SUPPORTED_FIELDS:
                # Treat as free text if field is not recognized
                continue

            terms.append(QueryTerm(
                field=field,
                operator=operator,
                value=value,
                is_free_text=False
            ))

            # Remove this match from remaining text
            remaining = remaining.replace(match.group(0), " ", 1)

        # Extract remaining free text (respecting quotes)
        free_text_parts = []
        for quoted_match in self.QUOTED_PATTERN.finditer(remaining):
            free_text_parts.append(quoted_match.group(1))
            remaining = remaining.replace(quoted_match.group(0), " ", 1)

        # Add unquoted remaining text
        remaining_tokens = remaining.split()
        free_text_parts.extend(remaining_tokens)

        # Combine free text
        free_text = " ".join(free_text_parts).strip()

        # Add free text terms
        if free_text:
            for token in free_text.split():
                if len(token) >= 2:  # Skip single chars
                    terms.append(QueryTerm(
                        value=token,
                        is_free_text=True
                    ))

        return ParsedQuery(terms=terms, free_text_query=free_text)

    def _parse_operator(self, op_str: str) -> QueryOperator:
        """Parse operator string to enum."""
        mapping = {
            ":": QueryOperator.CONTAINS,
            "=": QueryOperator.EQ,
            ">": QueryOperator.GT,
            "<": QueryOperator.LT,
            ">=": QueryOperator.GTE,
            "<=": QueryOperator.LTE,
        }
        return mapping.get(op_str, QueryOperator.CONTAINS)

    def validate_field_value(self, field: str, value: str) -> bool:
        """
        Validate that a value is appropriate for a field.

        Args:
            field: Field name
            value: Field value

        Returns:
            True if valid, False otherwise
        """
        try:
            if field in ("date_created", "date"):
                # Try parsing as ISO date
                self._parse_date(value)
            elif field == "size":
                # Try parsing size with units
                self._parse_size(value)
            return True
        except (ValueError, QueryParseError):
            return False

    def _parse_date(self, value: str) -> date:
        """Parse date string (supports partial dates)."""
        # Try full ISO date
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return date.fromisoformat(value)

        # Try year-month
        if re.match(r'^\d{4}-\d{2}$', value):
            return date.fromisoformat(f"{value}-01")

        # Try year
        if re.match(r'^\d{4}$', value):
            return date.fromisoformat(f"{value}-01-01")

        raise QueryParseError(f"Invalid date format: {value}")

    def _parse_size(self, value: str) -> int:
        """Parse size string (e.g., '100MB', '1.5GB') to bytes."""
        match = re.match(r'^([\d.]+)\s*([KMGT]?B)?$', value.upper())
        if not match:
            raise QueryParseError(f"Invalid size format: {value}")

        number = float(match.group(1))
        unit = match.group(2) or "B"

        multipliers = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 ** 2,
            "GB": 1024 ** 3,
            "TB": 1024 ** 4,
        }

        return int(number * multipliers[unit])


def suggest_field_completions(partial: str) -> List[str]:
    """
    Suggest field names for autocomplete.

    Args:
        partial: Partial field name

    Returns:
        List of matching field names
    """
    partial_lower = partial.lower()
    return [
        f for f in QueryParser.SUPPORTED_FIELDS
        if f.startswith(partial_lower)
    ]


def suggest_operator_completions(field: str) -> List[str]:
    """
    Suggest operators for a field.

    Args:
        field: Field name

    Returns:
        List of valid operators
    """
    if field in ("date_created", "date", "size"):
        return [":", ">", "<", ">=", "<="]
    return [":"]
