# Sexual Content Audio Classifier
This repository provides the means to train a neural network that can detect whether certain sounds appear in the audio track of a video.
The primary application is to detect sexual content in videos by listening for moans.

The framework can be extended to detect additional or different sounds to optimize sexual content detection.

## Requirements

### Detecting Sounds
- Python 3.7

### Training the Model
- Python 3.7
- cuda & cudnn libraries

### Creating datasets
- Python 3.7
- [Praat](https://www.praat.org/) as a command line program.

## Setup
- Create a virtual environment and install the required packages from requirements.txt.

### Detecting sounds
- Execute `src/predict.py` with `-f path/to/audio_file -m path/to/model`.
- Pre-trained models are included with this repository.

### Training the model
- Change parameters in `src/config.py` if necessary.
- Execute `src/train.py`.
- Execute `src/validate.py`.
- The trained models can be found in the dataset directory under `models`.

### Creating datasets
`python src/create_dataset_script.py -m train -f urls_train.txt -d dataset`

The mode can be `train` or `validation` to create the training and validation datasets.
The URL file must contain one URL per line. For each URL the audio track is downloaded and used to create the data.
The resulting data is saved to the dataset directory.

The annotation of the spectrogram has to be done by hand with Praat.
A tutorial for annotating with Praat can be found [here](https://www.youtube.com/watch?v=zm5fqASjtWQ).
The default tiers should be replaced by a single tier named `sound`.
The tier should only contain the label 'Moan', wherever a moan is present on the audio track.
The annotated TextGrid file has to be saved to the asset directory.

## Pre-trained dataset
The data set on which the accompanying paper was trained is included in the repository as a release.
The data is split into two subsets, `train` and `validation`. 
Both sets have an `images` and an `annotations` folder.
The `models` folder contains all pre-trained models created from the data set.
Finally, in `log.csv`, the mapping of UUIDs to URLs the data was extracted from can be found.