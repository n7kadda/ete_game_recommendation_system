import joblib
import comet_ml
import numpy as np
import os
import sys
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
from src.logger import get_logger
from src.custom_exception import CustomException
from src.base_model import BaseModel
from config.paths_config import *

logger = get_logger(__name__)

class ModelTrainer:
    def __init__(self,data_path):
        self.data_path = data_path

        self.experiment = comet_ml.Experiment(
            api_key="OSCeElC3kQjRl4GosqgsO5FvD",
            project_name="game-reco",
            workspace = "n7kadda"
        )
        logger.info(f"Initialized ModelTrainer and comet ml with data path: {self.data_path}")

    def load_data(self):
        try:
            logger.info("Loading data...............")
            X_train_array = joblib.load(X_TRAIN_PKL)
            X_test_array = joblib.load(X_TEST_PKL)
            y_train_array = joblib.load(Y_TRAIN_PKL)
            y_test_array = joblib.load(Y_TEST_PKL)
            logger.info("Data loaded successfully for training.")
            return X_train_array, X_test_array, y_train_array, y_test_array
        except Exception as e:
            raise CustomException(e, sys)
    
    def train_model(self):
        try:
            X_train_array, X_test_array, y_train_array, y_test_array = self.load_data()
            
            n_users = len(joblib.load(USER_TO_ENCODED_PKL))
            n_games = len(joblib.load(GAME_TO_ENCODED_PKL))

            base_model = BaseModel(config_path=CONFIG_PATH)

            model = base_model.RecommenderNet(n_users=n_users,n_games=n_games)

            start_lr = 0.00001
            min_lr = 0.0001
            max_lr = 0.00005
            batch_size = 64

            ramup_epochs = 5
            sustain_epochs = 0
            exp_decay = 0.8

            def lrfn(epoch):
                if epoch<ramup_epochs:
                    return (max_lr - start_lr) / ramup_epochs * epoch + start_lr
                elif epoch<ramup_epochs+sustain_epochs:
                    return max_lr
                else:
                    return (max_lr - min_lr) * exp_decay**(epoch-ramup_epochs-sustain_epochs) + min_lr
                
            lr_callback = LearningRateScheduler(lambda epoch:lrfn(epoch) , verbose=0)

            model_checkpoint = ModelCheckpoint(filepath=CHECKPOINT_FILE_PATH,save_weights_only=True,monitor="val_loss",mode="min",save_best_only=True)

            early_stopping = EarlyStopping(patience=3,monitor="val_loss",mode="min",restore_best_weights=True)

            my_callbacks = [model_checkpoint,lr_callback,early_stopping]

            os.makedirs(os.path.dirname(CHECKPOINT_FILE_PATH),exist_ok=True)
            os.makedirs(MODEL_DIR,exist_ok=True)
            os.makedirs(WEIGHTS_DIR,exist_ok=True)

            try:
                history = model.fit(
                        x=X_train_array,
                        y=y_train_array,
                        batch_size=batch_size,
                        epochs=20,
                        verbose=1,
                        validation_data = (X_test_array,y_test_array),
                        callbacks=my_callbacks
                    )
                model.load_weights(CHECKPOINT_FILE_PATH)
                logger.info("Model training Completedd.....")

                for epoch in range(len(history.history['loss'])):
                    train_loss = history.history['loss'][epoch]
                    val_loss = history.history['val_loss'][epoch]
                    self.experiment.log_metric("train_loss", train_loss, step=epoch)
                    self.experiment.log_metric("val_loss", val_loss, step=epoch)






            except Exception as e:
                logger.error(f"Error training model: {e}")
                raise CustomException(e, sys)
            self.save_model_weights(model)
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise CustomException(e, sys)

    def extract_weights(self, layer_name,model):
        try:
            weight_layer = model.get_layer(layer_name)
            weights = weight_layer.get_weights()[0]
            weights = weights / np.linalg.norm(weights, axis=1).reshape((-1, 1))
            logger.info(f"Weights extracted successfully for layer: {layer_name}") 
            return weights
        except Exception as e:
            logger.error(f"Error extracting weights: {e}")
            raise CustomException(e, sys)
        
    def save_model_weights(self,model):
        try:
            model.save(MODEL_PATH)
            logger.info("Model weights saved successfully.")
            
            user_weights = self.extract_weights("user_embedding",model)
            game_weights = self.extract_weights("game_embedding",model)

            joblib.dump(user_weights, USER_WEIGHTS_PATH)
            joblib.dump(game_weights, GAME_WEIGHTS_PATH)
            
            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)
            self.experiment.log_asset(GAME_WEIGHTS_PATH)
            
            
            logger.info("User and game weights saved successfully.")
        except Exception as e:
            logger.error(str(e))
            raise CustomException(e, sys)
        
if __name__ == "__main__":
    model_trainer = ModelTrainer(PROCESSED_DIR)
    model_trainer.train_model()
