# birdseye.py

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTabWidget,
    QWidget, QVBoxLayout, QTextEdit, QAction, QMenuBar, QMessageBox
)
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QTimer, QRegExp
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

class EditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier", 11))
        self.highlighter = CodeHighlighter(self.text_edit.document())
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
        self.file_path = None

class Birdseye(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Birdseye v1.32")
        self.setGeometry(200, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.statusBar()

        self.init_menu()
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_all)
        self.autosave_timer.start(30000)

        self.new_tab()

    def init_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

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
