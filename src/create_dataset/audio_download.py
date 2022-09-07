import argparse
from yt_dlp import YoutubeDL

AUDIO_EXTENSION = 'wav'
FILE_TITLE = '%(title)s'
FILE_EXTENSION = '%(ext)s'


def download_audio(url, output_path, output_title=''):
    # Strip redundant slashes and add file template
    output_path_list = [p for p in output_path.split('/') if p]
    file_template = f'{output_title if output_title else FILE_TITLE}.{FILE_EXTENSION}'
    output_path_list.append(file_template)
    output_template = '/'.join(output_path_list)

    ydl_opts = {
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': AUDIO_EXTENSION,
        }]}

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Copy info dict and change video extension to audio extension
        info_with_audio_extension = dict(info)
        info_with_audio_extension['ext'] = AUDIO_EXTENSION
        return ydl.prepare_filename(info_with_audio_extension), info_with_audio_extension


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and extract audio from videos")
    parser.add_argument("-u", "--urls", nargs="+", help="URLs to download from", default=[])
    parser.add_argument("-o", "--output", help="Directory to write downloads to")
    args = parser.parse_args()

    for u in args.urls:
        f = download_audio(u, args.output)
        print("Downloaded {} to {}".format(u, f))
