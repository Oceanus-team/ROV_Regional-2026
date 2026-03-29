import sys
import cv2
import datetime
import serial
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSizePolicy, QComboBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap


# --- FULL VIEW WINDOW ---
class FullViewWindow(QWidget):
    def __init__(self, camera_name="Camera"):
        super().__init__()
        self.setWindowTitle(f"{camera_name} - Full Control")
        self.resize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.image_label = QLabel("WAITING...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)


# --- CAMERA WIDGET ---
class CameraWidget(QWidget):
    def __init__(self, camera_index, name):
        super().__init__()
        self.capture = cv2.VideoCapture(camera_index)
        self.name = name

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("NO SIGNAL")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.btn = QPushButton("Open Full")
        layout.addWidget(self.btn)

        self.full = FullViewWindow(name)
        self.btn.clicked.connect(self.full.show)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(img))

            if self.full.isVisible():
                self.full.image_label.setPixmap(QPixmap.fromImage(img))


# --- SENSOR WIDGET ---
class SensorWidget(QFrame):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("DEPTH: --")
        layout.addWidget(self.label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(200)

    def update_data(self):
        depth = random.uniform(0, 10)
        self.label.setText(f"DEPTH: {depth:.2f} m")


# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ROV Control System")
        self.resize(1000, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # --- TOP BAR ---
        top_bar = QFrame()
        top_layout = QHBoxLayout()
        top_bar.setLayout(top_layout)

        # SERIAL
        try:
            self.arduino = serial.Serial("COM21", 9600, timeout=0.5)
        except:
            self.arduino = None

        # SAFETY BUTTON
        self.btn_safety = QPushButton("🛡 Safety")
        self.btn_safety.clicked.connect(self.safety)
        top_layout.addWidget(self.btn_safety)

        # 🚀 START FLOAT BUTTON
        self.btn_start = QPushButton("🚀 Start Float Task")
        self.btn_start.setStyleSheet("background:green;color:white;")
        self.btn_start.clicked.connect(self.start_float)
        top_layout.addWidget(self.btn_start)

        main_layout.addWidget(top_bar)

        # --- GRID ---
        grid = QGridLayout()
        main_layout.addLayout(grid)

        names = ["FRONT", "BACK", "DOWN", "LEFT", "RIGHT"]
        self.cams = []

        for i in range(5):
            cam = CameraWidget(i, names[i])
            self.cams.append(cam)
            grid.addWidget(cam, i // 2, i % 2)

        grid.addWidget(SensorWidget(), 2, 1)

    # --- BUTTON FUNCTIONS ---
    def safety(self):
        if self.arduino:
            self.arduino.write(b"SAFETY\n")
            print("Safety sent")

    def start_float(self):
        if self.arduino:
            self.arduino.write(b"S\n")
            print("🚀 Float Started")

            self.btn_start.setText("⏳ Running...")
            self.btn_start.setStyleSheet("background:orange;color:black;")
        else:
            print("Arduino not connected")


# --- RUN ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
