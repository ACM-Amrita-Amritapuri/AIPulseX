# AI-Powered Music Remix Project

### AI Algorithm and Model

The AI model used in this project is based on **Spleeter**, which utilizes a **Convolutional Neural Network (CNN)**. This model was developed by **Deezer**, a music streaming service, and is specifically trained for the task of **source separation** in audio.

#### How the Model Works:

1. **Convolutional Neural Networks (CNNs)**:
   - Spleeter's AI relies on CNNs, a type of neural network that excels at processing patterns in data, such as images and audio spectrograms.
   - A **spectrogram** is a visual representation of the audio signal, showing how the sound frequencies vary over time. By converting audio into this format, the CNN can analyze and learn patterns that distinguish different sources (e.g., vocals vs. instruments).

2. **Training Process**:
   - The model was trained on a large dataset of audio tracks with known separate vocal and instrumental parts.
   - During training, it learns to identify and separate features that are unique to vocals (like certain frequency ranges) versus those found in instruments.
   - The training process involves adjusting the model to minimize errors in predicting the separated components, refining its ability to differentiate between sound sources.

3. **2-Stem Model**:
   - Spleeter offers various models, and in this project, the **2-stem model** is used. This model separates audio into two components: **vocals** and **accompaniment** (all the instruments combined).
   - More complex models (like 4-stem or 5-stem) can split audio into multiple elements such as drums, bass, piano, vocals, and other instruments separately.

4. **Inference**:
   - When you input a new song, the trained CNN model analyzes the audio, recognizes patterns, and separates it into distinct audio files (vocals and accompaniment).
   - The model is pre-trained, so you don't need to train it yourself. Instead, you can directly use it for efficient and accurate source separation.

This approach is an example of **deep learning applied to audio processing**, specifically leveraging the capabilities of CNNs to extract features from time-frequency representations (spectrograms) of audio. The result is a tool that can quickly and accurately separate vocals and music, even from complex tracks.

## How It Works

### AI Separation

The AI model behind this project is **pre-trained on a deep learning architecture** specifically designed to isolate different audio sources. Spleeter uses a convolutional neural network (CNN) that has been trained on thousands of music samples, enabling it to accurately separate vocals from background music. The model learns patterns in frequencies and rhythms that distinguish vocals from instruments. By using Spleeter, we can quickly and effectively separate a song into its core components without needing extensive training data or model development.

### Tempo Adjustment

To modify the music, we use the **Librosa library**, which allows us to change the speed (tempo) of the accompaniment. Librosa analyzes the waveforms and uses time-stretching algorithms to either speed up or slow down the track without altering the pitch, preserving the natural sound of the music.

### Recombining Tracks

After modifying the accompaniment, the remixed song is created by **mixing the adjusted accompaniment back with the original vocals**. By normalizing the volume and ensuring the tracks are aligned, the remix sounds smooth and cohesive. This step uses basic audio processing techniques to adjust volume levels and combine the two tracks into a single audio file.

---

## Prerequisites

- **Python** 3.6+
- **FFmpeg** (for audio processing)

---

## Installation

### Step 1: Install FFmpeg

- **Windows:** Download and add to PATH from [FFmpeg Download](https://ffmpeg.org/download.html).
- **macOS:** Use Homebrew: `brew install ffmpeg`
- **Linux:** Use APT: `sudo apt install ffmpeg`

### Step 2: Install Python Dependencies

Run the following command to install necessary libraries:
- `pip install spleeter librosa soundfile`

---

## Usage

### 1. Separating Sources

To start, use Spleeter to separate the input song into vocals and accompaniment. The following code separates sources and saves them in the 'separated' folder.

```python
def separate_sources(input_file, output_directory):

    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_file, output_directory)
    print(f"Separation complete. Files saved to {output_directory}")
```

### 2. Changing Tempo

Next, adjust the tempo of the accompaniment. The provided function loads the accompaniment audio, modifies its speed, and saves the output. You can change the `tempo_factor` to make the music faster or slower.

```python
def change_tempo(input_file, output_file, tempo_factor=1.25):

    y, sr = librosa.load(input_file)
    y_fast = librosa.effects.time_stretch(y, tempo_factor)
    sf.write(output_file, y_fast, sr)
    print(f"Tempo changed by a factor of {tempo_factor}. Saved to {output_file}")

```

### 3. Combining Tracks

Now, combine the processed accompaniment with the original vocals to create the remixed version. This function will mix the two tracks, normalize the volume, and save the final result.

```python
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
```