import os
import sys
import pandas as pd
# Assume these are in your src folder
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.helpers import RecommendationHelpers # Import the helper class

logger = get_logger(__name__)

class PredictionPipeline:
    def __init__(self):
        try:
            # Create an instance of the helper class
            self.helpers = RecommendationHelpers()
            logger.info("Prediction pipeline initialized with recommendation helpers.")
        except Exception as e:
            raise CustomException(e, sys)

    def hybrid_recommendation(self, user_id, n=10, user_weight=1.0, content_weight=0.5):
        try:
            logger.info(f"Generating hybrid recommendations for user: {user_id}")
            # 1. Get user-based recommendations from the helper
            user_recs_df = self.helpers.get_user_recommendations(user_id, n=20)
            if user_recs_df is None:
                return "User not found."
            user_recs = user_recs_df['Recommended Game'].tolist()
            
            # 2. Get content-based recommendations from the helper
            user_top_games = self.helpers.get_user_preferences(user_id)['GameName_x'].tolist()
            content_recs = []
            for game_name in user_top_games[:5]:
                similar_games = self.helpers.find_similar_games(game_name)
                if similar_games is not None:
                    content_recs.extend(similar_games['Similar Games'].tolist())

            # 3. Combine and re-rank
            combined_scores = {}
            for i, game in enumerate(user_recs):
                score = user_weight * (1 / (i + 1))
                combined_scores[game] = combined_scores.get(game, 0) + score
            
            for i, game in enumerate(content_recs):
                score = content_weight * (1 / (i + 1))
                combined_scores[game] = combined_scores.get(game, 0) + score

            sorted_recs = sorted(combined_scores.items(), key=lambda item: item[1], reverse=True)
            final_recs = [(rec, score) for rec, score in sorted_recs if rec not in user_top_games]
            
            logger.info(f"Successfully generated {len(final_recs[:n])} recommendations.")
            return pd.DataFrame(final_recs[:n], columns=['Recommended Game', 'Hybrid Score'])
        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        # Example of how to use the pipeline
        pipeline = PredictionPipeline()
        test_user_id = 151603712
        
        print(f"--- Recommendations for User {test_user_id} ---")
        recommendations = pipeline.hybrid_recommendation(test_user_id)
        print(recommendations)

    except Exception as e:
        logger.error(f"An error occurred during pipeline execution: {e}")
