from pytube import YouTube

from PyQt6.QtCore import QThread, pyqtSignal
from utils import get_file_path
import os

class DownloadThread(QThread):
    download_progress_signal = pyqtSignal(int)
    file_path_signal = pyqtSignal(str)
    video_title_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.is_cancelled = False

    def run(self):
        try:
            yt = YouTube(self.url, on_progress_callback=self._emit_download_progress)
            audio_stream = yt.streams.filter(only_audio=True).first()
            file_path = get_file_path(audio_stream, self.output_path)
            print(f"Attempting to download to: {file_path}")  # Debugging

            if not os.path.exists(file_path):
                file_path = audio_stream.download(output_path=self.output_path)
                print(f"Downloaded to: {file_path}")  # Debugging
            else:
                print("File already exists. Skipping download.")

            self.download_progress_signal.emit(100)
            self.msleep(100)
            self.file_path_signal.emit(file_path)
            self.video_title_signal.emit(audio_stream.title)

        except Exception as e:
            self.error_signal.emit(f"Error in DownloadThread: {e}")

    def _emit_download_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        progress_percentage = int((bytes_downloaded / total_size) * 100)
        self.download_progress_signal.emit(progress_percentage)

    def stop(self):
        self.is_cancelled = True
        while self.isRunning():
            self.msleep(10)
