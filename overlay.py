import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint

console_colors = {
    "PS5": "blue",
    "XBOX SERIES X": "green",
    "XBOX SERIES S": "green",
    "PC": "white",
    "NINTENDO SWITCH": "red",
    "MOBILE": "yellow"
}
CONSOLE = "PS5"

class Field:
    def __init__(self, field_name, color, size, is_graph, value):
        self.field_name = field_name
        self.color = color
        self.size = size
        self.is_graph = is_graph
        self.value = value
        self.history = [] if is_graph else None
        self.height = 400 if is_graph else 20 

    def update_value(self, new_value):
        self.value = new_value
        if self.is_graph:
            self.history.append(new_value)
            if len(self.history) > 200:
                self.history.pop(0)

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.fields = {}

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.setGeometry(100, 100, 1920, 1080)
        self.show()


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    def add_field(self, field):
        self.fields[field.field_name] = field

    def update_field(self, field_name, new_value):
        if field_name in self.fields:
            self.fields[field_name].update_value(new_value)

    def update_display(self):
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        y_offset = 10
        for field in self.fields.values():
            #field name
            painter.setPen(QColor(field.color))
            painter.setFont(QFont("Consolas", field.size, QFont.Bold))
            metrics = QFontMetrics(QFont("Consolas", field.size, QFont.Bold))
            text_height = metrics.height()
            painter.drawText(QRect(10, y_offset, metrics.width(field.field_name + ": "), text_height), Qt.AlignLeft, field.field_name + ": ")

            #field value
            painter.setPen(QColor("white"))

            if field.is_graph:
                self.draw_graph(painter, field, y_offset + 10, text_height)
                y_offset += field.height + 10
            else:
                painter.drawText(QRect(10 + metrics.width(field.field_name + ": ") + 5, y_offset, metrics.width(field.value), text_height), Qt.AlignLeft, field.value)
                y_offset += text_height + 10

    def draw_graph(self, painter, field, y_offset, text_height):
        if not field.history:
            return
        max_value = max(field.history) if field.history else 1
        graph_height = field.height
        graph_width = 900
        base_x = 10
        base_y = y_offset + text_height + graph_height

        increment = 20 if max_value > 60 else 10
        for i in range(0, int(max_value) + increment, increment):
            line_y = base_y - (i / (max_value + increment)) * graph_height
            painter.setPen(QColor("white"))
            metrics = QFontMetrics(QFont("Consolas", field.size))
            size_max = metrics.width(f"{int(max_value + increment)} FPS") + 10
            painter.drawText(base_x, int(line_y) + int(metrics.height()/3) , f"{i} FPS")
            painter.drawLine(base_x + size_max, int(line_y), base_x + size_max + graph_width, int(line_y))
            

        painter.setPen(QColor("cyan"))
        for j in range(len(field.history) - 1):
            start_point = QPoint(int(base_x + size_max + (j * graph_width / len(field.history))), int(base_y - (field.history[j] / (max_value + increment)) * graph_height))
            end_point = QPoint(int(base_x + size_max + ((j + 1) * graph_width / len(field.history))), int(base_y - (field.history[j + 1] / (max_value + increment)) * graph_height))
            painter.drawLine(start_point, end_point)

    def make_fields(self):
        self.add_field(Field("Resolution", "orange", 20, False, "Initializing..."))
        self.add_field(Field("FPS", "orange", 20, False, "Initializing..."))
        self.add_field(Field("AVG FPS", "orange", 20, False, "Initializing..."))
        self.add_field(Field("1% Low FPS", "orange", 20, False, "Initializing..."))
        graph = Field("FPS Graph", "orange", 20, True, 0)
        self.add_field(graph)

def create_overlay(video_capture):
    def setup_tray(app):
        tray_icon = QSystemTrayIcon(QIcon('icon.png'), app)
        menu = QMenu()
        exit_action = QAction("Exit")
        exit_action.triggered.connect(app.quit)
        menu.addAction(exit_action)

        tray_icon.setContextMenu(menu)
        tray_icon.show()

    app = QApplication(sys.argv)
    setup_tray(app)
    overlay = Overlay()
    overlay.make_fields()

    def update_fields():
        overlay.update_field("Resolution", video_capture.frame_deque[-1]["resolution"])
        overlay.update_field("FPS", video_capture.frame_deque[-1]["frame_rate"])
        overlay.update_field("AVG FPS", video_capture.frame_deque[-1]["avg_fps"])
        overlay.update_field("1% Low FPS", video_capture.frame_deque[-1]["low_1_fps"])
        overlay.update_field("FPS Graph", float(video_capture.frame_deque[-1]["frame_rate"]))

    timer = QTimer()
    timer.timeout.connect(update_fields)
    timer.start(1000) 

    sys.exit(app.exec_())





