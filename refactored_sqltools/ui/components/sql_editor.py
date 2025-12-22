"""
SQL Editor Component

Provides a SQL text editor with syntax highlighting, indentation, and formatting.
"""

from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont, 
                        QTextCursor, QKeySequence)
import re


class SQLSyntaxHighlighter(QSyntaxHighlighter):
    """SQL syntax highlighter for QTextEdit"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """Setup syntax highlighting rules for SQL"""
        self.highlighting_rules = []
        
        # SQL Keywords (blue)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 100, 200))  # Blue
        keyword_format.setFontWeight(QFont.Bold)
        
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'PROCEDURE',
            'FUNCTION', 'TRIGGER', 'CONSTRAINT', 'PRIMARY', 'FOREIGN', 'KEY', 'UNIQUE',
            'NOT', 'NULL', 'DEFAULT', 'AUTO_INCREMENT', 'IDENTITY', 'CHECK',
            'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'JOIN', 'ON', 'UNION',
            'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'TOP', 'DISTINCT',
            'AS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IF', 'EXISTS',
            'IN', 'BETWEEN', 'LIKE', 'IS', 'AND', 'OR', 'XOR', 'ISNULL',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CAST', 'CONVERT', 'SUBSTRING',
            'UPPER', 'LOWER', 'TRIM', 'LTRIM', 'RTRIM', 'REPLACE', 'LEN', 'LENGTH',
            'DATEPART', 'DATEDIFF', 'GETDATE', 'NOW', 'CURRENT_TIMESTAMP',
            'BEGIN', 'END', 'COMMIT', 'ROLLBACK', 'TRANSACTION', 'SAVEPOINT',
            'GRANT', 'REVOKE', 'DENY', 'EXECUTE', 'EXEC', 'RETURN', 'DECLARE',
            'SET', 'PRINT', 'RAISERROR', 'TRY', 'CATCH', 'THROW', 'WHILE', 'BREAK',
            'CONTINUE', 'GOTO', 'WAITFOR', 'WITH', 'CTE', 'OVER', 'PARTITION',
            'ROW_NUMBER', 'RANK', 'DENSE_RANK', 'NTILE', 'LAG', 'LEAD',
            'FIRST_VALUE', 'LAST_VALUE', 'PERCENT_RANK', 'CUME_DIST'
        ]
        
        for keyword in sql_keywords:
            pattern = QRegExp(f'\\b{keyword}\\b', Qt.CaseInsensitive)
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Data types (green)
        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(0, 150, 0))  # Green
        datatype_format.setFontWeight(QFont.Bold)
        
        datatypes = [
            'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT', 'BIT',
            'DECIMAL', 'NUMERIC', 'FLOAT', 'REAL', 'MONEY', 'SMALLMONEY',
            'CHAR', 'VARCHAR', 'NCHAR', 'NVARCHAR', 'TEXT', 'NTEXT',
            'DATE', 'TIME', 'DATETIME', 'DATETIME2', 'SMALLDATETIME', 'TIMESTAMP',
            'BINARY', 'VARBINARY', 'IMAGE', 'UNIQUEIDENTIFIER', 'XML',
            'CURSOR', 'SQL_VARIANT', 'HIERARCHYID', 'GEOMETRY', 'GEOGRAPHY'
        ]
        
        for datatype in datatypes:
            pattern = QRegExp(f'\\b{datatype}\\b', Qt.CaseInsensitive)
            self.highlighting_rules.append((pattern, datatype_format))
        
        # String literals (red)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(200, 0, 0))  # Red
        
        # Single quoted strings
        pattern = QRegExp("'[^']*'")
        self.highlighting_rules.append((pattern, string_format))
        
        # Double quoted strings
        pattern = QRegExp('"[^"]*"')
        self.highlighting_rules.append((pattern, string_format))
        
        # Numbers (purple)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(150, 0, 150))  # Purple
        
        pattern = QRegExp('\\b\\d+(\\.\\d+)?\\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Comments (gray)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # Gray
        comment_format.setFontItalic(True)
        
        # Single line comments
        pattern = QRegExp('--[^\n]*')
        self.highlighting_rules.append((pattern, comment_format))
        
        # Multi-line comments
        self.comment_start_expression = QRegExp('/\\*')
        self.comment_end_expression = QRegExp('\\*/')
        self.multiline_comment_format = comment_format
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Apply single-line rules
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        
        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.multiline_comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class SQLEditor(QTextEdit):
    """Enhanced SQL text editor with syntax highlighting and formatting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
        self.setup_highlighter()
    
    def setup_editor(self):
        """Setup the SQL editor properties"""
        # Font
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tab settings
        self.setTabStopWidth(40)  # 4 spaces equivalent
        
        # Line wrap
        self.setLineWrapMode(QTextEdit.NoWrap)
        
        # Read-only by default (can be changed)
        self.setReadOnly(True)
        
        # Placeholder text
        self.setPlaceholderText("SQL será exibido aqui...")
    
    def setup_highlighter(self):
        """Setup syntax highlighter"""
        self.highlighter = SQLSyntaxHighlighter(self.document())
    
    def format_sql(self, sql_text):
        """Format SQL text with proper indentation"""
        if not sql_text:
            return ""
        
        # Basic SQL formatting
        formatted = self.basic_sql_format(sql_text)
        return formatted
    
    def basic_sql_format(self, sql):
        """Apply basic SQL formatting"""
        if not sql:
            return ""
        
        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql.strip())
        
        # Keywords that should start new lines
        major_keywords = [
            'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
            'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'JOIN',
            'UNION', 'UNION ALL', 'EXCEPT', 'INTERSECT'
        ]
        
        # Add line breaks before major keywords
        for keyword in major_keywords:
            pattern = r'\b' + keyword.replace(' ', r'\s+') + r'\b'
            sql = re.sub(pattern, '\n' + keyword, sql, flags=re.IGNORECASE)
        
        # Clean up multiple line breaks
        sql = re.sub(r'\n\s*\n', '\n', sql)
        
        # Add proper indentation
        lines = sql.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Decrease indent for certain keywords
            if re.match(r'^\s*(FROM|WHERE|GROUP BY|ORDER BY|HAVING)\b', line, re.IGNORECASE):
                current_indent = 0
            elif re.match(r'^\s*(INNER JOIN|LEFT JOIN|RIGHT JOIN|FULL JOIN|JOIN)\b', line, re.IGNORECASE):
                current_indent = 1
            elif re.match(r'^\s*(AND|OR)\b', line, re.IGNORECASE):
                current_indent = 1
            else:
                current_indent = indent_level
            
            # Apply indentation
            indented_line = '    ' * current_indent + line
            formatted_lines.append(indented_line)
        
        return '\n'.join(formatted_lines)
    
    def set_sql_text(self, sql_text):
        """Set SQL text with formatting"""
        formatted_sql = self.format_sql(sql_text)
        self.setPlainText(formatted_sql)
    
    def keyPressEvent(self, event):
        """Handle key press events for better editing experience"""
        if event.key() == Qt.Key_Tab:
            # Insert 4 spaces instead of tab
            cursor = self.textCursor()
            cursor.insertText("    ")
            return
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Auto-indent on new line
            cursor = self.textCursor()
            current_line = cursor.block().text()
            
            # Count leading spaces
            leading_spaces = len(current_line) - len(current_line.lstrip())
            
            # Insert new line with same indentation
            cursor.insertText("\n" + " " * leading_spaces)
            return
        
        super().keyPressEvent(event)
    
    def get_formatted_text(self):
        """Get the formatted SQL text"""
        return self.toPlainText()
    
    def set_editable(self, editable):
        """Set whether the editor is editable"""
        self.setReadOnly(not editable)
        
        if editable:
            self.setPlaceholderText("Digite seu SQL aqui...")
        else:
            self.setPlaceholderText("SQL será exibido aqui...")


class SQLEditorWidget(QWidget):
    """Widget wrapper for SQL Editor with additional controls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # SQL Editor
        self.sql_editor = SQLEditor()
        layout.addWidget(self.sql_editor)
    
    def set_sql_text(self, sql_text):
        """Set SQL text"""
        self.sql_editor.set_sql_text(sql_text)
    
    def get_sql_text(self):
        """Get SQL text"""
        return self.sql_editor.get_formatted_text()
    
    def set_editable(self, editable):
        """Set editor editable state"""
        self.sql_editor.set_editable(editable)
    
    def clear(self):
        """Clear the editor"""
        self.sql_editor.clear()