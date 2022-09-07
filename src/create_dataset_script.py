import argparse
import os.path
import uuid
import subprocess

from src.create_dataset.audio_download import download_audio
from src.create_dataset.mel_spectrogram import create_mel_spectrogram
from src.create_dataset.textgrid_to_xml import convert_textgrid_to_xml

SPECTROGRAM_FILE_EXTENSION = 'png'


def create_dataset_directory(dataset_directory):
    if not os.path.isdir(dataset_directory):
        os.mkdir(dataset_directory)

    for sub_directory in ['train', 'validation']:
        sub_directory_path = os.path.join(dataset_directory, sub_directory)
        if not os.path.isdir(sub_directory_path):
            os.mkdir(sub_directory_path)

        for sub_sub_directory in ['annotations', 'images']:
            sub_sub_directory_path = os.path.join(sub_directory_path, sub_sub_directory)
            if not os.path.isdir(sub_sub_directory_path):
                os.mkdir(sub_sub_directory_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an annotated dataset for training")
    parser.add_argument("-m", "--mode", help="Type of data to create", choices=['train', 'validation'], required=True)
    parser.add_argument("-u", "--urls", nargs="+",
                        help="URLs to use as input for training. Takes precedence over urls-file", default=[])
    parser.add_argument("-f", "--urls-file", help="File to read URLs from. Each URL on a separate line", default='')
    parser.add_argument("-d", "--dataset-directory", help="Directory to write dataset to", required=True)
    args = parser.parse_args()

    if args.urls:
        urls = args.urls
    elif args.urls_file:
        with open(args.urls_file, 'r') as log_file:
            urls = log_file.read().splitlines()
    else:
        raise Exception("No URLs provided")

    mode = args.mode

    create_dataset_directory(args.dataset_directory)

    with open('../dataset/log.csv', 'r') as log_file:
        log_file_empty = log_file.read() == ''

    with open('../dataset/log.csv', 'a+') as log_file:
        if log_file_empty:
            # Write CSV header
            log_file.write('mode,uuid,url,duration(s)\n')

        # For every url
        for url in urls:
            if url.startswith('#'):
                print(f'Skipping commented out url: {url}')
                continue

            datum_uuid = str(uuid.uuid4())

            # Download audio
            audio_path, audio_info = download_audio(url, '../assets', datum_uuid)
            print("Downloaded {} to {}".format(url, audio_path))

            # Annotate textgrid
            textgrid_path = f'../assets/{datum_uuid}.TextGrid'
            i = 0
            # If the TextGrid file wasn't created correctly, try again
            while not os.path.isfile(textgrid_path):
                if i in range(1, 4):
                    print(f"Textgrid file {textgrid_path} was not found. Trying again.")
                elif i > 4:
                    raise f"Textgrid file {textgrid_path} was not found 5 times in a row."
                subprocess.run(['praat', '--open', '--hide-picture', audio_path], capture_output=True, cwd='../assets')
                i += 1

            # Extract spectrogram
            spectrogram_path = f'../assets/{datum_uuid}.{SPECTROGRAM_FILE_EXTENSION}'
            create_mel_spectrogram(audio_path, spectrogram_path)
            print(f"Created spectrogram as {spectrogram_path}")

            # Generate xml
            xml_path = f'../assets/{datum_uuid}.xml'
            convert_textgrid_to_xml(textgrid_path, spectrogram_path, xml_path)

            # Put into dataset folders
            xml_destination = ''
            spectrogram_destination = ''
            if mode == "train":
                xml_destination = os.path.join(args.dataset_directory, 'train/annotations', f'{datum_uuid}.xml')
                spectrogram_destination = os.path.join(args.dataset_directory, 'train/images',
                                                       f'{datum_uuid}.{SPECTROGRAM_FILE_EXTENSION}')
            elif mode == "validation":
                xml_destination = os.path.join(args.dataset_directory, 'validation/annotations', f'{datum_uuid}.xml')
                spectrogram_destination = os.path.join(args.dataset_directory, 'validation/images',
                                                       f'{datum_uuid}.{SPECTROGRAM_FILE_EXTENSION}')
            print(f"Moving {xml_path} to {xml_destination}")
            print(f"Moving {spectrogram_path} to {spectrogram_destination}")
            # TODO: Add keep-artifacts option
            os.rename(xml_path, xml_destination)
            os.rename(spectrogram_path, spectrogram_destination)
            os.remove(audio_path)
            os.remove(textgrid_path)

            log_file.write(f'{mode},{datum_uuid},{url},{audio_info["duration"]}\n')
