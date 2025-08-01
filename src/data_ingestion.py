import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_names = self.config["bucket_file_names"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Initialized DataIngestion with bucket: {self.bucket_name} and files: {self.file_names}")

    def download_data(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR, file_name)
                blob = bucket.blob(file_name)
                blob.download_to_filename(file_path)
                logger.info(f"Downloaded {file_name} to {file_path}") 
        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            raise CustomException(f"Failed to download data from bucket {self.bucket_name}: {e}")
    def run(self):
        try:
            logger.info("Starting data ingestion process...")
            self.download_data()
            logger.info("Data ingestion completed successfully.")
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            raise CustomException(f"Data ingestion process failed: {e}")
        finally:
            logger.info("Data ingestion process finished.")
            print("Data ingestion process finished.")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()


