# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTabWidget,
    QWidget, QVBoxLayout, QTextEdit, QAction, QMenuBar, QMessageBox,
    QSplitter, QTreeView, QFileSystemModel, QHBoxLayout, QComboBox, QLabel
)
from PyQt5.QtWidgets import QPlainTextEdit 
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor, QPainter
from PyQt5.QtCore import Qt, QTimer, QRegExp, QFileInfo, QFileSystemWatcher
import sys, os

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)

        type_format = QTextCharFormat()
        type_format.setForeground(QColor("darkMagenta"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("darkGreen"))
        comment_format.setFontItalic(True)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("darkRed"))

        # Common C/C++/C# keywords
        cpp_keywords = [
            'int', 'float', 'double', 'char', 'bool', 'void', 'string',
            'if', 'else', 'switch', 'case', 'while', 'for', 'do', 'break', 'continue',
            'return', 'struct', 'class', 'public', 'private', 'protected',
            'new', 'delete', 'try', 'catch', 'throw', 'namespace', 'using',
            'true', 'false', 'nullptr', 'const', 'static', 'virtual', 'override'
        ]

        # C#-specific keywords
        csharp_keywords = [
            'var', 'dynamic', 'object', 'string', 'int', 'long', 'decimal',
            'using', 'namespace', 'get', 'set', 'async', 'await', 'yield',
            'interface', 'enum', 'event', 'delegate'
        ]

        # Python keywords
        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]

        all_keywords = set(cpp_keywords + csharp_keywords + python_keywords)
        self.highlighting_rules += [(QRegExp(r'\b' + kw + r'\b'), keyword_format) for kw in all_keywords]

        # Types
        types = ['int', 'float', 'double', 'char', 'string', 'bool', 'void', 'var', 'object', 'dynamic']
        self.highlighting_rules += [(QRegExp(r'\b' + t + r'\b'), type_format) for t in types]

        # Comments: // and # for Python, /* ... */ is not multiline supported here
        self.highlighting_rules.append((QRegExp(r'//.*'), comment_format))
        self.highlighting_rules.append((QRegExp(r'#.*'), comment_format))

        # Strings
        self.highlighting_rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.width(), self.editor.fontMetrics().height(),
                                 Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

class CodeEditor(QPlainTextEdit):  # Change QTextEdit to QPlainTextEdit
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.setFont(QFont("Courier", 11))
        self.update_line_number_area_width(0)
        self.bracket_pairs = {'(': ')', '{': '}', '[': ']'}

    def line_number_area_width(self):
        digits = len(str(self.blockCount()))
        return 10 + self.fontMetrics().width('9') * digits

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), self.line_number_area_width(), cr.height())

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def keyPressEvent(self, event):
        # Auto indentation
        if event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.select(QTextCursor.LineUnderCursor)
            line = cursor.selectedText()
            indent = len(line) - len(line.lstrip(' '))
            super().keyPressEvent(event)
            self.insertPlainText(' ' * indent)
            return
        # Bracket matching
        if event.text() in self.bracket_pairs:
            super().keyPressEvent(event)
            self.insertPlainText(self.bracket_pairs[event.text()])
            self.moveCursor(QTextCursor.Left)
            return
        super().keyPressEvent(event)

class EditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.text_edit = CodeEditor()
        self.highlighter = CodeHighlighter(self.text_edit.document())
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
        self.file_path = None
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)

    def set_file_path(self, path):
        if self.file_path:
            self.file_watcher.removePath(self.file_path)
        self.file_path = path
        if path:
            self.file_watcher.addPath(path)

    def on_file_changed(self, path):
        reply = QMessageBox.question(self, "File Changed",
            f"{os.path.basename(path)} was changed outside Birdseye. Reload?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            with open(path, 'r') as f:
                self.text_edit.setText(f.read())

class Birdseye(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Birdseye v2.20.8 (FranchukOS stable build)")
        self.setGeometry(200, 100, 1000, 700)

        # Project sidebar
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath('')
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.hide()
        self.file_tree.clicked.connect(self.open_from_tree)

        # Split view
        self.splitter = QSplitter()
        self.tabs = QTabWidget()
        self.tabs2 = QTabWidget()  # For split view
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.tabs2)
        self.tabs2.hide()

        # Layout
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.addWidget(self.file_tree)
        layout.addWidget(self.splitter)
        self.setCentralWidget(central)
        self.statusBar()

        self.init_menu()
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_all)
        self.autosave_timer.start(30000)

        self.new_tab()

    def init_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        view_menu = menu.addMenu("View")
        project_menu = menu.addMenu("Project")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        saveas_action = QAction("Save As", self)
        saveas_action.triggered.connect(self.save_as)
        file_menu.addAction(saveas_action)

        split_action = QAction("Split View", self)
        split_action.triggered.connect(self.toggle_split_view)
        view_menu.addAction(split_action)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.open_folder)
        project_menu.addAction(open_folder_action)

        show_tree_action = QAction("Show/Hide File Tree", self)
        show_tree_action.triggered.connect(self.toggle_file_tree)
        view_menu.addAction(show_tree_action)

        # Language selection
        lang_menu = menu.addMenu("Language")
        for lang in ["Auto", "Python", "C++", "C#", "Plain Text"]:
            action = QAction(lang, self)
            action.triggered.connect(lambda _, l=lang: self.set_language(l))
            lang_menu.addAction(action)

    def set_language(self, lang):
        editor = self.tabs.currentWidget()
        if not editor:
            return
        if lang == "Auto":
            # Guess from file extension.
            if editor.file_path:
                ext = os.path.splitext(editor.file_path)[1].lower()
                if ext in [".py"]:
                    lang = "Python"
                elif ext in [".cpp", ".cxx", ".cc", ".c", ".h", ".hpp"]:
                    lang = "C++"
                elif ext in [".cs"]:
                    lang = "C#"
                else:
                    lang = "Plain Text"
            else:
                lang = "Plain Text"
        # This really sucks! But just send it. 
        if lang == "Python":
            keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
            ]
        elif lang == "C++":
            keywords = [
            'int', 'float', 'double', 'char', 'bool', 'void', 'string',
            'if', 'else', 'switch', 'case', 'while', 'for', 'do', 'break', 'continue',
            'return', 'struct', 'class', 'public', 'private', 'protected',
            'new', 'delete', 'try', 'catch', 'throw', 'namespace', 'using',
            'true', 'false', 'nullptr', 'const', 'static', 'virtual', 'override'
            ]
        elif lang == "C#":
            keywords = [
            'var', 'dynamic', 'object', 'string', 'int', 'long', 'decimal',
            'using', 'namespace', 'get', 'set', 'async', 'await', 'yield',
            'interface', 'enum', 'event', 'delegate', 'public', 'private', 'protected',
            'class', 'struct', 'if', 'else', 'switch', 'case', 'while', 'for', 'do', 'break', 'continue',
            'return', 'try', 'catch', 'throw', 'true', 'false', 'null', 'const', 'static', 'override'
            ]
        else:
            keywords = []

        # Recreate the highlighter with new rules
        class CustomHighlighter(CodeHighlighter):
            def __init__(self, document):
                super().__init__(document)
                if keywords:
                    keyword_format = QTextCharFormat()
                    keyword_format.setForeground(QColor("blue"))
                    keyword_format.setFontWeight(QFont.Bold)
                    self.highlighting_rules = [(QRegExp(r'\b' + kw + r'\b'), keyword_format) for kw in keywords]
                else:
                    self.highlighting_rules = []

                comment_format = QTextCharFormat()
                comment_format.setForeground(QColor("darkGreen"))
                comment_format.setFontItalic(True)
                self.highlighting_rules.append((QRegExp(r'//.*'), comment_format))
                self.highlighting_rules.append((QRegExp(r'#.*'), comment_format))

                string_format = QTextCharFormat()
                string_format.setForeground(QColor("darkRed"))
                self.highlighting_rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
                self.highlighting_rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Replace the highlighter
        editor.highlighter = CustomHighlighter(editor.text_edit.document())
        self.statusBar().showMessage(f"Language set to {lang}", 2000)

    def toggle_split_view(self):
        if self.tabs2.isVisible():
            self.tabs2.hide()
        else:
            self.tabs2.show()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.file_model.setRootPath(folder)
            self.file_tree.setRootIndex(self.file_model.index(folder))
            self.file_tree.show()

    def toggle_file_tree(self):
        self.file_tree.setVisible(not self.file_tree.isVisible())

    def open_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            with open(path, 'r') as f:
                content = f.read()
            editor = EditorTab()
            editor.text_edit.setText(content)
            editor.set_file_path(path)
            self.tabs.addTab(editor, os.path.basename(path))
            self.tabs.setCurrentWidget(editor)

    def current_editor(self):
        return self.tabs.currentWidget().text_edit

    def new_tab(self):
        editor = EditorTab()
        self.tabs.addTab(editor, "Untitled")
        self.tabs.setCurrentWidget(editor)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if path:
            with open(path, 'r') as f:
                content = f.read()
            editor = EditorTab()
            editor.text_edit.setText(content)
            editor.file_path = path
            self.tabs.addTab(editor, os.path.basename(path))
            self.tabs.setCurrentWidget(editor)

    def save_file(self):
        editor = self.tabs.currentWidget()
        if editor.file_path:
            with open(editor.file_path, 'w') as f:
                f.write(editor.text_edit.toPlainText())
            self.statusBar().showMessage("Saved", 2000)
        else:
            self.save_as()

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File")
        if path:
            editor = self.tabs.currentWidget()
            editor.file_path = path
            with open(path, 'w') as f:
                f.write(editor.text_edit.toPlainText())
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))
            self.statusBar().showMessage("Saved As", 2000)

    def autosave_all(self):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor.file_path:
                with open(editor.file_path, 'w') as f:
                    f.write(editor.text_edit.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Birdseye()
    window.show()
    sys.exit(app.exec_())
