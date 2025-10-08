"""
UI integration test for Bug #10 fix: Multi-term search badge display.

Tests that the HomeScreen correctly displays multiple badges for multi-term searches.
"""
import pytest
from textual.widgets import Static

from mini_datahub.ui.views.home import HomeScreen


@pytest.mark.asyncio
async def test_filter_badges_display_multiple_terms():
    """
    Test that multi-term search displays multiple badges, not one combined badge.
    
    Fixes Bug #10.
    """
    app = HomeScreen()
    
    async with app.run_test() as pilot:
        # Wait for app to initialize
        await pilot.pause()
        
        # Simulate multi-term search input
        query = "rainfall temp rice"
        screen = app.screen
        screen._update_filter_badges(query)
        
        # Check badges container
        badges_container = screen.query_one("#filter-badges-container")
        badges = list(badges_container.query(Static))
        
        # Should have 3 separate badges (one per term)
        assert len(badges) == 3, \
            f"BUG #10: Expected 3 badges for 3 terms, got {len(badges)}"
        
        # Verify each term has its own badge
        badge_texts = [badge.renderable for badge in badges]
        # Each term should appear in some badge
        assert any("rainfall" in str(text) for text in badge_texts)
        assert any("temp" in str(text) for text in badge_texts)
        assert any("rice" in str(text) for text in badge_texts)


@pytest.mark.asyncio
async def test_filter_badges_with_field_filters():
    """
    Test that field filters and free text terms each get their own badges.
    """
    app = HomeScreen()
    
    async with app.run_test() as pilot:
        await pilot.pause()
        
        # Mix of field filter and free text
        query = "format:csv rainfall temp"
        screen = app.screen
        screen._update_filter_badges(query)
        
        badges_container = screen.query_one("#filter-badges-container")
        badges = list(badges_container.query(Static))
        
        # Should have 3 badges: 1 field filter + 2 free text
        assert len(badges) == 3, \
            f"Expected 3 badges (1 filter + 2 terms), got {len(badges)}"
        
        badge_texts = [str(badge.renderable) for badge in badges]
        
        # Field filter should be present
        assert any("format:csv" in text for text in badge_texts)
        
        # Free text terms should each have a badge
        assert any("rainfall" in text for text in badge_texts)
        assert any("temp" in text for text in badge_texts)


@pytest.mark.asyncio
async def test_quoted_phrase_single_badge():
    """
    Test that quoted phrases are treated as single badges.
    """
    app = HomeScreen()
    
    async with app.run_test() as pilot:
        await pilot.pause()
        
        query = '"rice field" rainfall'
        screen = app.screen
        screen._update_filter_badges(query)
        
        badges_container = screen.query_one("#filter-badges-container")
        badges = list(badges_container.query(Static))
        
        # Should have 2 badges: quoted phrase + free term
        assert len(badges) == 2, \
            f"Expected 2 badges (1 phrase + 1 term), got {len(badges)}"


@pytest.mark.asyncio
async def test_empty_query_no_badges():
    """Test that empty queries don't create badges."""
    app = HomeScreen()
    
    async with app.run_test() as pilot:
        await pilot.pause()
        
        query = ""
        screen = app.screen
        screen._update_filter_badges(query)
        
        badges_container = screen.query_one("#filter-badges-container")
        badges = list(badges_container.query(Static))
        
        # Should have no badges
        assert len(badges) == 0
