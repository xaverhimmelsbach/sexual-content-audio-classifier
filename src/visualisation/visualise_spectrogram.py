import argparse
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Visualise spectrograms")
    parser.add_argument('-f', '--file', help='Audio file to create spectrogram from', required=True)
    args = parser.parse_args()

    samples, sample_rate = librosa.load(args.file)
    samples_fourier_transformed = librosa.stft(samples)
    samples_db = librosa.amplitude_to_db(np.abs(samples_fourier_transformed), ref=np.max)

    # fig, ax = plt.subplots()
    # img = librosa.display.specshow(S_db, x_axis='s', y_axis='linear', ax=ax)
    # fig.colorbar(img, ax=ax, format="%+2.f dB")

    figure, ax = plt.subplots()  # (figsize=(10, 1), dpi=200, frameon=False)
    # ax.set_axis_off()
    mel_spectrogram = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
    mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
    image = librosa.display.specshow(mel_spectrogram_db, y_axis='mel', x_axis='s', ax=ax)
    # fig.colorbar(img, ax=ax, format="%+2.f dB")

    plt.show()  # (aspect='auto')
