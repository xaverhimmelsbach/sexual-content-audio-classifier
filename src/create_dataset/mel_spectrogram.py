import librosa
import argparse
import numpy as np
import skimage.io


def parse_arguments():
    parser = argparse.ArgumentParser(description="Construct a mel spectrogram from a sound file")
    parser.add_argument("-i", "--input_file", help="Sound file to read")
    parser.add_argument("-o", "--output_file", help="Image file to write")
    args = parser.parse_args()

    return args.input_file, args.output_file


def scale_min_max(value, min_value, max_value):
    value_std = (value - min_value) / (max_value - min_value)
    value_scaled = value_std * (max_value - min_value) + min_value
    return value_scaled


def create_mel_spectrogram(input_file, output_file):
    # Load audio file
    time_series, sample_rate = librosa.load(input_file)

    # Calculate mel spectrogram
    # TODO: Put into separate file so these settings can also be used for inferring
    mel_spec = librosa.feature.melspectrogram(
        y=time_series,  # audio signal
        sr=sample_rate,  # sampling rate
        n_fft=2048,  # fft window size
        hop_length=512,  # Lower -> Higher horizontal resolution (1 = 'native')
        n_mels=128  # Higher -> Higher vertical resolution
    )
    mel_spec = librosa.power_to_db(mel_spec, ref=np.max)

    # Scale image to 0-255
    im = scale_min_max(mel_spec, 0, 255).astype(np.uint8)
    # Put low frequencies at the bottom of the image
    im = np.flip(im, axis=0)
    # Invert image so black pixels mean higher energy
    im = 255 - im

    # Write image
    skimage.io.imsave(output_file, im)


if __name__ == "__main__":
    input_file_argument, output_file_argument = parse_arguments()
    create_mel_spectrogram(input_file_argument, output_file_argument)
