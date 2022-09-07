import argparse
import csv
from dataclasses import dataclass


@dataclass
class BoundingBox:
    start: float
    end: float


class Detection:
    start: float
    end: float

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __lt__(self, other):
        return self.start < other.start


# Analyse a prediction output and aggregate bounding boxes
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse prediction file")
    parser.add_argument("-f", "--file", help="Prediction file to read from", required=True)
    parser.add_argument("-p", "--period", help="Period to aggregate bounding boxes within", required=True, type=float)
    args = parser.parse_args()

    # Read logfile
    with open(args.file, 'r') as log:
        fieldnames = ['name', 'probability', 'point1', 'point2', 'point3', 'point4', 'start', 'end']
        logreader = csv.DictReader(log, fieldnames=fieldnames)

        # Skip header
        next(logreader, None)

        # Fill detections
        detections = []
        for row in logreader:
            detections.append(row)

        # Convert start and end to float
        converted_detections = sorted(
            [Detection(float(detection['start']), float(detection['end'])) for detection in detections])

        bounding_boxes = []
        last_timestamp = 0
        for detection in converted_detections:
            # Add new detection if current bounding box is more than period seconds apart from last bounding box
            # Or if there aren't any bounding boxes yet
            if detection.start - last_timestamp > args.period or len(bounding_boxes) == 0:
                bounding_boxes.append(BoundingBox(detection.start, detection.end))
                last_timestamp = detection.end
            # Else extend the last detection
            elif detection.start - last_timestamp >= 0:
                bounding_boxes[len(bounding_boxes) - 1].end = detection.end
                last_timestamp = detection.end
            else:
                raise Exception('Invalid detection')

        for bounding_box in bounding_boxes:
            print(f"{bounding_box.start},{bounding_box.end}")
