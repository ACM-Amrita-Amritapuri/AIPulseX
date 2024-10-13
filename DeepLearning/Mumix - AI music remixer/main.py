import os
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import librosa
import soundfile as sf
import matplotlib.pyplot as plt

def separate_sources(input_file, output_directory):

    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_file, output_directory)
    print(f"Separation complete. Files saved to {output_directory}")

def change_tempo(input_file, output_file, tempo_factor=1.25):

    y, sr = librosa.load(input_file)
    y_fast = librosa.effects.time_stretch(y, tempo_factor)
    sf.write(output_file, y_fast, sr)
    print(f"Tempo changed by a factor of {tempo_factor}. Saved to {output_file}")

def combine_tracks(vocals_file, accompaniment_file, output_file):

    vocals, sr1 = librosa.load(vocals_file, sr=None)
    accompaniment, sr2 = librosa.load(accompaniment_file, sr=None)

    if sr1 != sr2:
        raise ValueError("Sample rates of vocals and accompaniment do not match.")

    min_length = min(len(vocals), len(accompaniment))
    vocals = vocals[:min_length]
    accompaniment = accompaniment[:min_length]

    accompaniment = accompaniment * 0.7 
    remixed = vocals + accompaniment


    remixed = remixed / max(abs(remixed))

    sf.write(output_file, remixed, sr1)
    print(f"Remixed track saved to {output_file}")

def plot_waveform(audio_file, title="Waveform"):

    y, sr = librosa.load(audio_file, sr=None)
    plt.figure(figsize=(14, 5))
    librosa.display.waveshow(y, sr=sr)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.show()

if __name__ == "__main__":
    input_song = 'input_song.mp3'
    separation_output = 'separated'
    vocals = os.path.join(separation_output, 'input_song', 'vocals.wav')
    accompaniment = os.path.join(separation_output, 'input_song', 'accompaniment.wav')
    remixed_song = 'remixed_song.wav'
    remixed_song_tempo = 'remixed_song_tempo.wav'

    separate_sources(input_song, separation_output)

    change_tempo(accompaniment, 'accompaniment_fast.wav', tempo_factor=1.25)

    combine_tracks(vocals, 'accompaniment_fast.wav', remixed_song_tempo)

    print("Music remixing complete!")
