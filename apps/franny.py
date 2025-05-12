# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import json
import os

BOOKMARKS_PATH = "config/bookmarks.json"
HISTORY_PATH = "config/history.json"

class FrannyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Franny Browser (13.0.1224.97)")
        self.setGeometry(100, 100, 1024, 768)

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)  # <-- Set the tab widget as central

        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.tabs.addTab(self.browser, "New Tab")

        self.browser.urlChanged.connect(self.update_history)

        # Menu Bar
        self.init_menu()

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # History
        self.history = self.load_history()

        # Zoom Level
        self.zoom_level = 1.0

    def init_menu(self):
        """Initialize the menu bar."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)

        # Navigation Menu
        navigation_menu = menu_bar.addMenu("Navigation")
        back_action = QAction("Back", self)
        back_action.triggered.connect(self.browser.back)
        navigation_menu.addAction(back_action)

        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.browser.forward)
        navigation_menu.addAction(forward_action)

        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.browser.reload)
        navigation_menu.addAction(reload_action)

        # Incognito Mode
        incognito_action = QAction("Incognito Mode", self)
        incognito_action.triggered.connect(self.toggle_incognito)
        file_menu.addAction(incognito_action)

        # Bookmarks
        bookmark_menu = menu_bar.addMenu("Bookmarks")
        self.bookmarks_action = QAction("Bookmarks", self)
        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmark_menu.addAction(self.bookmarks_action)

        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        file_menu.addAction(add_bookmark_action)

        # Clear Data
        clear_data_action = QAction("Clear Data", self)
        clear_data_action.triggered.connect(self.clear_data)
        file_menu.addAction(clear_data_action)

        # Zoom Controls
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        file_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        file_menu.addAction(zoom_out_action)

        # Find in Page
        find_in_page_action = QAction("Find in Page", self)
        find_in_page_action.triggered.connect(self.find_in_page)
        file_menu.addAction(find_in_page_action)

    def new_tab(self):
        """Open a new tab in the browser."""
        new_browser = QWebEngineView(self)
        new_browser.setUrl(QUrl("https://www.google.com"))
        self.tabs.addTab(new_browser, "New Tab")
        self.tabs.setCurrentWidget(new_browser)
        new_browser.urlChanged.connect(self.update_history)

    def update_history(self, url):
        """Update the browsing history."""
        self.history.append(url.toString())
        self.save_history()

        self.status_bar.showMessage(f"Visited: {url.toString()}")

    def toggle_incognito(self):
        """Toggle incognito mode (private browsing)."""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("about:blank"))  # Placeholder URL for incognito mode
            self.status_bar.showMessage("Incognito Mode Enabled")

    def show_bookmarks(self):
        """Show bookmarks."""
        bookmarks = self.load_bookmarks()
        bookmark_dialog = QDialog(self)
        bookmark_dialog.setWindowTitle("Bookmarks")

        layout = QVBoxLayout()
        for bookmark in bookmarks:
            button = QPushButton(bookmark, self)
            button.clicked.connect(lambda url=bookmark: self.load_bookmark(url))
            layout.addWidget(button)

        bookmark_dialog.setLayout(layout)
        bookmark_dialog.exec_()

    def add_bookmark(self):
        """Add a new bookmark."""
        current_url = self.browser.url().toString()
        bookmarks = self.load_bookmarks()

        if current_url not in bookmarks:
            bookmarks.append(current_url)
            self.save_bookmarks(bookmarks)
            self.status_bar.showMessage(f"Bookmark added: {current_url}")
        else:
            self.status_bar.showMessage("This page is already bookmarked.")

    def remove_bookmark(self, url):
        """Remove a bookmark."""
        bookmarks = self.load_bookmarks()
        if url in bookmarks:
            bookmarks.remove(url)
            self.save_bookmarks(bookmarks)
            self.status_bar.showMessage(f"Bookmark removed: {url}")
        else:
            self.status_bar.showMessage("Bookmark not found.")

    def load_bookmarks(self):
        """Load bookmarks from a file."""
        if os.path.exists(BOOKMARKS_PATH):
            with open(BOOKMARKS_PATH, "r") as file:
                return json.load(file)
        return []

    def save_bookmarks(self, bookmarks):
        """Save bookmarks to a file."""
        with open(BOOKMARKS_PATH, "w") as file:
            json.dump(bookmarks, file)

    def save_history(self):
        """Save the browsing history to a file."""
        with open(HISTORY_PATH, "w") as file:
            json.dump(self.history, file)

    def load_history(self):
        """Load browsing history from a file."""
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r") as file:
                return json.load(file)
        return []

    def clear_data(self):
        """Clear browsing history and cache."""
        self.history.clear()
        self.save_history()
        self.browser.page().profile().clearHttpCache()
        self.status_bar.showMessage("Browsing data cleared.")

    def zoom_in(self):
        """Zoom in on the webpage."""
        self.zoom_level += 0.1
        self.browser.setZoomFactor(self.zoom_level)

    def zoom_out(self):
        """Zoom out on the webpage."""
        self.zoom_level -= 0.1
        self.browser.setZoomFactor(self.zoom_level)

    def find_in_page(self):
        """Find text in the current page."""
        search_text, ok = QInputDialog.getText(self, "Find in Page", "Enter text to find:")
        if ok and search_text:
            self.browser.findText(search_text, QWebEnginePage.FindFlags(QWebEnginePage.FindCaseSensitively))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrannyBrowser()
    window.show()
    sys.exit(app.exec_())
