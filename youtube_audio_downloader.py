import sys
import os
from pytube import YouTube
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QFileDialog, QHBoxLayout, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal

import librosa
import numpy as np


def detect_music_key(file_path):
    y, sr = librosa.load(file_path)
    chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr, bins_per_octave=24)
    chroma_vals = np.sum(chroma_cqt, axis=1)
    pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    keyfreqs = {pitches[i]: chroma_vals[i] for i in range(12)}

    maj_profile = [6.35, 2.23, 3.48, 2.33, 4.38,
                   4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    min_profile = [6.33, 2.68, 3.52, 5.38, 2.60,
                   3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

    maj_key_corrs = []
    min_key_corrs = []
    for i in range(12):
        key_test = [keyfreqs.get(pitches[(i + m) % 12]) for m in range(12)]
        maj_key_corrs.append(
            round(np.corrcoef(maj_profile, key_test)[1, 0], 3))
        min_key_corrs.append(
            round(np.corrcoef(min_profile, key_test)[1, 0], 3))

    keys = [pitches[i] +
            ' major' for i in range(12)] + [pitches[i] + ' minor' for i in range(12)]
    key_dict = {**{keys[i]: maj_key_corrs[i]
                   for i in range(12)}, **{keys[i + 12]: min_key_corrs[i] for i in range(12)}}

    detected_key = max(key_dict, key=key_dict.get)
    return detected_key


def get_file_path(stream, output_path):
    file_name = stream.default_filename.replace(".mp4", ".mp3")
    return os.path.join(output_path, file_name)


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    music_key_signal = pyqtSignal(str)
    file_path_signal = pyqtSignal(str)
    video_title_signal = pyqtSignal(str)

    def __init__(self, url, output_path, progress_callback):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.is_cancelled = False
        self.progress_callback = progress_callback

    def run(self):
        try:
            yt = YouTube(self.url, on_progress_callback=self.progress_callback)
            yt.register_on_progress_callback(self.progress_callback)
            audio_stream = yt.streams.filter(only_audio=True).first()
            file_path = get_file_path(audio_stream, self.output_path)

            if not os.path.exists(file_path):
                file_path = audio_stream.download(output_path=self.output_path)
            else:
                print("File already exists. Skipping download.")

            music_key = detect_music_key(file_path)

            self.progress_signal.emit(100)
            self.msleep(100)
            self.music_key_signal.emit(music_key)
            self.file_path_signal.emit(file_path)
            self.video_title_signal.emit(yt.title)

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
        self.create_status_label(layout)
        self.create_music_key_label(layout)
        self.create_file_path_label(layout)
        self.create_video_title_label(layout)

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

    def create_status_label(self, layout):
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

    def create_music_key_label(self, layout):
        self.music_key_label = QLabel('')
        layout.addWidget(self.music_key_label)

    def create_file_path_label(self, layout):
        self.file_path_label = QLabel('')
        layout.addWidget(self.file_path_label)

    def create_video_title_label(self, layout):
        self.video_title_label = QLabel('')
        layout.addWidget(self.video_title_label)

    def display_music_key(self, music_key):
        self.music_key_label.setText(f'Music key: {music_key}')

    def display_file_path(self, file_path):
        self.file_path_label.setText(f'Saved to: {file_path}')

    def display_video_title(self, title):
        self.video_title_label.setText(f'Title: {title}')

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f'{progress}%')

    def download_audio(self):
        url = self.url_input.text()

        if not url:
            QMessageBox.warning(self, 'Warning', 'Please enter a YouTube URL.')
            return
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)

        self.download_thread = DownloadThread(
            url, self.save_location, self.pyqt_progress)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.music_key_signal.connect(self.display_music_key)
        self.download_thread.file_path_signal.connect(self.display_file_path)
        self.download_thread.video_title_signal.connect(
            self.display_video_title)
        self.download_thread.finished.connect(self.download_complete)
        self.download_thread.start()

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.progress_bar.setValue(0)
        self.progress_label.setText('0%')
        self.status_label.setText('')

    def pyqt_progress(self, stream, chunk, bytes_remaining):
        progress = int((1 - bytes_remaining / stream.filesize) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f'{progress}%')

    def download_complete(self):
        if not self.download_thread.is_cancelled:
            self.status_label.setText('Download completed')
        else:
            self.status_label.setText('Download cancelled')
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait()
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YoutubeAudioDownloader()
    window.show()
    sys.exit(app.exec())
