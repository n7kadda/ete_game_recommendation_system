import os

RAW_DIR = "artifacts/raw"
CONFIG_PATH = "config/config.yaml"


import os

PROCESSED_DIR = "artifacts/processed"

INTERACTION_DATA_CSV = os.path.join(RAW_DIR, "steam-200k.csv")
METADATA_CSV = os.path.join(RAW_DIR, "steam.csv")


MERGED_DATA_CSV = os.path.join(PROCESSED_DIR, "merged_game_data.csv")

USER_TO_ENCODED_PKL = os.path.join(PROCESSED_DIR, "user_to_encoded.pkl")
ENCODED_TO_USER_PKL = os.path.join(PROCESSED_DIR, "encoded_to_user.pkl")
GAME_TO_ENCODED_PKL = os.path.join(PROCESSED_DIR, "game_to_encoded.pkl")
ENCODED_TO_GAME_PKL = os.path.join(PROCESSED_DIR, "encoded_to_game.pkl")

X_TRAIN_PKL = os.path.join(PROCESSED_DIR, "X_train.pkl")
X_TEST_PKL = os.path.join(PROCESSED_DIR, "X_test.pkl")
Y_TRAIN_PKL = os.path.join(PROCESSED_DIR, "y_train.pkl")
Y_TEST_PKL = os.path.join(PROCESSED_DIR, "y_test.pkl")

MODEL_DIR = "artifacts/models"
WEIGHTS_DIR = "artifacts/weights"
MODEL_PATH = os.path.join(MODEL_DIR, "model.h5")
GAME_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "game_weights.pkl")
USER_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "user_weights.pkl")
CHECKPOINT_FILE_PATH = "artifacts/checkpoints/weights.weights.h5"
