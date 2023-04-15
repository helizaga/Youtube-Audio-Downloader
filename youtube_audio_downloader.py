import sys
import os
from pytube import YouTube
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QFileDialog, QHBoxLayout, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, url, output_path, progress_callback):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.is_cancelled = False
        self.progress_callback = progress_callback

    def run(self):
        try:
            yt = YouTube(self.url, on_progress_callback=self.progress_callback)
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(output_path=self.output_path)
        except Exception as e:
            print(f"Error: {e}")

    def stop(self):
        self.is_cancelled = True
        self.terminate()


class YoutubeAudioDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.download_thread = None

    def init_ui(self):
        self.setWindowTitle('YouTube Audio Downloader')
        self.setGeometry(100, 100, 400, 150)

        layout = QVBoxLayout()
        self.create_widgets(layout)
        self.setLayout(layout)

    def create_widgets(self, layout):
        self.create_url_label(layout)
        self.create_url_input(layout)
        self.create_buttons(layout)
        self.create_progress_label(layout)
        self.create_progress_bar(layout)

        self.save_location = os.path.join(
            os.path.expanduser('~'), 'Desktop', 'saved songs')

    def create_url_label(self, layout):
        self.url_label = QLabel('Enter YouTube URL:')
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
        self.download_button = QPushButton('Download Audio')
        self.download_button.clicked.connect(self.download_audio)
        layout.addWidget(self.download_button)

    def create_cancel_button(self, layout):
        self.cancel_button = QPushButton('Cancel Download')
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)

    def create_change_location_button(self, layout):
        self.change_location_button = QPushButton('Change Save Location')
        self.change_location_button.clicked.connect(self.change_save_location)
        layout.addWidget(self.change_location_button)

    def create_progress_label(self, layout):
        self.progress_label = QLabel('0%')
        layout.addWidget(self.progress_label)

    def create_progress_bar(self, layout):
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

    def change_save_location(self):
        new_location = QFileDialog.getExistingDirectory(
            self, 'Select Save Location', self.save_location)

        if new_location:
            self.save_location = new_location

    def download_audio(self):
        url = self.url_input.text()

        if not url:
            QMessageBox.warning(self, 'Warning', 'Please enter a YouTube URL.')
            return
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)

        self.download_thread = DownloadThread(
            url, self.save_location, self.pyqt_progress)
        self.download_thread.progress_signal.connect(
            self.progress_bar.setValue)
        self.download_thread.finished.connect(self.download_complete)
        self.download_thread.start()

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

    def pyqt_progress(self, stream, chunk, bytes_remaining):
        progress = int((1 - bytes_remaining / stream.filesize) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f'{progress}%')

    def download_complete(self):
        if not self.download_thread.is_cancelled:
            QMessageBox.information(
                self, 'Download Complete', 'Download completed')
        else:
            QMessageBox.information(
                self, 'Download Cancelled', 'Download cancelled')
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait()
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YoutubeAudioDownloader()
    window.show()
    sys.exit(app.exec())
