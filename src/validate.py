import os.path
import time
from src.config import DATASET_DIR, DONE_FILE

from imageai.Detection.Custom import DetectionModelTrainer
from prevent_cublas_crash import prevent_cublas_crash

if __name__ == '__main__':
    # Check periodically if training.py has finished
    while not os.path.isfile(f'{DATASET_DIR}/{DONE_FILE}'):
        print(f'Checked done file ({DATASET_DIR}/{DONE_FILE}), doesn\'t exist yet')
        time.sleep(300)

    # Prevent cublas crash by activating memory growth
    prevent_cublas_crash()

    # Validate models
    trainer = DetectionModelTrainer()
    trainer.setModelTypeAsYOLOv3()
    trainer.setDataDirectory(data_directory=DATASET_DIR)
    trainer.evaluateModel(model_path=f"{DATASET_DIR}/models", json_path=f"{DATASET_DIR}/json/detection_config.json",
                          iou_threshold=0.5, object_threshold=0.3, nms_threshold=0.5)
