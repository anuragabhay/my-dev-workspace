"""
UI structure tests: verify index.html contains required elements for AC3, AC4, AC5.
"""

import re
from pathlib import Path

import pytest

INDEX_PATH = Path(__file__).resolve().parent.parent / "static" / "index.html"


class TestDarkGlassUI:
    """AC3: Dark glass aesthetic, polished layout."""

    def test_css_vars_present(self):
        """--bg, --surface, glass styles defined."""
        html = INDEX_PATH.read_text()
        assert "--bg:" in html or "--bg " in html
        assert "#0a0a0f" in html
        assert "backdrop-filter" in html or "-webkit-backdrop-filter" in html
        assert "rgba(18, 18, 26" in html

    def test_glass_class_exists(self):
        """Glass panel class for chat bubbles and reasoning."""
        html = INDEX_PATH.read_text()
        assert 'class="glass"' in html or ".glass" in html


class TestReasoningPanel:
    """AC4: Reasoning panel collapsible."""

    def test_reasoning_panel_exists(self):
        """Reasoning panel and toggle present."""
        html = INDEX_PATH.read_text()
        assert "reasoning-panel" in html
        assert "reasoning-toggle" in html
        assert "collapsed" in html

    def test_toggle_handler_exists(self):
        """toggleReasoning or collapse logic in JS."""
        html = INDEX_PATH.read_text()
        assert "toggleReasoning" in html or "reasoningCollapsed" in html
        assert "reasoningPanel.classList" in html or "reasoning-panel" in html

    def test_chat_mode_hint(self):
        """Chat mode shows 'no reasoning flow' hint."""
        html = INDEX_PATH.read_text()
        assert "Chat mode" in html
        assert "no reasoning flow" in html


class TestModeToggle:
    """AC5: Mode toggle functional (Auto/Chat/Orchestrate)."""

    def test_mode_buttons_exist(self):
        """Auto, Chat, Orchestrate buttons present."""
        html = INDEX_PATH.read_text()
        assert "data-mode=\"auto\"" in html or 'data-mode="auto"' in html
        assert "data-mode=\"chat\"" in html or 'data-mode="chat"' in html
        assert "data-mode=\"orchestration\"" in html or 'data-mode="orchestration"' in html

    def test_mode_sent_in_request(self):
        """selectedMode sent in API request."""
        html = INDEX_PATH.read_text()
        assert "mode:" in html and "selectedMode" in html
        assert "/api/chat" in html
