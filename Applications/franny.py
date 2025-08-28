# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
from PyQt5.QtGui import QIcon, QPalette, QColor, QFontMetrics, QKeySequence
from PyQt5.QtWidgets import QStyle, QProxyStyle, QShortcut
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSlider
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import json
import os
from collections import defaultdict
import random

BOOKMARKS_PATH = "config/bookmarks.json"
HISTORY_PATH = "config/history.json"

class ChromiumTabStyle(QProxyStyle):
    # A custom style to tweak tab size and margins for a Chromium look. 
    # Doesn't it look awesome????? Right Max?
    def subControlRect(self, control, option, subControl, widget=None):
        rect = super().subControlRect(control, option, subControl, widget)
        if control == QStyle.CC_TabBar and subControl == QStyle.SC_TabBarTab:
            # Make tabs a bit wider and taller
            rect.setHeight(rect.height() + 8)
            rect.setWidth(rect.width() + 24)
            # Add more left-right padding
            rect.adjust(-10, 0, 10, 0)
        return rect

    def drawControl(self, element, option, painter, widget=None):
        super().drawControl(element, option, painter, widget)

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        profile = self.page().profile()
        default_agent = profile.httpUserAgent()
        custom_agent = default_agent.replace(
            default_agent.split(' ')[0],
            "Franny/19.0.910"
        )
        profile.setHttpUserAgent(custom_agent)
        self.setUrl(QUrl("https://www.google.com"))
        self.page().fullScreenRequested.connect(self.handle_fullscreen_request)

    def handle_fullscreen_request(self, request):
        if request.toggleOn():
            self.window().showFullScreen()
        else:
            self.window().showNormal()
        request.accept()

    def show_devtools(self):
        if not hasattr(self, 'devtools') or self.devtools is None:
            self.devtools = QWebEngineView()
            self.page().setDevToolsPage(self.devtools.page())
        self.devtools.show()

    def show_element_inspector(self):
        self.page().runJavaScript("inspect()")

class PDFViewerTab(QWebEngineView):
    def __init__(self, pdf_url, parent=None):
        super().__init__(parent)
        self.setUrl(pdf_url)
        self.loadFinished.connect(self.inject_annotation_js)

    def inject_annotation_js(self):
        js_code = """
        (function() {
            if (document.getElementById('franny-pdf-annotator')) return;
            var canvas = document.createElement('canvas');
            canvas.id = 'franny-pdf-annotator';
            canvas.style.position = 'fixed';
            canvas.style.left = '0';
            canvas.style.top = '0';
            canvas.style.width = '100vw';
            canvas.style.height = '100vh';
            canvas.style.pointerEvents = 'auto';
            canvas.style.zIndex = 9999;
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            document.body.appendChild(canvas);

            var ctx = canvas.getContext('2d');
            var drawing = false;
            var lastX = 0, lastY = 0;

            function getXY(e) {
                if (e.touches) {
                    return [e.touches[0].clientX, e.touches[0].clientY];
                }
                return [e.clientX, e.clientY];
            }

            canvas.addEventListener('mousedown', function(e) {
                drawing = true;
                [lastX, lastY] = getXY(e);
            });
            canvas.addEventListener('mousemove', function(e) {
                if (!drawing) return;
                var [x, y] = getXY(e);
                ctx.strokeStyle = '#ffeb3b';
                ctx.lineWidth = 3;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(lastX, lastY);
                ctx.lineTo(x, y);
                ctx.stroke();
                [lastX, lastY] = [x, y];
            });
            canvas.addEventListener('mouseup', function(e) {
                drawing = false;
            });
            canvas.addEventListener('mouseleave', function(e) {
                drawing = false;
            });

            // Touch support
            canvas.addEventListener('touchstart', function(e) {
                drawing = true;
                [lastX, lastY] = getXY(e);
            });
            canvas.addEventListener('touchmove', function(e) {
                if (!drawing) return;
                var [x, y] = getXY(e);
                ctx.strokeStyle = '#ffeb3b';
                ctx.lineWidth = 3;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(lastX, lastY);
                ctx.lineTo(x, y);
                ctx.stroke();
                [lastX, lastY] = [x, y];
                e.preventDefault();
            }, {passive: false});
            canvas.addEventListener('touchend', function(e) {
                drawing = false;
            });

            // Simple clear button
            var btn = document.createElement('button');
            btn.textContent = 'Clear Annotations';
            btn.style.position = 'fixed';
            btn.style.top = '10px';
            btn.style.right = '10px';
            btn.style.zIndex = 10000;
            btn.style.background = '#222';
            btn.style.color = '#fff';
            btn.style.padding = '8px 16px';
            btn.style.border = 'none';
            btn.style.borderRadius = '6px';
            btn.style.cursor = 'pointer';
            btn.onclick = function() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            };
            document.body.appendChild(btn);

            // Export button
            var exportBtn = document.createElement('button');
            exportBtn.textContent = 'Export Annotations';
            exportBtn.style.position = 'fixed';
            exportBtn.style.top = '50px';
            exportBtn.style.right = '10px';
            exportBtn.style.zIndex = 10000;
            exportBtn.style.background = '#222';
            exportBtn.style.color = '#fff';
            exportBtn.style.padding = '8px 16px';
            exportBtn.style.border = 'none';
            exportBtn.style.borderRadius = '6px';
            exportBtn.style.cursor = 'pointer';
            exportBtn.onclick = function() {
                var canvas = document.getElementById('franny-pdf-annotator');
                var dataURL = canvas.toDataURL('image/png');
                var a = document.createElement('a');
                a.href = dataURL;
                a.download = 'annotations.png';
                a.click();
            };
            document.body.appendChild(exportBtn);

            // Resize canvas on window resize
            window.addEventListener('resize', function() {
                var img = ctx.getImageData(0, 0, canvas.width, canvas.height);
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                ctx.putImageData(img, 0, 0);
            });
        })();
        """
        self.page().runJavaScript(js_code)

class GroupedTabBar(QTabBar):
    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()
        for i in range(self.count()):
            self.initStyleOption(opt, i)
            group = self.tabData(i)
            if group:
                color = self.parent().group_colors.get(group, "#888")
                opt.palette.setColor(QPalette.Window, QColor(color))
                opt.palette.setColor(QPalette.Button, QColor(color))
                opt.palette.setColor(QPalette.ButtonText, QColor("#fff"))
            painter.drawControl(QStyle.CE_TabBarTab, opt)

class FrannyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Franny (v19.0.910)")  

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tab_bar = GroupedTabBar(self.tabs)
        self.tabs.setTabBar(self.tab_bar)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4b4b4b, stop:1 #2b2b2b);
                color: #ddd;
                padding: 10px 22px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 3px;
                font-weight: 500;
                min-width: 110px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a8cff, stop:1 #0069d9);
                color: white;
                font-weight: 700;
                margin-bottom: 0px;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d9cff, stop:1 #007acc);
                color: white;
            }
            QTabWidget::pane {
                border-top: 2px solid #1a8cff;
                background-color: #222;
            }
        """)

        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address_bar)
        self.setCentralWidget(self.tabs)

        self.history = self.load_history()
        self.zoom_level = 1.0
        self.closed_tabs = []  # Stack for closed tabs
        self.tab_groups = {}  # tab index -> group name
        self.group_colors = {}  # group name -> color

        self.minimalist_mode = False  # Minimalist mode state

        self.init_toolbar()
        self.init_menu()
        self.init_shortcuts()
        self.init_bookmarks_bar()

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)

    def init_toolbar(self):
        self.toolbar = QToolBar("Navigation", self)
        self.toolbar.setIconSize(QSize(28, 28))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: #222;
                border-bottom: 1px solid #1a8cff;
                padding: 6px 10px;
                spacing: 10px;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background: #1a8cff;
                border-radius: 4px;
            }
            QLineEdit {
                background: #333;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px 10px;
                color: #eee;
                min-width: 400px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1a8cff;
                background: #222;
            }
        """)
        self.addToolBar(self.toolbar)

        back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_btn.setToolTip("Go Back")
        back_btn.triggered.connect(lambda: self.current_browser().back())
        self.toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_btn.setToolTip("Go Forward")
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        reload_btn.setToolTip("Reload Page")
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.toolbar.addAction(reload_btn)

        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.setToolTip("Go Home")
        home_btn.triggered.connect(self.go_home)
        self.toolbar.addAction(home_btn)

        self.toolbar.addSeparator()

        self.address_bar = QLineEdit(self)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.address_bar)

        new_tab_btn = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        new_tab_btn.setToolTip("Open New Tab")
        new_tab_btn.triggered.connect(self.new_tab)
        self.toolbar.addAction(new_tab_btn)

    def init_menu(self):
        menu_bar = self.menuBar()

        
        file_menu = menu_bar.addMenu("Tabs and Modes")
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

        save_pdf_action = QAction("Save as PDF", self)
        save_pdf_action.triggered.connect(self.save_as_pdf)
        file_menu.addAction(save_pdf_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()
        clear_data_action = QAction("Clear Data", self)
        clear_data_action.triggered.connect(self.clear_data)
        file_menu.addAction(clear_data_action)

        # View menu
        view_menu = menu_bar.addMenu("View")
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        find_in_page_action = QAction("Find in Page", self)
        find_in_page_action.triggered.connect(self.find_in_page)
        view_menu.addAction(find_in_page_action)

        devtools_action = QAction("Open DevTools", self)
        devtools_action.setShortcut("F12")
        devtools_action.triggered.connect(lambda: self.current_browser().show_devtools())
        view_menu.addAction(devtools_action)

        minimalist_toggle_action = QAction("Toggle Minimalist Mode", self)
        minimalist_toggle_action.triggered.connect(self.toggle_minimalist_mode)
        view_menu.addAction(minimalist_toggle_action)

        resource_viewer_action = QAction("Site Resource Viewer", self)
        resource_viewer_action.triggered.connect(self.show_resource_viewer)
        view_menu.addAction(resource_viewer_action)

        # Bookmarks menu
        bookmarks_menu = menu_bar.addMenu("Bookmarks")
        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)

        import_bookmarks_action = QAction("Import Bookmarks", self)
        import_bookmarks_action.triggered.connect(self.import_bookmarks)
        bookmarks_menu.addAction(import_bookmarks_action)

        export_bookmarks_action = QAction("Export Bookmarks", self)
        export_bookmarks_action.triggered.connect(self.export_bookmarks)
        bookmarks_menu.addAction(export_bookmarks_action)

        self.bookmarks_action = QAction("Show Bookmarks", self)
        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmarks_menu.addAction(self.bookmarks_action)

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        download_manager_action = QAction("Download Manager", self)
        download_manager_action.triggered.connect(self.show_download_manager)
        tools_menu.addAction(download_manager_action)

        minimalist_toggle_action = QAction("Toggle Minimalist Mode", self)
        minimalist_toggle_action.triggered.connect(self.toggle_minimalist_mode)
        file_menu.addAction(minimalist_toggle_action)

        resource_viewer_action = QAction("Site Resource Viewer", self)
        resource_viewer_action.triggered.connect(self.show_resource_viewer)
        file_menu.addAction(resource_viewer_action)

    def init_bookmarks_bar(self):
        self.bookmarks_bar = QToolBar("Bookmarks Bar", self)
        self.bookmarks_bar.setIconSize(QSize(20, 20))
        self.bookmarks_bar.setStyleSheet("""
            QToolBar {
                background: #222;
                border-bottom: 1px solid #1a8cff;
                padding: 4px 6px;
            }
            QToolButton {
                background: transparent;
                border: none;
                color: #ccc;
                padding: 4px 10px;
                font-weight: 500;
            }
            QToolButton:hover {
                background: #1a8cff;
                color: white;
                border-radius: 4px;
            }
        """)
        self.addToolBar(Qt.TopToolBarArea, self.bookmarks_bar)
        self.update_bookmarks_bar()

    def update_bookmarks_bar(self):
        self.bookmarks_bar.clear()
        bookmarks = self.load_bookmarks()
        for url in bookmarks:
            action = QAction(QIcon.fromTheme("bookmark"), url, self)
            action.setToolTip(url)
            action.triggered.connect(lambda checked, u=url: self.add_new_tab(QUrl(u), u))
            self.bookmarks_bar.addAction(action)

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
        # Download handling
        browser.page().profile().downloadRequested.connect(self.handle_download_requested)
        self.update_tab_group_styles()

    def new_tab(self):
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            browser = self.tabs.widget(index)
            url = browser.url()
            title = browser.title()
            self.closed_tabs.append((url, title))
            self.tabs.removeTab(index)
            browser.deleteLater()  # Free resources
        else:
            self.close()
        if index in self.tab_groups:
            del self.tab_groups[index]
        # Shift group indices after removal
        new_tab_groups = {}
        for idx, group in self.tab_groups.items():
            if idx > index:
                new_tab_groups[idx - 1] = group
            elif idx < index:
                new_tab_groups[idx] = group
        self.tab_groups = new_tab_groups
        self.update_tab_group_styles()

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
            self.update_bookmarks_bar()
        else:
            self.status_bar.showMessage("This page is already bookmarked.")

    def remove_bookmark(self, url):
        bookmarks = self.load_bookmarks()
        if url in bookmarks:
            bookmarks.remove(url)
            self.save_bookmarks(bookmarks)
            self.status_bar.showMessage(f"Bookmark removed: {url}")
            self.update_bookmarks_bar()
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

    def import_bookmarks(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Bookmarks", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r") as f:
                    imported = json.load(f)
                bookmarks = self.load_bookmarks()
                # Merge and deduplicate
                for url in imported:
                    if url not in bookmarks:
                        bookmarks.append(url)
                self.save_bookmarks(bookmarks)
                self.status_bar.showMessage("Bookmarks imported.")
            except Exception as e:
                self.status_bar.showMessage(f"Import failed: {e}")

    def export_bookmarks(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Bookmarks", "", "JSON Files (*.json)")
        if path:
            try:
                bookmarks = self.load_bookmarks()
                with open(path, "w") as f:
                    json.dump(bookmarks, f, indent=2)
                self.status_bar.showMessage("Bookmarks exported.")
            except Exception as e:
                self.status_bar.showMessage(f"Export failed: {e}")

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
        browser.page().profile().downloadRequested.connect(self.handle_download_requested)
        self.update_tab_group_styles()

    def handle_download_requested(self, download: QWebEngineDownloadItem):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path())
        if save_path:
            download.setPath(save_path)
            download.accept()
            if not hasattr(self, "downloads"):
                self.downloads = []
            self.downloads.append(download)
            download.finished.connect(lambda: self.notify_download_finished(download))
            download.downloadProgress.connect(lambda rec, tot: self.update_download_manager())
            self.update_download_manager()

    def notify_download_finished(self, download):
        self.status_bar.showMessage(f"Download finished: {os.path.basename(download.path())}")

    def show_download_manager(self):
        if not hasattr(self, "downloads"):
            self.downloads = []
        dialog = QDialog(self)
        dialog.setWindowTitle("Download Manager")
        layout = QVBoxLayout()
        for download in self.downloads:
            status = "Finished" if download.isFinished() else "Downloading"
            progress = ""
            if not download.isFinished():
                try:
                    percent = int((download.receivedBytes() / max(download.totalBytes(), 1)) * 100)
                    progress = f" ({percent}%)"
                except Exception:
                    progress = ""
            label = QLabel(f"{os.path.basename(download.path())} - {status}{progress}")
            layout.addWidget(label)
            if download.isFinished():
                open_btn = QPushButton("Open File Location")
                open_btn.clicked.connect(lambda _, p=download.path(): os.startfile(os.path.dirname(p)))
                layout.addWidget(open_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def update_download_manager(self):
        pass

    def init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Tab"), self, activated=self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=self.prev_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.new_tab)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.find_in_page)
        QShortcut(QKeySequence("Ctrl++"), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, activated=self.search_tabs)

    def next_tab(self):
        idx = self.tabs.currentIndex()
        count = self.tabs.count()
        self.tabs.setCurrentIndex((idx + 1) % count)

    def prev_tab(self):
        idx = self.tabs.currentIndex()
        count = self.tabs.count()
        self.tabs.setCurrentIndex((idx - 1) % count)

    def show_tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index == -1:
            return
        menu = QMenu(self)
        create_group_action = QAction("Create New Group", self)
        create_group_action.triggered.connect(lambda: self.create_tab_group(index))
        menu.addAction(create_group_action)
        if self.group_colors:
            submenu = menu.addMenu("Add to Existing Group")
            for group in self.group_colors:
                act = QAction(group, self)
                act.triggered.connect(lambda checked, g=group: self.add_tab_to_group(index, g))
                submenu.addAction(act)
        if index in self.tab_groups:
            remove_action = QAction("Remove from Group", self)
            remove_action.triggered.connect(lambda: self.remove_tab_from_group(index))
            menu.addAction(remove_action)
        menu.exec_(self.tabs.tabBar().mapToGlobal(pos))

    def create_tab_group(self, index):
        group_name, ok = QInputDialog.getText(self, "New Tab Group", "Enter group name:")
        if ok and group_name:
            color = QColor(*random.sample(range(80, 220), 3)).name()
            self.group_colors[group_name] = color
            self.tab_groups[index] = group_name
            self.update_tab_group_styles()

    def add_tab_to_group(self, index, group_name):
        self.tab_groups[index] = group_name
        self.update_tab_group_styles()

    def remove_tab_from_group(self, index):
        if index in self.tab_groups:
            del self.tab_groups[index]
            self.update_tab_group_styles()

    def update_tab_group_styles(self):
        for idx in range(self.tabs.count()):
            group = self.tab_groups.get(idx)
            if group:
                self.tabs.tabBar().setTabData(idx, group)
            else:
                self.tabs.tabBar().setTabData(idx, None)
        self.tabs.tabBar().update()

    def save_as_pdf(self):
        browser = self.current_browser()
        if not browser:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save as PDF", "", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            def pdf_finished(path, ok):
                if ok:
                    self.status_bar.showMessage(f"Saved PDF: {path}")
                else:
                    self.status_bar.showMessage("Failed to save PDF.")
            browser.page().printToPdf(file_path, pageLayout=None, callback=lambda ok: pdf_finished(file_path, ok))

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout()

        home_label = QLabel("Homepage URL:")
        home_input = QLineEdit(self)
        home_input.setText(getattr(self, "homepage", "https://www.google.com"))
        layout.addWidget(home_label)
        layout.addWidget(home_input)

        zoom_label = QLabel("Default Zoom:")
        zoom_slider = QSlider(Qt.Horizontal)
        zoom_slider.setRange(5, 20)
        zoom_slider.setValue(int(getattr(self, "zoom_level", 1.0) * 10))
        layout.addWidget(zoom_label)
        layout.addWidget(zoom_slider)

        theme_label = QLabel("Theme:")
        theme_combo = QComboBox()
        theme_combo.addItems(THEMES.keys())
        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)

        adblock_checkbox = QCheckBox("Enable Ad/Tracker Blocker")
        adblock_checkbox.setChecked(getattr(self, "adblock_enabled", False))
        layout.addWidget(adblock_checkbox)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.apply_settings(
            home_input.text(), zoom_slider.value() / 10, theme_combo.currentText(),
            adblock_checkbox.isChecked(), dialog))
        layout.addWidget(save_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def apply_settings(self, homepage, zoom, theme, adblock_enabled, dialog):
        self.homepage = homepage
        self.zoom_level = zoom
        self.current_browser().setZoomFactor(zoom)
        apply_theme(QApplication.instance(), theme)
        self.adblock_enabled = adblock_enabled
        if adblock_enabled:
            self._adblocker = FrannyAdBlocker()
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                browser.page().profile().setRequestInterceptor(self._adblocker)
        else:
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                browser.page().profile().setRequestInterceptor(None)
        self.status_bar.showMessage("Settings applied.")
        dialog.accept()

    # --- Toolbar Customization Example ---
    def show_toolbar_customization(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Customize Toolbar")
        layout = QVBoxLayout()
        btns = []
        for action in self.toolbar.actions():
            cb = QCheckBox(action.text())
            cb.setChecked(action.isVisible())
            cb.stateChanged.connect(lambda state, a=action: a.setVisible(state == Qt.Checked))
            layout.addWidget(cb)
            btns.append(cb)
        dialog.setLayout(layout)
        dialog.exec_()

    # --- Per-site Permissions Example ---
    def show_site_permissions(self):
        browser = self.current_browser()
        page = browser.page()
        dialog = QDialog(self)
        dialog.setWindowTitle("Site Permissions")
        layout = QVBoxLayout()
        for perm in [QWebEnginePage.PermissionCamera, QWebEnginePage.PermissionMicrophone, QWebEnginePage.PermissionNotifications]:
            label = QLabel(str(perm))
            btn = QPushButton("Toggle")
            btn.clicked.connect(lambda _, p=perm: page.setFeaturePermission(
                page.url(), p, QWebEnginePage.PermissionGrantedByUser))
            layout.addWidget(label)
            layout.addWidget(btn)
        dialog.setLayout(layout)
        dialog.exec_()

# --- Privacy & Security: Simple Ad/Tracker Blocker ---
class FrannyAdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocklist=None):
        super().__init__()
        self.blocklist = blocklist or [
            "doubleclick.net", "googlesyndication.com", "adservice.google.com",
            "ads.yahoo.com", "adnxs.com", "tracking", "analytics"
        ]
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(bad in url for bad in self.blocklist):
            info.block(True)

# --- Customization: Theme Selection ---
THEMES = {
    "Dark": {
        "window": QColor(53, 53, 53),
        "text": Qt.white,
        "base": QColor(35, 35, 35),
        "highlight": QColor(42, 130, 218)
    },
    "Light": {
        "window": Qt.white,
        "text": Qt.black,
        "base": QColor(245, 245, 245),
        "highlight": QColor(42, 130, 218)
    }
}

def apply_theme(app, theme_name):
    theme = THEMES.get(theme_name, THEMES["Dark"])
    palette = QPalette()
    palette.setColor(QPalette.Window, theme["window"])
    palette.setColor(QPalette.WindowText, theme["text"])
    palette.setColor(QPalette.Base, theme["base"])
    palette.setColor(QPalette.Text, theme["text"])
    palette.setColor(QPalette.Highlight, theme["highlight"])
    palette.setColor(QPalette.HighlightedText, theme["text"])
    app.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    window = FrannyBrowser()
    window.show()
    sys.exit(app.exec_())
