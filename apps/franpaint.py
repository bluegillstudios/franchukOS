# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QColorDialog,
    QFileDialog, QLabel, QComboBox, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QMouseEvent, QFont
from PyQt5.QtCore import Qt, QPoint, QRect
import sys


class Franpaint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Franpaint v1.03")
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
                painter.drawRect(QRect(self.last_point, event.pos()))
            elif self.current_tool == 'ellipse':
                painter.drawEllipse(QRect(self.last_point, event.pos()))

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Franpaint()
    window.show()
    sys.exit(app.exec_())
