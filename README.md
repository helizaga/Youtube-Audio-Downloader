# YouTube Audio Downloader & Key Detector

This Python script downloads YouTube audio files and analyzes the music key using a PyQt6 GUI. The application uses `pytube` for downloading, `librosa` for key detection, and `soundfile` for audio file manipulation. It also provides a progress bar and information display for the download and analysis processes.

## Features

- Download YouTube audio files in mp3 format
- Analyze the music key of the downloaded audio
- Display download progress with a progress bar
- Display analysis progress with a progress bar
- Display the detected music key, file path, and video title
- Change the download location

## Dependencies

- PyQt6
- pytube
- librosa
- soundfile
- pydub
- ffmpeg

## Installation

Before running the script, make sure to install the required dependencies by running:

pip install PyQt6 pytube librosa soundfile pydub ffmpeg

## Usage

To use the application, simply run the script:

python youtube_audio_downloader.py

A graphical interface will open, allowing you to enter a YouTube URL, download the audio, and analyze the music key. The application also provides options to cancel the download and analysis processes or change the download location.

## Code Structure

The code is organized into the following main components:

- **detect_music_key**: a function that analyzes the music key of an audio file
- **DownloadThread**: a QThread subclass for downloading YouTube audio
- **AnalysisThread**: a QThread subclass for analyzing the music key
- **YoutubeAudioDownloader**: a QWidget subclass for the main PyQt6 application

The `__main__` block initializes the QApplication and displays the main window.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
