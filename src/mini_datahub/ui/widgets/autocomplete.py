"""
Search autocomplete suggester for Textual Input widget.
Provides inline suggestions for search field and operators.
"""
from typing import Optional
from textual.suggester import Suggester

from mini_datahub.core.queries import QueryParser, suggest_field_completions


class SearchSuggester(Suggester):
    """
    Suggester for search input with field-aware autocomplete.

    Provides suggestions for:
    - Field names (source:, format:, type:, etc.)
    - Field values (based on existing datasets)
    """

    def __init__(self, case_sensitive: bool = False):
        """
        Initialize search suggester.

        Args:
            case_sensitive: Whether suggestions are case-sensitive
        """
        super().__init__(case_sensitive=case_sensitive)
        self._load_autocomplete_data()

    def _load_autocomplete_data(self) -> None:
        """Load autocomplete data from existing datasets."""
        try:
            from mini_datahub.services.autocomplete import get_autocomplete_manager

            self.manager = get_autocomplete_manager()
            # Ensure manager has loaded data
            if not self.manager.file_formats and not self.manager.data_types:
                self.manager.load_from_catalog()
        except Exception:
            self.manager = None

    async def get_suggestion(self, value: str) -> Optional[str]:
        """
        Get autocomplete suggestion for the current input value.

        Args:
            value: Current input value

        Returns:
            Suggested completion or None
        """
        if not value or not value.strip():
            return None

        # Get the last token being typed
        tokens = value.split()
        if not tokens:
            return None

        last_token = tokens[-1]

        # Check if we're typing a field name (ends with :)
        if ":" not in last_token:
            # Suggest field name
            matches = suggest_field_completions(last_token)
            if matches:
                # Return the full value with the first match
                rest_of_input = " ".join(tokens[:-1])
                if rest_of_input:
                    return f"{rest_of_input} {matches[0]}:"
                return f"{matches[0]}:"

        # Check if we're typing a value after a colon
        elif ":" in last_token:
            parts = last_token.split(":", 1)
            if len(parts) == 2:
                field, partial_value = parts

                if not self.manager:
                    return None

                # Get suggestions for this field
                suggestions = []
                if field in ("format", "file_format"):
                    suggestions = self.manager.suggest_file_formats(partial_value, limit=5)
                elif field in ("type", "data_type"):
                    suggestions = self.manager.suggest_data_types(partial_value, limit=5)
                elif field == "project":
                    suggestions = self.manager.suggest_projects(partial_value, limit=5)

                if suggestions:
                    # Return the full value with the first match
                    rest_of_input = " ".join(tokens[:-1])
                    if rest_of_input:
                        return f"{rest_of_input} {field}:{suggestions[0]}"
                    return f"{field}:{suggestions[0]}"

        return None


class FieldNameSuggester(Suggester):
    """
    Simple suggester that only suggests field names.
    Lightweight alternative to SearchSuggester.
    """

    def __init__(self, case_sensitive: bool = False):
        """Initialize field name suggester."""
        super().__init__(case_sensitive=case_sensitive)

        # Pre-compute all field suggestions
        self.fields = sorted(QueryParser.SUPPORTED_FIELDS)

    async def get_suggestion(self, value: str) -> Optional[str]:
        """
        Get field name suggestion.

        Args:
            value: Current input value

        Returns:
            Suggested field name or None
        """
        if not value or not value.strip():
            return None

        # Get the last token
        tokens = value.split()
        if not tokens:
            return None

        last_token = tokens[-1].lower()

        # Don't suggest if already has colon or is quoted
        if ":" in last_token or '"' in last_token:
            return None

        # Find first matching field
        for field in self.fields:
            if field.startswith(last_token) and field != last_token:
                # Return the full value with suggestion
                rest_of_input = " ".join(tokens[:-1])
                if rest_of_input:
                    return f"{rest_of_input} {field}:"
                return f"{field}:"

        return None
