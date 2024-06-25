import sys
import subprocess
import cv2
import json
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QComboBox, QPushButton, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

def list_devices():
    result = subprocess.run(['ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'], stderr=subprocess.PIPE, text=True)
    devices = result.stderr.split('\n')
    video_devices = []

    for line in devices:
        if 'video' in line:
            video_devices.append(line)

    return video_devices

class DeviceSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle('Select your capturing device')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.video_devices = list_devices()

        self.video_label = QLabel('Select Video Device:', self)
        layout.addWidget(self.video_label)

        self.video_combo = QComboBox(self)
        self.video_combo.addItems(self.video_devices)
        layout.addWidget(self.video_combo)

        self.select_button = QPushButton('Select', self)
        self.select_button.clicked.connect(self.on_select)
        layout.addWidget(self.select_button)

        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(640, 480)
        layout.addWidget(self.preview_label)

        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_selection)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def on_select(self):
        device_name = self.video_combo.currentText()
        device_index = self.video_devices.index(device_name)
        QMessageBox.information(self, 'Selection', f'Video Device: {device_name}')

        if self.capture:
            self.capture.release()

        self.capture = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)

        if not self.capture.isOpened():
            QMessageBox.critical(self, 'Error', 'Failed to open video device.')
            return
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized_frame = cv2.resize(frame, (self.preview_label.width(), self.preview_label.height()), interpolation=cv2.INTER_AREA)
            image = QImage(resized_frame, resized_frame.shape[1], resized_frame.shape[0], resized_frame.strides[0], QImage.Format_RGB888)
            self.preview_label.setPixmap(QPixmap.fromImage(image))

    def save_selection(self):
        device_name = self.video_combo.currentText()
        config = {'selected_device': device_name}
        with open('config.json', 'w') as f:
            json.dump(config, f)
        QMessageBox.information(self, 'Saved', 'Device selection saved to config.json')

    def closeEvent(self, event):
        self.timer.stop()
        if self.capture:
            self.capture.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    selector = DeviceSelector()
    selector.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
