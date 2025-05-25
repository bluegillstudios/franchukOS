# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon
import json
import os

BOOKMARKS_PATH = "config/bookmarks.json"
HISTORY_PATH = "config/history.json"

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUrl(QUrl("https://www.google.com"))

class FrannyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Franny Browser (14.3.5671.224)")
        self.setGeometry(100, 100, 1024, 768)

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)
        self.setCentralWidget(self.tabs)

        self.history = self.load_history()
        self.zoom_level = 1.0
        self.closed_tabs = []  # Stack for closed tabs

        self.init_toolbar()
        self.init_menu()

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

    def init_toolbar(self):
        self.toolbar = QToolBar("Navigation", self)
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        self.toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.toolbar.addAction(reload_btn)

        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.triggered.connect(self.go_home)
        self.toolbar.addAction(home_btn)

        self.toolbar.addSeparator()

        self.address_bar = QLineEdit(self)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.address_bar)

        new_tab_btn = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        new_tab_btn.triggered.connect(self.new_tab)
        self.toolbar.addAction(new_tab_btn)

    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Options")
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)

        restore_tab_action = QAction("Restore Closed Tab", self)
        restore_tab_action.setShortcut("Ctrl+Shift+T")
        restore_tab_action.triggered.connect(self.restore_closed_tab)
        file_menu.addAction(restore_tab_action)

        incognito_action = QAction("Incognito Mode", self)
        incognito_action.triggered.connect(self.toggle_incognito)
        file_menu.addAction(incognito_action)

        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        file_menu.addAction(add_bookmark_action)

        clear_data_action = QAction("Clear Data", self)
        clear_data_action.triggered.connect(self.clear_data)
        file_menu.addAction(clear_data_action)

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        file_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        file_menu.addAction(zoom_out_action)

        find_in_page_action = QAction("Find in Page", self)
        find_in_page_action.triggered.connect(self.find_in_page)
        file_menu.addAction(find_in_page_action)

        bookmark_menu = menu_bar.addMenu("Bookmarks")
        self.bookmarks_action = QAction("Bookmarks", self)
        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmark_menu.addAction(self.bookmarks_action)

    def add_new_tab(self, qurl=None, label="New Tab"):
        browser = BrowserTab(self)
        browser.setUrl(qurl or QUrl("https://www.google.com"))
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda url, b=browser: self.update_tab_title(url, b))
        browser.urlChanged.connect(self.update_history)
        browser.titleChanged.connect(lambda title, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), title))
        browser.iconChanged.connect(lambda icon, b=browser: self.tabs.setTabIcon(self.tabs.indexOf(b), icon))
        browser.loadFinished.connect(lambda: self.update_address_bar(self.tabs.currentIndex()))

    def new_tab(self):
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            browser = self.tabs.widget(index)
            url = browser.url()
            title = browser.title()
            self.closed_tabs.append((url, title))
            self.tabs.removeTab(index)
        else:
            self.close()

    def restore_closed_tab(self):
        if self.closed_tabs:
            url, title = self.closed_tabs.pop()
            self.add_new_tab(url, title)
        else:
            self.status_bar.showMessage("No closed tabs to restore.")

    def current_browser(self):
        return self.tabs.currentWidget()

    def update_tab_title(self, url, browser):
        if browser:
            self.tabs.setTabText(self.tabs.indexOf(browser), browser.title() or "New Tab")

    def update_address_bar(self, index):
        browser = self.tabs.widget(index)
        if browser:
            url = browser.url().toString()
            self.address_bar.setText(url)
            if url.startswith("https://"):
                self.status_bar.showMessage("Secure connection (HTTPS)")
            elif url.startswith("http://"):
                self.status_bar.showMessage("Not secure (HTTP)")
            elif url.startswith("ssh://"):
                self.status_bar.showMessage("SSH protocol detected")
            else:
                self.status_bar.clearMessage()

    def navigate_to_url(self):
        url = QUrl(self.address_bar.text())
        if url.scheme() == "":
            url.setScheme("http")
        self.current_browser().setUrl(url)

    def go_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com"))

    def update_history(self, url):
        self.history.append(url.toString())
        self.save_history()
        self.status_bar.showMessage(f"Visited: {url.toString()}")

    def toggle_incognito(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.setUrl(QUrl("about:blank"))
            self.status_bar.showMessage("Incognito Mode Enabled")

    def show_bookmarks(self):
        bookmarks = self.load_bookmarks()
        bookmark_dialog = QDialog(self)
        bookmark_dialog.setWindowTitle("Bookmarks")
        layout = QVBoxLayout()
        for bookmark in bookmarks:
            button = QPushButton(bookmark, self)
            favicon = QIcon()
            try:
                browser = BrowserTab()
                browser.setUrl(QUrl(bookmark))
                favicon = browser.icon()
            except Exception:
                pass
            button.setIcon(favicon)
            button.clicked.connect(lambda _, url=bookmark: self.add_new_tab(QUrl(url), url))
            layout.addWidget(button)
        bookmark_dialog.setLayout(layout)
        bookmark_dialog.exec_()

    def add_bookmark(self):
        current_url = self.current_browser().url().toString()
        bookmarks = self.load_bookmarks()
        if current_url not in bookmarks:
            bookmarks.append(current_url)
            self.save_bookmarks(bookmarks)
            self.status_bar.showMessage(f"Bookmark added: {current_url}")
        else:
            self.status_bar.showMessage("This page is already bookmarked.")

    def remove_bookmark(self, url):
        bookmarks = self.load_bookmarks()
        if url in bookmarks:
            bookmarks.remove(url)
            self.save_bookmarks(bookmarks)
            self.status_bar.showMessage(f"Bookmark removed: {url}")
        else:
            self.status_bar.showMessage("Bookmark not found.")

    def load_bookmarks(self):
        if os.path.exists(BOOKMARKS_PATH):
            with open(BOOKMARKS_PATH, "r") as file:
                return json.load(file)
        return []

    def save_bookmarks(self, bookmarks):
        with open(BOOKMARKS_PATH, "w") as file:
            json.dump(bookmarks, file)

    def save_history(self):
        with open(HISTORY_PATH, "w") as file:
            json.dump(self.history, file)

    def load_history(self):
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r") as file:
                return json.load(file)
        return []

    def clear_data(self):
        self.history.clear()
        self.save_history()
        self.current_browser().page().profile().clearHttpCache()
        self.status_bar.showMessage("Browsing data cleared.")

    def zoom_in(self):
        self.zoom_level += 0.1
        self.current_browser().setZoomFactor(self.zoom_level)

    def zoom_out(self):
        self.zoom_level -= 0.1
        self.current_browser().setZoomFactor(self.zoom_level)

    def find_in_page(self):
        search_text, ok = QInputDialog.getText(self, "Find in Page", "Enter text to find:")
        if ok and search_text:
            self.current_browser().findText(search_text, QWebEnginePage.FindFlags(QWebEnginePage.FindCaseSensitively))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrannyBrowser()
    window.show()
    sys.exit(app.exec_())
