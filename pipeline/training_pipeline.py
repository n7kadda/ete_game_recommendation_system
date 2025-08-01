import os
from utils.common_functions import read_yaml
from config.paths_config import *
from src.data_preprocessing import DataPreprocessor
from src.data_ingestion import DataIngestion
from src.model_training import ModelTrainer
from src.logger import get_logger
from src.custom_exception import CustomException








if __name__ == "__main__":
#    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
#    data_ingestion.run()
# We will not use this as already have the data in dvc

    data_processor = DataPreprocessor(
            interaction_file=INTERACTION_DATA_CSV,
            metadata_file=METADATA_CSV,
            output_dir=PROCESSED_DIR
        )
    data_processor.run()
    model_trainer = ModelTrainer(PROCESSED_DIR)
    model_trainer.train_model()