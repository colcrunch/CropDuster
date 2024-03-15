import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, 
    QSpacerItem, QSizePolicy, QDialog, QMessageBox, QStyle, QDialogButtonBox
)
from PIL import ImageQt, Image


class FrameWindow(QDialog):
    def __init__(self, image: QImage, save_location, parent_pos: tuple = (100,100)):
        super().__init__()

        POS_OFFSET = 40
        IMAGE_HEIGHT = 450
        x, y = parent_pos

        self.setWindowTitle("Frame Preview")
        self.setGeometry(x+POS_OFFSET, y+POS_OFFSET, 1100, 520)
        self.setWindowIcon(QIcon('./window_icon.png'))

        self.name_label = QLabel("Image Name:")
        self.name_box = QLineEdit()
        self.name_box.returnPressed.connect(self.save_images)

        self.save_button = QPushButton("Save")
        self.save_location = save_location
        self.save_button.clicked.connect(self.save_images)

        self.image = image

        """
        Full Frame
        """
        self.full_frame_label = QLabel("Full Frame:")

        self.frame = QLabel()
        self.frame_pix = QPixmap(image)
        self.frame.setPixmap(self.frame_pix)
        self.frame.setScaledContents(True)
        self.frame.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        frm_size = QSize(1920, 1080)
        frm_size.scale(1920, IMAGE_HEIGHT, Qt.KeepAspectRatio)
        self.frame.setFixedSize(frm_size)


        """
        Cropped Frame
        """

        self.cropped_label = QLabel("Cropped Image:")

        self.cropped_frame = QLabel()
        self.cropped_frame_image = self.cropped_image()
        self.cropped_pix = QPixmap(self.cropped_frame_image)
        self.cropped_frame.setPixmap(self.cropped_pix)
        self.cropped_frame.setScaledContents(True)
        size = QSize(480, 1029)
        size.scale(480, IMAGE_HEIGHT, Qt.KeepAspectRatio)
        self.cropped_frame.setFixedSize(size)

        """
        Layout
        """

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.name_label)
        top_layout.addWidget(self.name_box)
        top_layout.addWidget(self.save_button)

        full_frame_layout = QVBoxLayout()
        full_frame_layout.addWidget(self.full_frame_label, alignment=Qt.AlignmentFlag.AlignLeft)
        full_frame_layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignLeft)

        cropped_layout = QVBoxLayout()
        cropped_layout.addWidget(self.cropped_label, alignment=Qt.AlignmentFlag.AlignLeft)
        cropped_layout.addWidget(self.cropped_frame, alignment=Qt.AlignmentFlag.AlignLeft)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(full_frame_layout)
        bottom_layout.addSpacerItem(QSpacerItem(50, 1))
        bottom_layout.addLayout(cropped_layout)

        window_layout = QVBoxLayout()
        window_layout.addLayout(top_layout)
        window_layout.addLayout(bottom_layout)
        window_layout.addSpacerItem(QSpacerItem(1,1, vData=QSizePolicy.Policy.Expanding))

        self.setLayout(window_layout)
        self.setFixedSize(QSize(1100, 520))

    def cropped_image(self) -> QImage:
        p_image = ImageQt.fromqimage(self.image)
        width, height = self.image.size().toTuple()
        return p_image.crop((600, 51, width-831, height)).toqimage()
    
    def save_images(self):
        if self.name_box.text() == "":
            return
        
        name = self.name_box.text()
        if self.file_name_is_unique(name):
            self.image.save(f"{self.save_location}/{name}_full.jpg")
            self.cropped_frame_image.save(f"{self.save_location}/{name}_cropped.jpg")
            self.close()
        else:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning))
            box.setWindowTitle("File Name Taken")
            box.setText("The file name provided is already in use, please select a different name.")
            box.setDefaultButton(QMessageBox.StandardButton.Ok)
            box.exec()

    def file_name_is_unique(self, name):
        full = f"{self.save_location}/{name}_full.jpg"
        cropped = f"{self.save_location}/{name}_cropped.jpg"
        if os.path.exists(full) or os.path.exists(cropped):
            return False
        return True
