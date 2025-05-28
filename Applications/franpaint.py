# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QColorDialog,
    QFileDialog, QLabel, QComboBox, QMessageBox, QInputDialog, QMenu, QClipboard
)
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QMouseEvent, QFont, QImage, QTransform
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtPrintSupport import QPrinter
import sys


class Franpaint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Franpaint v3.2.7")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = QLabel()
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

        self.fill_shapes = False  # For fill option
        self.current_fill_color = Qt.white  # Default fill color

        self.init_toolbar()

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

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)

        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_image)
        toolbar.addAction(load_action)

        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.redo)
        toolbar.addAction(redo_action)

        fill_action = QAction("Fill Shapes", self)
        fill_action.setCheckable(True)
        fill_action.toggled.connect(self.toggle_fill)
        toolbar.addAction(fill_action)

        fill_color_action = QAction("Fill Color", self)
        fill_color_action.triggered.connect(self.select_fill_color)
        toolbar.addAction(fill_color_action)

        export_pdf_action = QAction("Export PDF", self)
        export_pdf_action.triggered.connect(self.export_pdf)
        toolbar.addAction(export_pdf_action)

        export_svg_action = QAction("Export SVG", self)
        export_svg_action.triggered.connect(self.export_svg)
        toolbar.addAction(export_svg_action)

        copy_clipboard_action = QAction("Copy to Clipboard", self)
        copy_clipboard_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_clipboard_action)

        crop_action = QAction("Crop", self)
        crop_action.triggered.connect(self.crop_image)
        toolbar.addAction(crop_action)

        resize_action = QAction("Resize", self)
        resize_action.triggered.connect(self.resize_image)
        toolbar.addAction(resize_action)

        rotate_action = QAction("Rotate", self)
        rotate_action.triggered.connect(self.rotate_image)
        toolbar.addAction(rotate_action)

        eyedropper_action = QAction("Eyedropper", self)
        eyedropper_action.triggered.connect(lambda: self.set_tool('eyedropper'))
        toolbar.addAction(eyedropper_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.undo_stack.append(self.pixmap.copy())
            self.redo_stack.clear()
            self.drawing = True
            self.last_point = event.pos()
            self.current_point = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing and self.current_tool == 'freehand':
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color, self.pen_width, self.pen_style)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.canvas.setPixmap(self.pixmap)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color, self.pen_width, self.pen_style)
            painter.setPen(pen)

            if self.current_tool == 'rectangle':
                rect = QRect(self.last_point, event.pos())
                if self.fill_shapes:
                    painter.fillRect(rect, self.current_fill_color)
                painter.drawRect(rect)
            elif self.current_tool == 'ellipse':
                rect = QRect(self.last_point, event.pos())
                if self.fill_shapes:
                    painter.setBrush(self.current_fill_color)
                else:
                    painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(rect)
            elif self.current_tool == 'eyedropper':
                img = self.pixmap.toImage()
                color = QColor(img.pixel(event.pos()))
                self.pen_color = color

            self.canvas.setPixmap(self.pixmap)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color

    def change_pen_width(self):
        self.pen_width = int(self.brush_size.currentText())

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
        QMessageBox.about(self, "About Franpaint", "Franpaint v3.2.7\nA simple paint program for FranchukOS.\n Copyright (c) 2025 the FranchukOS Project Authors and Bluegill Studios.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Franpaint()
    window.show()
    sys.exit(app.exec_())
