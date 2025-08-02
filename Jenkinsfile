pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'game-reco'
        GCLOUD_PATH = "/usr/lib/google-cloud-sdk/bin"
        KUBECTL_PATH = "/usr/lib/google-cloud-sdk/bin"
    } 

    stages{
        stage("Cloning from github"){
            steps{
                script{
                    echo 'Cloning the repository from Github'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/n7kadda/ete_game_recommendation_system.git']])
                }
            }
        }
        stage("Making a virtual environment........"){
            steps{
                script{
                    echo 'Making a virtual environment'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc 
                    '''
                }
            }
        }
        stage('DVC PULL'){
            steps{
                withCredentials([file(credentialsId:'gcp-key',  variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script{
                        echo 'Pulling DVC data'
                        sh '''
                        . ${VENV_DIR}/bin/activate
                        dvc pull
                        '''
                    }
                }
            }
        }
        stage('Build and push image to gcr'){
            steps{
                withCredentials([file(credentialsId:'gcp-key',  variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script{
                        echo 'Build and push image to gcr'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/game-reco-system:latest .
                        docker push gcr.io/${GCP_PROJECT}/game-reco-system:latest
                        '''
                    }
                }
            }
        }
        stage('Deploy to Kubernetes'){
            steps{
                withCredentials([file(credentialsId:'gcp-key',  variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script{
                        echo 'Deploy to Kubernetes'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials game-app-cluster --region us-central1
                        kubectl apply -f deployment.yaml
                    
                        '''
                    }
                }
            }
        }
    }
}
