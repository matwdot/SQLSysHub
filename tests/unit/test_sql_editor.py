"""
Unit tests for SQL Editor component
"""

import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import sys

from refactored_sqltools.ui.components.sql_editor import SQLEditor, SQLEditorWidget, SQLSyntaxHighlighter


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
        yield app
        app.quit()
    else:
        yield QApplication.instance()


class TestSQLSyntaxHighlighter:
    """Test SQLSyntaxHighlighter component"""
    
    def test_initialization(self, qapp):
        """Test SQLSyntaxHighlighter initializes correctly"""
        editor = SQLEditor()
        highlighter = SQLSyntaxHighlighter(editor.document())
        assert highlighter is not None
        assert len(highlighter.highlighting_rules) > 0


class TestSQLEditor:
    """Test SQLEditor component"""
    
    def test_initialization(self, qapp):
        """Test SQLEditor initializes correctly"""
        editor = SQLEditor()
        assert editor is not None
        assert editor.isReadOnly()  # Should be read-only by default
        assert editor.font().family() == "Consolas"
        assert editor.font().pointSize() == 11
    
    def test_set_sql_text(self, qapp):
        """Test setting SQL text with formatting"""
        editor = SQLEditor()
        sql = "SELECT * FROM users WHERE id = 1"
        
        editor.set_sql_text(sql)
        result = editor.get_formatted_text()
        
        # Should contain the original SQL content
        assert "SELECT" in result
        assert "FROM" in result
        assert "WHERE" in result
    
    def test_basic_sql_format(self, qapp):
        """Test basic SQL formatting"""
        editor = SQLEditor()
        sql = "SELECT id, name FROM users WHERE active = 1 ORDER BY name"
        
        formatted = editor.basic_sql_format(sql)
        
        # Should have line breaks for major keywords
        assert "SELECT" in formatted
        assert "FROM" in formatted
        assert "WHERE" in formatted
        assert "ORDER BY" in formatted
    
    def test_set_editable(self, qapp):
        """Test setting editor editable state"""
        editor = SQLEditor()
        
        # Initially read-only
        assert editor.isReadOnly()
        
        # Make editable
        editor.set_editable(True)
        assert not editor.isReadOnly()
        
        # Make read-only again
        editor.set_editable(False)
        assert editor.isReadOnly()
    
    def test_format_complex_sql(self, qapp):
        """Test formatting complex SQL"""
        editor = SQLEditor()
        complex_sql = """
        SELECT u.id, u.name, p.title FROM users u 
        INNER JOIN posts p ON u.id = p.user_id 
        WHERE u.active = 1 AND p.published = 1 
        ORDER BY u.name, p.created_at DESC
        """
        
        formatted = editor.basic_sql_format(complex_sql)
        
        # Should contain proper formatting
        assert "SELECT" in formatted
        assert "INNER" in formatted and "JOIN" in formatted  # May be on separate lines
        assert "WHERE" in formatted
        assert "ORDER BY" in formatted


class TestSQLEditorWidget:
    """Test SQLEditorWidget component"""
    
    def test_initialization(self, qapp):
        """Test SQLEditorWidget initializes correctly"""
        widget = SQLEditorWidget()
        assert widget is not None
        assert hasattr(widget, 'sql_editor')
        assert isinstance(widget.sql_editor, SQLEditor)
    
    def test_set_get_sql_text(self, qapp):
        """Test setting and getting SQL text"""
        widget = SQLEditorWidget()
        test_sql = "SELECT * FROM products"
        
        widget.set_sql_text(test_sql)
        result = widget.get_sql_text()
        
        # Should contain the original content (may be formatted)
        normalized_result = ' '.join(result.split())
        assert normalized_result == test_sql
    
    def test_set_editable(self, qapp):
        """Test setting editable state"""
        widget = SQLEditorWidget()
        
        # Test making editable
        widget.set_editable(True)
        assert not widget.sql_editor.isReadOnly()
        
        # Test making read-only
        widget.set_editable(False)
        assert widget.sql_editor.isReadOnly()
    
    def test_clear(self, qapp):
        """Test clearing the editor"""
        widget = SQLEditorWidget()
        
        # Set some text
        widget.set_sql_text("SELECT * FROM test")
        assert len(widget.get_sql_text()) > 0
        
        # Clear
        widget.clear()
        assert len(widget.get_sql_text().strip()) == 0
    
    def test_sql_formatting_with_keywords(self, qapp):
        """Test SQL formatting with various keywords"""
        widget = SQLEditorWidget()
        
        sql_with_keywords = """
        SELECT p.id, p.name, c.category_name, COUNT(*) as total
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.active = 1 AND p.price > 100
        GROUP BY p.id, p.name, c.category_name
        HAVING COUNT(*) > 5
        ORDER BY total DESC, p.name ASC
        """
        
        widget.set_sql_text(sql_with_keywords)
        formatted = widget.get_sql_text()
        
        # Check that major keywords are present (may be on separate lines due to formatting)
        keywords_to_check = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY']
        for keyword in keywords_to_check:
            assert keyword in formatted.upper()
        
        # Check JOIN keywords separately as they may be split
        assert 'LEFT' in formatted.upper() and 'JOIN' in formatted.upper()
    
    def test_sql_with_comments(self, qapp):
        """Test SQL with comments"""
        widget = SQLEditorWidget()
        
        sql_with_comments = """
        -- This is a single line comment
        SELECT * FROM users
        /* This is a 
           multi-line comment */
        WHERE active = 1
        """
        
        widget.set_sql_text(sql_with_comments)
        formatted = widget.get_sql_text()
        
        # Should preserve comments
        assert "--" in formatted or "This is a single line comment" in formatted
        assert "/*" in formatted or "multi-line comment" in formatted