

from PyQt6.QtCore import QThread, pyqtSignal
from utils import detect_music_key

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
