from download_thread import DownloadThread
from analysis_thread import AnalysisThread
import os

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QHBoxLayout,
    QProgressBar,
)

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from download_thread import DownloadThread
from analysis_thread import AnalysisThread



from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QDrag

class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(False)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()
            url = QUrl.fromLocalFile(self.text())
            mimeData.setUrls([url])
            drag.setMimeData(mimeData)
            drag.exec(Qt.DropAction.CopyAction)

class DraggableTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['Title', 'File Path', 'Music Key'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        row = self.currentRow()
        if row > -1:
            drag = QDrag(self)
            mimeData = QMimeData()
            file_path = self.item(row, 1).text()  # Assuming the file path is in the second column
            mimeData.setUrls([QUrl.fromLocalFile(file_path)])
            drag.setMimeData(mimeData)
            drag.exec(Qt.DropAction.CopyAction)

class YoutubeAudioDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_row = -1  # Initialize current row to -1



    def init_ui(self):
        self.setWindowTitle("YouTube Audio Downloader")
        self.setGeometry(100, 100, 400, 150)

        layout = QVBoxLayout()
        self.create_widgets(layout)
        self.setLayout(layout)
        
    def create_widgets(self, layout):
        self.create_url_label(layout)
        self.create_url_input(layout)
        self.create_buttons(layout)
        self.create_download_progress_label(layout)
        self.create_download_progress_bar(layout)
        self.create_analysis_progress_label(layout)
        self.create_analysis_progress_bar(layout)
        self.create_status_label(layout)
        self.create_music_key_label(layout)
        self.create_file_path_label(layout)
        self.create_video_title_label(layout)
        self.table = DraggableTableWidget()
        layout.addWidget(self.table)

        self.save_location = os.path.join(
            os.path.expanduser("~"), "Desktop", "saved_songs"
        )

    def create_download_progress_label(self, layout):
        self.download_progress_label = QLabel("Downloading: 0%")
        layout.addWidget(self.download_progress_label)

    def create_download_progress_bar(self, layout):
        self.download_progress_bar = QProgressBar()
        layout.addWidget(self.download_progress_bar)

    def create_analysis_progress_label(self, layout):
        self.analysis_progress_label = QLabel("Analyzing: 0%")
        layout.addWidget(self.analysis_progress_label)

    def create_analysis_progress_bar(self, layout):
        self.analysis_progress_bar = QProgressBar()
        layout.addWidget(self.analysis_progress_bar)

    def create_url_label(self, layout):
        self.url_label = QLabel("Enter YouTube URL:")
        layout.addWidget(self.url_label)

    def create_url_input(self, layout):
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

    def create_buttons(self, layout):
        button_layout = QHBoxLayout()

        self.create_download_button(button_layout)
        self.create_cancel_button(button_layout)
        self.create_change_location_button(button_layout)

        layout.addLayout(button_layout)

    def create_download_button(self, layout):
        self.download_button = QPushButton("Download Audio")
        self.download_button.clicked.connect(self.download_audio)
        layout.addWidget(self.download_button)

    def create_cancel_button(self, layout):
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)

    def create_change_location_button(self, layout):
        self.change_location_button = QPushButton("Change Save Location")
        self.change_location_button.clicked.connect(self.change_save_location)
        layout.addWidget(self.change_location_button)

    def create_progress_label(self, layout):
        self.progress_label = QLabel("0%")
        layout.addWidget(self.progress_label)

    def create_progress_bar(self, layout):
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

    def change_save_location(self):
        new_location = QFileDialog.getExistingDirectory(
            self, "Select Save Location", self.save_location
        )

        if new_location:
            self.save_location = new_location

    def create_status_label(self, layout):
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def create_music_key_label(self, layout):
        self.music_key_label = QLabel("")
        layout.addWidget(self.music_key_label)

    def create_file_path_label(self, layout):
        self.file_path_label = DraggableLabel("")
        layout.addWidget(self.file_path_label)

    def create_video_title_label(self, layout):
        self.video_title_label = QLabel("")
        layout.addWidget(self.video_title_label)

    def display_music_key(self, music_key):
        if self.current_row >= 0:
            self.table.setItem(self.current_row, 2, QTableWidgetItem(music_key))

    def display_file_path(self, file_path):
        if self.current_row >= 0:  # Check if the current row is valid
            self.table.setItem(self.current_row, 1, QTableWidgetItem(file_path))
            print(f"File path updated in row {self.current_row}: {file_path}")
        else:
            print("Invalid row index, cannot update file path in the table.")
            
    def display_video_title(self, title):
        if self.current_row >= 0:
            self.table.setItem(self.current_row, 0, QTableWidgetItem(title))
        else:
            print("Invalid row index, cannot update video title in the table.")

    def display_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def download_audio(self):
        self.reset_output()
        url = self.url_input.text()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube URL.")
            return
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)

        self.current_row += 1
        self.table.insertRow(self.current_row)

        self.download_thread = DownloadThread(
            url, self.save_location
        )
        self.download_thread.download_progress_signal.connect(
            self.update_download_progress
        )
        self.download_thread.file_path_signal.connect(self.start_analysis)
        self.download_thread.video_title_signal.connect(self.display_video_title)
        self.download_thread.finished.connect(self.download_complete)
        self.download_thread.error_signal.connect(self.display_error)
        self.download_thread.start()

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.download_progress_bar.setValue(0)
        self.download_progress_label.setText("Downloading: 0%")
        self.analysis_progress_bar.setValue(0)
        self.analysis_progress_label.setText("Analyzing: 0%")
        self.status_label.setText("")

    def start_analysis(self, file_path):
        self.display_file_path(file_path)
        self.analysis_thread = AnalysisThread(file_path)
        self.analysis_thread.analysis_progress_signal.connect(
            self.update_analysis_progress
        )
        self.analysis_thread.music_key_signal.connect(self.display_music_key)
        self.analysis_thread.finished.connect(self.analysis_complete)
        self.analysis_thread.error_signal.connect(self.display_error)
        self.analysis_thread.start()
        self.analysis_progress_bar.setValue(0)
        self.analysis_progress_label.setText("Analyzing: 0%")
        self.status_label.setText("Analyzing...")


    def analysis_complete(self):
        if not self.analysis_thread.is_cancelled:
            self.status_label.setText("Analysis completed")
        else:
            self.status_label.setText("Analysis cancelled")
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def update_download_progress(self, progress):
        self.download_progress_bar.setValue(progress)
        self.download_progress_label.setText(f"Downloading: {progress}%")

    def update_analysis_progress(self, progress):
        self.analysis_progress_bar.setValue(progress)
        self.analysis_progress_label.setText(f"Analyzing: {progress}%")

    def reset_output(self):
        self.download_progress_label.setText("Downloading: 0%")
        self.download_progress_bar.setValue(0)
        self.analysis_progress_label.setText("Analyzing: 0%")
        self.analysis_progress_bar.setValue(0)
        self.status_label.setText("")
        self.music_key_label.setText("")
        self.file_path_label.setText("")
        self.video_title_label.setText("")

    def download_complete(self):
        if not self.download_thread.is_cancelled:
            self.status_label.setText("Download completed")
        else:
            self.status_label.setText("Download cancelled")
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait()
            self.status_label.setText("Download cancelled")
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.stop()
            self.analysis_thread.wait()
            self.status_label.setText("Analysis cancelled")
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
