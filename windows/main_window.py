import glob, os
from PySide6.QtCore import Qt, QUrl, QSize, QSize, QFileSystemWatcher
from PySide6.QtGui import QKeyEvent, QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSlider, QFileDialog, QLabel,
    QVBoxLayout, QHBoxLayout, QLineEdit, QStyle, QSpacerItem, QSizePolicy,
    QFrame, QListView, QMessageBox
)
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink
from PySide6.QtMultimediaWidgets import QVideoWidget

from .image_window import FrameWindow
from .components.custom_button import CustomButton as CPushButton


class MainWindow(QMainWindow):
    def __init__(self, version, icon_path) -> None:
        super().__init__()
        self.icons = {
            "play": self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "pause": self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause),
            "stop": self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop),
            "capture": self.style().standardIcon(QStyle.StandardPixmap.SP_DialogNoButton)
        }

        self.setWindowTitle(f"CropDuster v{version}")
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowIcon(QIcon(icon_path))

        """
        Video Layout (LHS)
        """
        self.file_label = QLabel("Video File:")
        self.file_box = QLineEdit("Select \"Open File\"...")
        self.file_box.setReadOnly(True)

        self.open_button = CPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)

        self.sink = QVideoSink()
        self.video_player = QMediaPlayer(parent=None)
        self.video_player.setVideoSink(self.sink)
        self.video_player.positionChanged.connect(self.position_changed)
        self.video_player.durationChanged.connect(self.duration_changed)
        self.video_widget = QVideoWidget()

        self.start_button = CPushButton(icon=self.icons["play"])
        self.start_button.setFixedWidth(40)
        self.start_button.setIconSize(QSize(32,32))
        self.start_button.clicked.connect(self.play_pause_video)

        self.stop_button = CPushButton(icon=self.icons["stop"])
        self.stop_button.setFixedWidth(40)
        self.stop_button.setIconSize(QSize(32,32))
        self.stop_button.clicked.connect(self.stop_video)

        self.capture_button = CPushButton(icon=self.icons["capture"])
        self.capture_button.setFixedWidth(40)
        self.capture_button.setIconSize(QSize(32,32))
        self.capture_button.setToolTip("Capture the current frame.")
        self.capture_button.clicked.connect(self.capture_frame)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_box)
        file_layout.addWidget(self.open_button)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.slider)
        control_buttons = QHBoxLayout()
        control_buttons.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignLeft)
        control_buttons.addWidget(self.stop_button, alignment=Qt.AlignmentFlag.AlignLeft)
        control_buttons.addSpacerItem(QSpacerItem(1, 1, hData=QSizePolicy.Policy.Expanding))
        control_buttons.addWidget(self.capture_button, alignment=Qt.AlignmentFlag.AlignRight)
        control_layout.addLayout(control_buttons)

        video_layout = QVBoxLayout()
        video_layout.addLayout(file_layout)
        video_layout.addWidget(self.video_widget)
        video_layout.addLayout(control_layout)

        """
        Image Layout (RHS)
        """
        self.save_label = QLabel("Save Location:")
        self.location = None
        self.location_box = QLineEdit("Select \"Browse\" to set location...")
        self.location_box.setReadOnly(True)
        
        self.location_button = CPushButton("Browse")
        self.location_button.clicked.connect(self.set_save_location)

        self.watcher = QFileSystemWatcher()
        self.watcher.directoryChanged.connect(self.update_lists)

        self.full_frame_label = QLabel("Full Frames:")
        self.full_frame_list = QListView()
        self.full_frame_list.setViewMode(QListView.ViewMode.IconMode)
        self.full_frame_list.setModel(QStandardItemModel())
        self.full_frame_list.setUniformItemSizes(True)
        self.full_frame_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.full_frame_list.setIconSize(QSize(128, 128))

        self.crop_frame_label = QLabel("Cropped Frames:")
        self.crop_frame_list = QListView()
        self.crop_frame_list.setViewMode(QListView.ViewMode.IconMode)
        self.crop_frame_list.setModel(QStandardItemModel())
        self.crop_frame_list.setUniformItemSizes(True)
        self.crop_frame_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.crop_frame_list.setIconSize(QSize(128, 128))

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.save_label)
        location_layout.addWidget(self.location_box)
        location_layout.addWidget(self.location_button)

        image_layout = QVBoxLayout()
        image_layout.addLayout(location_layout)
        image_layout.addWidget(self.full_frame_label)
        image_layout.addWidget(self.full_frame_list)
        image_layout.addWidget(self.crop_frame_label)
        image_layout.addWidget(self.crop_frame_list)

        """
        Window Layout... all the contents of the window.
        """
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        window_layout = QHBoxLayout()
        window_layout.addLayout(video_layout,2)
        window_layout.addWidget(line)
        window_layout.addLayout(image_layout,1)

        container = QWidget()
        container.setLayout(window_layout)
        self.setCentralWidget(container)
        container.setMinimumSize(QSize(1280, 720))

    def play_pause_video(self):
        state = self.video_player.playbackState()
        if not self.video_player.hasVideo():
            return
        if state in (QMediaPlayer.PlaybackState.PausedState, QMediaPlayer.PlaybackState.StoppedState):
            self.play_video()
        else:
            self.pause_video()
    
    def play_video(self):
        self.video_player.play()
        self.start_button.setIcon(self.icons["pause"])

    def pause_video(self):
        self.video_player.pause()
        self.start_button.setIcon(self.icons["play"])

    def stop_video(self):
        self.video_player.stop()
        self.start_button.setIcon(self.icons["play"])

    def set_position(self, position):
        self.video_player.setPosition(position)

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key.Key_Space:
            self.play_pause_video()
        elif key == Qt.Key.Key_Period:
            if self.video_player.playbackState() == self.video_player.PlaybackState.PausedState:
                self.video_player.play()
                self.video_player.setPosition(self.video_player.position()+1000)
                self.video_player.pause()
            else:
                event.ignore()
        elif key == Qt.Key.Key_C:
            self.capture_frame()
    
    def open_file(self):
        self.file = QFileDialog.getOpenFileName( 
            filter="Video Files (*.mp4 *.mov *.mkv *.wmv)"
        )
        if self.file[0] == "":
            return
        self.file_box.setText(self.file[0])
        self.video_player.setSource(QUrl.fromLocalFile(self.file[0]))
        self.video_player.setVideoOutput(self.video_widget)
    
    def set_save_location(self):
        self.location = QFileDialog.getExistingDirectory()
        if self.location == "":
            return
        self.location_box.setText(self.location)
        self.watcher.addPath(self.location)
        self.update_lists()

    def show_save_error(self):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning))
        box.setWindowTitle("No Save Location")
        box.setText("Please select a location to save your images to and try again.")
        box.setDefaultButton(QMessageBox.StandardButton.Ok)
        box.exec()

    def capture_frame(self):
        if (not self.video_player.hasVideo 
            or self.video_player.playbackState() == QMediaPlayer.PlaybackState.StoppedState):
            return
        
        if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause_video()
        
        if self.location is None:
            return self.show_save_error()

        frame = self.video_player.videoSink().videoFrame().toImage()
        FrameWindow(frame, self.location_box.text()).exec()

    def update_lists(self):
        self.full_frame_list.model().removeRows(0, self.full_frame_list.model().rowCount())
        self.crop_frame_list.model().removeRows(0, self.crop_frame_list.model().rowCount())
        for file in glob.glob(f"{self.location}/*.jpg"):
            file_name = os.path.basename(file)
            if file_name.endswith("_cropped.jpg"):
                self.crop_frame_list.model().appendRow(QStandardItem(QIcon(file), file_name))
            elif file_name.endswith("_full.jpg"):
                self.full_frame_list.model().appendRow(QStandardItem(QIcon(file), file_name))
