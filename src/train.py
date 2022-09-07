import tensorflow.python.client.device_lib as device_lib
from imageai.Detection.Custom import DetectionModelTrainer
from prevent_cublas_crash import prevent_cublas_crash
from src.config import CLASSES, DATASET_DIR, DONE_FILE

if __name__ == '__main__':
    # Prevent cublas crash by activating memory growth
    prevent_cublas_crash()

    # GPU is only detected if conda is used and libcusolver.so.10 is linked to libcusolver.so.11
    print(device_lib.list_local_devices())

    # Train model
    trainer = DetectionModelTrainer()
    trainer.setModelTypeAsYOLOv3()
    trainer.setDataDirectory(data_directory=DATASET_DIR)
    trainer.setTrainConfig(object_names_array=CLASSES, batch_size=1, num_experiments=200)
    trainer.trainModel()

    # Signal to validate.py that training is done
    open(f'{DATASET_DIR}/{DONE_FILE}', 'a').close()
