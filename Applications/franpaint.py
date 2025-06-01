# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QColorDialog,
    QFileDialog, QLabel, QComboBox, QMessageBox, QInputDialog, QMenu, 
    QSizePolicy
)
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QMouseEvent, QFont, QImage, QTransform, QClipboard
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtPrintSupport import QPrinter
import sys


class Franpaint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Franpaint v3.3.35")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = QLabel()
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.pixmap = QPixmap(800, 600)
        self.pixmap.fill(Qt.white)
        self.canvas.setPixmap(self.pixmap)
        self.setCentralWidget(self.canvas)

        self.drawing = False
        self.last_point = QPoint()
        self.current_point = QPoint()
        self.pen_color = Qt.black
        self.pen_width = 2
        self.pen_style = Qt.SolidLine
        self.current_tool = 'freehand'
        self.undo_stack = []
        self.redo_stack = []

        self.fill_shapes = False 
        self.current_fill_color = Qt.white  # Default fill color

        self.brush_shape = 'round'  

        self.init_menu()
        self.init_toolbar()

    def init_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New", self.clear_canvas)
        file_menu.addAction("Open...", self.load_image)
        file_menu.addAction("Save...", self.save_image)
        file_menu.addSeparator()
        file_menu.addAction("Export as PDF...", self.export_pdf)
        file_menu.addAction("Export as SVG...", self.export_svg)
        file_menu.addAction("Copy to Clipboard", self.copy_to_clipboard)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo", self.undo)
        edit_menu.addAction("Redo", self.redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Crop", self.crop_image)
        edit_menu.addAction("Resize", self.resize_image)
        edit_menu.addAction("Rotate", self.rotate_image)

        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Freehand", lambda: self.set_tool('freehand'))
        tools_menu.addAction("Rectangle", lambda: self.set_tool('rectangle'))
        tools_menu.addAction("Ellipse", lambda: self.set_tool('ellipse'))
        tools_menu.addAction("Text", self.insert_text)
        tools_menu.addSeparator()
        tools_menu.addAction("Eyedropper", lambda: self.set_tool('eyedropper'))
        tools_menu.addSeparator()
        fill_shapes_action = QAction("Fill Shapes", self, checkable=True)
        fill_shapes_action.setChecked(self.fill_shapes)
        fill_shapes_action.toggled.connect(self.toggle_fill)
        tools_menu.addAction(fill_shapes_action)
        tools_menu.addAction("Fill Color...", self.select_fill_color)
        tools_menu.addAction("Pen Color...", self.select_color)

        # Help Menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)

    def clear_canvas(self):
        self.undo_stack.append(self.pixmap.copy())
        self.redo_stack.clear()
        self.pixmap.fill(Qt.white)
        self.canvas.setPixmap(self.pixmap)

    def init_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        color_action = QAction("Color", self)
        color_action.triggered.connect(self.select_color)
        toolbar.addAction(color_action)

        self.brush_size = QComboBox()
        self.brush_size.addItems(["2", "4", "8", "12", "16", "20"])
        self.brush_size.currentIndexChanged.connect(self.change_pen_width)
        toolbar.addWidget(self.brush_size)

        # Add brush shape selector
        self.brush_shape_box = QComboBox()
        self.brush_shape_box.addItems(["Round", "Square"])
        self.brush_shape_box.currentIndexChanged.connect(self.change_brush_shape)
        toolbar.addWidget(self.brush_shape_box)

        freehand_action = QAction("Freehand", self)
        freehand_action.triggered.connect(lambda: self.set_tool('freehand'))
        toolbar.addAction(freehand_action)

        rect_action = QAction("Rectangle", self)
        rect_action.triggered.connect(lambda: self.set_tool('rectangle'))
        toolbar.addAction(rect_action)

        ellipse_action = QAction("Ellipse", self)
        ellipse_action.triggered.connect(lambda: self.set_tool('ellipse'))
        toolbar.addAction(ellipse_action)

        text_action = QAction("Text", self)
        text_action.triggered.connect(self.insert_text)
        toolbar.addAction(text_action)

    def resizeEvent(self, event):
        # Resize the pixmap to fit the new window size, preserving content
        new_size = self.canvas.size()
        if new_size.width() > 0 and new_size.height() > 0:
            new_pixmap = QPixmap(new_size)
            new_pixmap.fill(Qt.white)
            painter = QPainter(new_pixmap)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()
            self.pixmap = new_pixmap
            self.canvas.setPixmap(self.pixmap)
        super().resizeEvent(event)

    def _canvas_pos(self, event):
        # Map global event position to canvas coordinates
        return self.canvas.mapFromParent(event.pos())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.undo_stack.append(self.pixmap.copy())
            self.redo_stack.clear()
            self.drawing = True
            pos = self._canvas_pos(event)
            self.last_point = pos
            self.current_point = pos

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing and self.current_tool == 'freehand':
            pos = self._canvas_pos(event)
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color, self.pen_width, self.pen_style)
            painter.setPen(pen)
            if self.brush_shape == 'round':
                painter.setBrush(self.pen_color)
                painter.drawEllipse(pos, self.pen_width // 2, self.pen_width // 2)
            elif self.brush_shape == 'square':
                painter.setBrush(self.pen_color)
                size = self.pen_width
                painter.drawRect(pos.x() - size // 2, pos.y() - size // 2, size, size)
            else:
                painter.drawLine(self.last_point, pos)
            self.last_point = pos
            self.canvas.setPixmap(self.pixmap)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            pos = self._canvas_pos(event)
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color, self.pen_width, self.pen_style)
            painter.setPen(pen)

            if self.current_tool == 'rectangle':
                rect = QRect(self.last_point, pos)
                if self.fill_shapes:
                    painter.fillRect(rect, self.current_fill_color)
                painter.drawRect(rect)
            elif self.current_tool == 'ellipse':
                rect = QRect(self.last_point, pos)
                if self.fill_shapes:
                    painter.setBrush(self.current_fill_color)
                else:
                    painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(rect)
            elif self.current_tool == 'eyedropper':
                img = self.pixmap.toImage()
                color = QColor(img.pixel(pos))
                self.pen_color = color

            self.canvas.setPixmap(self.pixmap)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color

    def change_pen_width(self):
        self.pen_width = int(self.brush_size.currentText())

    def change_brush_shape(self):
        self.brush_shape = self.brush_shape_box.currentText().lower()

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_path:
            self.pixmap.save(file_path)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            self.pixmap.load(file_path)
            self.canvas.setPixmap(self.pixmap)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.pixmap.copy())
            self.pixmap = self.undo_stack.pop()
            self.canvas.setPixmap(self.pixmap)
        else:
            QMessageBox.information(self, "Undo", "Nothing to undo.")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.pixmap.copy())
            self.pixmap = self.redo_stack.pop()
            self.canvas.setPixmap(self.pixmap)
        else:
            QMessageBox.information(self, "Redo", "Nothing to redo.")

    def set_tool(self, tool):
        self.current_tool = tool

    def insert_text(self):
        text, ok = QInputDialog.getText(self, "Insert Text", "Enter text:")
        if ok and text:
            x, ok_x = QInputDialog.getInt(self, "X Position", "Enter X:", 50)
            y, ok_y = QInputDialog.getInt(self, "Y Position", "Enter Y:", 50)
            if ok_x and ok_y:
                self.undo_stack.append(self.pixmap.copy())
                self.redo_stack.clear()
                painter = QPainter(self.pixmap)
                painter.setPen(QPen(self.pen_color))
                painter.setFont(QFont("Arial", 14))
                painter.drawText(x, y, text)
                self.canvas.setPixmap(self.pixmap)

    def toggle_fill(self, checked):
        self.fill_shapes = checked

    def select_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_fill_color = color

    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PDF", "", "PDF Files (*.pdf)")
        if file_path:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.pixmap.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.pixmap.rect())
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()

    def export_svg(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as SVG", "", "SVG Files (*.svg)")
        if file_path:
            generator = QSvgGenerator()
            generator.setFileName(file_path)
            generator.setSize(self.pixmap.size())
            generator.setViewBox(self.pixmap.rect())
            painter = QPainter(generator)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.pixmap)
        QMessageBox.information(self, "Clipboard", "Image copied to clipboard.")

    def crop_image(self):
        x, ok1 = QInputDialog.getInt(self, "Crop", "X:", 0, 0, self.pixmap.width())
        y, ok2 = QInputDialog.getInt(self, "Crop", "Y:", 0, 0, self.pixmap.height())
        w, ok3 = QInputDialog.getInt(self, "Crop", "Width:", self.pixmap.width(), 1, self.pixmap.width())
        h, ok4 = QInputDialog.getInt(self, "Crop", "Height:", self.pixmap.height(), 1, self.pixmap.height())
        if ok1 and ok2 and ok3 and ok4:
            self.undo_stack.append(self.pixmap.copy())
            self.redo_stack.clear()
            self.pixmap = self.pixmap.copy(x, y, w, h)
            self.canvas.setPixmap(self.pixmap)

    def resize_image(self):
        w, ok1 = QInputDialog.getInt(self, "Resize", "Width:", self.pixmap.width(), 1, 4096)
        h, ok2 = QInputDialog.getInt(self, "Resize", "Height:", self.pixmap.height(), 1, 4096)
        if ok1 and ok2:
            self.undo_stack.append(self.pixmap.copy())
            self.redo_stack.clear()
            self.pixmap = self.pixmap.scaled(w, h)
            self.canvas.setPixmap(self.pixmap)

    def rotate_image(self):
        angle, ok = QInputDialog.getInt(self, "Rotate", "Angle (degrees):", 90, -360, 360)
        if ok:
            self.undo_stack.append(self.pixmap.copy())
            self.redo_stack.clear()
            transform = QTransform().rotate(angle)
            self.pixmap = self.pixmap.transformed(transform)
            self.canvas.setPixmap(self.pixmap)

    def show_about(self):
        QMessageBox.about(self, "About Franpaint", "Franpaint v3.3.35\nA simple paint program for FranchukOS.\n Copyright (c) 2025 the FranchukOS Project Authors.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Franpaint()
    window.show()
    sys.exit(app.exec_())
