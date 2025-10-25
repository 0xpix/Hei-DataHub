"""
Smart autocomplete suggestions for Hei-DataHub search.

Provides context-aware autocomplete with:
- Field-specific suggestions (source:, project:, tag:, owner:, size:)
- Ranked by frequency, recency, and prefix match
"""

import logging
from typing import Optional
from textual.suggester import Suggester

logger = logging.getLogger(__name__)


class SmartSearchSuggester(Suggester):
    """Context-aware search suggester using metadata from index."""

    def __init__(self, case_sensitive: bool = False):
        super().__init__(case_sensitive=case_sensitive)
        self._suggestion_service = None

    def _get_service(self):
        if self._suggestion_service is None:
            try:
                from mini_datahub.services.suggestion_service import get_suggestion_service
                self._suggestion_service = get_suggestion_service()
            except Exception as e:
                logger.warning(f"Failed to load suggestion service: {e}")
        return self._suggestion_service

    def _parse_input(self, value: str):
        """
        Parse input to detect if we're typing a field name or field value.

        Returns:
            tuple: (field_key, partial_value, is_typing_field_name)
            - field_key: "project", "source", etc., or None if typing field name
            - partial_value: the partial text being typed
            - is_typing_field_name: True if typing field name, False if typing value
        """
        if not value or not value.strip():
            return (None, "", True)
        tokens = value.split()
        if not tokens:
            return (None, "", True)
        last_token = tokens[-1]

        # Check if typing a field value (has colon with something after it)
        if ":" in last_token:
            parts = last_token.split(":", 1)
            if len(parts) == 2:
                field = parts[0].lower()
                partial_value = parts[1]
                supported_fields = {"source", "project", "tag", "owner", "size", "format", "type"}
                if field in supported_fields:
                    # Typing field value
                    return (field, partial_value, False)

        # Typing field name (no colon yet, or unrecognized field)
        return (None, last_token, True)

    async def get_suggestion(self, value: str):
        service = self._get_service()
        if not service or not value or not value.strip():
            return None
        try:
            field_key, partial_value, is_typing_field = self._parse_input(value)

            # If typing field name, suggest field names
            if is_typing_field:
                field_names = ["source:", "project:", "tag:", "owner:", "size:", "format:", "type:"]
                partial_lower = partial_value.lower()

                # Find matching field names
                for field_name in field_names:
                    if field_name.startswith(partial_lower) and field_name != partial_lower:
                        # Found a match - return full suggestion
                        tokens = value.split()
                        if tokens:
                            tokens[-1] = field_name
                            return " ".join(tokens)
                        else:
                            return field_name

                # No field name match
                return None

            # Otherwise, suggest field values
            suggestions = service.get_suggestions(key=field_key, typed=partial_value, max_suggestions=1)
            if not suggestions:
                return None
            top = suggestions[0]
            tokens = value.split()
            if tokens:
                tokens[-1] = top.insert_text.rstrip()
                return " ".join(tokens)
            else:
                return top.insert_text.rstrip()
        except Exception as e:
            logger.debug(f"Suggestion error: {e}")
            return None
