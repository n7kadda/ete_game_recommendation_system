import os
import sys
import pandas as pd
import numpy as np
import joblib
import re
from sklearn.model_selection import train_test_split
# Assume these are in your src folder
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *

logger = get_logger(__name__)

class DataPreprocessor:
    def __init__(self, interaction_file, metadata_file, output_dir):
        self.interaction_file = interaction_file
        self.metadata_file = metadata_file
        self.output_dir = output_dir
        self.merged_df = None
        self.user_to_encoded = {}
        self.encoded_to_user = {}
        self.game_to_encoded = {}
        self.encoded_to_game = {}
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Initialized DataPreprocessor...")

    def load_data(self):
        try:
            logger.info("Loading interaction data...")
            interaction_cols = ['UserID', 'GameName', 'Action', 'HoursPlayed', 'Dummy']
            df_interaction = pd.read_csv(self.interaction_file, header=None, names=interaction_cols)
            df_interaction.drop('Dummy', axis=1, inplace=True)
            df_play = df_interaction[df_interaction['Action'] == 'play'].copy()
            df_play.drop('Action', axis=1, inplace=True)

            logger.info("Loading metadata data...")
            df_metadata = pd.read_csv(self.metadata_file)
            df_game_info = df_metadata[['appid', 'name', 'genres']].copy()
            df_game_info.rename(columns={'name': 'GameName'}, inplace=True)
            return df_play, df_game_info
        except Exception as e:
            raise CustomException(e, sys)

    def merge_data(self, df_play, df_game_info):
        try:
            logger.info("Merging interaction and metadata data...")
            # --- CRITICAL FIX ---
            # Clean game names thoroughly to ensure a successful merge
            def clean_name(name):
                if isinstance(name, str):
                    return re.sub(r'[^A-Za-z0-9]+', '', name).lower()
                return ''
            
            df_play['clean_name'] = df_play['GameName'].apply(clean_name)
            df_game_info['clean_name'] = df_game_info['GameName'].apply(clean_name)

            self.merged_df = pd.merge(df_play, df_game_info, on='clean_name', how='inner')
            self.merged_df.drop(columns=['clean_name'], inplace=True)

            if self.merged_df.empty:
                raise ValueError("Merge resulted in an empty DataFrame. Please check the raw data files.")
            
            logger.info(f"Merged data shape: {self.merged_df.shape}")
        except Exception as e:
            raise CustomException(e, sys)

    def create_ratings(self):
        try:
            logger.info("Creating ratings data...")
            self.merged_df['ImplicitRating'] = np.log1p(self.merged_df['HoursPlayed'])
            min_rating = self.merged_df['ImplicitRating'].min()
            max_rating = self.merged_df['ImplicitRating'].max()
            self.merged_df['rating_normalized'] = self.merged_df['ImplicitRating'].apply(
                lambda x: (x - min_rating) / (max_rating - min_rating)
            ).values.astype(np.float64)
        except Exception as e:
            raise CustomException(e, sys)

    def encode_and_split(self, test_size=0.2, random_state=42):
        try:
            logger.info("Encoding and splitting data...")
            user_ids = self.merged_df["UserID"].unique().tolist()
            self.user_to_encoded = {x: i for i, x in enumerate(user_ids)}
            self.encoded_to_user = {i: x for i, x in enumerate(user_ids)}
            self.merged_df["user_encoded"] = self.merged_df["UserID"].map(self.user_to_encoded)

            game_ids = self.merged_df["appid"].unique().tolist()
            self.game_to_encoded = {x: i for i, x in enumerate(game_ids)}
            self.encoded_to_game = {i: x for i, x in enumerate(game_ids)}
            self.merged_df["game_encoded"] = self.merged_df["appid"].map(self.game_to_encoded)

            X = self.merged_df[["user_encoded","game_encoded"]].values
            y = self.merged_df["rating_normalized"].values
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
            
            self.X_train_array = [X_train[:,0], X_train[:, 1]]
            self.X_test_array = [X_test[:,0], X_test[:, 1]]
            self.y_train = y_train
            self.y_test = y_test
        except Exception as e:
            raise CustomException(e, sys)

    def save_artifacts(self):
        try:
            logger.info("Saving artifacts...")
            joblib.dump(self.user_to_encoded, USER_TO_ENCODED_PKL)
            joblib.dump(self.encoded_to_user, ENCODED_TO_USER_PKL)
            joblib.dump(self.game_to_encoded, GAME_TO_ENCODED_PKL)
            joblib.dump(self.encoded_to_game, ENCODED_TO_GAME_PKL)
            joblib.dump(self.X_train_array, X_TRAIN_PKL)
            joblib.dump(self.X_test_array, X_TEST_PKL)
            joblib.dump(self.y_train, Y_TRAIN_PKL)
            joblib.dump(self.y_test, Y_TEST_PKL)
            self.merged_df.to_csv(MERGED_DATA_CSV, index=False)
            logger.info("All artifacts saved successfully.")
        except Exception as e:
            raise CustomException(e, sys)

    def run(self):
        try:
            df_play, df_game_info = self.load_data()
            self.merge_data(df_play, df_game_info)
            self.create_ratings()
            self.encode_and_split()
            self.save_artifacts()
            logger.info("Data Processing successfully completed")
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    if not os.path.exists(INTERACTION_DATA_CSV) or not os.path.exists(METADATA_CSV):
        print(f"Please ensure '{os.path.basename(INTERACTION_DATA_CSV)}' and '{os.path.basename(METADATA_CSV)}' are in the '{RAW_DIR}' directory.")
    else:
        data_processor = DataPreprocessor(
            interaction_file=INTERACTION_DATA_CSV,
            metadata_file=METADATA_CSV,
            output_dir=PROCESSED_DIR
        )
        data_processor.run()
