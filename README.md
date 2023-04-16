# YouTube Audio Downloader

This program allows you to download audio from YouTube videos by providing the URL of the video. The audio is saved in the specified location on your computer.

## Features

- Download audio from YouTube videos
- Show download progress
- Change the save location for downloaded audio
- Cancel downloads in progress

## Dependencies

- **Python 3.6+**
- **PyQt6** (for the graphical user interface)
- **pytube** (for downloading YouTube videos)

To install the required dependencies, run the following command:

pip install PyQt6 pytube


## Usage

1. Run the script `python youtube_audio_downloader.py`.
2. Enter the YouTube URL in the provided input field.
3. Click **Download Audio** to start downloading the audio.
4. Optionally, you can change the save location for the downloaded audio by clicking the **Change Save Location** button.
5. During the download process, you can click the **Cancel Download** button to cancel the download.

## Example

```python
from youtube_audio_downloader import YoutubeAudioDownloader

app = QApplication(sys.argv)
window = YoutubeAudioDownloader()
window.show()
sys.exit(app.exec())
```

## Notes
- The downloaded audio will be in the .mp4 format, which is an audio format provided by the pytube API.
- This application is for educational purposes only. Please respect the rights of content creators and follow YouTube's Terms of Service.
