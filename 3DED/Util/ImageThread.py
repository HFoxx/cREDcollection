from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage


class ImageThread(QThread):
    image_signal = pyqtSignal(QImage)
    request_photo_signal = pyqtSignal()

    def run(self):
        # 发出拍照请求
        self.request_photo_signal.emit()
