import os
import sys
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Assume these are in your src folder
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *

logger = get_logger(__name__)

class RecommendationHelpers:
    def __init__(self):
        try:
            logger.info("Loading artifacts for recommendation helpers...")
            self.model = load_model(MODEL_PATH)
            
            self.merged_df = pd.read_csv(MERGED_DATA_CSV)
            
            self.user_to_encoded = joblib.load(USER_TO_ENCODED_PKL)
            self.encoded_to_user = joblib.load(ENCODED_TO_USER_PKL)
            self.game_to_encoded = joblib.load(GAME_TO_ENCODED_PKL)
            self.encoded_to_game = joblib.load(ENCODED_TO_GAME_PKL)
            
            self.user_embeddings = self.model.get_layer('user_embedding').get_weights()[0]
            self.user_embeddings = self.user_embeddings / np.linalg.norm(self.user_embeddings, axis=1).reshape((-1, 1))
            
            self.game_embeddings = self.model.get_layer('game_embedding').get_weights()[0]
            self.game_embeddings = self.game_embeddings / np.linalg.norm(self.game_embeddings, axis=1).reshape((-1, 1))

            logger.info("Recommendation helpers loaded successfully.")
        except Exception as e:
            raise CustomException(e, sys)

    def find_similar_games(self, name, n=10):
        try:
            # --- FIX WAS HERE ---
            # The error occurs if '.value' is used instead of '.values'.
            # Also, the column name from the merged data is 'GameName_x'.
            game_id = self.merged_df[self.merged_df['GameName_x'] == name]['appid'].values[0]
            encoded_id = self.game_to_encoded[game_id]

            dists = np.dot(self.game_embeddings, self.game_embeddings[encoded_id])
            sorted_dists = np.argsort(dists)
            closest = sorted_dists[-n-1:-1]
            
            similar_games = []
            for c in reversed(closest):
                decoded_id = self.encoded_to_game[c]
                game_name = self.merged_df[self.merged_df['appid'] == decoded_id]['GameName_x'].values[0]
                similar_games.append(game_name)
            
            # Using list(set(...)) to ensure unique game recommendations
            return pd.DataFrame(list(set(similar_games)), columns=['Similar Games'])
        except (IndexError, KeyError) as e:
            logger.error(f"Error finding similar games for '{name}': {e}")
            return None

    def find_similar_users(self, user_id, n=10):
        try:
            encoded_id = self.user_to_encoded[user_id]
            dists = np.dot(self.user_embeddings, self.user_embeddings[encoded_id])
            sorted_dists = np.argsort(dists)
            closest = sorted_dists[-n-1:-1]
            similar_users = [self.encoded_to_user[c] for c in reversed(closest)]
            return pd.DataFrame(similar_users, columns=['Similar Users'])
        except KeyError:
            logger.error(f"User '{user_id}' not found.")
            return None

    def get_user_preferences(self, user_id):
        games_played = self.merged_df[self.merged_df["UserID"] == user_id]
        if games_played.empty:
            return pd.DataFrame(columns=['GameName_x'])
        rating_percentile = np.percentile(games_played.rating_normalized, 75)
        top_games = games_played[games_played["rating_normalized"] >= rating_percentile]
        return top_games.sort_values("rating_normalized", ascending=False)

    def get_user_recommendations(self, user_id, n=10):
        similar_users_df = self.find_similar_users(user_id)
        if similar_users_df is None: return None
        
        similar_users = similar_users_df['Similar Users'].tolist()
        user_played_games = self.get_user_preferences(user_id)['GameName_x'].tolist()
        
        recommended_games = []
        for other_user in similar_users:
            top_games = self.get_user_preferences(other_user)
            recommended_games.extend(top_games['GameName_x'].tolist())

        rec_counts = pd.Series(recommended_games).value_counts()
        rec_counts = rec_counts[~rec_counts.index.isin(user_played_games)]
        
        return pd.DataFrame(rec_counts.head(n)).reset_index().rename(columns={'index': 'Recommended Game', 0: 'Recommendation Score'})
