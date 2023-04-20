import sys
import os
from pytube import YouTube
from PyQt6.QtWidgets import (
    QApplication,
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
from PyQt6.QtCore import QThread, pyqtSignal

import librosa
import numpy as np
import soundfile as sf
import io
from pydub import AudioSegment


def detect_music_key(file_path, progress_callback=None):
    if progress_callback:
        progress_callback(10)  # Emit 10% progress after starting analysis

    audio_segment = AudioSegment.from_file(file_path, format="mp4")
    audio_data = audio_segment.export(format="wav")

    with io.BytesIO(audio_data.read()) as buffer:
        buffer.seek(0)
        y, sr = sf.read(buffer, dtype="float32")
        y = librosa.to_mono(y.T)

    if progress_callback:
        progress_callback(30)  # Emit 30% progress after loading audio data

    chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr, bins_per_octave=24)

    if progress_callback:
        progress_callback(50)  # Emit 50% progress after calculating chroma_cqt

    chroma_vals = np.sum(chroma_cqt, axis=1)
    pitches = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    keyfreqs = {pitches[i]: chroma_vals[i] for i in range(12)}

    maj_profile = [
        6.35,
        2.23,
        3.48,
        2.33,
        4.38,
        4.09,
        2.52,
        5.19,
        2.39,
        3.66,
        2.29,
        2.88,
    ]
    min_profile = [
        6.33,
        2.68,
        3.52,
        5.38,
        2.60,
        3.53,
        2.54,
        4.75,
        3.98,
        2.69,
        3.34,
        3.17,
    ]

    maj_key_corrs = []
    min_key_corrs = []
    for i in range(12):
        key_test = [keyfreqs.get(pitches[(i + m) % 12]) for m in range(12)]
        maj_key_corrs.append(round(np.corrcoef(maj_profile, key_test)[1, 0], 3))
        min_key_corrs.append(round(np.corrcoef(min_profile, key_test)[1, 0], 3))

    if progress_callback:
        progress_callback(70)  # Emit 70% progress after calculating correlations

    keys = [pitches[i] + " major" for i in range(12)] + [
        pitches[i] + " minor" for i in range(12)
    ]
    key_dict = {
        **{keys[i]: maj_key_corrs[i] for i in range(12)},
        **{keys[i + 12]: min_key_corrs[i] for i in range(12)},
    }

    detected_key = max(key_dict, key=key_dict.get)

    if progress_callback:
        progress_callback(100)  # Emit 100% progress after detecting key

    return detected_key


def get_file_path(stream, output_path):
    return os.path.join(output_path, stream.default_filename)


class DownloadThread(QThread):
    download_progress_signal = pyqtSignal(int)
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

            self.download_progress_signal.emit(100)
            self.msleep(100)
            self.file_path_signal.emit(file_path)
            self.video_title_signal.emit(audio_stream.title)

        except KeyError as e:
            if "streamingData" in str(e):
                print("Error: streamingData not found. Retrying...")
                self.run()  # Retry
                return
            else:
                print(f"Error: {e}")
                return

    def stop(self):
        self.is_cancelled = True
        self.terminate()


class AnalysisThread(QThread):
    analysis_progress_signal = pyqtSignal(int)
    music_key_signal = pyqtSignal(str)
    video_title_signal = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.is_cancelled = False

    def run(self):
        try:
            music_key = detect_music_key(
                self.file_path,
                lambda progress: self.analysis_progress_signal.emit(progress),
            )
            self.msleep(100)
            self.music_key_signal.emit(music_key)

        except Exception as e:
            print(f"Error: {e}")
            return

    def stop(self):
        self.is_cancelled = True
        self.terminate()


class YoutubeAudioDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.download_thread = None

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
        self.file_path_label = QLabel("")
        layout.addWidget(self.file_path_label)

    def create_video_title_label(self, layout):
        self.video_title_label = QLabel("")
        layout.addWidget(self.video_title_label)

    def display_music_key(self, music_key):
        self.music_key_label.setText(f"Music key: {music_key}")

    def display_file_path(self, file_path):
        self.file_path_label.setText(f"Saved to: {file_path}")

    def display_video_title(self, title):
        self.video_title_label.setText(f"Title: {title}")

    def download_audio(self):
        self.reset_output()
        url = self.url_input.text()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube URL.")
            return
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)

        self.download_thread = DownloadThread(
            url, self.save_location, self.pyqt_progress
        )
        self.analysis_thread = AnalysisThread(None)
        self.download_thread.download_progress_signal.connect(
            self.update_download_progress
        )
        self.download_thread.file_path_signal.connect(self.start_analysis)
        self.download_thread.video_title_signal.connect(self.display_video_title)
        self.download_thread.finished.connect(self.download_complete)
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
        self.analysis_thread.file_path = file_path
        self.analysis_thread.analysis_progress_signal.connect(
            self.update_analysis_progress
        )
        self.analysis_thread.music_key_signal.connect(self.display_music_key)
        self.analysis_thread.video_title_signal.connect(self.display_video_title)
        self.analysis_thread.finished.connect(self.analysis_complete)
        self.analysis_thread.start()
        self.analysis_progress_bar.setValue(0)
        self.analysis_progress_label.setText("Analyzing: 0%")
        self.status_label.setText("")

    def analysis_complete(self):
        if not self.analysis_thread.is_cancelled:
            self.status_label.setText("Analysis completed")
        else:
            self.status_label.setText("Analysis cancelled")
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def pyqt_progress(self, stream, chunk, bytes_remaining):
        progress = int((1 - bytes_remaining / stream.filesize) * 100)
        self.download_progress_bar.setValue(progress)
        self.download_progress_label.setText(f"Downloading: {progress}%")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YoutubeAudioDownloader()
    window.show()
    sys.exit(app.exec())
