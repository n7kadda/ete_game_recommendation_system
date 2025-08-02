# End-to-End Game Recommender System

This repository contains the code for an end-to-end MLOps project that builds, trains, and deploys a hybrid game recommender system. The system learns from user playtime data to provide personalized game recommendations and is deployed as a web application using a complete CI/CD pipeline.

## 🚀 Features

- **Hybrid Recommendation Model**: Combines collaborative filtering (what similar users play) and content-based filtering (what games are similar) using a neural network-based matrix factorization model built with TensorFlow/Keras.
- **Data Preprocessing Pipeline**: A robust script to clean, merge, and transform raw user interaction and game metadata into a model-ready format.
- **DVC for Data Versioning**: Uses Data Version Control (DVC) to manage large data files and track data versions, with Google Cloud Storage (GCS) as the remote storage backend.
- **CI/CD with Jenkins**: A complete Jenkins pipeline (`Jenkinsfile`) that automates the entire workflow:
    - Cloning the repository.
    - Setting up a Python environment.
    - Pulling data from DVC.
    - Building the application's Docker image.
    - Pushing the image to Google Container Registry (GCR).
    - Deploying the application to Google Kubernetes Engine (GKE).
- **Containerization**: The application is containerized using Docker for consistent and reproducible deployments.
- **Flask Web Application**: A simple web interface built with Flask to serve the recommendations.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **ML/Data Science**: TensorFlow/Keras, Pandas, NumPy, Scikit-learn
- **MLOps & CI/CD**: Jenkins, Docker, DVC, Kubernetes (GKE)
- **Cloud**: Google Cloud Platform (GCP) for GCS and GKE

## 📂 Project Structure

```
├── artifacts/                # Stores all data, models, and processed files
├── config/                   # Configuration files (e.g., paths)
├── custom_jenkins/           # Dockerfile for the custom Jenkins environment
├── src/                      # Source code for the project
│   ├── components/           # Modular components of the pipeline (data processing, training)
│   ├── pipeline/             # Main pipeline scripts
│   ├── logger.py             # Custom logger
│   └── custom_exception.py   # Custom exception handling
├── templates/                # HTML templates for the Flask app
├── application.py            # Main Flask application entry point
├── Dockerfile                # Dockerfile for the Flask application
├── Jenkinsfile               # Jenkins pipeline definition
├── deployment.yml            # Kubernetes deployment configuration
├── dvc.yaml                  # DVC pipeline definition
├── requirements.txt          # Python dependencies
└── setup.py                  # Project setup script
```

## ⚙️ Setup and Installation

Follow these steps to set up the project locally and prepare the Jenkins environment.

### 1. Clone the Repository
```bash
git clone [https://github.com/n7kadda/ete_game_recommendation_system.git](https://github.com/n7kadda/ete_game_recommendation_system.git)
cd ete_game_recommendation_system
```

### 2. Set Up Python Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 3. Configure DVC with Google Cloud Storage
You will need a Google Cloud account and a GCS bucket.

```bash
# Log in to your Google Cloud account
gcloud auth application-default login

# Initialize DVC
dvc init

# Add your GCS bucket as the remote storage
dvc remote add -d myremote gs://<your-gcs-bucket-name>/

# Set the GCP project for DVC
dvc remote modify myremote project <your-gcp-project-id>

# Pull the data from the remote storage
dvc pull
```

### 4. Set Up the Custom Jenkins Container
This project uses a custom Jenkins image with Docker and other tools pre-installed.

**Prerequisites**: Docker Desktop must be installed and running.

1.  **Navigate to the `custom_jenkins` directory:**
    ```bash
    cd custom_jenkins
    ```

2.  **Build the Jenkins Docker image:**
    ```bash
    docker build -t jenkins-dind .
    ```

3.  **Run the Jenkins container:**
    ```bash
    docker run -d --name jenkins-dind --privileged -p 8080:8080 -p 50000:50000 -v /var/run/docker.sock:/var/run/docker.sock -v jenkins_home:/var/jenkins_home jenkins-dind
    ```

4.  **Get the Initial Admin Password:**
    Wait a minute for Jenkins to start, then get the password from the logs.
    ```bash
    docker logs jenkins-dind
    ```
    Copy the password from the output.

5.  **Complete Jenkins Setup:**
    - Open your browser and go to `http://localhost:8080`.
    - Paste the password and follow the setup wizard (install suggested plugins and create your admin user).

## 🚀 How to Run the Pipeline

### 1. Manual Pipeline Execution
You can run the data processing and training pipelines manually from your terminal.

**a. Run the Data Preprocessing Pipeline:**
This will clean the data, create ratings, and save all artifacts to the `artifacts/processed` directory.
```bash
python src/data_preprocessing.py
```

**b. Run the Model Training Pipeline:**
This will load the processed data and train the neural network model.
```bash
python src/model_training.py
```

### 2. CI/CD Pipeline with Jenkins

1.  **Configure Jenkins:**
    - Go to your Jenkins dashboard (`http://localhost:8080`).
    - Create a **New Item**, name it (e.g., `game-reco-pipeline`), and select **Pipeline**.
    - In the configuration, scroll down to the **Pipeline** section.
    - Set **Definition** to **"Pipeline script from SCM"**.
    - Set **SCM** to **"Git"**.
    - **Repository URL**: `https://github.com/n7kadda/ete_game_recommendation_system.git`
    - **Credentials**: Add your GitHub credentials.
    - **Script Path**: `Jenkinsfile`
    - Save the pipeline.

2.  **Run the Build:**
    - Click **"Build Now"** on the pipeline's main page to start the CI/CD process.

## 🧠 Prediction Pipeline Usage

To get recommendations, you can use the `PredictionPipeline` class.

```python
from src.prediction_pipeline import PredictionPipeline

# Initialize the pipeline (loads the model and all artifacts)
pipeline = PredictionPipeline()

# Get recommendations for a user
user_id = 151603712
recommendations = pipeline.hybrid_recommendation(user_id)

print(recommendations)
