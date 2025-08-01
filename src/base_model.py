import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dot, Flatten, Dense, Activation, BatchNormalization
from utils.common_functions import read_yaml
from src.logger import get_logger
from src.custom_exception import CustomException
import sys

logger = get_logger(__name__)

class BaseModel:
    def __init__(self, config_path):
        try:
            self.config = read_yaml(config_path)
            logger.info("Model configuration loaded successfully")
        except Exception as e:
            raise CustomException(e, sys)
            
    def RecommenderNet(self,n_users, n_games):
        try:
            embedding_dim = self.config['model']['embedding_size']
            user_input = Input(shape=[1], name="user_input")
            user_embedding = Embedding(n_users, embedding_dim, name="user_embedding")(user_input)
            user_vec = Flatten(name="flatten_user")(user_embedding)

            game_input = Input(shape=[1], name="game_input")
            game_embedding = Embedding(n_games, embedding_dim, name="game_embedding")(game_input)
            game_vec = Flatten(name="flatten_game")(game_embedding)

            dot_product = Dot(axes=1, name="dot_product")([user_vec, game_vec])

            output = Dense(1, activation="sigmoid", name="output")(dot_product)

            model = Model(inputs=[user_input, game_input], outputs=output)
            model.compile(
                loss = self.config['model']['loss'],
                optimizer = self.config['model']['optimizer'],
                metrics = self.config['model']['metrics']
                )
            logger.info("RecommenderNet model compiled successfully")
            return model
        except Exception as e:
            raise CustomException(e, sys)
