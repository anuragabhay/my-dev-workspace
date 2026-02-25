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


class TestPhase4TerminalPanel:
    """Phase 4: Terminal panel collapsible."""

    def test_terminal_panel_exists(self):
        """Terminal panel and toggle present."""
        html = INDEX_PATH.read_text()
        assert "terminal-panel" in html
        assert "terminal-toggle" in html
        assert "id=\"terminal-panel\"" in html or 'id="terminal-panel"' in html

    def test_terminal_placeholder_or_content(self):
        """Terminal has placeholder or content area."""
        html = INDEX_PATH.read_text()
        assert "Terminal" in html
        assert "terminal-content" in html or "terminal-placeholder" in html


class TestPhase4LayoutPersistence:
    """Phase 4: Layout persistence via localStorage."""

    def test_layout_storage_keys_present(self):
        """Layout persistence uses expected localStorage keys."""
        html = INDEX_PATH.read_text()
        assert "orchestrator-ui-layout" in html or "LAYOUT_KEY" in html
        assert "localStorage" in html

    def test_load_layout_function_exists(self):
        """loadLayout function for restoring persisted layout."""
        html = INDEX_PATH.read_text()
        assert "loadLayout" in html

    def test_save_layout_function_exists(self):
        """saveLayout function for persisting layout changes."""
        html = INDEX_PATH.read_text()
        assert "saveLayout" in html

    def test_init_layout_collapsed_exists(self):
        """initLayoutCollapsed restores collapsed state on load."""
        html = INDEX_PATH.read_text()
        assert "initLayoutCollapsed" in html

    def test_collapsed_state_persisted(self):
        """Tree, reasoning, terminal collapsed states are persisted."""
        html = INDEX_PATH.read_text()
        assert "treeCollapsed" in html
        assert "reasoningCollapsed" in html
        assert "terminalCollapsed" in html


class TestEditorModule:
    """Regression: Editor container, EditorView, updateListener exist and load without throwing."""

    def test_editor_container_and_related_dom_exist(self):
        """Editor container, section, placeholder, toolbar present in index.html."""
        html = INDEX_PATH.read_text()
        assert 'id="editor-container"' in html
        assert "editor-section" in html
        assert "editor-placeholder" in html
        assert "editor-toolbar" in html
        assert "editor-path" in html
        assert "editor-save-btn" in html
        assert "editor-revert-btn" in html

    def test_editor_initEditor_and_EditorView_import(self):
        """initEditor uses EditorView and updateListener (codemirror imports)."""
        html = INDEX_PATH.read_text()
        assert "EditorView" in html
        assert "updateListener" in html
        assert "initEditor" in html
        assert "codemirror" in html or "esm.sh" in html
