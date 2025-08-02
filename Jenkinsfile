pipeline{
    agent any

    stages{
        stage("Colning from github"){
            steps{
                script{
                    echo 'Cloning the repository from Github'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/n7kadda/ete_game_recommendation_system.git']])
                }
            }
        }
    }
}