import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QFileDialog, QWidget, QComboBox, QMessageBox,
    QStatusBar, QSlider, QHBoxLayout, QScrollArea, QInputDialog, QMenuBar, QAction
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обработчик Изображений")
        self.setGeometry(100, 100, 1200, 800)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: white;") 

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("border: none;")  

        self.load_image_button = QPushButton("Загрузить Изображение", self)
        self.load_image_button.clicked.connect(self.load_image)

        self.capture_image_button = QPushButton("Сделать Фото", self)
        self.capture_image_button.clicked.connect(self.capture_image)

        self.channel_selector = QComboBox(self)
        self.channel_selector.addItems(["Исходное Изображение", "Красный Канал", "Зеленый Канал", "Синий Канал"])
        self.channel_selector.currentIndexChanged.connect(self.show_channel)

        self.negative_image_button = QPushButton("Показать Негативное Изображение", self)
        self.negative_image_button.clicked.connect(self.show_negative_image)

        self.rotate_image_button = QPushButton("Вращать Изображение", self)
        self.rotate_image_button.clicked.connect(self.rotate_image)

        self.draw_circle_button = QPushButton("Нарисовать Круг", self)
        self.draw_circle_button.clicked.connect(self.draw_circle)

        self.scaling_factor_slider = QSlider(Qt.Horizontal, self)
        self.scaling_factor_slider.setRange(1, 100)
        self.scaling_factor_slider.setValue(50) 
        self.scaling_factor_slider.setTickPosition(QSlider.TicksBelow)
        self.scaling_factor_slider.setTickInterval(10)
        self.scaling_factor_slider.setSingleStep(1)
        self.scaling_factor_slider.valueChanged.connect(self.update_scaling_factor)

        self.scaling_factor_label = QLabel(f"50%", self)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_image_button)
        button_layout.addWidget(self.capture_image_button)
        button_layout.addWidget(self.negative_image_button)
        button_layout.addWidget(self.rotate_image_button)
        button_layout.addWidget(self.draw_circle_button)

        channel_layout = QHBoxLayout()
        channel_layout.addWidget(self.channel_selector)

        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(QLabel("Масштаб:", self))
        scaling_layout.addWidget(self.scaling_factor_slider)
        scaling_layout.addWidget(self.scaling_factor_label)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(channel_layout)
        main_layout.addLayout(scaling_layout)

        main_layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        menubar = self.menuBar()
        edit_menu = menubar.addMenu('Правка')

        negative_action = QAction('Показать Негативное Изображение', self)
        negative_action.triggered.connect(self.show_negative_image)
        edit_menu.addAction(negative_action)

        rotate_action = QAction('Вращать Изображение', self)
        rotate_action.triggered.connect(self.rotate_image)
        edit_menu.addAction(rotate_action)

        draw_circle_action = QAction('Нарисовать Круг', self)
        draw_circle_action.triggered.connect(self.draw_circle)
        edit_menu.addAction(draw_circle_action)

        self.image = None
        self.original_image = None
        self.is_negative = False

        self.scaling_factor = 0.5

    def load_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть Файл Изображения", "", "Images (*.png *.jpg *.jpeg)",
                                                   options=options)
        if file_name:
            try:
                image = cv2.imread(file_name)
                if image is None:
                    raise ValueError("Не удалось прочитать файл изображения.")
                self.image = image
                self.original_image = self.image.copy()
                self.display_image(self.image)
                self.status_bar.showMessage("Изображение успешно загружено.", 5000)
                self.channel_selector.setCurrentIndex(0)
            except Exception as e:
                self.show_error(f"Не удалось загрузить изображение: {str(e)}")
        else:
            self.status_bar.showMessage("Загрузка изображения отменена.", 5000)

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.show_error("Невозможно получить доступ к камере.")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            self.show_error("Не удалось сделать фото.")
            return

        self.image = frame
        self.original_image = self.image.copy()
        self.display_image(self.image)
        self.status_bar.showMessage("Фото успешно сделано.", 5000)
        self.channel_selector.setCurrentIndex(0)

    def display_image(self, img):
        h, w, _ = img.shape
        new_w = int(w * self.scaling_factor)
        new_h = int(h * self.scaling_factor)
        resized_img = cv2.resize(img, (new_w, new_h))

        img_rgb = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))

        self.image_label.setFixedSize(new_w, new_h)

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.horizontalScrollBar().setValue(
            (self.scroll_area.horizontalScrollBar().maximum() - self.scroll_area.horizontalScrollBar().minimum()) // 2
        )
        self.scroll_area.verticalScrollBar().setValue(
            (self.scroll_area.verticalScrollBar().maximum() - self.scroll_area.verticalScrollBar().minimum()) // 2
        )

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.status_bar.showMessage("Изображение отображено.", 5000)

    def show_channel(self):
        if self.image is None:
            self.show_error("Изображение не загружено.")
            return

        channel = self.channel_selector.currentText()
        if channel == "Исходное Изображение":
            self.display_image(self.image)
        elif channel == "Красный Канал":
            channel_img = self.image.copy()
            channel_img[:, :, 0] = 0
            channel_img[:, :, 1] = 0
            self.display_image(channel_img)
        elif channel == "Зеленый Канал":
            channel_img = self.image.copy()
            channel_img[:, :, 0] = 0
            channel_img[:, :, 2] = 0
            self.display_image(channel_img)
        elif channel == "Синий Канал":
            channel_img = self.image.copy()
            channel_img[:, :, 1] = 0
            channel_img[:, :, 2] = 0
            self.display_image(channel_img)

        self.status_bar.showMessage(f"{channel} отображен.", 5000)

    def show_negative_image(self):
        if self.image is None:
            self.show_error("Изображение не загружено.")
            return

        if not self.is_negative:
            negative_image = cv2.bitwise_not(self.image)
            self.display_image(negative_image)
            self.is_negative = True
            self.status_bar.showMessage("Негативное изображение отображено.", 5000)
        else:
            self.display_image(self.original_image)
            self.is_negative = False
            self.status_bar.showMessage("Исходное изображение восстановлено.", 5000)

    def rotate_image(self):
        if self.image is None:
            self.show_error("Изображение не загружено")
            return

        angle, ok = QInputDialog.getDouble(self, 'Вращать Изображение', 'Введите угол в градусах:', 0, -360, 360, 1)
        if ok:
            (h, w) = self.image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(self.image, rotation_matrix, (w, h))
            self.display_image(rotated_image)
            self.status_bar.showMessage(f"Изображение повернуто на {angle} градусов.", 5000)

    def draw_circle(self):
        if self.image is None:
            self.show_error("Изображение не загружено.")
            return

        x, ok1 = QInputDialog.getInt(self, 'Нарисовать Круг', 'Введите координату x:', 0, 0, self.image.shape[1], 1)
        y, ok2 = QInputDialog.getInt(self, 'Нарисовать Круг', 'Введите координату y:', 0, 0, self.image.shape[0], 1)
        radius, ok3 = QInputDialog.getInt(self, 'Нарисовать Круг', 'Введите радиус круга:', 10, 1, 10000,
                                          1)  # Убираем ограничение радиуса

        if ok1 and ok2 and ok3:
            circle_image = self.image.copy()
            cv2.circle(circle_image, (x, y), radius, (0, 0, 255), 2)  # Рисуем круг красным цветом
            self.display_image(circle_image)
            self.status_bar.showMessage(f"Круг нарисован в ({x}, {y}) с радиусом {radius}.", 5000)

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.status_bar.showMessage(message, 5000)

    def update_scaling_factor(self, value):
        self.scaling_factor = value / 100.0
        self.scaling_factor_label.setText(f"{int(self.scaling_factor * 100)}%")
        if self.image is not None:
            self.display_image(self.image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec_())