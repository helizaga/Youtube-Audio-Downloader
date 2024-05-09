from pytube import YouTube

from PyQt6.QtCore import QThread, pyqtSignal
from utils import get_file_path
import os

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
            print(f"Error in DownloadThread: {e}")  # Error handling
    def stop(self):
        self.is_cancelled = True
        self.terminate()
