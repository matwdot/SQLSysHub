"""
SQL Editor Component with syntax highlighting.
Uses qfluentwidgets PlainTextEdit for proper theme support.
"""

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
                        QTextCursor, QKeySequence)
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import PlainTextEdit, isDarkTheme, qconfig
import re


class SQLSyntaxHighlighter(QSyntaxHighlighter):
    """SQL syntax highlighter that adapts to dark/light themes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_highlighting_rules()

    def setup_highlighting_rules(self):
        self.highlighting_rules = []

        dark = isDarkTheme()

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214) if dark else QColor(0, 100, 200))
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

        datatype_format = QTextCharFormat()
        datatype_format.setForeground(QColor(78, 201, 176) if dark else QColor(0, 150, 0))
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

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(214, 157, 133) if dark else QColor(200, 0, 0))

        pattern = QRegExp("'[^']*'")
        self.highlighting_rules.append((pattern, string_format))

        pattern = QRegExp('"[^"]*"')
        self.highlighting_rules.append((pattern, string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168) if dark else QColor(150, 0, 150))

        pattern = QRegExp('\\b\\d+(\\.\\d+)?\\b')
        self.highlighting_rules.append((pattern, number_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(108, 153, 77) if dark else QColor(128, 128, 128))
        comment_format.setFontItalic(True)

        pattern = QRegExp('--[^\n]*')
        self.highlighting_rules.append((pattern, comment_format))

        self.comment_start_expression = QRegExp('/\\*')
        self.comment_end_expression = QRegExp('\\*/')
        self.multiline_comment_format = comment_format

    def rebuild_rules(self):
        self.setup_highlighting_rules()
        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

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


class SQLEditor(PlainTextEdit):
    """Enhanced SQL text editor with syntax highlighting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
        self.setup_highlighter()
        qconfig.themeChanged.connect(self._on_theme_changed)

    def setup_editor(self):
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setTabStopDistance(40)
        self.setLineWrapMode(self.NoWrap)
        self.setReadOnly(True)
        self.setPlaceholderText("SQL será exibido aqui...")

    def setup_highlighter(self):
        self.highlighter = SQLSyntaxHighlighter(self.document())

    def format_sql(self, sql_text):
        if not sql_text:
            return ""
        return self.basic_sql_format(sql_text)

    def basic_sql_format(self, sql):
        if not sql:
            return ""

        sql = re.sub(r'\s+', ' ', sql.strip())

        major_keywords = [
            'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
            'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'JOIN',
            'UNION', 'UNION ALL', 'EXCEPT', 'INTERSECT'
        ]

        for keyword in major_keywords:
            pattern = r'\b' + keyword.replace(' ', r'\s+') + r'\b'
            sql = re.sub(pattern, '\n' + keyword, sql, flags=re.IGNORECASE)

        sql = re.sub(r'\n\s*\n', '\n', sql)

        lines = sql.split('\n')
        formatted_lines = []
        indent_level = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r'^\s*(FROM|WHERE|GROUP BY|ORDER BY|HAVING)\b', line, re.IGNORECASE):
                ci = 0
            elif re.match(r'^\s*(INNER JOIN|LEFT JOIN|RIGHT JOIN|FULL JOIN|JOIN)\b', line, re.IGNORECASE):
                ci = 1
            elif re.match(r'^\s*(AND|OR)\b', line, re.IGNORECASE):
                ci = 1
            else:
                ci = indent_level
            formatted_lines.append('    ' * ci + line)

        return '\n'.join(formatted_lines)

    def set_sql_text(self, sql_text):
        self.setPlainText(self.format_sql(sql_text))

    def _on_theme_changed(self):
        self.highlighter.rebuild_rules()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")
            return
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            leading = len(cursor.block().text()) - len(cursor.block().text().lstrip())
            cursor.insertText("\n" + " " * leading)
            return
        super().keyPressEvent(event)

    def set_editable(self, editable):
        self.setReadOnly(not editable)
        self.setPlaceholderText("Digite seu SQL aqui..." if editable else "SQL será exibido aqui...")


class SQLEditorWidget(QWidget):
    """Widget wrapper for SQL Editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.sql_editor = SQLEditor()
        layout.addWidget(self.sql_editor)

    def set_sql_text(self, sql_text):
        self.sql_editor.set_sql_text(sql_text)

    def get_sql_text(self):
        return self.sql_editor.toPlainText()

    def set_editable(self, editable):
        self.sql_editor.set_editable(editable)

    def clear(self):
        self.sql_editor.clear()
