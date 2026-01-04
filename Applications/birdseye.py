# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTabWidget,
    QWidget, QVBoxLayout, QPlainTextEdit, QAction, QMenuBar, QMessageBox,
    QSplitter, QTreeView, QFileSystemModel, QHBoxLayout, QInputDialog, QColorDialog,
    QDialog, QFormLayout, QPushButton, QDialogButtonBox, QLineEdit, QLabel, QCheckBox,
    QTextEdit  
)
from PyQt5.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor, QPainter, QPalette, QIcon, QTextDocument
)
from PyQt5.QtCore import Qt, QTimer, QRegExp, QFileSystemWatcher, QSize
import sys, os, subprocess, re, json, time

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#66d9ef"))  # light blue
        keyword_format.setFontWeight(QFont.Bold)

        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#f92672"))  # pink

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#75715e"))  # olive green
        comment_format.setFontItalic(True)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#e6db74"))  # yellow

        cpp_keywords = [
            'int', 'float', 'double', 'char', 'bool', 'void', 'string',
            'if', 'else', 'switch', 'case', 'while', 'for', 'do', 'break', 'continue',
            'return', 'struct', 'class', 'public', 'private', 'protected',
            'new', 'delete', 'try', 'catch', 'throw', 'namespace', 'using',
            'true', 'false', 'nullptr', 'const', 'static', 'virtual', 'override'
        ]

        csharp_keywords = [
            'var', 'dynamic', 'object', 'string', 'int', 'long', 'decimal',
            'using', 'namespace', 'get', 'set', 'async', 'await', 'yield',
            'interface', 'enum', 'event', 'delegate', 'public', 'private', 'protected',
            'class', 'struct', 'if', 'else', 'switch', 'case', 'while', 'for', 'do', 'break', 'continue',
            'return', 'try', 'catch', 'throw', 'true', 'false', 'null', 'const', 'static', 'override'
        ]

        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]

        rust_keywords = [
            'as', 'break', 'const', 'continue', 'crate', 'else', 'enum', 'extern',
            'false', 'fn', 'for', 'if', 'impl', 'in', 'let', 'loop', 'match',
            'mod', 'move', 'mut', 'pub', 'ref', 'return', 'self', 'Self', 'static',
            'struct', 'super', 'trait', 'true', 'type', 'unsafe', 'use', 'where',
            'while', 'async', 'await', 'dyn', 'abstract', 'become', 'box', 'do',
            'final', 'macro', 'override', 'priv', 'try', 'typeof', 'unsized',
            'virtual', 'yield'
        ]

        javascript_keywords = [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
            'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
            'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
            'void', 'while', 'with', 'yield', 'enum', 'await', 'implements',
            'package', 'protected', 'static', 'interface', 'private', 'public'
        ]

        java_keywords = [
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
            'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
            'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
            'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
            'volatile', 'while', 'true', 'false', 'null'
        ]

        go_keywords = [
            'break', 'case', 'chan', 'const', 'continue', 'default', 'defer', 'else', 'fallthrough',
            'for', 'func', 'go', 'goto', 'if', 'import', 'interface', 'map', 'package', 'range',
            'return', 'select', 'struct', 'switch', 'type', 'var', 'true', 'false', 'nil'
        ]

        kotlin_keywords = [
            'as', 'break', 'class', 'continue', 'do', 'else', 'false', 'for', 'fun', 'if', 'in',
            'interface', 'is', 'null', 'object', 'package', 'return', 'super', 'this', 'throw',
            'true', 'try', 'typealias', 'val', 'var', 'when', 'while'
        ]

        html_keywords = [
            'html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style', 'div', 'span',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table',
            'tr', 'td', 'th', 'form', 'input', 'button', 'select', 'option', 'textarea', 'br', 'hr'
        ]

        css_keywords = [
            'color', 'background', 'margin', 'padding', 'border', 'font', 'display', 'position',
            'top', 'left', 'right', 'bottom', 'width', 'height', 'min-width', 'max-width',
            'min-height', 'max-height', 'flex', 'grid', 'align', 'justify', 'content', 'gap',
            'overflow', 'z-index', 'float', 'clear', 'visibility', 'opacity'
        ]

        shell_keywords = [
            'if', 'then', 'else', 'fi', 'for', 'while', 'do', 'done', 'case', 'esac', 'function',
            'echo', 'exit', 'break', 'continue', 'return', 'in', 'local', 'export', 'readonly',
            'declare', 'typeset', 'set', 'unset', 'test', 'true', 'false'
        ]

        all_keywords = set(
            cpp_keywords + csharp_keywords + python_keywords + rust_keywords + javascript_keywords + java_keywords +
            go_keywords + kotlin_keywords + html_keywords + css_keywords + shell_keywords
        )
        self.highlighting_rules += [(QRegExp(r'\b' + kw + r'\b'), keyword_format) for kw in all_keywords]

        # Types
        types = ['int', 'float', 'double', 'char', 'string', 'bool', 'void', 'var', 'object', 'dynamic']
        self.highlighting_rules += [(QRegExp(r'\b' + t + r'\b'), type_format) for t in types]

        # Comments
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

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#2d2d30"))
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        painter.setPen(QColor("#75715e"))
        font = QFont("JetBrains Mono", 10)
        painter.setFont(font)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.width() - 4, self.editor.fontMetrics().height(),
                                 Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.setFont(QFont("JetBrains Mono", 13))
        self.update_line_number_area_width(0)
        self.bracket_pairs = {'(': ')', '{': '}', '[': ']'
        }
        self.highlight_current_line()
        self._default_font_size = 13
        # Create a highlighter per editor document
        self.highlighter = CodeHighlighter(self.document())

    def line_number_area_width(self):
        digits = len(str(self.blockCount()))
        space = 10 + self.fontMetrics().width('9') * digits
        return space

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
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#3e3e42")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.select(QTextCursor.LineUnderCursor)
            line = cursor.selectedText()
            indent = len(line) - len(line.lstrip(' '))
            super().keyPressEvent(event)
            self.insertPlainText(' ' * indent)
            return
        if event.text() in self.bracket_pairs:
            super().keyPressEvent(event)
            self.insertPlainText(self.bracket_pairs[event.text()])
            self.moveCursor(QTextCursor.Left)
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            font = self.font()
            size = font.pointSize()
            if delta > 0:
                size += 1
            elif delta < 0:
                size -= 1
            size = max(6, min(size, 48))  # Clamp between 6pt and 48pt
            font.setPointSize(size)
            self.setFont(font)
            self._default_font_size = size
            # ensure line number area font matches
            try:
                self.line_number_area.editor.setFont(font)
            except Exception:
                pass
            self.update_line_number_area_width(0)
        else:
            super().wheelEvent(event)

class EditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.text_edit = CodeEditor()
        # highlighter is created inside CodeEditor now
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
        self.file_path = None
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)

    def set_file_path(self, path):
        if self.file_path:
            try:
                self.file_watcher.removePath(self.file_path)
            except Exception:
                pass
        self.file_path = path
        if path:
            try:
                self.file_watcher.addPath(path)
            except Exception:
                pass

    def on_file_changed(self, path):
        reply = QMessageBox.question(self, "File Changed",
            f"{os.path.basename(path)} was changed outside Birdseye. Reload?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.text_edit.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not reload file:\n{e}")

class ThemeEditorDialog(QDialog):
    def __init__(self, parent, current_theme):
        super().__init__(parent)
        self.setWindowTitle("Custom Theme Editor")
        self.colors = current_theme.copy()
        layout = QFormLayout(self)
        self.color_buttons = {}
        for key, val in self.colors.items():
            btn = QPushButton()
            btn.setStyleSheet(f"background:{val}")
            btn.clicked.connect(lambda _, k=key: self.pick_color(k))
            layout.addRow(key, btn)
            self.color_buttons[key] = btn
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def pick_color(self, key):
        color = QColorDialog.getColor(QColor(self.colors[key]), self)
        if color.isValid():
            self.colors[key] = color.name()
            self.color_buttons[key].setStyleSheet(f"background:{color.name()}")

    def get_theme(self):
        return self.colors

class SearchReplaceDialog(QDialog):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.setWindowTitle("Search and Replace")
        self.editor = editor
        layout = QFormLayout(self)
        self.search_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.case_checkbox = QCheckBox("Case sensitive")
        layout.addRow("Find:", self.search_input)
        layout.addRow("Replace with:", self.replace_input)
        layout.addRow(self.case_checkbox)
        btns = QDialogButtonBox(QDialogButtonBox.Find | QDialogButtonBox.Replace | QDialogButtonBox.ReplaceAll | QDialogButtonBox.Close)
        btns.button(QDialogButtonBox.Find).clicked.connect(self.find_next)
        btns.button(QDialogButtonBox.Replace).clicked.connect(self.replace_one)
        btns.button(QDialogButtonBox.ReplaceAll).clicked.connect(self.replace_all)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def find_next(self):
        text = self.search_input.text()
        flags = QTextDocument.FindFlags()
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        found = self.editor.find(text, flags)
        if not found:
            QMessageBox.information(self, "Search", "No more matches found.")

    def replace_one(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        search = self.search_input.text()
        replace = self.replace_input.text()
        if not search:
            return
        text = self.editor.toPlainText()
        if self.case_checkbox.isChecked():
            count = text.count(search)
            new_text = text.replace(search, replace)
        else:
            count = len(re.findall(re.escape(search), text, re.IGNORECASE))
            new_text = re.sub(re.escape(search), replace, text, flags=re.IGNORECASE)
        self.editor.setPlainText(new_text)
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrence(s).")

class Birdseye(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Birdseye v5.3.0")
        self.setGeometry(100, 100, 1280, 800)
        self.setWindowIcon(QIcon()) 

        # File tree
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath('')
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setHeaderHidden(True)
        self.file_tree.hide()
        self.file_tree.setStyleSheet("QTreeView { border: none; font-size: 13px; }")
        self.file_tree.clicked.connect(self.open_from_tree)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("QTabBar::tab { font-size: 14px; padding: 6px 20px; margin: 3px; }")

        # Splitter layout
        self.splitter = QSplitter()
        self.splitter.addWidget(self.file_tree)
        self.splitter.addWidget(self.tabs)
        self.splitter.setStretchFactor(1, 1)

        central = QWidget()
        central_layout = QHBoxLayout(central)
        central_layout.addWidget(self.splitter)
        self.setCentralWidget(central)

        # Status bar styling
        self.statusBar().setStyleSheet("color: #aaa; font-size: 12px;")

        self.recent_files = []
        self.recent_limit = 10

        self.init_menu()
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_all)
        self.autosave_timer.start(30000)

        self.custom_theme = {
            "Editor Background": "#272822",
            "Editor Text": "#f8f8f2",
            "Tab Background": "#1e1e1e",
            "Tab Text": "#f8f8f2",
            "Sidebar": "#1f1f1f",
            "Sidebar Text": "#eeeeee",
            "Highlight": "#89ddff"
        }

        self.set_theme("Dark")

        # create initial tab
        self.new_tab()

    def init_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        view_menu = menu.addMenu("View")
        project_menu = menu.addMenu("Project")
        edit_menu = menu.addMenu("Edit")
        search_action = QAction("Search/Replace", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.open_search_replace)
        edit_menu.addAction(search_action)

        new_action = QAction("New", self)
        new_action.triggered.connect(lambda: self.new_tab())
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

        # Run Current File action (F5)
        run_action = QAction("Run Current File", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_file)
        file_menu.addAction(run_action)

        split_action = QAction("Toggle File Tree", self)
        split_action.triggered.connect(self.toggle_file_tree)
        view_menu.addAction(split_action)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.open_folder)
        project_menu.addAction(open_folder_action)

        # Language selection
        lang_menu = menu.addMenu("Language")
        for lang in ["Auto", "Python", "C++", "C#", "Rust", "JavaScript", "Java", "Plain Text", "Go", "Kotlin", "HTML", "CSS", "Shell"]:
            action = QAction(lang, self)
            action.triggered.connect(lambda _, l=lang: self.set_language(l))
            lang_menu.addAction(action)

        # Git menu
        git_menu = menu.addMenu("Git")
        git_status_action = QAction("Show Status", self)
        git_status_action.triggered.connect(self.show_git_status)
        git_menu.addAction(git_status_action)
        git_commit_action = QAction("Commit...", self)
        git_commit_action.triggered.connect(self.git_commit)
        git_menu.addAction(git_commit_action)

        # Theme menu
        theme_menu = menu.addMenu("Theme")
        for theme in ["Light", "Dark"]:
            action = QAction(theme, self)
            action.triggered.connect(lambda _, t=theme: self.set_theme(t))
            theme_menu.addAction(action)
        custom_action = QAction("Customize...", self)
        custom_action.triggered.connect(self.open_theme_editor)
        theme_menu.addAction(custom_action)

        # About menu
        help_menu = menu.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Recent files menu
        recent_menu = menu.addMenu("Recent")
        self.recent_menu = recent_menu
        self.update_recent_menu()

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Birdseye",
            "<b>Birdseye v5.3.0</b><br>"
            "A simple multi-language code editor for FranchukOS.<br><br>"
            "Copyright 2025 the FranchukOS project authors.<br>"
            "Licensed under the Apache License, Version 2.0.<br><br>"
            "View the source code here: </ul>https://github.com/bluegillstudios/franchukOS</ul>"
        )

    def set_language(self, lang):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab:
            return
        editor = editor_tab.text_edit
        if lang == "Auto":
            if editor_tab.file_path:
                ext = os.path.splitext(editor_tab.file_path)[1].lower()
                if ext in [".py"]:
                    lang = "Python"
                elif ext in [".cpp", ".cxx", ".cc", ".c", ".h", ".hpp"]:
                    lang = "C++"
                elif ext in [".cs"]:
                    lang = "C#"
                elif ext in [".rs"]:
                    lang = "Rust"
                elif ext in [".js", ".jsx", ".mjs"]:
                    lang = "JavaScript"
                elif ext in [".java"]:
                    lang = "Java"
                elif ext in [".go"]:
                    lang = "Go"
                elif ext in [".kt"]:
                    lang = "Kotlin"
                elif ext in [".html", ".htm"]:
                    lang = "HTML"
                elif ext in [".css"]:
                    lang = "CSS"
                elif ext in [".sh", ".bash"]:
                    lang = "Shell"
                else:
                    lang = "Plain Text"
            else:
                lang = "Plain Text"

        keywords = []
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
        elif lang == "Rust":
            keywords = [
                'as', 'break', 'const', 'continue', 'crate', 'else', 'enum', 'extern',
                'false', 'fn', 'for', 'if', 'impl', 'in', 'let', 'loop', 'match',
                'mod', 'move', 'mut', 'pub', 'ref', 'return', 'self', 'Self', 'static',
                'struct', 'super', 'trait', 'true', 'type', 'unsafe', 'use', 'where',
                'while', 'async', 'await', 'dyn', 'abstract', 'become', 'box', 'do',
                'final', 'macro', 'override', 'priv', 'try', 'typeof', 'unsized',
                'virtual', 'yield'
            ]
        elif lang == "JavaScript":
            keywords = [
                'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
                'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
                'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
                'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
                'void', 'while', 'with', 'yield', 'enum', 'await', 'implements',
                'package', 'protected', 'static', 'interface', 'private', 'public'
            ]
        elif lang == "Java":
            keywords = [
                'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
                'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
                'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
                'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
                'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
                'volatile', 'while', 'true', 'false', 'null'
            ]
        elif lang == "Go":
            keywords = [
                'break', 'case', 'chan', 'const', 'continue', 'default', 'defer', 'else', 'fallthrough',
                'for', 'func', 'go', 'goto', 'if', 'import', 'interface', 'map', 'package', 'range',
                'return', 'select', 'struct', 'switch', 'type', 'var', 'true', 'false', 'nil'
            ]
        elif lang == "Kotlin":
            keywords = [
                'as', 'break', 'class', 'continue', 'do', 'else', 'false', 'for', 'fun', 'if', 'in',
                'interface', 'is', 'null', 'object', 'package', 'return', 'super', 'this', 'throw',
                'true', 'try', 'typealias', 'val', 'var', 'when', 'while'
            ]
        elif lang == "HTML":
            keywords = [
                'html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style', 'div', 'span',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table',
                'tr', 'td', 'th', 'form', 'input', 'button', 'select', 'option', 'textarea', 'br', 'hr'
            ]
        elif lang == "CSS":
            keywords = [
                'color', 'background', 'margin', 'padding', 'border', 'font', 'display', 'position',
                'top', 'left', 'right', 'bottom', 'width', 'height', 'min-width', 'max-width',
                'min-height', 'max-height', 'flex', 'grid', 'align', 'justify', 'content', 'gap',
                'overflow', 'z-index', 'float', 'clear', 'visibility', 'opacity'
            ]
        elif lang == "Shell":
            keywords = [
                'if', 'then', 'else', 'fi', 'for', 'while', 'do', 'done', 'case', 'esac', 'function',
                'echo', 'exit', 'break', 'continue', 'return', 'in', 'local', 'export', 'readonly',
                'declare', 'typeset', 'set', 'unset', 'test', 'true', 'false'
            ]
        else:
            keywords = []

        # Rebuild the highlighter with new keywords
        editor.highlighter.highlighting_rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#66d9ef"))
        keyword_format.setFontWeight(QFont.Bold)
        editor.highlighter.highlighting_rules += [(QRegExp(r'\b' + kw + r'\b'), keyword_format) for kw in keywords]

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#75715e"))
        comment_format.setFontItalic(True)
        editor.highlighter.highlighting_rules.append((QRegExp(r'//.*'), comment_format))
        editor.highlighter.highlighting_rules.append((QRegExp(r'#.*'), comment_format))
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#e6db74"))
        editor.highlighter.highlighting_rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        editor.highlighter.highlighting_rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        editor.highlighter.rehighlight()
        self.statusBar().showMessage(f"Language set to {lang}", 3000)

    def toggle_file_tree(self):
        if self.file_tree.isVisible():
            self.file_tree.hide()
        else:
            self.file_tree.show()

    def new_tab(self, path=None):
        editor_tab = EditorTab()
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    editor_tab.text_edit.setPlainText(f.read())
                editor_tab.set_file_path(path)
                tab_label = f"📝 {os.path.basename(path)}"
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file:\n{e}")
                tab_label = "📝 Untitled"
        else:
            tab_label = "📝 Untitled"
        self.tabs.addTab(editor_tab, tab_label)
        self.tabs.setCurrentWidget(editor_tab)
        if path:
            if path not in self.recent_files:
                self.recent_files.insert(0, path)
                self.recent_files = self.recent_files[:self.recent_limit]
                self.update_recent_menu()
        return editor_tab

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*);;Python Files (*.py);;C++ Files (*.cpp *.h);;C# Files (*.cs);;Rust Files (*.rs);;JavaScript Files (*.js)')
        if fname:
            # open in a new tab (or focus existing)
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                if editor.file_path == fname:
                    self.tabs.setCurrentIndex(i)
                    return
            self.new_tab(fname)

    def open_path(self, path):
        # kept for compatibility with file tree open
        self.open_file()  # this function now handled by open_file dialog; preserve but try to open path directly
        # fallback: try to open directly like open_file would
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor.file_path == path:
                self.tabs.setCurrentIndex(i)
                return
        self.new_tab(path)

    def open_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            # reuse new_tab logic
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                if editor.file_path == path:
                    self.tabs.setCurrentIndex(i)
                    return
            self.new_tab(path)

    def save_file(self):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab:
            return
        if editor_tab.file_path:
            try:
                with open(editor_tab.file_path, 'w', encoding='utf-8') as f:
                    f.write(editor_tab.text_edit.toPlainText())
                self.statusBar().showMessage(f"Saved {editor_tab.file_path}", 3000)
                editor_tab.text_edit.document().setModified(False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file:\n{e}")
        else:
            self.save_as()

    def save_as(self):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab:
            return
        fname, _ = QFileDialog.getSaveFileName(self, 'Save As', '', 'All Files (*)')
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(editor_tab.text_edit.toPlainText())
                editor_tab.set_file_path(fname)
                self.tabs.setTabText(self.tabs.currentIndex(), f"📝 {os.path.basename(fname)}")
                self.statusBar().showMessage(f"Saved {fname}", 3000)
                # update recent files
                if fname not in self.recent_files:
                    self.recent_files.insert(0, fname)
                    self.recent_files = self.recent_files[:self.recent_limit]
                    self.update_recent_menu()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file:\n{e}")

    def open_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if dir_path:
            self.file_model.setRootPath(dir_path)
            self.file_tree.setRootIndex(self.file_model.index(dir_path))
            self.file_tree.show()

    def autosave_all(self):
        # only autosave modified files to .autosave next to original
        for i in range(self.tabs.count()):
            editor_tab = self.tabs.widget(i)
            if editor_tab.file_path:
                try:
                    if editor_tab.text_edit.document().isModified():
                        autosave_path = editor_tab.file_path + '.autosave'
                        with open(autosave_path, 'w', encoding='utf-8') as f:
                            f.write(editor_tab.text_edit.toPlainText())
                except Exception:
                    pass

    def close_tab(self, index):
        editor_tab = self.tabs.widget(index)
        if editor_tab and editor_tab.text_edit.document().isModified():
            reply = QMessageBox.question(self, "Save changes?", "Save changes before closing?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                # save current tab
                self.tabs.setCurrentIndex(index)
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        # remove watchers
        try:
            if editor_tab.file_path:
                editor_tab.file_watcher.removePath(editor_tab.file_path)
        except Exception:
            pass
        self.tabs.removeTab(index)

    def show_git_status(self):
        # simple git status check
        editor_tab = self.tabs.currentWidget()
        if not editor_tab or not editor_tab.file_path:
            QMessageBox.information(self, "Git Status", "Open a file inside a git repo to check status.")
            return
        repo_dir = os.path.dirname(editor_tab.file_path)
        try:
            output = subprocess.check_output(['git', '-C', repo_dir, 'status'], stderr=subprocess.STDOUT, universal_newlines=True)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Git Status")
            dlg.setText(output)
            dlg.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Git Error", f"Git status failed:\n{e}")

    def git_commit(self):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab or not editor_tab.file_path:
            QMessageBox.information(self, "Git Commit", "Open a file inside a git repo to commit.")
            return
        repo_dir = os.path.dirname(editor_tab.file_path)
        text, ok = QInputDialog.getText(self, "Git Commit", "Enter commit message:")
        if ok and text:
            try:
                subprocess.check_call(['git', '-C', repo_dir, 'add', '.'])
                subprocess.check_call(['git', '-C', repo_dir, 'commit', '-m', text])
                QMessageBox.information(self, "Git Commit", "Commit successful.")
            except Exception as e:
                QMessageBox.warning(self, "Git Error", f"Git commit failed:\n{e}")

    def set_theme(self, theme_name):
        palette = QPalette()
        if theme_name == "Light":
            palette.setColor(QPalette.Window, QColor("#ffffff"))
            palette.setColor(QPalette.Base, QColor("#f5f5f5"))
            palette.setColor(QPalette.Text, QColor("#000000"))
            self.setStyleSheet("""
                QPlainTextEdit, QTextEdit {
                    background: #f5f5f5;
                    color: #000000;
                    font-family: Consolas, monospace;
                    font-size: 14px;
                    border: none;
                }
                QTabWidget::pane {
                    border: 1px solid #ccc;
                    background: #eaeaea;
                }
                QTabBar::tab {
                    background: #eaeaea;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 6px 14px;
                    margin-right: 4px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    border: 1px solid #007acc;
                }
                QTreeView {
                    background: #ffffff;
                    color: #000000;
                    font-size: 13px;
                    padding: 4px;
                }
                QMenuBar, QMenu {
                    background-color: #eaeaea;
                    color: #000000;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton {
                    background: #dcdcdc;
                    color: #000000;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background: #c0c0c0;
                }
            """)
        else:
            # Dark theme (Material + Monokai hybrid)
            palette.setColor(QPalette.Window, QColor("#1e1e1e"))
            palette.setColor(QPalette.Base, QColor("#272822"))
            palette.setColor(QPalette.Text, QColor("#f8f8f2"))
            palette.setColor(QPalette.Highlight, QColor("#89ddff"))
            palette.setColor(QPalette.HighlightedText, QColor("#000000"))
            self.setStyleSheet("""
                QPlainTextEdit, QTextEdit {
                    background: #272822;
                    color: #f8f8f2;
                    font-family: Consolas, monospace;
                    font-size: 14px;
                    border: none;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background: #1e1e1e;
                }
                QTabBar::tab {
                    background: #1e1e1e;
                    color: #f8f8f2;
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 6px 14px;
                    margin-right: 4px;
                }
                QTabBar::tab:selected {
                    background: #2d2d30;
                    border: 1px solid #89ddff;
                }
                QTreeView {
                    background: #1f1f1f;
                    color: #eeeeee;
                    font-size: 13px;
                    padding: 4px;
                }
                QMenuBar, QMenu {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton {
                    background: #3c3f41;
                    color: #ffffff;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background: #505357;
                }
            """)
        QApplication.instance().setPalette(palette)
        self.statusBar().showMessage(f"Theme set to {theme_name}", 3000)

    def open_theme_editor(self):
        dlg = ThemeEditorDialog(self, self.custom_theme)
        if dlg.exec_():
            self.custom_theme = dlg.get_theme()
            self.apply_custom_theme()

    def apply_custom_theme(self):
        # Apply custom theme values to the application's stylesheet and palette
        bg = self.custom_theme.get("Editor Background", "#272822")
        text = self.custom_theme.get("Editor Text", "#f8f8f2")
        tab_bg = self.custom_theme.get("Tab Background", "#1e1e1e")
        tab_text = self.custom_theme.get("Tab Text", "#f8f8f2")
        sidebar = self.custom_theme.get("Sidebar", "#1f1f1f")
        sidebar_text = self.custom_theme.get("Sidebar Text", "#eeeeee")
        highlight = self.custom_theme.get("Highlight", "#89ddff")

        stylesheet = f"""
            QPlainTextEdit, QTextEdit {{
                background: {bg};
                color: {text};
                font-family: Consolas, monospace;
                font-size: 14px;
                border: none;
            }}
            QTabWidget::pane {{
                border: 1px solid #444;
                background: {tab_bg};
            }}
            QTabBar::tab {{
                background: {tab_bg};
                color: {tab_text};
                border: 1px solid #555;
                border-radius: 8px;
                padding: 6px 14px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: {bg};
                border: 1px solid {highlight};
            }}
            QTreeView {{
                background: {sidebar};
                color: {sidebar_text};
                font-size: 13px;
                padding: 4px;
            }}
            QMenuBar, QMenu {{
                background-color: {tab_bg};
                color: {tab_text};
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton {{
                background: {tab_bg};
                color: {tab_text};
                border-radius: 6px;
                padding: 6px 14px;
            }}
            QPushButton:hover {{
                background: {highlight};
            }}
        """
        self.setStyleSheet(stylesheet)
        pal = QApplication.instance().palette()
        try:
            pal.setColor(QPalette.Window, QColor(bg))
            pal.setColor(QPalette.Base, QColor(bg))
            pal.setColor(QPalette.Text, QColor(text))
            pal.setColor(QPalette.Highlight, QColor(highlight))
            pal.setColor(QPalette.HighlightedText, QColor("#000000"))
            QApplication.instance().setPalette(pal)
        except Exception:
            pass
        self.statusBar().showMessage("Applied custom theme", 3000)

    def run_current_file(self):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab or not editor_tab.file_path:
            QMessageBox.information(self, "Run", "Save the file before running.")
            return
        # ensure file saved
        if editor_tab.text_edit.document().isModified():
            # prompt or auto-save
            try:
                with open(editor_tab.file_path, 'w', encoding='utf-8') as f:
                    f.write(editor_tab.text_edit.toPlainText())
                editor_tab.text_edit.document().setModified(False)
            except Exception as e:
                QMessageBox.warning(self, "Run", f"Could not save file:\n{e}")
                return

        ext = os.path.splitext(editor_tab.file_path)[1].lower()
        cmd = None
        if ext == ".py":
            cmd = ["python", editor_tab.file_path]
        elif ext == ".js":
            cmd = ["node", editor_tab.file_path]
        elif ext == ".sh":
            cmd = ["bash", editor_tab.file_path]
        elif ext == ".java":
            # Compile then run
            dir_path = os.path.dirname(editor_tab.file_path)
            base = os.path.splitext(os.path.basename(editor_tab.file_path))[0]
            compile_cmd = ["javac", editor_tab.file_path]
            run_cmd = ["java", "-cp", dir_path, base]
            try:
                subprocess.check_call(compile_cmd)
                cmd = run_cmd
            except Exception as e:
                QMessageBox.warning(self, "Run", f"Java compilation failed:\n{e}")
                return
        elif ext in [".cpp", ".cxx", ".cc"]:
            exe_path = os.path.splitext(editor_tab.file_path)[0] + ".exe"
            compile_cmd = ["g++", editor_tab.file_path, "-o", exe_path]
            try:
                subprocess.check_call(compile_cmd)
                cmd = [exe_path]
            except Exception as e:
                QMessageBox.warning(self, "Run", f"C++ compilation failed:\n{e}")
                return
        else:
            QMessageBox.information(self, "Run", "Running is only supported for Python, JavaScript, Shell, Java, and C++ files.")
            return
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            QMessageBox.information(self, "Run Output", output)
        except Exception as e:
            QMessageBox.warning(self, "Run", f"Run failed:\n{e}")

    def update_recent_menu(self):
        self.recent_menu.clear()
        for path in self.recent_files:
            action = QAction(path, self)
            action.triggered.connect(lambda _, p=path: self.open_path(p))
            self.recent_menu.addAction(action)

    def update_status_bar(self):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab:
            self.statusBar().clearMessage()
            return
        text = editor_tab.text_edit.toPlainText()
        lines = text.count('\n') + 1
        words = len(text.split())
        self.statusBar().showMessage(f"Lines: {lines} | Words: {words}")

    def open_search_replace(self):
        editor_tab = self.tabs.currentWidget()
        if not editor_tab:
            return
        dlg = SearchReplaceDialog(self, editor_tab.text_edit)
        dlg.exec_()

def main():
    app = QApplication(sys.argv)
    editor = Birdseye()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()