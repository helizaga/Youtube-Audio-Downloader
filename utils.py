import os
import librosa
import numpy as np
import soundfile as sf
import io
from pydub import AudioSegment



def get_file_path(stream, output_path):
    return os.path.join(output_path, stream.default_filename)

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

