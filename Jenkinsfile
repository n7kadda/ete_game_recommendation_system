pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
    } 

    stages{
        stage("Colning from github"){
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
                withCredentials([file(credentialsID:'gcp-key',  variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
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
}