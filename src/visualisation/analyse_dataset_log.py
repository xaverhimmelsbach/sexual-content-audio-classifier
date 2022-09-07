import argparse
import csv
from dataclasses import dataclass


@dataclass
class Result:
    count: int
    duration: int


# Analyse a data set creation log file and output the number of files and total duration
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse data set log file")
    parser.add_argument("-f", "--file", help="Data set logfile to read from", required=True)
    args = parser.parse_args()

    train = Result(0, 0)
    validation = Result(0, 0)

    # Accumulate video durations
    with open(args.file, 'r') as log:
        logreader = csv.reader(log)
        for row in logreader:
            if row[0] == 'train':
                train.count += 1
                train.duration += int(row[3])
            elif row[0] == 'validation':
                validation.count += 1
                validation.duration += int(row[3])

    print(f'train: {train.count} videos with duration of {train.duration} seconds')
    print(f'validation: {validation.count} videos with duration of {validation.duration} seconds')
