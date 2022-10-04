import argparse
import uuid
import csv
import wave
import contextlib
from PIL import Image
from imageai.Detection.Custom import CustomObjectDetection
from src.create_dataset import mel_spectrogram
from src.config import DATASET_DIR, ASSETS_DIR, MIN_PREDICTION_PROBABILITY

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect objects in images")
    parser.add_argument("-f", "--file", help="Audio file to detect in", required=True)
    parser.add_argument("-m", "--model", help="Model to use", required=True)
    args = parser.parse_args()

    file_uuid = str(uuid.uuid4())

    # Create spectrogram
    mel_spectrogram.create_mel_spectrogram(args.file, f"{ASSETS_DIR}/{file_uuid}.png")

    # Get duration from audio file
    with contextlib.closing(wave.open(args.file, 'r')) as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        duration = frames / float(rate)

    # Get spectrogram dimensions
    with Image.open(f"../assets/{file_uuid}.png") as spectrogram:
        max_width, max_height = spectrogram.size

    # Detect objects
    detector = CustomObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(args.model)
    detector.setJsonPath(f"{DATASET_DIR}/json/detection_config.json")
    detector.loadModel()
    detections = detector.detectObjectsFromImage(input_image=f"{ASSETS_DIR}/{file_uuid}.png",
                                                 output_image_path=f"{ASSETS_DIR}/{file_uuid}_out.png",
                                                 minimum_percentage_probability=MIN_PREDICTION_PROBABILITY)

    # Write detections to CSV
    with open(f'../assets/{file_uuid}_out.csv', 'w') as out_file:
        fieldnames = ['name', 'probability', 'point1', 'point2', 'point3', 'point4', 'start', 'end']
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        for detection in detections:
            writer.writerow({
                'name': detection['name'],
                'probability': detection['percentage_probability'],
                'point1': detection['box_points'][0],
                'point2': detection['box_points'][1],
                'point3': detection['box_points'][2],
                'point4': detection['box_points'][3],
                'start': detection['box_points'][0] / max_width * duration,
                'end': detection['box_points'][2] / max_width * duration
            })

    print(f"Finished detections for UUID {file_uuid}")
