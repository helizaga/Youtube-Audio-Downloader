import sys
from PyQt6.QtWidgets import QApplication


from components import YoutubeAudioDownloader

# Constants
APP_GEOMETRY = (100, 100, 400, 150)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YoutubeAudioDownloader()
    window.setWindowTitle("YouTube Audio Downloader")
    window.setGeometry(*APP_GEOMETRY)
    window.show()
    sys.exit(app.exec())